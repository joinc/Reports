from django.db import models
from django.contrib.auth.models import User


######################################################################################################################

class Reports(models.Model):
    TitleShort = models.CharField('Краткое наименование', max_length=64, default='', )
    TitleLong = models.CharField('Полное наименование', max_length=1024, default='', )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}'.format(self.TitleShort)

    class Meta:
        ordering = 'TitleShort',
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        managed = True


######################################################################################################################

class Columns(models.Model):
    Title = models.CharField('Наименование', max_length=64, default='', )
    ReportID = models.ForeignKey(Reports, verbose_name='Отчет', null=False, related_name='ReportID', on_delete=models.
                                 CASCADE, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0}'.format(self.Title)

    class Meta:
        ordering = 'CreateDate',
        verbose_name = 'Столбец'
        verbose_name_plural = 'Столбцы'
        managed = True


######################################################################################################################

class Cells(models.Model):
    Value = models.CharField('Значение', max_length=10, default='', )
    ColumnID = models.ForeignKey(Columns, verbose_name='Столбец', null=False, related_name='ColumnID', on_delete=models.
                                 CASCADE, )
    Owner = models.ForeignKey(User, verbose_name='Владелец ячейки', null=True, related_name='Owner', on_delete=models.
                              SET_NULL, )
    CreateDate = models.DateTimeField('Дата создания', auto_now_add=True, null=True, )

    def __str__(self):
        return '{0} - {1}'.format(self.ColumnID, self.Value)

    class Meta:
        ordering = 'ColumnID', 'id',
        verbose_name = 'Ячейка'
        verbose_name_plural = 'Ячейки'
        managed = True


######################################################################################################################
