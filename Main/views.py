# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView
from django.conf import settings
from Main.models import Reports, Columns, Cells
from .forms import FormReport, FormColumn

######################################################################################################################


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    report_list = Reports.objects.all()
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

    report_form = FormReport()
    breadcrumb = 'Создание таблицы отчета'
    return render(request, 'reports.html',
                  {'report_form': report_form, 'breadcrumb': breadcrumb, })

######################################################################################################################


def report_save(request):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    if request.POST:
        report_title_short = request.POST['report_title_short']
        report_title_long = request.POST['report_title_long']
        report = Reports()
        report.TitleShort = report_title_short
        report.TitleLong = report_title_long
        report.save()
        return HttpResponseRedirect(reverse('column_create', args=(report.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def report_view(request, report_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    report = get_object_or_404(Reports, id=report_id)
    column_list = Columns.objects.filter(ReportID=report)
    breadcrumb = 'Просмотр отчета "' + report.TitleShort + '"'
    return render(request, 'report.html',
                  {'report': report, 'column_list': column_list, 'breadcrumb': breadcrumb, })

######################################################################################################################


def column_create(request, report_id):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    report = get_object_or_404(Reports, id=report_id)
    column_list = Columns.objects.filter(ReportID=report)
    column_form = FormColumn()
    breadcrumb = 'Создание столбца таблицы отчета'
    return render(request, 'columns.html',
                  {'report': report, 'column_list': column_list, 'column_form': column_form, 'breadcrumb': breadcrumb, })

######################################################################################################################


def column_save(request):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    if request.POST:
        column_title = request.POST['column_title']
        column = Columns()
        column.Title = column_title
        column.save()

    return HttpResponseRedirect(reverse('index'))

