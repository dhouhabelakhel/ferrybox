
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from .models import Measurements, Metadata, Parameters
from django.db.models import Avg, Min, Max
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
import pandas as pd
import glob
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
#this part is for uploading files in the database ( the famous csv files !)
import csv , io 
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
import os
import sys
import pathlib
import django
from django.db import transaction
import datetime
#the date button part
from django.views.generic import TemplateView, CreateView, DetailView, FormView
from django.shortcuts import render
from django.http import JsonResponse
#this part is : sigin users 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from Ferry_plot.models import Metadata, Measurements, Parameters
from django.db.models import Q, Count

import threading

#don't you lose the reference app pages...

# from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template

# from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group


#download table part

from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
import importlib.util



#     return reponse
def is_valid_queryparam(param):
    return param != '' and param is not None




from django.core.exceptions import ObjectDoesNotExist

# middleware.py
from django.shortcuts import redirect

# class RestrictURLMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Vérifiez l'URL demandée
#         restricted_urls = ['/upload.html/', '/page2/']  # Ajoutez les URLs à restreindre
#         if request.path_info in restricted_urls and not request.user.is_authenticated:
#             return redirect('login')  # Redirigez vers la page de connexion

#         response = self.get_response(request)
#         return response

# views.py
from django.shortcuts import render


@login_required
def upload(request):
    # Votre logique de vue ici
    return render(request, 'upload.html')

# @login_required(login_url="/login/")
def index(request):

    #total space
    qs1=Metadata.objects.all()
    from django.db.models import Sum

    sum_size=qs1.aggregate(Sum('Size_ko'))
    sum_size=int(sum_size['Size_ko__sum']/1000000)

    # nbr of files 
# Assuming 'Ref_trip' is the correct field name in your Measurements model
 
    df = pd.DataFrame(list(Measurements.objects.all().values('Ref_trip'))) 
    df_once=list(set(list(df['Ref_trip'])))
    df_once = list(map(int, df_once)) 

    # print(df_once)
    nbr_files=int(df_once[-1])

    # downloaded data
    #not yet

    # users
    from django.contrib.auth import get_user_model
    User = get_user_model()

    nbr_users=User.objects.count()

    #statistics
    #sum of summers

    #sum of winters

    #average values (summer/winter)

    #total transect genova

    #total transect marseille

    #this block is picking "admin interface" or "data dowbload"
    try:
        is_admin=bool(False)  

        if (str(request.user.groups.all()[0]))=="admin":
            is_admin=bool(True)

        context= { 'is_admin': is_admin,
        "nbr_files":nbr_files,
        "sum_size":sum_size,
        "overview":True,

         }

    except IndexError:
        context={"not_admin": bool(True),
        "nbr_files":nbr_files,
        "sum_size":sum_size,
        "nbr_users":nbr_users,
        "overview":True,
        }


    path='C:/FerryBox/Indexed_files/Genova/'
    PM='C:/FerryBox/Indexed_files/Marseille/'
    # paths=[PG,PM]

    df = pd.DataFrame(list(Measurements.objects.all().values('Ref_trip'))) 
    df_once=list(set(list(df['Ref_trip'])))
    df_once = list(map(int, df_once)) 

    # for path in paths:
        
    files = glob.glob(path+"*.csv")

    for file in files:
        # print(file.split('\\'))
        
        ref=int(file.split('\\')[1].split('_')[0])

        if ref not in df_once:

            # print("already in")
            with open(file) as csvfile:

                reader = csv.DictReader(csvfile)

                for row in reader:

                    # The header row values become your keys
                    ref_trip = row['Ref_trip']
                    date = row['Date']
                    time=row['Time']
                    nbr_minutes= row['Nbr_minutes']
                    latitude= row['Latitude']
                    longitude= row['Longitude']
                    distance= row['Distance']
                    cumul_Distance= row['Cumul_Distance']
                    area= row['Area']
                    salinity_SBE45= row['Salinity_SBE45']
                    qC_Salinity_SBE45= row['QC_Salinity_SBE45']
                    variance_Salinity_SBE45= row['Variance_Salinity_SBE45']
                    temp_in_SBE38= row['Temp_in_SBE38']
                    qC_Temp_in_SBE38= row['QC_Temp_in_SBE38']
                    variance_Temp_in_SBE38= row['Variance_Temp_in_SBE38']
                    oxygen= row['Oxygen']
                    qC_Oxygen= row['QC_Oxygen']
                    variance_Oxygen= row['Variance_Oxygen']
                    turbidity= row['Turbidity']
                    qC_Turbidity= row['QC_Turbidity']
                    variance_Turbidity= row['Variance_Turbidity']
                    chl_a= row['Chl_a']
                    qC_Chl_a= row['QC_Chl_a']
                    variance_Chl_a= row['Variance_Chl_a']
                    course= row['Course']
                    variance_course=row['Variance_course']
                    speed= row['Speed']
                    variance_Speed= row['Variance_Speed']
                    temp_SBE45= row['Temp_SBE45']
                    variance_Temp_SBE45= row['Variance_Temp_SBE45']
                    cond_SBE45= row['Cond_SBE45']
                    variance_Cond_SBE45= row['Variance_Cond_SBE45']
                    soundVel_SBE45= row['SoundVel_SBE45']
                    variance_SoundVel_SBE45= row['Variance_SoundVel_SBE45']
                    saturation= row['Saturation']
                    variance_Saturation= row['Variance_Saturation']
                    PH= row['pH']
                    variance_pH= row['Variance_pH']
                    PH_Satlantic= row['pH_Satlantic']
                    variance_pH_Satlantic= row['Variance_pH_Satlantic']
                    Pressure= row['pressure']
                    variance_pressure= row['Variance_pressure']
                    Flow_in= row['flow_in']
                    variance_flow_in= row['Variance_flow_in']
                    Flow_main= row['flow_main']
                    variance_flow_main= row['Variance_flow_main']
                    Flow_pH= row['flow_pH']
                    variance_flow_pH= row['Variance_flow_pH']
                    Flow_pCO2= row['flow_pCO2']
                    variance_flow_pCO2= row['Variance_flow_pCO2']
                    Halffull= row['halffull']
                    variance_halffull= row['Variance_halffull']

                    new_revo = Measurements(Ref_trip =ref_trip, Date=date,Time=time,Nbr_minutes=nbr_minutes,Latitude=latitude,          
                       Longitude=longitude, Distance=distance, Cumul_Distance=cumul_Distance,
                        Area=area, Salinity_SBE45=salinity_SBE45, QC_Salinity_SBE45=qC_Salinity_SBE45,
                        Variance_Salinity_SBE45=variance_Salinity_SBE45,Temp_in_SBE38=temp_in_SBE38,
                        QC_Temp_in_SBE38=qC_Temp_in_SBE38, Variance_Temp_in_SBE38=variance_Temp_in_SBE38,
                        Oxygen=oxygen, QC_Oxygen=qC_Oxygen, Variance_Oxygen=variance_Oxygen,
                        Turbidity=turbidity, QC_Turbidity=qC_Turbidity, Variance_Turbidity=variance_Turbidity,
                        Chl_a=chl_a,  QC_Chl_a=qC_Chl_a, Variance_Chl_a=variance_Chl_a,Course=course,Variance_course=variance_course,
                        Speed=speed,Variance_Speed=variance_Speed,Temp_SBE45=temp_SBE45,
                        Variance_Temp_SBE45=variance_Temp_SBE45,Cond_SBE45=cond_SBE45,
                        Variance_Cond_SBE45=variance_Cond_SBE45,SoundVel_SBE45=soundVel_SBE45,
                        Variance_SoundVel_SBE45=variance_SoundVel_SBE45,Saturation=saturation,
                        Variance_Saturation=variance_Saturation,pH=PH,Variance_pH=variance_pH,
                        pH_Satlantic=PH_Satlantic,Variance_pH_Satlantic=variance_pH_Satlantic,
                        pressure=Pressure,Variance_pressure=variance_pressure,flow_in=Flow_in,
                        Variance_flow_in=variance_flow_in,flow_main=Flow_main,
                        Variance_flow_main=variance_flow_main,flow_pH=Flow_pH,
                        Variance_flow_pH=variance_flow_pH,flow_pCO2=Flow_pCO2,
                        Variance_flow_pCO2=variance_flow_pCO2,halffull=Halffull,
                        Variance_halffull=variance_halffull
                         )
                    new_revo.save()
    # print("Injection process done")


    # print(df_once)

    return render(request, "index.html",context)



def data_description(request):
    qs = Metadata.objects.all()
    template_name="data_description.html"

    #total space
    qs1=Metadata.objects.all()
    from django.db.models import Sum

    sum_size=qs1.aggregate(Sum('Size_ko'))
    sum_size=int(sum_size['Size_ko__sum']/1000000)

    # nbr of files 

    df = pd.DataFrame(list(Measurements.objects.all().values('Ref_trip'))) 
    df_once=list(set(list(df['Ref_trip'])))
    df_once = list(map(int, df_once)) 

    # print(df_once)
    nbr_files=int(df_once[-1])

    # downloaded data
    #not yet

    # users
    from django.contrib.auth import get_user_model
    User = get_user_model()

    nbr_users=User.objects.count()



    context={
        "metadata":qs,
        'is_admin':bool(True),
        "nbr_files":nbr_files,
        "sum_size":sum_size,
        "nbr_users":nbr_users,
        "interface":True
        # "departs":departs,
        # "destinations":destinations,
    }

    return render(request, template_name,context)


# @login_required(login_url="/login/")
def page_user_view(request):    
   #this is to parse the download form user inputs

   #get the inputs
    if request.method == "POST":
        # user_id_query_download=request.POST.get('user_id')        
        email_address_query_download=request.POST.get('email_address')
        # user_name_query_download=request.POST.get('user_name')
        first_name_query_download_=request.POST.get('first_name')
        last_name_query_download=request.POST.get('last_name')
        subject_query_download=request.POST.get('subject')
        transects_query_download=request.POST.get('transect_select_download')


        new_down = Download(Email=email_address_query_download,
            Name=first_name_query_download_,L_name=last_name_query_download,
            Subject=subject_query_download,Transects=transects_query_download)
        new_down.save()


        # send_mail(subject= subject,message= message,from_email=settings.DEFAULT_FROM_EMAIL,recipient_list = [email],fail_silently  = True,)


    #this is to activate the available transects button

    qs = Measurements.objects.all()
    template_name="page-user.html"


    #this part is to select the available transects in the database
    #it is here because it should still be visible with no nuttons selected

    list_of_metadata_references=[]

    for met in Metadata.objects.all():
        list_of_metadata_references.append(met.Path_Reference)

    list_available_transects=[]



    context={'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements" : Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects":list_available_transects,
        "not_admin":bool(True),
        "downed":True,
                
            }
    
    return render(request, template_name,context)
    





from .models import Download

# @login_required(login_url="/login/")
def ui_notifications_view(request, *args, **kwargs):

    qs = Measurements.objects.all()
    qs_actual=Download.objects.all()
    template_name="ui-notifications.html"

    #total space
    qs1=Metadata.objects.all()
    from django.db.models import Sum

    sum_size=qs1.aggregate(Sum('Size_ko'))
    sum_size=int(sum_size['Size_ko__sum']/1000000)

    # nbr of files 

    df = pd.DataFrame(list(Measurements.objects.all().values('Ref_trip'))) 
    df_once=list(set(list(df['Ref_trip'])))
    df_once = list(map(int, df_once)) 

    # print(df_once)
    nbr_files=int(df_once[-1])

    # downloaded data
    #not yet

    # users
    from django.contrib.auth import get_user_model
    User = get_user_model()

    nbr_users=User.objects.count()

    # Measurements.objects.all().delete()

    # people=Person.objects.all()


    #this part is to select the available transects in the database
    #it is here because it should still be visible with no nuttons selected

    list_of_metadata_references=[]

    for met in Metadata.objects.all():
        list_of_metadata_references.append(met.Path_Reference)

    list_available_transects=[]


    #get the download requests list:
    qs_down=Download.objects.all()



    context={'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements" : Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects":list_available_transects,
        # "people":permission_requiredple,
        "download": qs_actual, 
        'is_admin':bool(True),
        "nbr_files":nbr_files,
        "sum_size":sum_size,
        "nbr_users":nbr_users,
        "interface":True,
        "qs_down":qs_down
            }

    return render(request, template_name,context)




    
def download(request):

    qs = Measurements.objects.all()
    template_name="download.html"

    #total space
    qs1=Metadata.objects.all()
    from django.db.models import Sum

    sum_size=qs1.aggregate(Sum('Size_ko'))
    sum_size=int(sum_size['Size_ko__sum']/1000000)


    # nbr of files 

    df = pd.DataFrame(list(Measurements.objects.all().values('Ref_trip'))) 
    df_once=list(set(list(df['Ref_trip'])))
    df_once = list(map(int, df_once)) 

    # print(df_once)
    nbr_files=int(df_once[-1])

    # downloaded data
    #not yet

    # users
    # users
    from django.contrib.auth import get_user_model
    User = get_user_model()

    nbr_users=User.objects.count()


    #this part is to select the available transects in the database
    #it is here because it should still be visible with no nuttons selected

    list_of_metadata_references=[]

    for met in Metadata.objects.all():
        list_of_metadata_references.append(met.Path_Reference)

    # print(list_of_metadata_references)
    list_available_transects=[]


    #download part

    response = HttpResponse(content_type="text/csv")

    writer = csv.writer(response)
    writer.writerow(['Ref_trip', 'Date', 'Time', 'Nbr_minutes', 'Latitude', 'Longitude',
       'Distance', 'Cumul_Distance', 'Area', 'Salinity_SBE45',
       'QC_Salinity_SBE45', 'Variance_Salinity_SBE45', 'Temp_in_SBE38',
       'QC_Temp_in_SBE38', 'Variance_Temp_in_SBE38', 'Oxygen', 'QC_Oxygen',
       'Variance_Oxygen', 'Turbidity', 'QC_Turbidity', 'Variance_Turbidity',
       'Chl_a', 'QC_Chl_a', 'Variance_Chl_a', 'Course', 'Variance_course', 'Speed',
       'Variance_Speed', 'Temp_SBE45', 'Variance_Temp_SBE45', 'Cond_SBE45',
       'Variance_Cond_SBE45', 'SoundVel_SBE45', 'Variance_SoundVel_SBE45',
       'Saturation', 'Variance_Saturation', 'pH', 'Variance_pH',
       'pH_Satlantic', 'Variance_pH_Satlantic', 'pressure',
       'Variance_pressure', 'flow_in', 'Variance_flow_in', 'flow_main',
       'Variance_flow_main', 'flow_pH', 'Variance_flow_pH', 'flow_pCO2',
       'Variance_flow_pCO2', 'halffull', 'Variance_halffull'])

    #get the request
    transect_query_download_query=request.GET.get('transect_select_download')

    # parameter_query_download_query=request.GET.get('test')

    
    # if is_valid_queryparam(parameter_query_download_query):
    #     print(parameter_query_download_query)

    if is_valid_queryparam(transect_query_download_query):

        chosen_transect= qs.filter(Ref_trip=(transect_query_download_query.split('_')[0]))

        for element in chosen_transect.values_list('Ref_trip', 'Date', 'Time', 'Nbr_minutes', 'Latitude', 'Longitude',
       'Distance', 'Cumul_Distance', 'Area', 'Salinity_SBE45',
       'QC_Salinity_SBE45', 'Variance_Salinity_SBE45', 'Temp_in_SBE38',
       'QC_Temp_in_SBE38', 'Variance_Temp_in_SBE38', 'Oxygen', 'QC_Oxygen',
       'Variance_Oxygen', 'Turbidity', 'QC_Turbidity', 'Variance_Turbidity',
       'Chl_a', 'QC_Chl_a', 'Variance_Chl_a', 'Course', 'Variance_course', 'Speed',
       'Variance_Speed', 'Temp_SBE45', 'Variance_Temp_SBE45', 'Cond_SBE45',
       'Variance_Cond_SBE45', 'SoundVel_SBE45', 'Variance_SoundVel_SBE45',
       'Saturation', 'Variance_Saturation', 'pH', 'Variance_pH',
       'pH_Satlantic', 'Variance_pH_Satlantic', 'pressure',
       'Variance_pressure', 'flow_in', 'Variance_flow_in', 'flow_main',
       'Variance_flow_main', 'flow_pH', 'Variance_flow_pH', 'flow_pCO2',
       'Variance_flow_pCO2', 'halffull', 'Variance_halffull'):
            writer.writerow(element)

# response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

        filename=str(transect_query_download_query)+".csv"

        response['Content-Disposition']='attachment;filename="{}"'.format(filename)

        return response

    context={'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements" : Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects":list_available_transects,
        'is_admin':bool(True),
        "nbr_files":nbr_files,
        "sum_size":sum_size,
        "nbr_users":nbr_users,
        "interface":True
        
            }

    return render(request, template_name,context)


from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Measurements

# def handle_uploaded_file(f):
#     with open('some/file/name.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)


import csv
import os.path
from os import path
from django.db.models import Sum

def upload(request):
    #total space
    qs1 = Metadata.objects.all()
    
    sum_size = qs1.aggregate(Sum('Size_ko'))
    
    if sum_size['Size_ko__sum'] is not None:
        sum_size = int(sum_size['Size_ko__sum'] / 1000000)
    else:
        sum_size = 0

    # nbr of files 

    df = pd.DataFrame(list(Measurements.objects.all().values('Ref_trip'))) 
    df_once=list(set(list(df['Ref_trip'])))
    df_once = list(map(int, df_once)) 

    # print(df_once)
    nbr_files=int(df_once[-1])

    # downloaded data
    #not yet

    # users
    from django.contrib.auth import get_user_model
    User = get_user_model()

    nbr_users=User.objects.count()

    file_query_result=request.GET.get('myfile')

    path_1="C:/FerryBox/Indexed_files/Marseille/"
    path_2="C:/FerryBox/Indexed_files/Genova/"

    if is_valid_queryparam(file_query_result):

        if path.exists(path_1+file_query_result):
            file=path_1+file_query_result
        else:
            file=path_2+file_query_result

        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # The header row values become your keys
                ref_trip = row['Ref_trip']
                date = row['Date']
                time=row['Time']
                nbr_minutes= row['Nbr_minutes']
                latitude= row['Latitude']
                longitude= row['Longitude']
                distance= row['Distance']
                cumul_Distance= row['Cumul_Distance']
                area= row['Area']
                salinity_SBE45= row['Salinity_SBE45']
                qC_Salinity_SBE45= row['QC_Salinity_SBE45']
                variance_Salinity_SBE45= row['Variance_Salinity_SBE45']
                temp_in_SBE38= row['Temp_in_SBE38']
                qC_Temp_in_SBE38= row['QC_Temp_in_SBE38']
                variance_Temp_in_SBE38= row['Variance_Temp_in_SBE38']
                oxygen= row['Oxygen']
                qC_Oxygen= row['QC_Oxygen']
                variance_Oxygen= row['Variance_Oxygen']
                turbidity= row['Turbidity']
                qC_Turbidity= row['QC_Turbidity']
                variance_Turbidity= row['Variance_Turbidity']
                chl_a= row['Chl_a']
                qC_Chl_a= row['QC_Chl_a']
                variance_Chl_a= row['Variance_Chl_a']
                course= row['Course']
                variance_course=row['Variance_course']
                speed= row['Speed']
                variance_Speed= row['Variance_Speed']
                temp_SBE45= row['Temp_SBE45']
                variance_Temp_SBE45= row['Variance_Temp_SBE45']
                cond_SBE45= row['Cond_SBE45']
                variance_Cond_SBE45= row['Variance_Cond_SBE45']
                soundVel_SBE45= row['SoundVel_SBE45']
                variance_SoundVel_SBE45= row['Variance_SoundVel_SBE45']
                saturation= row['Saturation']
                variance_Saturation= row['Variance_Saturation']
                PH= row['pH']
                variance_pH= row['Variance_pH']
                PH_Satlantic= row['pH_Satlantic']
                variance_pH_Satlantic= row['Variance_pH_Satlantic']
                Pressure= row['pressure']
                variance_pressure= row['Variance_pressure']
                Flow_in= row['flow_in']
                variance_flow_in= row['Variance_flow_in']
                Flow_main= row['flow_main']
                variance_flow_main= row['Variance_flow_main']
                Flow_pH= row['flow_pH']
                variance_flow_pH= row['Variance_flow_pH']
                Flow_pCO2= row['flow_pCO2']
                variance_flow_pCO2= row['Variance_flow_pCO2']
                Halffull= row['halffull']
                variance_halffull= row['Variance_halffull']

                new_revo = Measurements(Ref_trip =ref_trip, Date=date,Time=time,Nbr_minutes=nbr_minutes,Latitude=latitude,          
                 Longitude=longitude, Distance=distance, Cumul_Distance=cumul_Distance,
                  Area=area, Salinity_SBE45=salinity_SBE45, QC_Salinity_SBE45=qC_Salinity_SBE45,
                  Variance_Salinity_SBE45=variance_Salinity_SBE45,Temp_in_SBE38=temp_in_SBE38,
                  QC_Temp_in_SBE38=qC_Temp_in_SBE38, Variance_Temp_in_SBE38=variance_Temp_in_SBE38,
                  Oxygen=oxygen, QC_Oxygen=qC_Oxygen, Variance_Oxygen=variance_Oxygen,
                  Turbidity=turbidity, QC_Turbidity=qC_Turbidity, Variance_Turbidity=variance_Turbidity,
                  Chl_a=chl_a,  QC_Chl_a=qC_Chl_a, Variance_Chl_a=variance_Chl_a,Course=course,Variance_course=variance_course,
                  Speed=speed,Variance_Speed=variance_Speed,Temp_SBE45=temp_SBE45,
                  Variance_Temp_SBE45=variance_Temp_SBE45,Cond_SBE45=cond_SBE45,
                  Variance_Cond_SBE45=variance_Cond_SBE45,SoundVel_SBE45=soundVel_SBE45,
                  Variance_SoundVel_SBE45=variance_SoundVel_SBE45,Saturation=saturation,
                  Variance_Saturation=variance_Saturation,pH=PH,Variance_pH=variance_pH,
                  pH_Satlantic=PH_Satlantic,Variance_pH_Satlantic=variance_pH_Satlantic,
                  pressure=Pressure,Variance_pressure=variance_pressure,flow_in=Flow_in,
                  Variance_flow_in=variance_flow_in,flow_main=Flow_main,
                  Variance_flow_main=variance_flow_main,flow_pH=Flow_pH,
                  Variance_flow_pH=variance_flow_pH,flow_pCO2=Flow_pCO2,
                  Variance_flow_pCO2=variance_flow_pCO2,halffull=Halffull,
                  Variance_halffull=variance_halffull
                   )
                new_revo.save()
    

    template_name="upload.html"

    # print(request.POST)
    context={ 'is_admin':bool(True),
    "nbr_files":nbr_files,
    "sum_size":sum_size,
    "nbr_users":nbr_users,
    "interface":True
    }


    return render(request, template_name,context)


  
    # return render(request, "transect_plotting.html")


#this is the admin dashboard part ?? download and data description should be merged here


def data(request):
    qs = Measurements.objects.all()

    context={
            "metadata": Metadata.objects.all(),
            "Measurements" : Measurements.objects.all(),
            "parameter": Parameters.objects.all(),}

    return render(request, 'data.html')


#this is the heart of your app : a dynamic filter that you are definately keeping..
    




def transect_plotting(request):
    # saving the entered values
    answered= False


     # graph_choice_query = request.GET.get('graph_choice')

    #get the querysets responses

    #confirm process


    #for transect selection
    transect_query_result_times=request.GET.get('transect_select_times')
    # cell_query_result_times=request.GET.get('cell_selection_times')
    mindate_query_result_times=request.GET.get('date_min')
    maxdate_query_result_times=request.GET.get('date_max')
    parameter_query_result_times=request.GET.get('parameter_selection_times')
    position_query_result_times_lat=request.GET.get('position_times_lat')
    position_query_result_times_lon=request.GET.get('position_times_lon')

    size_query_result_times=request.GET.get('size_times')
    qc_param_query_times=request.GET.get('qc_times')

    #for scatter selection
    transect_query_result_scatter=request.GET.get('transect_select_scatter')
    param1_query_result_scatter=request.GET.get('para1_selection_scatter')
    param2_query_result_scatter=request.GET.get('para2_selection_scatter')

    #for bubble, replaced by heat map
    transect_selection_result_heat=request.GET.get('transect_selection_heat')
    parameter_selection_result_heat=request.GET.get('parameter_selection_heat')
    qc_param_result_heat=request.GET.get('qc_param_heat')

    #for the map, not finalised yet
    param_query_map = request.GET.get('parameter_selection_map')  
    transect_query_map= request.GET.get('transect_selection_map') 
    transect_query_qc= request.GET.get('qc_param_map')
    
    #missing query : transect_selection_map , and qc with map prefix

    #this is the reference template
    template_name='transect_plotting.html'

    #this one to populate the buttons
    qs = Measurements.objects.all()


    #i forgot what those are meant for..
    param_query = request.GET.get('parameter_selection')
    xaxis_query=request.GET.get('xaxis_label')
    qc_param_query=request.GET.get('qc_param')

    
    qc_param_query_scatter=request.GET.get('scatter_qc_param')

    #this part is to select the available transects in the database
    #it is here because it should still be visible with no nuttons selected

    list_of_metadata_references=[]

    # print(list_of_metadata_references)

    list_available_transects=[]


    # user_id_query_download=request.POST.get('user_id')        
    email_address_query_download=request.POST.get('email_address')
    # user_name_query_download=request.POST.get('user_name')
    first_name_query_download_=request.POST.get('first_name')
    last_name_query_download=request.POST.get('last_name')
    subject_query_download=request.POST.get('subject')
    transects_query_download=request.POST.get('transect_select_download')


#send e-mail part 
    user_name_query_email=request.GET.get('user_id')
    subject_query_email_=request.GET.get('subject')
    file_query_email=request.GET.get('request_file')
    email_query_email=request.GET.get('mail')
    answer_query_email=request.GET.get('answer')



    if is_valid_queryparam(user_name_query_email):
        if is_valid_queryparam(subject_query_email_):
            if is_valid_queryparam(file_query_email):
                if is_valid_queryparam(email_query_email):
                    if is_valid_queryparam(answer_query_email):


                        qs_mes = Measurements.objects.all()
                        qs_down=Download.objects.all()
                        template_name="ui-notifications.html"

                        if (answer_query_email=="Reject"):
                            Download.objects.filter(Name=user_name_query_email).delete()
                            # print(answer_query_email)
                        if (answer_query_email=="Accept"):     
                            from django.core.mail import send_mail, EmailMessage
                            
                            #format query email
                            file_query_email=file_query_email.split('[\'')[1].split('\']')[0]

                            if "Genova" in file_query_email:

                                path="C:/FerryBox/Indexed_files/Genova/"

                            else:

                                path="C:/FerryBox/Indexed_files/Marseille/"
                            #get the file
                            file=open(path+file_query_email+"_pre.csv","r")
                            # print(file_query_email)
                            email=EmailMessage('Hello from INSTM team',
                                'This e-amil contains the file that you requested in the Tunisian FerryBos dashboard',
                                'tun.ferrybox@gmail.com',
                                [email_query_email])

                            email.content_subtype='html'

                            email.attach("C:/FerryBox/Indexed_files/Marseille/"+file_query_email+"_pre.csv",file.read(),"text/plain")

                            email.send()


                            Download.objects.filter(Name=user_name_query_email).delete()




                        context={'queryset': qs_mes,
                            "metadata": Metadata.objects.all(),
                            "qs_down" : qs_down,
                            'not_admin':bool(True),
                            "down":str("false"),
                            "downed": True
                                    
                                }        
                        return render(request, template_name,context)


#send e-mail part

    if is_valid_queryparam(email_address_query_download):
        if is_valid_queryparam(first_name_query_download_):
            if is_valid_queryparam(last_name_query_download):
                if is_valid_queryparam(subject_query_download):
                    if is_valid_queryparam(transects_query_download):
                        # send_mail(subject= subject,message= message,from_email=settings.DEFAULT_FROM_EMAIL,
                        # recipient_list = [email],fail_silently  = True,)
                    #this is to activate the available transects button
                            #this is filtering based on download requests 
                       #get the inputs
                        if request.method == "POST":
                            new_down = Download(ID_user=request.user.id,Email=email_address_query_download,
                                Name=first_name_query_download_,L_name=last_name_query_download,
                                Subject=subject_query_download,Transects=transects_query_download)
                            new_down.save()

#changement ici
                        qs = Measurements.objects.all()
                        template_name="page-user.html"
                        #this part is to select the available transects in the database
                        #it is here because it should still be visible with no nuttons selected

                        context={'queryset': qs,
                            "metadata": Metadata.objects.all(),
                            "Measurements" : Measurements.objects.all(),
                            "parameter": Parameters.objects.all(),
                            "av_transects":list_available_transects,
                            'not_admin':bool(True),
                            "down":str("false"),
                            "downed": True
                                    
                                }        
                        return render(request, template_name,context)


#end of send e-mail part

    #this is the actual filtering part, for the data access window
    #then, we recieve the user's requests and treat them..
    if is_valid_queryparam(xaxis_query):
        if is_valid_queryparam(qc_param_query):
            if is_valid_queryparam(param_query):

                measurement_query_result=request.GET.get('metadata')

                if is_valid_queryparam(measurement_query_result):

                    

                    qs = qs.filter(Ref_trip=(measurement_query_result.split('_')[0]))

                    #filter based on quality control
                    if (param_query=="Salinity_SBE45"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs

                        else:
                            qs = qs.filter(QC_Salinity_SBE45=float(qc_param_query[0]))
                    
                    if (param_query=="Temp_in_SBE38"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs

                        else:

                            qs = qs.filter(QC_Temp_in_SBE38=float(qc_param_query[0]))

                    if (param_query=="Oxygen"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Oxygen=float(qc_param_query[0]))

                    if (param_query=="Turbidity"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Turbidity=float(qc_param_query[0]))

                    if (param_query=="Chl_a"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        if ((qc_param_query)=="1 - Good"):
                            qs=qs.exclude(QC_Chl_a=2).exclude(QC_Chl_a=3).exclude(QC_Chl_a=4)
                        else:
                            qs = qs.filter(QC_Chl_a=float(qc_param_query[0]))

                    #get the parameter

                    param_column = qs.values_list(str(param_query))

                    if (str(param_query)=="Salinity_SBE45"):
                        axe_title=str(param_query) + " (PSU)"
                    if (str(param_query)=="Temp_in_SBE38"):
                        axe_title=str(param_query) + " (°C)"
                    if (str(param_query)=="Oxygen"):
                        axe_title=str(param_query) + " (ml/l)"
                    if (str(param_query)=="Turbidity"):
                        axe_title=str(param_query) + " (NTU)"
                    if (str(param_query)=="Chl_a"):
                        axe_title=str(param_query) + " (ug/l)"


                        #convert param_column into a good list
                    res = []
                    for r in param_column:
                        res.append((str(r).strip('(),')))

                    param_column=[]
                    for r in res:
                        param_column.append(float(r))


                    #regions part
                    index_latitude= qs.values_list('Latitude')
                    #fix the tuple problem
                    res = []
                    for r in index_latitude:
                        res.append((str(r).strip('(),')))

                    index_latitude=[]
                    for r in res:
                        r=round(float(r), 1)
                        index_latitude.append(float(r))
                    index_latitude=sorted(list(index_latitude))

                    #define 4 regions
                    #regions names: Gulf of Tunis, Sardinia canal, west of Sardinia, north of the blp (tunis-marseille)
                    #(tunis-genova) Gulf of Tunis, southern Sardinia, eastern Sardinia, east of Corsica, Gulf of Genoa

                    #concerned data list: x-axis: categories with latitude

                    #the function
                    takeClosest = lambda num, list_values: min(list_values, key=lambda x: abs(x - num)) if list_values else None
                    direction=False

                    #pick the path: 
                    if "Marseille" in measurement_query_result:
                        template_name="transect_plotting.html"

                        direction=True
                        #tunis-marseille :
                        #limit 1:
                        #coordinates: latitude : 37.229189
                        in_list_value_1=takeClosest(37.229189,index_latitude)
                        if in_list_value_1 is None or in_list_value_1 not in index_latitude:
                            messages.error(request, "La valeur de latitude sélectionnée est invalide ou manquante.")
                            return redirect("Ferry_plot:transect_plotting")  
                        else:
                           limit_1 = index_latitude.index(in_list_value_1)

                        #limit 2:
                        #coordinates: latitude : 38.871362
                        in_list_value_2=takeClosest(38.871362,index_latitude)
                        if in_list_value_2 is None or in_list_value_2 not in index_latitude:
                            messages.error(request, "La valeur de latitude sélectionnée est invalide ou manquante.")
                            return redirect("Ferry_plot:transect_plotting")  
                        else:
                           limit_2 = index_latitude.index(in_list_value_2)

                        #limit 3:
                        #coordinates: latitude : 41.741184
                        in_list_value_3=takeClosest(41.741184,index_latitude)
                        if in_list_value_3 is None or in_list_value_3 not in index_latitude:
                            messages.error(request, "La valeur de latitude sélectionnée est invalide ou manquante.")
                            return redirect("Ferry_plot:transect_plotting")  
                        else:
                           limit_3 = index_latitude.index(in_list_value_3)

                        limit_4=len(index_latitude)
                        limit_5=0

                    else:
                        template_name="transect_plotting_genova.html"
                        #tunis-genoa :
                        #limit 1:
                        #coordinates: latitude : 37.229189
                        in_list_value_1=takeClosest(37.229189,index_latitude)
                        if in_list_value_1 is not None and in_list_value_1 in index_latitude:
                            limit_1 = index_latitude.index(in_list_value_1)
                        else:
                          print(f"[DEBUG] in_list_value_1 est None ou absent de index_latitude: {in_list_value_1}")
                          limit_1 = 1

                        #limit 2:
                        #coordinates: latitude : 39.07552 
                        in_list_value_2=takeClosest(39.07552,index_latitude)
                        if in_list_value_2 is None or in_list_value_2 not in index_latitude:
                            messages.error(request, "La valeur de latitude sélectionnée est invalide ou manquante.")
                            return redirect("Ferry_plot:transect_plotting")  
                        else:
                           limit_2 = index_latitude.index(in_list_value_2)

                        #limit 3:
                        #coordinates: latitude : 41.312946 
                        in_list_value_3=takeClosest(41.312946 ,index_latitude)
                        if in_list_value_3 is None or in_list_value_3 not in index_latitude:
                            messages.error(request, "La valeur de latitude sélectionnée est invalide ou manquante.")
                            return redirect("Ferry_plot:transect_plotting")  
                        else:
                           limit_3 = index_latitude.index(in_list_value_3)

                        #limit 4:
                        #coordinates: latitude : 43.013796
                        in_list_value_4=takeClosest(43.013796,index_latitude)
                        if in_list_value_4 is None or in_list_value_4 not in index_latitude:
                            messages.error(request, "La valeur de latitude sélectionnée est invalide ou manquante.")
                            return redirect("Ferry_plot:transect_plotting")  
                        else:
                           limit_4 = index_latitude.index(in_list_value_4)

                        limit_5=len(index_latitude)



                    #part of regions coloring


                    title="Trip reference : " + str(measurement_query_result.split('_')[0]) 

                    #sort ur values ..
                    if str(xaxis_query)== "Distance":
                        index_column= qs.values_list('Cumul_Distance')
                    # elif str(xaxis_query)== "Lalitude":
                        # index_column= qs.values_list('Latitude')
                    elif str(xaxis_query)== "Longitude":
                        index_column= qs.values_list('Longitude')
                    else:
                        index_column= qs.values_list('Latitude')

                    #convert index_column into a good list
                    res = []
                    for r in index_column:
                        res.append((str(r).strip('(),')))

                    index_column=[]
                    for r in res:
                        r=round(float(r), 1)
                        index_column.append(float(r))

                    #final result column
                    #add a condition here to sort this x column
                    #keep one single direction : Tunis - Europe ( will slightly complicate things..)

                    if str(xaxis_query)== "Distance":
                        index_column=sorted(list(index_column))
                    elif str(xaxis_query)== "Longitude":
                        index_column=sorted(list(index_column))
                        index_column.reverse()
                    else:
                        index_column=sorted(list(index_column))

                    #now reverse the y axis list to match it with the sorted x axis values
                    #reference: 24_2016-03-12_175646_genova_to_Goulette_731501_pre.csv
                    departure=str(measurement_query_result.split("_")[3])
                    if (departure != "goulette") and (departure != "Goulette"):
                        param_column=list(param_column) 
                        param_column.reverse()                    

                    matadata_save=str(measurement_query_result)

                    #save user's entries
                    save_transect=str(measurement_query_result)
                    save_parameter=str(param_query)
                    save_xaxis=str(xaxis_query)
                    save_qc=str(qc_param_query)


                    answered= True

                    #this block is picking "admin interface" or "data dowbload"
                    try:
                        is_admin=bool(False)  

                        if (str(request.user.groups.all()[0]))=="admin":
                            is_admin=bool(True)
                            down=str("true")

                        context= { 'is_admin': is_admin,
                        'queryset': qs,
                        "metadata": Metadata.objects.all(),
                        "Measurements" : Measurements.objects.all(),
                        "parameter": Parameters.objects.all(),
                        "categories": index_column,
                        "values": param_column,
                        "axe_title":axe_title,
                        "title":title,
                        "param_name":str(param_query),
                        "av_transects":list_available_transects,
                        "matadata_save": matadata_save,
                        "down":down,
                        "save_transect":save_transect,
                        "save_parameter":save_parameter,
                        "save_xaxis":save_xaxis,
                        "save_qc":save_qc,
                        "answered":answered,
                        # regions part
                        "direction":bool(direction),
                        "limit_1":int(limit_1),
                        "limit_2":int(limit_2),
                        "limit_3":int(limit_3),
                        "limit_4":int(limit_4),
                        "limit_5":int(limit_5),
                        "access":True,


                         }

                    except IndexError:
                        down=str("false")
                        context={"not_admin": bool(True),
                        'queryset': qs,
                        "metadata": Metadata.objects.all(),
                        "Measurements" : Measurements.objects.all(),
                        "parameter": Parameters.objects.all(),
                        "categories": index_column,
                        "values": param_column,
                        "axe_title":axe_title,
                        "title":title,
                        "param_name":str(param_query),
                        # "av_transects":list_available_transects,
                        "matadata_save": matadata_save,
                        "down":down,
                        "save_transect":save_transect,
                        "save_parameter":save_parameter,
                        "save_xaxis":save_xaxis,
                        "save_qc":save_qc,
                        "answered":answered,
                        #regions part
                        "direction":bool(direction),
                        "limit_1":int(limit_1),
                        "limit_2":int(limit_2),
                        "limit_3":int(limit_3),
                        "limit_4":int(limit_4),
                        "limit_5":int(limit_5),
                        "access":True,

                        }
    elif is_valid_queryparam(maxdate_query_result_times):
        if is_valid_queryparam(parameter_query_result_times):
            if is_valid_queryparam(position_query_result_times_lat) and is_valid_queryparam(position_query_result_times_lon):
                if is_valid_queryparam(size_query_result_times):
                    if is_valid_queryparam(mindate_query_result_times):
                        if is_valid_queryparam(transect_query_result_times):
                            if is_valid_queryparam(qc_param_query_times):
                                # plot the two segments for point picker
                                qs1=Measurements.objects.all()
                                qs_genova = qs1.filter(Ref_trip=59) #genova
                                qs_marseille = qs1.filter(Ref_trip=110) #marseille
                                

                                meta=Metadata.objects.all()                      

                                template_name="time_series.html"

                                dmin = datetime.strptime(mindate_query_result_times, '%Y-%m-%d').date()
                                dmax = datetime.strptime(maxdate_query_result_times, '%Y-%m-%d').date()         

                                #filter metadata per range of date
                                 
                                meta_filtered=Metadata.objects.filter(Date__range=[dmin, dmax]) 

                                #filter by transect Gen/mars
                                if "Marseille" in transect_query_result_times:
                                    trans="Marseille"
                                else: 
                                    trans="genova"

                                meta_filtered=meta_filtered.filter(Name__contains=trans) 

                                #grab the correspondant files

                                files_names=meta_filtered.values_list('Name') 

                                #transform to refrences 

                                list_ref=[]

                                for name in files_names:
                                    list_ref.append(int(str(name).split('_')[0].split('\'')[1]))

                                #initiate                            
                                avrg_graph=[]
                                date_graph=[]
                                max_graph=[]
                                min_graph=[]

                                #detect the files by filtering measurements 

                                def find_nearest(array, value):
                                    n = [abs(i-value) for i in array]
                                    idx = n.index(min(n))
                                    return array[idx]

                                import numpy as np

                                for ref in list_ref:

                                    file=Measurements.objects.all().filter(Ref_trip=ref)

                                    #u need a quality control option here !!

                                    param_query=parameter_query_result_times
                                    qc_param_query=qc_param_query_times
                                    qs=file

                                    #sort by date
                                    qs=qs.order_by('Date')

                                    # #filter based on quality control
                                    if (param_query=="Salinity_SBE45"):

                                        if ((qc_param_query)=="0 - None"):
                                            qs=qs

                                        else:
                                            qs = qs.filter(QC_Salinity_SBE45=float(qc_param_query[0]))
                                    
                                    if (param_query=="Temp_in_SBE38"):

                                        if ((qc_param_query)=="0 - None"):
                                            qs=qs

                                        else:

                                            qs = qs.filter(QC_Temp_in_SBE38=float(qc_param_query[0]))

                                    if (param_query=="Oxygen"):

                                        if ((qc_param_query)=="0 - None"):
                                            qs=qs
                                        else:

                                            qs = qs.filter(QC_Oxygen=float(qc_param_query[0]))

                                    if (param_query=="Turbidity"):

                                        if ((qc_param_query)=="0 - None"):
                                            qs=qs
                                        else:

                                            qs = qs.filter(QC_Turbidity=float(qc_param_query[0]))

                                    if (param_query=="Chl_a"):

                                        if ((qc_param_query)=="0 - None"):
                                            qs=qs
                                        if ((qc_param_query)=="1 - Good"):
                                            qs=qs.exclude(QC_Chl_a=2).exclude(QC_Chl_a=3).exclude(QC_Chl_a=4)
                                        else:
                                            qs = qs.filter(QC_Chl_a=float(qc_param_query[0])) 


                                    #now reverse your values !!

                                    parameter_query_result_times=param_query
                                    qc_param_query_times=qc_param_query
                                    file=qs.order_by('Date')


                                    #grab the latitude row (add a range of 0.05) (change this one)
                                    initial_latitude=float(position_query_result_times_lat)
                                    lat=[]
                                    listed=list(file.values_list("Latitude"))
                                    for v in listed:
                                        flt_value=float(str(v).split('(')[1].split(',')[0])
                                        lat.append(flt_value)
                                    if lat:
                                        # print(find_nearest(lat, initial_latitude))
                                        start_point=find_nearest(lat, initial_latitude)
                                    else: 
                                        start_point=38.869131
                                    #i know that the latitude value exists, that's why i can write :
                                    row=file.filter(Latitude=start_point)
                                    # print(type(row))
                                    
                                    # #which cumulated distance ?

                                    start_distance=row.values_list('Cumul_Distance').first()
                                    if start_distance != (0.0,) and start_distance != None:
                                        start_dist=float(str(start_distance).split('(')[1].split(',')[0])
                                    # else:
                                    #     start_dist=200

                                    # #range of distances ?
                                    min_dist=start_dist-(int(size_query_result_times)/2)
                                    max_dist=start_dist+(int(size_query_result_times)/2)
                                    range_distance=file.filter(Cumul_Distance__range=(min_dist, max_dist))

                                    # print(range_distance)

                                    #get the parameter comlumn

                                    selected_parameter=range_distance.values_list(parameter_query_result_times)

                                    from statistics import mean 
                                    #calculate average value

                                    #convert tuples to floats (change this one)
                                    flts=[]
                                    clmn=list(selected_parameter)
                                    for x in clmn:
                                        flts.append(float(str(x).split('(')[1].split(',')[0]))
                                    # print(flts)
                                    # clmn=function_to_convert(clmn)
                                    if flts:
                                        avrg=mean(list(flts))
                                        max_gr=max(list(flts))
                                        min_gr=min(list(flts))
                                    # else:
                                    #     avrg=5
                                    

                                    # #save to graph table
                                    avrg_graph.append(float(avrg))
                                    max_graph.append(float(max_gr))
                                    min_graph.append(float(min_gr))

                                    #what's the date for this file ?
                                    #i have the ref : ref
                                    #search in metadata table

                                    # file_date.append(Metadata.objects.filter(Path_Reference=ref))
                                    date_non_formatted=Metadata.objects.filter(Path_Reference=ref).first().Date
                                    # format_date =str(date_non_formatted).split('(')[2].split(')')[0]
                                    # format_date_final = date_non_formatted
                                    # format_date_final=format_date_final.strftime('%Y-%m-%d')
                                    date_graph.append(str(date_non_formatted))

                                
                                #cell column is the date one 

                                title= str(transect_query_result_times) + ": " + str(mindate_query_result_times) + ' to ' + str(maxdate_query_result_times)
                                

                                if (str(parameter_query_result_times)=="Salinity_SBE45"):
                                    axe_title=str(parameter_query_result_times) + " (PSU)"
                                if (str(parameter_query_result_times)=="Temp_in_SBE38"):
                                    axe_title=str(parameter_query_result_times) + " (°C)"
                                if (str(parameter_query_result_times)=="Oxygen"):
                                    axe_title=str(parameter_query_result_times) + " (ml/l)"
                                if (str(parameter_query_result_times)=="Turbidity"):
                                    axe_title=str(parameter_query_result_times) + " (NTU)"
                                if (str(parameter_query_result_times)=="Chl_a"):
                                    axe_title=str(parameter_queryresult_times) + " (u_g/l)"

                                #save user's entries
                                save_transect=str(transect_query_result_times)
                                save_parameter=str(parameter_query_result_times)
                                save_date1=str(mindate_query_result_times)
                                save_date2=str(maxdate_query_result_times)
                                save_position_lat=round(float(position_query_result_times_lat),4)
                                save_position_lon=round(float(position_query_result_times_lon),4)
                                save_size=int(size_query_result_times)
                                save_qc=(qc_param_query_times)
                                # save_cell=str(cell_query_result_times)

                                answered= True

                                    #this block is picking "admin interface" or "data dowbload"
                                try:
                                    is_admin=bool(False)  

                                    if (str(request.user.groups.all()[0]))=="admin":
                                        is_admin=bool(True)
                                        down=str("true")

                                    context= { 'is_admin': is_admin,
                                        'queryset': qs,
                                        "metadata": Metadata.objects.all(),
                                        "Measurements" : Measurements.objects.all(),
                                        "parameter": Parameters.objects.all(),
                                        # "cell":l,
                                        "categories": date_graph,
                                        "values": avrg_graph,
                                        "title_graph": title,
                                        "param_name": axe_title,
                                        # "av_transects":list_available_transects,
                                        "down":down,
                                        "save_transect":save_transect,
                                        "save_parameter":save_parameter,
                                        # "save_cell":save_cell,
                                        "answered":answered,
                                        "save_date1":save_date1,
                                        "save_date2":save_date2,
                                        "save_position_lat":save_position_lat,
                                        "save_position_lon":save_position_lon,
                                        "save_size":save_size,
                                        "save_qc":save_qc,
                                        "max_graph":max_graph,
                                        "min_graph":min_graph,
                                        "access":True,
                                        "qs_genova":qs_genova,
                                        "qs_marseille":qs_marseille,
                                     }

                                except IndexError:
                                    down=str("false")
                                    context={"not_admin": bool(True),
                                    'queryset': qs,
                                        "metadata": Metadata.objects.all(),
                                        "Measurements" : Measurements.objects.all(),
                                        "parameter": Parameters.objects.all(),
                                        # "cell":l,
                                        "categories": date_graph,
                                        "values": avrg_graph ,
                                        "title_graph": title,
                                        "param_name": axe_title,
                                        # "av_transects":list_available_transects,
                                        "down":down,
                                        "save_transect":save_transect,
                                        "save_parameter":save_parameter,
                                        # "save_cell":save_cell,
                                        "answered":answered,
                                        "save_date1":save_date1,
                                        "save_date2":save_date2,
                                        "save_position_lat":save_position_lat,
                                        "save_position_lon":save_position_lon,
                                        "save_size":save_size,
                                        "save_qc":save_qc,
                                        "max_graph":max_graph,
                                        "min_graph":min_graph,
                                        "access":True,
                                        "qs_genova":qs_genova,
                                        "qs_marseille":qs_marseille,
                                        }
               

    elif is_valid_queryparam(transect_query_result_scatter):
        if is_valid_queryparam(qc_param_query_scatter):
            qs = Measurements.objects.all()
            if is_valid_queryparam(param1_query_result_scatter):
                if is_valid_queryparam(param2_query_result_scatter):

                    template_name="scatter.html"


                    qs = qs.filter(Ref_trip=(transect_query_result_scatter.split('_')[0]))

                    qc_param_query=qc_param_query_scatter

                    #filter based on quality control (param1)
                    if (param1_query_result_scatter=="Salinity_SBE45"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs

                        else:
                            qs = qs.filter(QC_Salinity_SBE45=float(qc_param_query[0]))
                    
                    if (param1_query_result_scatter=="Temp_in_SBE38"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs

                        else:

                            qs = qs.filter(QC_Temp_in_SBE38=float(qc_param_query[0]))

                    if (param1_query_result_scatter=="Oxygen"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Oxygen=float(qc_param_query[0]))

                    if (param1_query_result_scatter=="Turbidity"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Turbidity=float(qc_param_query[0]))

                    if (param1_query_result_scatter=="Chl_a"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Chl_a=float(qc_param_query[0]))


                    #filter based on quality control (second param)
                    if (param2_query_result_scatter=="Salinity_SBE45"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:
                            qs = qs.filter(QC_Salinity_SBE45=float(qc_param_query[0]))
                    
                    if (param2_query_result_scatter=="Temp_in_SBE38"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs

                        else:

                            qs = qs.filter(QC_Temp_in_SBE38=float(qc_param_query[0]))

                    if (param2_query_result_scatter=="Oxygen"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Oxygen=float(qc_param_query[0]))

                    if (param2_query_result_scatter=="Turbidity"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Turbidity=float(qc_param_query[0]))

                    if (param2_query_result_scatter=="Chl_a"):

                        if ((qc_param_query)=="0 - None"):
                            qs=qs
                        else:

                            qs = qs.filter(QC_Chl_a=float(qc_param_query[0]))

                        #end of quality control part

                    qs = qs.values_list(str(param1_query_result_scatter),str(param2_query_result_scatter))

                    data_filtered=[]

                    for q in qs:
                        el1=q[0]
                        el2=q[1]
                        X=[el1,el2]
                        data_filtered.append(X)


                    data_filtered=list(data_filtered)

                    #regression line
                    import numpy as np
                    import matplotlib.pyplot as plt  # To visualize
                    import pandas as pd  # To read data
                    from sklearn.linear_model import LinearRegression 

                    #convert to datframe
                    from pandas import DataFrame  
                    data = DataFrame(data_filtered)

                    X = data.iloc[:, 0].values.reshape(-1, 1)  
                    Y = data.iloc[:, 1].values.reshape(-1, 1)

                    linear_regressor = LinearRegression()  
                    linear_regressor.fit(X, Y)
                    Y_pred = linear_regressor.predict(X) 

                    #regression line is composed of X and Y_pred values
                    X=X[:2]
                    Y_pred=Y_pred[:2] 


                    #verify whether the correlation is + or -:
                    corr_type=((X[1]-X[0])/(Y_pred[1]-Y_pred[0]))


                    #line equation : y=ax+b
                    if corr_type>0:                        
                        x1=min(X)[0]
                        x2=max(X)[0]
                        y1=min(Y_pred)[0]
                        y2=max(Y_pred)[0]
                    else:
                        x1=min(X)[0]
                        x2=max(X)[0]
                        y1=max(Y_pred)[0]
                        y2=min(Y_pred)[0]


                    a= (y2-y1)/(x2-x1)
                    # print(a)
                    b= y2 -(a*x2)

                    #new extreme points
                    #extand the line (y coordinates) :
                    x_min=min(data_filtered)[0]
                    x_max=max(data_filtered)[0]
                    #y coordinates
                    y_min=(a*x_min)+b
                    y_max=(a*x_max)+b

                    #final regression line
                    reg_line=list([[x_min,y_min],[x_max,y_max]])


                    #end of regression line

                    if (str(param1_query_result_scatter)=="Salinity_SBE45"):
                        p1_graph=str(param1_query_result_scatter) + " (PSU)"
                    if (str(param1_query_result_scatter)=="Temp_in_SBE38"):
                        p1_graph=str(param1_query_result_scatter) + " (°C)"
                    if (str(param1_query_result_scatter)=="Oxygen"):
                        p1_graph=str(param1_query_result_scatter) + " (ml/l)"
                    if (str(param1_query_result_scatter)=="Turbidity"):
                        p1_graph=str(param1_query_result_scatter) + " (NTU)"
                    if (str(param1_query_result_scatter)=="Chl_a"):
                        p1_graph=str(param1_query_result_scatter) + " (ug/l)"

                    if (str(param2_query_result_scatter)=="Salinity_SBE45"):
                        p2_graph=str(param2_query_result_scatter) + " (PSU)"
                    if (str(param2_query_result_scatter)=="Temp_in_SBE38"):
                        p2_graph=str(param2_query_result_scatter) + " (°C)"
                    if (str(param2_query_result_scatter)=="Oxygen"):
                        p2_graph=str(param2_query_result_scatter) + " (ml/l)"
                    if (str(param2_query_result_scatter)=="Turbidity"):
                        p2_graph=str(param2_query_result_scatter) + " (NTU)"
                    if (str(param2_query_result_scatter)=="Chl_a"):
                        p2_graph=str(param2_query_result_scatter) + " (ug/l)"

                    title_graph= "Transect ref: " + (transect_query_result_scatter.split('_')[0]) + " : " + p1_graph + " / " + p2_graph
                    

                    #save user's entries
                    save_transect=str(transect_query_result_scatter)
                    save_parameter1=str(param1_query_result_scatter)
                    save_parameter2=str(param2_query_result_scatter)

                    answered= True
                    #this block is picking "admin interface" or "data dowbload"
                    try:
                        is_admin=bool(False)  

                        if (str(request.user.groups.all()[0]))=="admin":
                            is_admin=bool(True)
                            down=str("true")

                        context= { 'is_admin': is_admin,
                            'queryset': qs,
                            "metadata": Metadata.objects.all(),
                            "Measurements" : Measurements.objects.all(),
                            "parameter": Parameters.objects.all(),
                            "data_filtered": data_filtered,
                            "title_graph":title_graph,
                            "p1_graph":p1_graph,
                            "p2_graph":p2_graph,
                            "av_transects":list_available_transects,
                            "down":down,
                            'answered':bool(answered),
                            "save_transect":save_transect,
                            "save_parameter1":save_parameter1,
                            "save_parameter2":save_parameter2,
                            'qc':(qc_param_query),
                            "reg_line":reg_line,
                            "access":True,
                         }

                    except IndexError:
                        down=str("false")
                        context={"not_admin": bool(True),
                            'queryset': qs,
                            "metadata": Metadata.objects.all(),
                            "Measurements" : Measurements.objects.all(),
                            "parameter": Parameters.objects.all(),
                            "data_filtered": data_filtered,
                            "title_graph":title_graph,
                            "p1_graph":p1_graph,
                            "p2_graph":p2_graph,
                            "av_transects":list_available_transects,
                            "down":down,
                            'answered':bool(answered),
                            "save_transect":save_transect,
                            "save_parameter1":save_parameter1,
                            "save_parameter2":save_parameter2,
                            'qc':(qc_param_query),
                            "reg_line":reg_line,
                            "access":True,

                            }

    elif is_valid_queryparam(param_query_map):
        if is_valid_queryparam(transect_query_map):            
            if is_valid_queryparam(transect_query_qc):
                qs_tot = Measurements.objects.all()
                qs = qs.filter(Ref_trip=(transect_query_map.split('_')[0]))

                # qs = qs.filter(Ref_trip=(measurement_query_result.split('_')[0]))

                #filter based on quality control
                if (param_query_map=="Salinity_SBE45"):

                    if ((transect_query_qc)=="0 - None"):
                        qs=qs

                    else:
                        qs = qs.filter(QC_Salinity_SBE45=float(transect_query_qc[0]))
                
                if (param_query_map=="Temp_in_SBE38"):

                    if ((transect_query_qc)=="0 - None"):
                        qs=qs

                    else:

                        qs = qs.filter(QC_Temp_in_SBE38=float(transect_query_qc[0]))

                if (param_query_map=="Oxygen"):

                    if ((transect_query_qc)=="0 - None"):
                        qs=qs
                    else:

                        qs = qs.filter(QC_Oxygen=float(transect_query_qc[0]))


                if (param_query_map=="Chl_a"):

                    if ((transect_query_qc)=="0 - None"):
                        qs=qs
                    else:

                        qs = qs.filter(QC_Chl_a=float(transect_query_qc[0]))

                if (param_query_map=="Turbidity"):

                    if ((transect_query_qc)=="0 - None"):
                        qs=qs
                    else:

                        qs = qs.filter(QC_Turbidity=float(transect_query_qc[0]))

            #i transformed those into points with good density
            # i need to add a quality control button


                #2158315 is the first element, delete it ! 

                if str(param_query_map)=="Salinity_SBE45":
                    template_name="map_Salinity_SBE45.html"
                elif str(param_query_map)=="Temp_in_SBE38":
                    template_name="map_Temp_SBE38.html"
                elif str(param_query_map)=="Oxygen":
                    template_name="map_Oxygen.html"
                elif str(param_query_map)=="Chl_a":
                    template_name="map_Chl_a.html"
                elif str(param_query_map)=="Turbidity":
                    template_name="map_Turbidity.html"
                else:
                    template_name="map.html"

                trip= str(transect_query_map.split('_')[0])
                transect=str(transect_query_map.split('_')[3])+ ' - ' + str(transect_query_map.split('_')[5])
                date=str(transect_query_map.split('_')[1])


                qc=transect_query_qc

                if (qc=="0 - None"):
                    quality='None applied'
                if (qc=="1 - Good"):
                    quality='Good'
                if (qc=="2 - Probably good"):
                    quality='Probably Good'
                if (qc=="3 - Probably bad"):
                    quality='Probably Bad'
                if (qc=="4 - Bad"):
                    quality='Bad'


                save_transect=str(transect_query_map)
                save_parameter=str(param_query_map)

                answered= True


                #this block is picking "admin interface" or "data dowbload"
                try:
                    is_admin=bool(False)  

                    if (str(request.user.groups.all()[0]))=="admin":
                        is_admin=bool(True)
                        down=str("true")

                    context= { 'is_admin': is_admin,
                    'queryset': qs,
                    "metadata": Metadata.objects.all(),
                    "Measurements" : Measurements.objects.all(),
                    "parameter": Parameters.objects.all(),
                    # "av_transects":list_available_transects,
                    "down":down,
                    'trip':trip,
                    'transect':transect,
                    'date':date,
                    'qc':transect_query_qc,
                    'quality':quality,
                    'save_transect':save_transect,
                    'save_parameter':save_parameter,
                    'answered': bool(answered),
                    "access":True,
                     }

                except IndexError:
                    down=str("false")
                    context={"not_admin": bool(True),
                    'queryset': qs,
                    "metadata": Metadata.objects.all(),
                    "Measurements" : Measurements.objects.all(),
                    "parameter": Parameters.objects.all(),
                    # "av_transects":list_available_transects,
                    "down":down,
                    'trip':trip,
                    'transect':transect,
                    'date':date,
                    'qc':transect_query_qc,
                    'quality':quality,
                    'save_transect':save_transect,
                    'save_parameter':save_parameter,
                    'answered':bool(answered),
                    "access":True,
                    }


    else:
                #this block is picking "admin interface" or "data dowbload"
        try:
            is_admin=bool(False)  

            if (str(request.user.groups.all()[0]))=="admin":
                is_admin=bool(True)
                down=str("true")

            context= { 'is_admin': is_admin,
                'queryset': qs,
                "metadata": Metadata.objects.all(),
                "Measurements" : Measurements.objects.all(),
                "parameter": Parameters.objects.all(),
                "av_transects":list_available_transects,
                "down":down,
                'answered':bool(answered),
                "access":True,
             }

        except IndexError:
            context={"not_admin": bool(True),
            'queryset': qs,
                "metadata": Metadata.objects.all(),
                "Measurements" : Measurements.objects.all(),
                "parameter": Parameters.objects.all(),
                "av_transects":list_available_transects,
                "down":str("false"),
                'answered':bool(answered),
                "access":True,
                }

    return render(request, template_name, context)





def scatter_view(request):

    qs = Measurements.objects.all()
    template_name="scatter.html"


    #this part is to select the available transects in the database
    #it is here because it should still be visible with no nuttons selected

    list_of_metadata_references=[]

    for met in Metadata.objects.all():
        list_of_metadata_references.append(met.Path_Reference)

    list_available_transects=[]
    # save_reapeated_ones=[]
 
    #this block is picking "admin interface" or "data dowbload"
    try:
        is_admin=bool(False)  

        if (str(request.user.groups.all()[0]))=="admin":
            is_admin=bool(True)
            down=down=str("true")

        context= { 'is_admin': is_admin,
        'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements" : Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects":list_available_transects,
        "down":down
         }

    except IndexError:
        down=down=str("false")
        context={"not_admin": bool(True),
        'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements" : Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects":list_available_transects,
        "down":down,
        "access":True,
        }   

    return render(request, template_name,context)







def time_series(request):
    # Récupération de toutes les données
    qs1 = Measurements.objects.all()
    qs_genova = qs1.filter(Ref_trip=99)
    qs_marseille = qs1.filter(Ref_trip=171)

    template_name = "time_series.html"

    # Bloc admin
    try:
        is_admin = False
        down = "false"
        if str(request.user.groups.all()[0]) == "admin":
            is_admin = True
            down = "true"
    except IndexError:
        is_admin = False
        down = "false"

    # Initialiser le context
    context = {
        'is_admin': is_admin,
        'down': down,
        'qs_genova': qs_genova,
        'qs_marseille': qs_marseille,
        'metadata': Metadata.objects.all(),
        'Measurements': Measurements.objects.all(),
        'parameter': Parameters.objects.all(),
        'access': True
    }

    # Traitement du formulaire GET
    if request.GET.get("parameter_selection_times"):
        param = request.GET.get("parameter_selection_times")
        date_min = request.GET.get("date_min")
        date_max = request.GET.get("date_max")
        lat = request.GET.get("position_times_lat")
        lon = request.GET.get("position_times_lon")
        size = float(request.GET.get("size_times", 2))

        # Filtrage des mesures autour du point sélectionné
        filtered = Measurements.objects.filter(
            Latitude__range=(float(lat)-size, float(lat)+size),
            Longitude__range=(float(lon)-size, float(lon)+size),
        )

        if date_min:
            filtered = filtered.filter(Date__gte=date_min)
        if date_max:
            filtered = filtered.filter(Date__lte=date_max)

        # Grouper par date, faire moy, min, max
        grouped = filtered.values("Date").annotate(
            avg_value=Avg(param),
            min_value=Min(param),
            max_value=Max(param)
        ).order_by("Date")

        categories = [item["Date"].strftime("%Y-%m-%d") for item in grouped]
        values = [item["avg_value"] for item in grouped]
        min_graph = [item["min_value"] for item in grouped]
        max_graph = [item["max_value"] for item in grouped]

        context.update({
            "categories": categories,
            "values": values,
            "min_graph": min_graph,
            "max_graph": max_graph,
            "title_graph": f"{param} over time",
            "param_name": param,
            "answered": True,
            "save_parameter": param,
            "save_position_lat": lat,
            "save_position_lon": lon,
            "save_date1": date_min,
            "save_date2": date_max,
            "save_size": size
        })

    return render(request, template_name, context)





NOTIFICATIONS = []

def get_notifications(request):
    """Renvoie les notifications stockées."""
    return JsonResponse({"notifications": NOTIFICATIONS})

def map_view(request):

    qs = Measurements.objects.all()
    template_name="map.html"

    list_available_transects=[]

    #this block is picking "admin interface" or "data dowbload"
    try:
        is_admin=bool(False)  

        if (str(request.user.groups.all()[0]))=="admin":
            is_admin=bool(True)
            down=str("true")

        context= { 'is_admin': is_admin,
        'queryset': qs,
            "metadata": Metadata.objects.all(),
            "Measurements" : Measurements.objects.all(),
            "parameter": Parameters.objects.all(),
            "av_transects":list_available_transects,
            "down":down,
            "access":True,
         }

    except IndexError:
        down=str("false")
        context={"not_admin": bool(True),
        'queryset': qs,
            "metadata": Metadata.objects.all(),
            "Measurements" : Measurements.objects.all(),
            "parameter": Parameters.objects.all(),
            "av_transects":list_available_transects,
            "down":down,
            "access":True,
                }
    

    return render(request, template_name,context)


def popup_map(request):

    qs = Measurements.objects.all()
    template_name="popup_map.html"
        # plot the two segments for point picker
    qs1=Measurements.objects.all()
    qs_genova = qs1.filter(Ref_trip=59) #genova
    qs_marseille = qs1.filter(Ref_trip=110) #marseille


    #this part is to select the available transects in the database
    #it is here because it should still be visible with no nuttons selected

    list_of_metadata_references=[]

    for met in Metadata.objects.all():
        list_of_metadata_references.append(met.Path_Reference)

    list_available_transects=[]
    # save_reapeated_ones=[]
 
    #this block is picking "admin interface" or "data dowbload"
    try:
        is_admin=bool(False)  

        if (str(request.user.groups.all()[0]))=="admin":
            is_admin=bool(True)
            down=down=str("true")

        context= { 'is_admin': is_admin,
        'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements" : Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects":list_available_transects,
        "down":down,
        "qs_genova":qs_genova,
        "qs_marseille":qs_marseille
         }

    except IndexError:
        down=down=str("false")
        context={"not_admin": bool(True),
        'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements" : Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects":list_available_transects,
        "down":down,
        "qs_genova":qs_genova,
        "qs_marseille":qs_marseille


        }   

    return render(request, template_name,context)



#algorithme de stockage des fichier dans la base de données

import csv
from django.shortcuts import render, HttpResponse, redirect
   
# dans votreapp/views.py
 

import pandas as pd

  

 
# /////////////////////////////////////////
from tablib import Dataset
from datetime import datetime

def importExcel(request):
    print("imported_data") 
    template_name="importExcel.html"

    if request.method == 'POST':
        print("okkkkkkkkkkkkk111***********")  # Add this line
        dataset = Dataset()
        new_file = request.FILES['my_file']
        with io.TextIOWrapper(new_file, encoding='utf-8') as text_file:
            imported_data = dataset.load(text_file.read(), format='csv')
        print("okkkkkkkkkkkkk*222**********")  # Add this line

        try:
            for row in imported_data:
                row_values = row[0].split(';')
                
                if not row_values[0].strip('“”'):  # Check if date-time is empty
                    continue

                date_time_str = row_values[0].strip('“”')  # Remove leading and trailing quotes

                try:
                    date_time = datetime.strptime(date_time_str, '%Y.%m.%d %H:%M:%S')
                except ValueError as ve:
                    print(f"Erreur lors de l'importation : {ve}")
                    continue  # Skip the row with invalid date-time format

                print(row)
                value = ClassifiedFilesGenova(
                   Date_Time=date_time,
                    Latitude=float(row_values[1].replace('.', '').replace(',', '.')),  # Convert to float and remove thousands separators
                    Longitude=float(row_values[2].replace('.', '').replace(',', '.')),  # Convert to float and remove thousands separators
                    Course=float(row_values[3].replace('.', '').replace(',', '.')),
                    Speed=float(row_values[4].replace('.', '').replace(',', '.')),
                    Temp_SBE45=float(row_values[5].replace('.', '').replace(',', '.')),
                    Cond_SBE45=float(row_values[6].replace('.', '').replace(',', '.')),
                    Salinity_SBE45=float(row_values[7].replace('.', '').replace(',', '.')),
                    SoundVel_SBE45=float(row_values[8].replace('.', '').replace(',', '.')),
                    Temp_in_SBE38=float(row_values[9].replace('.', '').replace(',', '.')),
                    Oxygen=float(row_values[10].replace('.', '').replace(',', '.')),
                    Saturation=float(row_values[11].replace('.', '').replace(',', '.')),
                    Temperature_Optode=float(row_values[12].replace('.', '').replace(',', '.')),
                    Turbidity=float(row_values[13].replace('.', '').replace(',', '.')),
                    Chl_a=float(row_values[14].replace('.', '').replace(',', '.')),
                    pH_Meinsberg=float(row_values[15].replace('.', '').replace(',', '.')),
                    Temp_Meinsberg=float(row_values[16].replace('.', '').replace(',', '.')),
                    pH_SeaFET=float(row_values[17].replace('.', '').replace(',', '.')),
                    pCO2=float(row_values[18].replace('.', '').replace(',', '.')),
                    pressure=float(row_values[19].replace('.', '').replace(',', '.')),
                    flow_in=float(row_values[20].replace('.', '').replace(',', '.')),
                    flow_main=float(row_values[21].replace('.', '').replace(',', '.')),
                    flow_pH=float(row_values[22].replace('.', '').replace(',', '.')),
                    flow_pCO2=float(row_values[23].replace('.', '').replace(',', '.')),
                    halffull=float(row_values[24].replace('.', '').replace(',', '.')),
                    full=float(row_values[25].replace('.', '').replace(',', '.')),
                
                )
                
                value.save()

            print("Importation réussie.")
            return render(request,template_name, {'success': True})
        except Exception as e:
            print(f"Erreur lors de l'importation : {e}")
            return render(request, template_name, {'error': str(e)})

    return render(request, template_name)
# /////////////////////////////

from .forms import UploadFileForm
from .models import Metadata

 
from datetime import datetime

# ...

# def mails(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             file_content = request.FILES['file'].read().decode('latin-1')

#             # Extraire les métadonnées du fichier
#             metadata = Metadata()
#             metadata.Name = file_content.split('$Filename;')[1].split('\n')[0].strip()
#             metadata.Departure = file_content.split('$TrackStart:')[1].split('\n')[0].strip()
#             metadata.Destination = file_content.split('$TrackEnd:')[1].split('\n')[0].strip()

#             # Trouver la ligne de la date et la nettoyer
#             raw_date_line = next(line for line in file_content.split('\n') if '$DateTime;' in line)
#             raw_date = raw_date_line.split('$DateTime;')[1].strip()

#             # Convertir la date au format 'YYYY-MM-DD'
#             metadata.Year = int(raw_date.split('.')[0])
#             metadata.Date = datetime.strptime(raw_date, '%Y.%m.%d %H:%M:%S').strftime('%Y-%m-%d')

#             # Enregistrez les métadonnées dans la base de données
#             metadata.save()

#             return redirect('success')  # Redirigez vers une page de succès

#     else:
#         form = UploadFileForm()

#     return render(request, 'mails.html', {'form': form})
# views.py
from .models import Metadata, Parameters
# views.py
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Metadata, Parameters
from datetime import datetime

# def mails(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             file_content = request.FILES['file'].read().decode('latin-1')

#             # Extraire les métadonnées du fichier
#             metadata = Metadata()
#             metadata.Name = file_content.split('$Filename;')[1].split('\n')[0].strip()
#             metadata.Departure = file_content.split('$TrackStart:')[1].split('\n')[0].strip()
#             metadata.Destination = file_content.split('$TrackEnd:')[1].split('\n')[0].strip()

#             # Convertir la date au format 'YYYY-MM-DD'
#             raw_date_line = next(line for line in file_content.split('\n') if '$DateTime;' in line)
#             raw_date = raw_date_line.split('$DateTime;')[1].strip()
#             metadata.Year = int(raw_date.split('.')[0])
#             metadata.Date = datetime.strptime(raw_date, '%Y.%m.%d %H:%M:%S').strftime('%Y-%m-%d')

#             # Enregistrez les métadonnées dans la base de données
#             metadata.save()

#             # Extraire les paramètres du fichier
#             parameters_data = next((line for line in file_content.split('\n') if '$DATASETS' in line), None)
            
#             if parameters_data:
#                 # Obtenez l'index de la ligne '$DATASETS'
#                 datasets_index = file_content.split('\n').index(parameters_data)

#                 # Lire la suite du fichier après la ligne '$DATASETS'
#                 datasets_content = file_content.split('\n')[datasets_index + 1:]

#                 # Assurez-vous qu'il y a au moins deux lignes avant d'essayer d'accéder à l'indice [1]
#                 if len(datasets_content) > 1:
#                     unit_values = datasets_content[0].split('\t')[1:]
#                     parameter_labels = datasets_content[1].split('\t')
#                     print(unit_values)
#                     # Enregistrez les paramètres dans la base de données
#                     for label in parameter_labels:
#                         # Ajoutez "variance_" devant chaque libellé
#                         # variance_label = f"variance_{label}"
                        
#                         # Enregistrez le paramètre dans la base de données
#                         # parameter, created = Parameters.objects.get_or_create(libelle=variance_label)
#                         parameter, created = Parameters.objects.get_or_create(libelle=label)
                    
#                     # Extraire les données de mesure du fichier
#                     measurements_data = datasets_content[2:]
#                     for measurement_line in measurements_data:
#                         if measurement_line:
#                             measurement_values = measurement_line.split('\t')

#                             # Vérifier que la ligne n'est pas une ligne d'en-tête
#                             if measurement_values[0] != 'Date Time':
#                                 measurement = Measurement.objects.create(id_meta=metadata)

#                                 # Associez les paramètres aux mesures
#                                 for index, label in enumerate(parameter_labels):
#                                     parameter = Parameters.objects.get(libelle=f"variance_{label}")
#                                     # Gérer dynamiquement les types de données
#                                     value = measurement_values[index].strip()
#                                     # print("label: " + str(label) + ", index: " + str(index) + ", value:" + str(value))
#                                     if ' ' in value:
#                                         setattr(measurement, parameter.libelle,
#                                                 datetime.strptime(value, '%Y.%m.%d %H:%M:%S').strftime('%Y-%m-%d'))
#                                     elif '.' in value or ',' in value:  # Float
#                                         setattr(measurement, parameter.libelle, float(value))
#                                     elif value.isdigit() or (value[1:].isdigit() and value[0] == '-'):  # Integer
#                                         setattr(measurement, parameter.libelle, int(value))
#                                     else:  # String (ou autre type à traiter selon les besoins)
#                                         setattr(measurement, parameter.libelle, value)

#                                 measurement.save()

#                                 # Associez les paramètres aux mesures
#                                 for label in parameter_labels:
#                                     parameter = Parameters.objects.get(libelle=f"variance_{label}")
#                                     Measur_param_assoc.objects.create(id_measurement=measurement, id_parametre=parameter)

#             return redirect('success')  # Redirigez vers une page de succès

#     else:
#         form = UploadFileForm()

#     return render(request, 'mails.html', {'form': form})
# def mails(request):
#     message = None

#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             file_content = request.FILES['file'].read().decode('latin-1')

#             # Extract metadata from the file
#             metadata = Metadata()
#             metadata.Name = file_content.split('$Filename;')[1].split('\n')[0].strip()

#             # Extracting relevant parts from the filename
#             file_name_parts = metadata.Name.split('_')
#             trip_number = file_name_parts[0].split('\\')[-1]  # Extracting the trip number from the file path
#             date_part = file_name_parts[1]
#             trip_name = '_'.join(file_name_parts[2:-2])  # Joining trip name parts (excluding date and time)
#             file_id = file_name_parts[-1].split('.')[0]  # Extracting the file identifier

#             # Combining extracted parts to form the desired name format
#             metadata.Name = f"{trip_number} {date_part} {trip_name} {file_id}"

#             metadata.Departure = file_content.split('$TrackStart:')[1].split('\n')[0].strip()
#             metadata.Destination = file_content.split('$TrackEnd:')[1].split('\n')[0].strip()

#             raw_date_line = next(line for line in file_content.split('\n') if '$DateTime;' in line)
#             raw_date = raw_date_line.split('$DateTime;')[1].strip()
#             metadata.Year = int(raw_date.split('.')[0])
#             metadata.Date = datetime.strptime(raw_date, '%Y.%m.%d %H:%M:%S').strftime('%Y-%m-%d')
#             metadata_name = metadata.Name.replace(" ", "_")
#             metadata.Name = metadata_name
#             metadata.save()


#             # Extract parameters from the file
#             parameters_data = next((line for line in file_content.split('\n') if '$DATASETS' in line), None)

#             if parameters_data:
#                 datasets_index = file_content.split('\n').index(parameters_data)
#                 datasets_content = file_content.split('\n')[datasets_index + 1:]

#                 if len(datasets_content) > 1:
#                     unit_values = datasets_content[0].split('\t')[1:]
#                     parameter_labels = datasets_content[1].split('\t')[0:]

#                     # Save parameters in the Parameters table
#                     previous_label = None

#                     for label, unit in zip(parameter_labels, unit_values):
#                         try:
#                             # Concatenate with the previous label if the current label is "Variance"
#                             if label == "Variance" or label == "Variance\n":
#                                 if previous_label:
#                                     label = f"{previous_label}_{label}"
                        
#                             # Replace empty unit with space ' '
#                             unit = unit.strip() if unit.strip() else ' '

#                             # Try to get an existing parameter or create a new one
#                             parameter, created = Parameters.objects.get_or_create(libelle=label, defaults={'unit': unit})

#                             if not created or parameter.unit != unit:
#                                 # Update the unit if it's different
#                                 parameter.unit = unit
#                                 parameter.save()
                            
#                             previous_label = label  # Update the previous_label for the next iteration

#                         except Parameters.MultipleObjectsReturned:
#                             # If multiple objects are returned, choose one arbitrarily (you may want to handle this better)
#                             parameter = Parameters.objects.filter(libelle=label, unit=unit).first()
#                         except Parameters.DoesNotExist:
#                             # Create a new parameter if it doesn't exist
#                             parameter = Parameters.objects.create(libelle=label, unit=unit)

#                         print(f"Parameter {label} - {unit} saved/updated.")


#                     # Extract measurement data from the file
#                     measurements_data = datasets_content[2:]
#                     # ...
#                     previous_label = None

#                     for measurement_line in measurements_data:
#                         if measurement_line:
#                             measurement_values = measurement_line.split('\t')

#                             # Check if the line is not a header
#                             if measurement_values[0] != 'Date Time':
                                

#                                 # Associate parameters with measurements
#                                 for index, label in enumerate(parameter_labels):
#                                     if label == "Variance" or label == "Variance\n":
#                                         if previous_label:
#                                             label = f"{previous_label}_{label}"
#                                     try:
#                                         # Try to get an existing parameter
#                                         parameter = Parameters.objects.get(libelle=label)
#                                     except Parameters.MultipleObjectsReturned:
#                                         # If multiple objects are returned, choose one arbitrarily (you may want to handle this better)
#                                         parameter = Parameters.objects.filter(libelle=label).first()
#                                     except Parameters.DoesNotExist:
#                                         # Handle the case where the parameter does not exist
#                                         print(f"Parameter {label} not found.")

#                                     value = str(measurement_values[index])
                                                                
#                                     previous_label = label                                    
#                                     # Handle datetime parsing

#                                     # setattr(measurement, parameter.libelle, value)
#                                     # setattr(measurement,  value)

#                                     print(value)
#                                     measurement = Measurement.objects.create(value=value,id_meta=metadata)  # Move this line outside of the parameter loop
                                
#                                     Measur_param_assoc.objects.create(id_measurement=measurement, id_parametre=parameter)
#                                     # print(f"Association created: Measurement {measurement.id} - Parameter {parameter.id}")

#                     # ...
#                     message = "Le traitement du fichier a été effectué avec succès."
#                     messages.success(request, message)
#                     print("Process completed.")
#                     return redirect('mails')
#         else:
#             # Si le formulaire est invalide, définissez un message d'échec
#             message = "Échec du traitement du fichier. Veuillez vérifier votre fichier."
#             messages.error(request, message)
#     else:
#         form = UploadFileForm()

#     return render(request, 'mails.html', {'form': form, 'message': message})

# from django.db import connection
# from django.shortcuts import render

# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# # def import_mails(request, id_meta):
# #     # Define your SQL query
# #     sql_query = """
# #     SELECT fm.id_mesurment, fm.value, p.libelle, p.unit
# #     FROM public."Ferry_plot_measurement" fm
# #     JOIN public."Ferry_plot_measur_param_assoc" mpa ON fm.id_mesurment = mpa.id_measurement_id
# #     JOIN public."Ferry_plot_parameters" p ON mpa.id_parametre_id = p.id_params
# #     JOIN public."Ferry_plot_metadata" me ON fm.id_meta_id = me.id_meta
# #     WHERE me.id_meta = 105
# #     """

# #     # Execute the raw SQL query
# #     with connection.cursor() as cursor:
# #         cursor.execute(sql_query, [id_meta])
# #         rows = cursor.fetchall()

# #     # Paginate the data
# #     paginator = Paginator(rows,10   )
# #     page = request.GET.get('page')

# #     try:
# #         measurements_data = paginator.page(page)
# #     except PageNotAnInteger:
# #         measurements_data = paginator.page(1)
# #     except EmptyPage:
# #         measurements_data = paginator.page(paginator.num_pages)

# #     # Pass the data to the template
# #     context = {
# #         'measurements_data': measurements_data,
# #     }

# #     return render(request, 'import_mails.html', context)
# from django.shortcuts import render
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.db import connection
# from django import template

# register = template.Library()

# @register.filter(name='get_range')
# def get_range(value):
#     return range(value)

# from django.shortcuts import redirect

# def import_mails(request, id_meta=None):
#      # Récupérer tous les métadonnées de la base de données
#     metadata_list = Metadata.objects.all()
    
#     # Si aucun id_meta n'est fourni dans l'URL ou s'il est vide, récupérer le premier id_meta de la base de données
#     if not id_meta or id_meta == '':
#         first_metadata = Metadata.objects.first()
#         if first_metadata:
#             # Rediriger l'utilisateur vers l'URL avec le premier id_meta
#             return redirect('import_mails', id_meta=first_metadata.id_meta)
    
#     # Récupérer la valeur sélectionnée de id_meta dans la liste déroulante
#     selected_id_meta = request.GET.get('id_meta', None)
    
#     # Vérifier si le formulaire a été soumis
#     if request.method == 'POST':
#         id_meta = request.GET.get('id_meta_id')
    
#     if id_meta is not None:
#         # Définir votre requête SQL
#         sql_query = """
#         SELECT
#             p.libelle,
#             p.unit,
#             ARRAY_AGG(fm.value) AS values
#         FROM
#             public."Ferry_plot_measurement" fm
#         JOIN
#             public."Ferry_plot_measur_param_assoc" mpa ON fm.id_mesurment = mpa.id_measurement_id
#         JOIN
#             public."Ferry_plot_parameters" p ON mpa.id_parametre_id = p.id_params
#         JOIN
#             public."Ferry_plot_metadata" me ON fm.id_meta_id = me.id_meta
#         WHERE
#             me.id_meta = %s
#         GROUP BY
#             p.libelle, p.unit ,p.id_params
#         ORDER BY 
#             p.id_params
#         """
#         # Exécuter la requête SQL brute avec id_meta comme paramètre
#         with connection.cursor() as cursor:
#             cursor.execute(sql_query, [id_meta])
#             rows = cursor.fetchall()

#         # Organiser les données pour le rendu dans le modèle
#         measurements_data = []
#         for row in rows:
#             measurements_data.append({
#                 'libelle': row[0],
#                 'unit': row[1],
#                 'values': row[2],
#             })
        
#         range_values = range(len(measurements_data[0]['values']))

#         # Préparer les données avec les valeurs en fonction de l'index dynamique
#         prepared_data = []
#         for m in range_values:
#             row_data = []
#             for measurement in measurements_data:
#                 if m < len(measurement['values']):
#                     row_data.append(measurement['values'][m])
#                 else:
#                     row_data.append(None)  # ou toute autre valeur de substitution
#             prepared_data.append(row_data)

#         # Paginer les données
#         paginator = Paginator(measurements_data, len(range_values))
#         page = request.GET.get('page')

#         try:
#             measurements_data_paginated = paginator.page(page)
#         except PageNotAnInteger:
#             measurements_data_paginated = paginator.page(1)
#         except EmptyPage:
#             measurements_data_paginated = paginator.page(paginator.num_pages)

#         # Passer les données au modèle
#         context = {
#             'measurements_data': measurements_data_paginated,
#             'range_values': range_values,
#             'prepared_data': prepared_data,
#             'metadata_list': metadata_list,
#             'id_meta': id_meta,
#             'selected_id_meta': selected_id_meta
#         }

#         return render(request, 'import_mails.html', context)
#     else:
#         # Gérer le cas où id_meta n'est pas fourni
#         # Vous pouvez rediriger l'utilisateur vers une autre page ou afficher un message d'erreur
#         return HttpResponse("Please provide a valid id_meta.")

# def dataLabel(request):
#     qs = Metadata.objects.all()
#     template_name="import_html.html"

#     #total space
#     qs1=Metadata.objects.all()
#     from django.db.models import Sum

#     sum_size=qs1.aggregate(Sum('Size_ko'))
#     sum_size=int(sum_size['Size_ko__sum']/1000000)

#     # nbr of files 

#     df = pd.DataFrame(list(Measurements.objects.all().values('Ref_trip'))) 
#     df_once=list(set(list(df['Ref_trip'])))
#     df_once = list(map(int, df_once)) 

#     # print(df_once)
#     nbr_files=int(df_once[-1])

#     # downloaded data
#     #not yet

#     # users
#     from django.contrib.auth import get_user_model
#     User = get_user_model()

#     nbr_users=User.objects.count()



#     context={
#         "metadata":qs,
#         'is_admin':bool(True),
#         "nbr_files":nbr_files,
#         "sum_size":sum_size,
#         "nbr_users":nbr_users,
#         "interface":True
#         # "departs":departs,
#         # "destinations":destinations,
#     }

#     return render(request, template_name,context)