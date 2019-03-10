"""Reports URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index', ),
    path('report/create/', views.report_create, name='report_create', ),
    path('report/<int:report_id>/', views.report_view, name='report_view', ),
    path('report/<int:report_id>/total', views.report_total, name='report_total', ),
    path('report/<int:report_id>/edit', views.report_edit, name='report_edit', ),
    path('report/<int:report_id>/save', views.report_save, name='report_save', ),
    path('report/<int:report_id>/publish', views.report_publish, name='report_publish', ),
    path('report/<int:report_id>/column/save/', views.column_save, name='column_save', ),
    path('report/<int:report_id>/cell/save/', views.cell_save, name='cell_save', ),
    path('column/<int:column_id>/delete/', views.column_delete, name='column_delete', ),
    path('login/', views.LoginFormView.as_view(), name='login', ),
    path('logout/', views.logout_view, name='logout', ),
]
