"""Reports URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Main import views

urlpatterns = [
    path('', views.index, name='index', ),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login', ),
    path('logout/', views.logout, name='logout', ),
    path('report/create/', views.report_create, name='report_create', ),
    path('report/<int:report_id>/show', views.report_show, name='report_show', ),
    path('report/<int:report_id>/total', views.report_total, name='report_total', ),
    path('report/<int:report_id>/download', views.report_download, name='report_download', ),
    path('report/<int:report_id>/edit', views.report_edit, name='report_edit', ),
    path('report/<int:report_id>/save', views.report_save, name='report_save', ),
    path('report/<int:report_id>/publish', views.report_publish, name='report_publish', ),
    path('report/<int:report_id>/column/save/', views.column_save, name='column_save', ),
    path('report/<int:report_id>/cell/save/', views.cells_save, name='cells_save', ),
    path('report/<int:report_id>/line/delete/', views.line_delete, name='linedelete', ),
    path('column/<int:column_id>/edit/', views.column_edit, name='column_edit', ),
    path('column/<int:column_id>/delete/', views.column_delete, name='column_delete', ),
]
