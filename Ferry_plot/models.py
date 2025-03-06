# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

from django.conf import settings
from datetime import date, datetime

import django_tables2 as tables





class Parameters(models.Model):

    PARAMETERS_CHOICES = (
        ('Time','Time'),
        ('Latitude','Latitude'),
        ('Longitude','Longitude'),
        ('Temp_SBE45','Temp_SBE45'),
        ('Cond_SBE45','Cond_SBE45'),
        ('Salinity_SBE45','Salinity_SBE45'),
        ('SoundVel_SBE45','SoundVel_SBE45'),
        ('Temp_in_SBE38','Temp_in_SBE38'),
        ('Oxygen','Oxygen'),
        ('Saturation','Saturation'),
        ('Turbidity','Turbidity'),
        ('Chl_a','Chl_a'),
        ('Temp_Meinsberg','Temp_Meinsberg'),
        ('pressure','pressure'),
        ('NV_Position','NV_Position'),
        ('Distance','Distance'),
    )

    parameter_name = models.CharField(
        max_length=100,
        choices=PARAMETERS_CHOICES,
        blank=True,
        default='none',
        help_text='Parameter name',
    )

    parameter_unit = models.CharField(max_length=200)
    parameter_sensor = models.CharField(max_length=200)


    def __str__(self):
        """Fonction requise par Django pour manipuler les objets Path dans la base de données."""
        return f'{self.parameter_name}'



#done and fixed (this part is good)
class Transect(models.Model):
    """Model representing an Transect."""
    departure_golf = models.CharField(max_length=100)
    arrival_golf = models.CharField(max_length=100)
    average_distance = models.FloatField(null=True, blank=True, default=0.0)    

    class Meta:
        ordering = ['departure_golf', 'arrival_golf']

    def get_absolute_url(self):
        """Returns the url to access a particular Transect instance."""
        return reverse('transect-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.departure_golf}, {self.arrival_golf}'               




from django.db.models import CharField, Model
from django_mysql.models import ListCharField

#done and fixed (this part is good)
class Download(models.Model):

    Subjects_CHOICES = (
        ('Get a full user account','Get a full user account'),
        ('Discuss partnership opportunities','Discuss partnership opportunities'),
        ('Get data samples','Get data samples'),
        ('Other','Other'),
    )
    """Model representing an Transect."""
    ID_user = models.CharField(max_length=100)
    Email = models.CharField(max_length=100)
    Name = models.CharField(max_length=100)
    L_name = models.CharField(max_length=100)
    Subject = models.CharField(max_length=100)
    Transects = ListCharField(
        base_field=CharField(max_length=100),
        size=6,
        max_length=(10 * 110)  # 6 * 10 character nominals, plus commas
    )   
    # Status = models.BooleanField(default=True)

    class Meta:
        ordering = ['Name', 'Transects']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.Name}, {self.Subject}'    





class Measurements(models.Model):

    #['Ref_trip','Date','Time','Nbr_minutes','Latitude','Longitude','Distance','Cumul_Distance','Area','Salinity_SBE45',
    #'QC_Salinity_SBE45','Variance.4','Temp_in_SBE38','QC_Temp_in_SBE38',
    #'Variance.6','Oxygen','QC_Oxygen','Variance.7','Turbidity','QC_Turbidity','Variance.10','Chl_a','QC_Chl_a','Variance.11']

    #add a full name here !!

    Ref_trip=models.FloatField(null=True, blank=True, default=0000)
    Date= models.DateField(null=True, blank=True) 
    Time=models.TimeField(null=True, blank=True) 
    Nbr_minutes=models.FloatField(null=True, blank=True, default=0000) 
    Latitude=models.FloatField(null=True, blank=True, default=0000) 
    Longitude=models.FloatField(null=True, blank=True, default=0000) 
    Distance=models.FloatField(null=True, blank=True, default=0000) 
    Cumul_Distance=models.FloatField(null=True, blank=True, default=0000) 
    Area=models.CharField(max_length=200) 
    Salinity_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    QC_Salinity_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Salinity_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    Temp_in_SBE38=models.FloatField(null=True, blank=True, default=0000) 
    QC_Temp_in_SBE38=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Temp_in_SBE38=models.FloatField(null=True, blank=True, default=0000) 
    Oxygen=models.FloatField(null=True, blank=True, default=0000) 
    QC_Oxygen=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Oxygen=models.FloatField(null=True, blank=True, default=0000) 
    Turbidity=models.FloatField(null=True, blank=True, default=0000) 
    QC_Turbidity=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Turbidity=models.FloatField(null=True, blank=True, default=0000) 
    Chl_a=models.FloatField(null=True, blank=True, default=0000) 
    QC_Chl_a=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Chl_a=models.FloatField(null=True, blank=True, default=0000) 


    Course=models.FloatField(null=True, blank=True, default=0000) 
    Variance_course=models.FloatField(null=True, blank=True, default=0000) 
    Speed=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Speed=models.FloatField(null=True, blank=True, default=0000) 
    Temp_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Temp_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    Cond_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Cond_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    SoundVel_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    Variance_SoundVel_SBE45=models.FloatField(null=True, blank=True, default=0000) 
    Saturation=models.FloatField(null=True, blank=True, default=0000) 
    Variance_Saturation=models.FloatField(null=True, blank=True, default=0000) 
    pH=models.FloatField(null=True, blank=True, default=0000) 
    Variance_pH=models.FloatField(null=True, blank=True, default=0000) 
    pH_Satlantic=models.FloatField(null=True, blank=True, default=0000) 

    Variance_pH_Satlantic=models.FloatField(null=True, blank=True, default=0000) 
    pressure=models.FloatField(null=True, blank=True, default=0000) 
    Variance_pressure=models.FloatField(null=True, blank=True, default=0000) 
    flow_in=models.FloatField(null=True, blank=True, default=0000) 
    Variance_flow_in=models.FloatField(null=True, blank=True, default=0000) 
    flow_main=models.FloatField(null=True, blank=True, default=0000) 
    Variance_flow_main=models.FloatField(null=True, blank=True, default=0000) 
    flow_pH=models.FloatField(null=True, blank=True, default=0000) 
    Variance_flow_pH=models.FloatField(null=True, blank=True, default=0000) 
    flow_pCO2=models.FloatField(null=True, blank=True, default=0000) 
    Variance_flow_pCO2=models.FloatField(null=True, blank=True, default=0000) 
    halffull=models.FloatField(null=True, blank=True, default=0000) 
    Variance_halffull=models.FloatField(null=True, blank=True, default=0000) 

    # ['Course', 'Variance', 'Speed',
    #    'Variance_Speed', 'Temp_SBE45', 'Variance_Temp_SBE45', 'Cond_SBE45',
    #    'Variance_Cond_SBE45', 'SoundVel_SBE45', 'Variance_SoundVel_SBE45',
    #    'Saturation', 'Variance_Saturation', 'pH', 'Variance_pH',
    #    'pH_Satlantic', 'Variance_pH_Satlantic', 'pressure',
    #    'Variance_pressure', 'flow_in', 'Variance_flow_in', 'flow_main',
    #    'Variance_flow_main', 'flow_pH', 'Variance_flow_pH', 'flow_pCO2',
    #    'Variance_flow_pCO2', 'halffull', 'Variance_halffull'],
    def __float__(self):
        return self.Ref_trip


#for the table rendering

# class SimpleTable(tables.Table):
#     class Meta:
#         model = Measurements




class Metadata(models.Model):

#['Path Reference','Port_name','Transect','Year','Month','Season','Start_time',
                                      #'End_time','Duration','Distance','Size','Number of lines',
                                      
    id_meta= models.AutoField(primary_key=True, unique=True)
    Name = models.CharField(max_length=500)
    sens = models.CharField(max_length=500)
    Path_Reference = models.IntegerField(null=True, blank=True, default=0000)
    Port_name = models.CharField(max_length=200)
    Departure = models.CharField(max_length=200)
    Destination = models.CharField(max_length=200)
    Year = models.IntegerField(null=True, blank=True, default=0000)
    Date = models.DateField(null=True, blank=True)
    Season = models.CharField(max_length=200)
    Start_time = models.TimeField(null=True, blank=True)
    End_time = models.TimeField(null=True, blank=True)
    Duration_h = models.IntegerField(null=True, blank=True, default=0000)
    Distance_km = models.IntegerField(null=True, blank=True, default=0000)
    Size_ko = models.IntegerField(null=True, blank=True, default=0000)
    Number_of_lines = models.IntegerField(null=True, blank=True, default=0000)

    def __float__(self):
        return self.Ref_trip

