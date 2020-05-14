# -*- coding: utf-8 -*-

from datetime import datetime
from pyexcel_ods3 import save_data
from collections import OrderedDict
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Main.models import Reports, Columns, Lines, Cells
from .tools import isfloat, save_cell, fill_cell
from .decorators import superuser_only
import os
import mimetypes

######################################################################################################################


@login_required
def index(request):
    if request.user.is_superuser:
        report_list = Reports.objects.all()
    else:
        report_list = Reports.objects.filter(Published=True)
    context = {'report_list': report_list, }
    return render(request, 'index.html', context)


######################################################################################################################


def login(request):
    # Вход пользователя
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect(request.POST['next'])
        else:
            messages.info(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        if request.GET.get('next'):
            context = {'next': request.GET.get('next'), }
        else:
            context = {'next': settings.SUCCESS_URL, }
        return render(request, 'login.html', context)


######################################################################################################################


def logout(request):
    # Выход пользователя
    auth.logout(request)
    return redirect(reverse('index'))


######################################################################################################################


@login_required
def report_show(request, report_id):
    if request.user.is_superuser:
        return redirect(reverse('report_total', args=(report_id,)))
    else:
        report = get_object_or_404(Reports, id=report_id)
        if request.GET:
            context = {'table': lines_show(request, report)}
            return render(request, 'lines_show.html', context)
        else:
            context = {'report': report, 'breadcrumb': 'Просмотр таблицы "' + report.TitleShort + '"', }
            columns = Columns.objects.filter(ReportID=report)
            context['columns'] = columns
            count = Lines.objects.filter(ReportID=report).filter(Editor=request.user).count()
            context['count'] = count
            if count > 0:
                line = Lines.objects.filter(ReportID=report).filter(Editor=request.user).first()
                context['line'] = line
                context['cells'] = fill_cell(line)
            return render(request, 'report_show.html', context)


######################################################################################################################


@superuser_only
def report_total_count(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    users_list = User.objects.filter(is_superuser=False).order_by('last_name')
    for column in Columns.objects.filter(ReportID=report):
        total = column_total(report, column, users_list)
        column.TotalValue = total
        column.save()

    return redirect(reverse('report_total', args=(report_id,)))


######################################################################################################################


@superuser_only
def report_total(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.GET:
        context = {'table': lines_show(request, report)}
        return render(request, 'lines_show.html', context)
    else:
        context = {'report': report, 'breadcrumb': 'Сводная таблицы "' + report.TitleShort + '"', }
        users_list = User.objects.filter(is_superuser=False).order_by('last_name')
        column_list = Columns.objects.filter(ReportID=report)
        context['column_list'] = column_list
        data_list = []
        for owner in users_list:
            count = Lines.objects.filter(ReportID=report).filter(Editor=owner).count()
            if count > 0:
                line = Lines.objects.filter(ReportID=report).filter(Editor=owner).first()
                cells = fill_cell(line)
                data_list.append([owner, count, cells, line])
        context['data_list'] = data_list
        return render(request, 'report_total.html', context)


######################################################################################################################


@superuser_only
def report_download(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    users_list = User.objects.filter(is_superuser=False).order_by('last_name')
    column_list = Columns.objects.filter(ReportID=report)
    now = datetime.now()
    file_name = 'export' + now.strftime('%y%m%d-%H%M%S') + '.ods'
    file = settings.EXPORT_FILE + file_name
    data_field = ['Центр занятости']
    for column in column_list:
        data_field.append(column.Title)
    data_field.append('Дата предоставления информации')
    data_ods = [data_field]
    for user in users_list:
        count = Lines.objects.filter(ReportID=report).filter(Editor=user).count()
        if count > 0:
            data_field = [user.get_full_name()]
            line = Lines.objects.filter(ReportID=report).filter(Editor=user).first()
            for column in column_list:
                cell = Cells.objects.filter(LineID=line).filter(ColumnID=column).first()
                value = cell.Value
                if isfloat(value):
                    value = float(value)
                    # value = float('{:.2f}'.format(value))
                data_field.append(value)
            data_field.append(line.CreateDate.strftime('%d-%m-%G'))
            data_ods.append(data_field)
    data_field = ['Итого:']
    for column in column_list:
        value = column.TotalValue
        if isfloat(value):
            value = float(value)
        data_field.append(value)
    data_ods.append(data_field)
    data = OrderedDict()
    data.update({'Данные': data_ods})
    save_data(file, data)
    fp = open(file, 'rb')
    response = HttpResponse(fp.read())
    fp.close()
    file_type = mimetypes.guess_type(file)
    if file_type is None:
        file_type = 'application/octet-stream'
    response['Content-Type'] = file_type
    response['Content-Length'] = str(os.stat(file).st_size)
    response['Content-Disposition'] = "attachment; filename=" + file_name
    os.remove(file)
    return response


######################################################################################################################


@superuser_only
def column_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column_title = request.POST['column_title']
        column_priority = request.POST['column_priority']
        column_color = request.POST['column_color']
        column_type = request.POST['column_type']
        column = Columns()
        column.Title = column_title
        column.Priority = column_priority
        column.Color = column_color
        column.TypeData = column_type
        column.ReportID = report
        column.save()
        return redirect(reverse('report_edit', args=(report.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@superuser_only
def column_edit(request, column_id):
    column = get_object_or_404(Columns, id=column_id)
    if request.POST:
        column_title = request.POST['column_title']
        column_priority = request.POST['column_priority']
        column_color = request.POST['column_color']
        column_type = request.POST['column_type']
        column_formula = request.POST['column_total']
        column.Title = column_title
        column.Priority = column_priority
        column.Color = column_color
        column.TypeData = column_type
        column.TotalFormula = column_formula
    column.save()
    return redirect(reverse('report_edit', args=(column.ReportID.id,)))


######################################################################################################################


def column_total(report, column, users_list):
    if column.TotalFormula == 1:
        total = 0
        for user in users_list:
            line = Lines.objects.filter(ReportID=report).filter(Editor=user).first()
            if line:
                cell = Cells.objects.filter(LineID=line).filter(ColumnID=column).first()
                if cell is not None:
                    try:
                        cell_value = float(cell.Value)
                    except ValueError:
                        cell_value = 0
                    total = total + cell_value
        total = float('{:.2f}'.format(total))
        return total
    else:
        return ''


######################################################################################################################


@superuser_only
def column_delete(request, column_id):
    column = get_object_or_404(Columns, id=column_id)
    report_id = column.ReportID.id
    column.delete()
    return redirect(reverse('report_edit', args=(report_id,)))


######################################################################################################################


@login_required
def line_delete(request, report_id):
    # Удаление строки автором или администратором
    if request.POST:
        line_id = request.POST['Line_ID']
        line = get_object_or_404(Lines, id=line_id)
        if line.Editor == request.user or request.user.is_superuser:
            line.delete()
    return redirect(reverse('report_show', args=(report_id,)))


######################################################################################################################


def lines_show(request, report):
    czn = int(request.GET.get('czn'))
    table = []
    lines = Lines.objects.filter(ReportID=report).filter(Editor_id=czn)
    for line in lines[1:]:
        table.append([line, fill_cell(line)])
    return table


######################################################################################################################


@login_required
def cells_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column_list = Columns.objects.filter(ReportID=report)
        last_line = Lines.objects.filter(ReportID=report).filter(Editor=request.user).first()
        line = Lines()
        line.ReportID = report
        line.Editor = request.user
        line.save()
        for column in column_list:
            cell_value = request.POST.get('column' + column.id.__str__(), '')
            if cell_value != '':
                print('Есть значение')
                if column.TotalFormula == 1:
                    cell_value = cell_value.replace(',', '.')
            print(cell_value)
            save_cell(line, column, cell_value)
    return redirect(reverse('report_show', args=(report.id,)))


######################################################################################################################
