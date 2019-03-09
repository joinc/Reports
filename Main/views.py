# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView
from django.conf import settings
from Main.models import Reports, Columns, Lines, Cells
from .forms import FormReportCreate, FormReportEdit, FormColumn

######################################################################################################################


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    report_list = Reports.objects.filter(Published=True)
    report_count = report_list.count()
    return render(request, 'index.html', {'report_list': report_list, 'report_count': report_count, })

######################################################################################################################


class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "login.html"
    # В случае успеха перенаправим на главную.
    success_url = settings.SUCCESS_URL

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()
        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)

        return super(LoginFormView, self).form_valid(form)

######################################################################################################################


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def report_create(request):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

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


def report_edit(request, report_id):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

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


def report_save(request, report_id):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

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


def report_view(request, report_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    report = get_object_or_404(Reports, id=report_id)
    column_list = Columns.objects.filter(ReportID=report)
    breadcrumb = 'Просмотр таблицы "' + report.TitleShort + '"'
    return render(request, 'report.html',
                  {'report': report, 'column_list': column_list, 'breadcrumb': breadcrumb, })

######################################################################################################################


def report_publish(request, report_id):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    report = get_object_or_404(Reports, id=report_id)
    if not report.Published:
        report.Published = True
    else:
        report.Published = False
    report.save()
    return HttpResponseRedirect(reverse('reports_list'))

######################################################################################################################


def reports_list(request):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    report_list = Reports.objects.all()
    breadcrumb = 'Список таблиц'
    return render(request, 'reports_list.html', {'report_list': report_list, 'breadcrumb': breadcrumb, })

######################################################################################################################


def column_save(request, report_id):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column_title = request.POST['column_title']
        column = Columns()
        column.Title = column_title
        column.ReportID = report
        column.save()
        return HttpResponseRedirect(reverse('report_edit', args=(report.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def cell_save(request, report_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    report = get_object_or_404(Reports, id=report_id)
    if request.POST:
        column_list = Columns.objects.filter(ReportID=report)
        line = Lines()
        line.ReportID = report
        line.Editor = request.user
        line.save()
        for column in column_list:
            cell_value = request.POST['column'+column.id.__str__()]
            cell = Cells()
            cell.Value = cell_value
            cell.ColumnID = column
            cell.LineID = line
            cell.Owner = request.user
            cell.save()
        return HttpResponseRedirect(reverse('report_view', args=(report.id,)))

    return HttpResponseRedirect(reverse('index'))
