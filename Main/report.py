# -*- coding: utf-8 -*-

import os
import mimetypes
from datetime import datetime
from pyexcel_ods3 import save_data
from collections import OrderedDict
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Reports, Columns, Lines, Cells
from .decorators import superuser_only
from .forms import FormReport, FormColumn
from .tools import save_report, show_lines, fill_cell, count_total_column, isfloat

######################################################################################################################


@superuser_only
def report_create(request):
    if request.POST:
        report = Reports()
        report = save_report(request, report)
        report.save()
        return redirect(reverse('report_edit', args=(report.id,)))
    else:
        context = {'report_form': FormReport(), 'breadcrumb': 'Создание таблицы', }
        return render(request, 'report_create.html', context)


######################################################################################################################


@superuser_only
def report_edit(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    context = {
        'report': report, 'breadcrumb': 'Редактирование таблицы "' + report.TitleShort + '"',
        'report_form': FormReport(initial={
            'report_title_short': report.TitleShort, 'report_title_long': report.TitleLong,
            'report_title_file': report.TitleFile, 'report_title_header': report.Header,
        })
    }
    columns = Columns.objects.filter(ReportID=report)
    column_list = []
    for column in columns:
        form = FormColumn(initial={
            'column_title': column.Title,
            'column_priority': column.Priority,
            'column_color': column.Color,
            'column_type': column.TypeData,
            'column_total': column.TotalFormula,
        })
        column_list.append([column, form])
    context['column_list'] = column_list
    context['column_form'] = FormColumn()
    return render(request, 'report_edit.html', context)


######################################################################################################################


@superuser_only
def report_publish(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if not report.Published:
        report.Published = True
    else:
        report.Published = False
    report.save()
    return_path = request.META.get('HTTP_REFERER')
    return redirect(return_path)


######################################################################################################################


@superuser_only
def report_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        report = save_report(request, report)
        report.save()
        return redirect(reverse('report_edit', args=(report.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@login_required
def report_show(request, report_id):
    if request.user.is_superuser:
        return redirect(reverse('report_show_total', args=(report_id,)))
    else:
        report = get_object_or_404(Reports, id=report_id)
        if request.GET:
            context = {'table': show_lines(request, report)}
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
def report_show_total(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.GET:
        context = {'table': show_lines(request, report)}
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
def report_count_total(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    users_list = User.objects.filter(is_superuser=False).order_by('last_name')
    for column in Columns.objects.filter(ReportID=report):
        column.TotalValue = count_total_column(report, column, users_list)
        column.save()

    return redirect(reverse('report_show_total', args=(report_id,)))


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
