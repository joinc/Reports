# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import auth, User
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.conf import settings
from Main.models import Reports, Columns, Lines, Cells
from .forms import FormReportCreate, FormReportEdit, FormColumn

######################################################################################################################


def superuser_only(function):
   def _inner(request, *args, **kwargs):
       if not request.user.is_superuser:
           return HttpResponseRedirect(reverse('index'))
       return function(request, *args, **kwargs)
   return _inner


######################################################################################################################

@login_required
def index(request):
    if request.user.is_superuser:
        report_list = Reports.objects.all()
    else:
        report_list = Reports.objects.filter(Published=True)
    return render(request, 'index.html', {'report_list': report_list, })

######################################################################################################################


def login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            #return redirect(request.META.get('HTTP_REFERER'))
            return redirect(settings.SUCCESS_URL)
        else:
            messages.info(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        return render(request, 'login.html')

######################################################################################################################


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))

######################################################################################################################


@superuser_only
def report_create(request):
    report_form = FormReportCreate()
    breadcrumb = 'Создание таблицы'
    if request.POST:
        report_title_short = request.POST['report_title_short']
        report_title_long = request.POST['report_title_long']
        report = Reports()
        report.TitleShort = report_title_short
        report.TitleLong = report_title_long
        report.save()
        return HttpResponseRedirect(reverse('report_edit', args=(report.id,)))
    return render(request, 'report_create.html', {'report_form': report_form, 'breadcrumb': breadcrumb, })

######################################################################################################################


@superuser_only
def report_edit(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    report_form = FormReportEdit(initial={'report_title_short': report.TitleShort,
                                          'report_title_long': report.TitleLong,
                                          'report_header': report.Header, })
    column_list = Columns.objects.filter(ReportID=report)
    column_form = FormColumn()
    breadcrumb = 'Редактирование таблицы "' + report.TitleShort + '"'
    return render(request, 'report_edit.html',
                  {'report': report, 'column_list': column_list, 'column_form': column_form,
                   'report_form': report_form, 'breadcrumb': breadcrumb, })

######################################################################################################################


@superuser_only
def report_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        report_title_short = request.POST['report_title_short']
        report_title_long = request.POST['report_title_long']
        report_header = request.POST['report_header']
        report.TitleShort = report_title_short
        report.TitleLong = report_title_long
        report.Header = report_header
        report.save()
        return HttpResponseRedirect(reverse('report_edit', args=(report.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


@login_required
def report_view(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse('report_total', args=(report.id,)))
    else:
        table = []
        column_list = Columns.objects.filter(ReportID=report)
        lines = Lines.objects.filter(ReportID=report).filter(Editor=request.user)
        if lines.count() > 0:
            for line in lines:
                cells = Cells.objects.filter(LineID=line)
                table.append([line, cells])
        last_cells = []
        for column in column_list:
            last_cells.append([column, Cells.objects.filter(LineID=lines.first()).filter(ColumnID=column).first()])

    breadcrumb = 'Просмотр таблицы "' + report.TitleShort + '"'
    return render(request, 'report.html',
                  {'report': report, 'column_list': column_list, 'last_cells': last_cells, 'table': table,
                   'breadcrumb': breadcrumb, })

######################################################################################################################


@login_required
def report_total(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.user.is_superuser:
        if request.GET:
            czn = int(request.GET.get('czn'))
            table = []
            lines = Lines.objects.filter(ReportID=report).filter(Editor_id=czn)
            for line in lines:
                cells = Cells.objects.filter(LineID=line)
                table.append([line, cells])
            return render(request, 'report_czn.html', {'table': table, })
        else:
            users = User.objects.all().order_by('last_name')
            column_list = Columns.objects.filter(ReportID=report)
            data_list = []
            total_list = []
            for column in column_list:
                if column.TypeData == 1:
                    total = 0
                    for owner in users:
                        line = Lines.objects.filter(ReportID=report).filter(Editor=owner).first()
                        cell = Cells.objects.filter(LineID=line).filter(ColumnID=column).first()
                        if cell is not None:
                            try:
                                cell_value = float(cell.Value)
                            except ValueError:
                                cell_value = 0
                            total = total + cell_value
                    total_list.append(float('{:.2f}'.format(total)))
                else:
                    total_list.append('')
            for owner in users:
                count = Lines.objects.filter(ReportID=report).filter(Editor=owner).count()
                if count > 0:
                    line = Lines.objects.filter(ReportID=report).filter(Editor=owner).first()
                    cells = Cells.objects.filter(LineID=line)
                    data_list.append([owner, count, cells, line.CreateDate])

    else:
        return HttpResponseRedirect(reverse('report_view', args=(report.id,)))
    breadcrumb = 'Сводная таблицы "' + report.TitleShort + '"'
    return render(request, 'report_total.html',
                  {'report': report, 'column_list': column_list, 'total_list': total_list, 'data_list': data_list,
                   'breadcrumb': breadcrumb, })

######################################################################################################################


@superuser_only
def report_publish(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if not report.Published:
        report.Published = True
    else:
        report.Published = False
    report.save()
    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


@superuser_only
def column_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column_title = request.POST['column_title']
        column = Columns()
        column.Title = column_title
        column.ReportID = report
        column.save()
        fill_cells(report)
        return HttpResponseRedirect(reverse('report_edit', args=(report.id,)))
    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


@superuser_only
def column_delete(request, column_id):
    column = get_object_or_404(Columns, id=column_id)
    report_id = column.ReportID.id
    column.delete()
    return HttpResponseRedirect(reverse('report_edit', args=(report_id,)))

######################################################################################################################


@login_required
def line_delete(request, line_id):
    line = get_object_or_404(Lines, id=line_id)
    if line.Editor == request.user or request.user.is_superuser:
        report_id = line.ReportID.id
        line.delete()
    return HttpResponseRedirect(reverse('report_view', args=(report_id,)))

######################################################################################################################


def cell_save(cell_line, cell_column, cell_owner, cell_value):
    # Процедура создания и заполнения значением новой ячейки

    cell = Cells()
    cell.LineID = cell_line
    cell.ColumnID = cell_column
    cell.Owner = cell_owner
    cell.Value = cell_value
    cell.save()

######################################################################################################################


@login_required
def cells_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column_list = Columns.objects.filter(ReportID=report)
        line = Lines()
        line.ReportID = report
        line.Editor = request.user
        line.save()
        for column in column_list:
            cell_value = request.POST['column'+column.id.__str__()]
            if cell_value:
                cell_value = cell_value.replace(',', '.')
                cell_save(line, column, request.user, cell_value)
            else:
                cell_save(line, column, request.user, '')
        return HttpResponseRedirect(reverse('report_view', args=(report.id,)))
    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def fill_cells(report):
    user_list = User.objects.all()
    for p_user in user_list:
        if not p_user.is_superuser:
            column_list = Columns.objects.filter(ReportID=report)
            line_list = Lines.objects.filter(Editor=p_user).filter(ReportID=report)
            if line_list.count() == 0:
                line = Lines()
                line.ReportID = report
                line.Editor = p_user
                line.save()
                for column in column_list:
                    cell_save(line, column, p_user, '')
            else:
                for line in line_list:
                    for column in column_list:
                        if Cells.objects.filter(LineID=line).filter(ColumnID=column).filter(Owner=p_user).count() == 0:
                            cell_save(line, column, p_user, '')

