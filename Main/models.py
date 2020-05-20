# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from .choices import TYPE_CHOICES, FORMULA_CHOICES, COLOR_CHOICES, EVENT_CHOICES

######################################################################################################################


class Reports(models.Model):
    TitleShort = models.CharField('Краткое наименование', max_length=64, default='', )
    TitleLong = models.CharField('Полное наименование', max_length=1024, default='', )
    TitleFile = models.FileField('Файл с шапкой таблицы', upload_to='%Y/%m/%d', null=True, )
    Published = models.BooleanField('Опубликована', default=False, )
    Header = models.CharField('Заголовок таблицы', max_length=10240, default='', )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}'.format(self.TitleShort)

    class Meta:
        ordering = '-Published', 'TitleShort',
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        managed = True


######################################################################################################################


class Columns(models.Model):
    Title = models.CharField('Наименование', max_length=256, default='', )
    ReportID = models.ForeignKey(Reports, verbose_name='Отчет', null=False, related_name='ColumnReportID',
                                 on_delete=models.CASCADE, )
    TypeData = models.SmallIntegerField('Тип данных', choices=TYPE_CHOICES, default=1, )
    Color = models.SmallIntegerField('Цает столбца', choices=COLOR_CHOICES, default=0, )
    TotalFormula = models.SmallIntegerField('Формула итого', choices=FORMULA_CHOICES, default=1, )
    TotalValue = models.CharField('Значение итого', max_length=1024, default='', )
    Priority = models.SmallIntegerField('Очередность столбцов', default=0, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}'.format(self.id)

    class Meta:
        ordering = 'Priority', 'CreateDate',
        verbose_name = 'Столбец'
        verbose_name_plural = 'Столбцы'
        managed = True


######################################################################################################################


class Lines(models.Model):
    ReportID = models.ForeignKey(Reports, verbose_name='Отчет', null=False, related_name='LineReportID',
                                 on_delete=models.CASCADE, )
    Editor = models.ForeignKey(User, verbose_name='Редактор строки', null=True, related_name='Editor',
                               on_delete=models.SET_NULL, )
    Prev = models.ForeignKey('self', verbose_name='Предыдущая строка', null=True, related_name='PrevLineID',
                             on_delete=models.SET_DEFAULT, default=None, )
    Current = models.BooleanField('Текущая строка', default=True, )
    Deleted = models.BooleanField('Удаленная строка', default=False, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}.{1}'.format(self.ReportID.id, self.id)

    class Meta:
        ordering = 'Editor', '-CreateDate',
        verbose_name = 'Строка'
        verbose_name_plural = 'Строки'
        managed = True


######################################################################################################################


class Cells(models.Model):

    Value = models.CharField('Значение', max_length=1024, default='', )
    ColumnID = models.ForeignKey(Columns, verbose_name='Столбец', null=False, related_name='ColumnID',
                                 on_delete=models.CASCADE, )
    LineID = models.ForeignKey(Lines, verbose_name='Строка', null=False, related_name='LineID',
                               on_delete=models.CASCADE, )

    def __str__(self):
        return '{0}:{1} - {2}'.format(self.LineID.id, self.ColumnID.id, self.Value)

    class Meta:
        ordering = 'ColumnID', '-id',
        verbose_name = 'Ячейка'
        verbose_name_plural = 'Ячейки'
        managed = True


######################################################################################################################


class Logs(models.Model):
    event = models.SmallIntegerField('Событие', choices=EVENT_CHOICES, default=0, null=False, blank=False, )
    participan = models.ForeignKey(User, verbose_name='Субъект события', null=True, related_name='Participan',
                                   on_delete=models.SET_NULL, )
    event_date = models.DateTimeField('Дата события', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}'.format(self.event_date)

    class Meta:
        ordering = '-event_date',
        verbose_name = 'Логи'
        verbose_name_plural = 'Логи'
        managed = True


######################################################################################################################
