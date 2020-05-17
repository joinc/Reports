# -*- coding: utf-8 -*-

from .models import Cells, Columns, Lines

######################################################################################################################


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


######################################################################################################################


def save_report(request, report):
    report.TitleShort = request.POST.get('report_title_short', '')
    report.TitleLong = request.POST.get('report_title_long', '')
    report.Header = request.POST.get('report_title_header', '')
    if request.FILES:
        file = request.FILES['report_title_file']
        report.TitleFile.save(file.name, file)
    return report


######################################################################################################################


def save_column(request, report, column):
    column.Title = request.POST.get('column_title', '')
    column.Priority = request.POST.get('column_priority', '')
    column.Color = request.POST.get('column_color', 0)
    column.TypeData = request.POST.get('column_type', 2)
    column.TotalFormula = request.POST.get('column_total', 0)
    column.TotalValue = request.POST.get('column_value', 0)
    column.ReportID = report
    column.save()


######################################################################################################################


def save_cell(cell_line, cell_column, cell_value):
    # Процедура создания и заполнения значением новой ячейки
    cell = Cells()
    cell.LineID = cell_line
    cell.ColumnID = cell_column
    cell.Value = cell_value
    cell.save()


######################################################################################################################


def fill_cell(line):
    if Columns.objects.filter(ReportID=line.ReportID).count() > Cells.objects.filter(LineID=line).count():
        for column in Columns.objects.filter(ReportID=line.ReportID):
            cell = Cells.objects.filter(ColumnID=column.id).filter(LineID=line.id).first()
            if not cell:
                if column.TypeData == 1:
                    save_cell(line, column, 0)
                else:
                    save_cell(line, column, '')
    return Cells.objects.filter(LineID=line)


######################################################################################################################


def show_lines(request, report):
    czn = int(request.GET.get('czn'))
    table = []
    lines = Lines.objects.filter(ReportID=report).filter(Editor_id=czn)
    for line in lines[1:]:
        table.append([line, fill_cell(line)])
    return table


######################################################################################################################

def count_total_column(report, column, users_list):
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
