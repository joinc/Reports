# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Reports, Columns
from .decorators import superuser_only
from .forms import FormReport, FormColumn
from .tools import save_report

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
