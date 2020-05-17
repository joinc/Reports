# -*- coding: utf-8 -*-

from django import forms
from .choices import TYPE_CHOICES, FORMULA_CHOICES, COLOR_CHOICES


######################################################################################################################


class FormReport(forms.Form):

    report_title_short = forms.CharField(
        label='Краткое наименование:',
        widget=forms.TextInput(attrs={
            'type': 'text', 'class': 'form-control', 'placeholder': 'Введите краткое наименование',
        }),
        required=True,
    )

    report_title_long = forms.CharField(
        label='Полное наименование:',
        widget=forms.Textarea(attrs={
            'type': 'text', 'class': 'form-control', 'placeholder': 'Введите полное наименование', 'rows': 3,
        }),
        required=True,
    )

    report_title_file = forms.FileField(
        label='Файл с заголовком таблицы в формате ods:',
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False,
    )

    report_title_header = forms.CharField(
        label='Заголовок таблицы:',
        widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control', 'rows': 3, }),
        required=False,
    )


######################################################################################################################


class FormColumn(forms.Form):

    column_title = forms.CharField(
        label='Наименование столбца:',
        widget=forms.TextInput(attrs={
            'type': 'text', 'class': 'form-control', 'placeholder': 'Введите наименование столбца',
        }),
        required=False,
    )

    column_priority = forms.CharField(
        label='Очередность:',
        widget=forms.TextInput(attrs={
            'type': 'text', 'class': 'form-control', 'placeholder': 'Введите очередность столбца',
        }),
        required=False,
    )

    column_color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        label='Цвет столбца:',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

    column_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label='Тип данных:',
        initial=1,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

    column_total = forms.ChoiceField(
        choices=FORMULA_CHOICES,
        label='Формула значения итого:',
        initial=1,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

    column_value = forms.CharField(
        label='Значение итого:',
        widget=forms.TextInput(attrs={
            'type': 'text', 'class': 'form-control',
        }),
        required=False
    )


######################################################################################################################
