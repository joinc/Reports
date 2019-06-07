# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.conf import settings
from Main.models import Reports, Columns, Lines, Cells
from .forms import FormReportCreate, FormReportEdit, FormColumn

######################################################################################################################


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.user.is_superuser:
        report_list = Reports.objects.all()
    else:
        report_list = Reports.objects.filter(Published=True)
    return render(request, 'index.html', {'report_list': report_list, })

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
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse('report_total', args=(report.id,)))
    else:
        last_line = Lines.objects.filter(ReportID=report).filter(Editor=request.user).first()
        last_items = Cells.objects.filter(LineID=last_line)
        line_list = Lines.objects.filter(ReportID=report).filter(Editor=request.user)
        cell_list = []
        for line in line_list:
            cells = Cells.objects.filter(LineID=line).filter(Owner=request.user)
            cell_list.append(cells)

    breadcrumb = 'Просмотр таблицы "' + report.TitleShort + '"'
    return render(request, 'report.html',
                  {'report': report, 'column_list': column_list, 'line_list': line_list, 'cell_list': cell_list,
                   'last_items': last_items, 'breadcrumb': breadcrumb, })

######################################################################################################################


def report_total(request, report_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    report = get_object_or_404(Reports, id=report_id)
    if request.user.is_superuser:
        column_list = Columns.objects.filter(ReportID=report)
        total_line = []
        user_list = []
        line_list = []
        for owner in User.objects.all().order_by('last_name'):
            lines = Lines.objects.filter(ReportID=report).filter(Editor=owner)
            if lines.count() > 0:
                cell_list = []
                for line in lines:
                    cells = Cells.objects.filter(LineID=line)
                    cell_list.append(cells)
                line_list.append(cell_list)
                user_list.append(owner)
        for column in column_list:
            if column.TypeData == 1:
                total = 0
                for owner in user_list:
                    last_line = Lines.objects.filter(ReportID=report).filter(Editor=owner).first()
                    cell = Cells.objects.filter(LineID=last_line).filter(ColumnID=column).first()
                    if cell is not None:
                        try:
                            cell_value = float(cell.Value)
                        except ValueError:
                            cell_value = 0
                        total = total + cell_value
                total_line.append(float('{:.2f}'.format(total)))
            else:
                total_line.append('')

    else:
        return HttpResponseRedirect(reverse('report_view', args=(report.id,)))

    breadcrumb = 'Сводная таблицы "' + report.TitleShort + '"'
    return render(request, 'report_total.html',
                  {'report': report, 'column_list': column_list, 'line_list': line_list, 'cell_list': cell_list,
                   'total_line': total_line, 'user_list': user_list, 'breadcrumb': breadcrumb, })

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
    return HttpResponseRedirect(reverse('index'))

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
        fill_cells(report_id)
        return HttpResponseRedirect(reverse('report_edit', args=(report.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def column_delete(request, column_id):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    column = get_object_or_404(Columns, id=column_id)
    report_id = column.ReportID.id
    column.delete()
    return HttpResponseRedirect(reverse('report_edit', args=(report_id,)))

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


def cells_save(request, report_id):

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
            if cell_value:
                cell_save(line, column, request.user, cell_value)
            else:
                cell_save(line, column, request.user, '')
        return HttpResponseRedirect(reverse('report_view', args=(report.id,)))

    return HttpResponseRedirect(reverse('index'))

######################################################################################################################


def fill_cells(report_id):

    report = get_object_or_404(Reports, id=report_id)
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

