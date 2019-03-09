# -*- coding: utf-8 -*-

from django import forms
from datetime import date
from .choices import TYPE_CHOICES, FORMULA_CHOICES

######################################################################################################################


class FormReportCreate(forms.Form):

    report_title_short = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите краткое наименование', }),
        required=True,
    )

    report_title_long = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите полное наименование', }),
        required=True,
    )

######################################################################################################################


class FormReportEdit(forms.Form):

    report_title_short = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите краткое наименование', }),
        required=True,
    )

    report_title_long = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите полное наименование', }),
        required=True,
    )

    report_header = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'type': 'text', 'class': 'form-control', 'rows': 3, }),
        required=False,
    )

######################################################################################################################


class FormColumn(forms.Form):

    column_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label='',
        initial=1,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )

    column_title = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите наименование столбца', }),
        required=False,
    )

    column_total = forms.ChoiceField(
        choices=FORMULA_CHOICES,
        label='',
        initial=1,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True
    )
