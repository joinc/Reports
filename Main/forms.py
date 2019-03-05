# -*- coding: utf-8 -*-

from django import forms
from datetime import date

######################################################################################################################


class FormReport(forms.Form):

    report_title_short = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите краткое наименование', }),
        required=False,
    )

    report_title_long = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите полное наименование', }),
        required=False,
    )

######################################################################################################################


class FormColumn(forms.Form):

    column_title = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите наименование столбца', }),
        required=False,
    )
