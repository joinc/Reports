# -*- coding: utf-8 -*-

from django import forms
from datetime import date

######################################################################################################################


class FormReport(forms.Form):

    report_title_short = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите краткое наименование', 'size': '40', }),
        required=False,
    )

    report_title_long = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите полное наименование', 'size': '60', }),
        required=False,
    )
