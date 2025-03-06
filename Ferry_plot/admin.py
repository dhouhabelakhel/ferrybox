from django.contrib import admin
import csv
from django.http import HttpResponse
from .models import *

from import_export.admin import ImportExportModelAdmin

from Ferry_plot.models import Transect, Measurements, Metadata, Parameters, Download


@admin.register(Metadata)
class ViewAdmin(ImportExportModelAdmin):
	list_display = ('id_meta', 'Name', 'Path_Reference', 'Departure','Destination', 'Year', 'Date', 'Season', 'Start_time', 'End_time', 'Duration_h', 'Distance_km', 'Size_ko', 'Number_of_lines')
	


@admin.register(Transect)
class ViewAdmin(ImportExportModelAdmin):
	pass

@admin.register(Measurements)
class ViewAdmin(ImportExportModelAdmin):
	list_display = ('id','Ref_trip', 'Date', 'Time', 'Nbr_minutes', 'Latitude', 'Longitude', 'Distance', 'Cumul_Distance', 'Area', 'Salinity_SBE45', 'QC_Salinity_SBE45', 'Variance_Salinity_SBE45', 'Temp_in_SBE38', 'QC_Temp_in_SBE38', 'Variance_Temp_in_SBE38', 'Oxygen', 'QC_Oxygen', 'Variance_Oxygen', 'Turbidity', 'QC_Turbidity', 'Variance_Turbidity', 'Chl_a', 'QC_Chl_a', 'Variance_Chl_a')



@admin.register(Download)
class ViewAdmin(ImportExportModelAdmin):
	list_display = ('ID_user', 'Email', 'Name', 'L_name', 'Subject', 'Transects')

admin.site.register(Parameters)


