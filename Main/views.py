# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Main.models import Reports, Columns, Lines, Cells
from .tools import save_cell, isfloat

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
def line_delete(request, report_id):
    # Удаление строки автором или администратором
    if request.POST:
        line_id = request.POST['Line_ID']
        line = get_object_or_404(Lines, id=line_id)
        if line.Editor == request.user or request.user.is_superuser:
            column_list = Columns.objects.filter(ReportID=line.ReportID)
            if Lines.objects.filter(ReportID=line.ReportID).filter(Editor=request.user).count() > 1:
                first_line = Lines.objects.filter(ReportID=line.ReportID).filter(Editor=request.user).first()
                if line.id == first_line.id:
                    second_line = Lines.objects.filter(ReportID=line.ReportID).filter(Editor=request.user)[1]
                    for column in column_list:
                        if column.TotalFormula == 1:
                            first_cell = Cells.objects.filter(ColumnID=column.id).filter(LineID=first_line.id).first()
                            second_cell = Cells.objects.filter(ColumnID=column.id).filter(LineID=second_line.id).first()
                            if isfloat(first_cell.Value):
                                if isfloat(second_cell.Value):
                                    column.TotalValue = str(float(column.TotalValue) - float(first_cell.Value)
                                                            + float(second_cell.Value))
                                else:
                                    column.TotalValue = str(float(column.TotalValue) - float(first_cell.Value))
                            else:
                                if isfloat(second_cell.Value):
                                    column.TotalValue = str(float(column.TotalValue) + float(second_cell.Value))
                            column.save()
            else:
                for column in column_list:
                    if column.TotalFormula == 1:
                        cell = Cells.objects.filter(ColumnID=column.id).filter(LineID=line.id).first()
                        if isfloat(cell.Value):
                            column.TotalValue = str(float(column.TotalValue) - float(cell.Value))
                            column.save()
            line.delete()
    return redirect(reverse('report_show', args=(report_id,)))


######################################################################################################################


@login_required
def cells_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column_list = Columns.objects.filter(ReportID=report)
        first_line = Lines.objects.filter(ReportID=report).filter(Editor=request.user).first()
        line = Lines()
        line.ReportID = report
        line.Editor = request.user
        line.save()
        for column in column_list:
            if column.TypeData == 1:
                cell_value = request.POST.get('column' + column.id.__str__(), 0)
                if cell_value == '':
                    cell_value = 0
                else:
                    cell_value = cell_value.replace(',', '.')
            else:
                cell_value = request.POST.get('column' + column.id.__str__(), '')
            save_cell(line, column, cell_value)
            if column.TotalFormula == 1:
                cell = Cells.objects.filter(ColumnID=column.id).filter(LineID=line.id).first()
                delta = 0
                if first_line:
                    first_cell = Cells.objects.filter(ColumnID=column.id).filter(LineID=first_line.id).first()
                    if first_cell and isfloat(first_cell.Value):
                        delta -= float(first_cell.Value)
                if isfloat(cell.Value):
                    delta += float(cell.Value)
                column.TotalValue = str(float(column.TotalValue) + delta)
                column.save()
    return redirect(reverse('report_show', args=(report.id,)))


######################################################################################################################
