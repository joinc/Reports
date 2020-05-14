# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from django.urls import reverse

######################################################################################################################


def superuser_only(function):
    # Декоратор - выполняется только администратором
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect(reverse('index'))
        return function(request, *args, **kwargs)

    return _inner


######################################################################################################################
