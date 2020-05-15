# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from Main.models import Reports, Columns
from .tools import save_column
from .decorators import superuser_only

######################################################################################################################


@superuser_only
def column_save(request, report_id):
    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column = Columns()
        save_column(request, report, column)
        return redirect(reverse('report_edit', args=(report.id,)))
    return redirect(reverse('index'))


######################################################################################################################


@superuser_only
def column_edit(request, column_id):
    column = get_object_or_404(Columns, id=column_id)
    if request.POST:
        save_column(request, column.ReportID, column)
    return redirect(reverse('report_edit', args=(column.ReportID.id,)))


######################################################################################################################


@superuser_only
def column_delete(request, column_id):
    column = get_object_or_404(Columns, id=column_id)
    report_id = column.ReportID.id
    column.delete()
    return redirect(reverse('report_edit', args=(report_id,)))


######################################################################################################################
