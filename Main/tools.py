# -*- coding: utf-8 -*-

from .models import Cells, Columns

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
