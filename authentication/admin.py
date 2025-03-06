from django.contrib import admin
from django.http import HttpResponse
from .models import *

from authentication.models import Download



@admin.register(Download)
class ViewAdmin(ImportExportModelAdmin):
	list_display = ('Name', 'Email', 'Subject', 'Profession', 'Application', 'transects_export')

