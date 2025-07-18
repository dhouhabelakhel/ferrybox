
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
import io
import sys
from contextlib import redirect_stdout
from django.http import HttpResponse
import logging

from django.shortcuts import render
from Ferry_app.apps import FerryAppConfig
from Ferry_plot.log_handler import WebLogHandler
from django.http import JsonResponse
from Ferry_plot.log_handler import WebLogHandler


def get_latest_notifications(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT file_name, received_at, date FROM ferry_plot_notifications ORDER BY received_at DESC LIMIT 5")
        rows = cursor.fetchall()
    
    notifications = [
        {
            "file_name": row[0],
            "received_at": row[1].strftime('%Y-%m-%d %H:%M:%S'),
            "date": row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else "N/A"
        }
        for row in rows
    ]

    return JsonResponse({"notifications": notifications})

def notifications_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT file_name, received_at, date FROM ferry_plot_notifications ORDER BY received_at DESC")
        rows = cursor.fetchall()
    
    # Structure the data into a list of dictionaries for the template
    notifications = [
        {
            "file_name": row[0],
            "received_at": row[1].strftime('%Y-%m-%d %H:%M:%S'),  # Format received_at for display
            "date": row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else "N/A"  # Format date or fallback to "N/A"
        }
        for row in rows
    ]

    return render(request, "notifications.html", {"notifications": notifications})
def terminal_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Requête AJAX
        logs = WebLogHandler.get_logs()
        return JsonResponse({"logs": logs})

    # Cas du premier chargement de la page (non-AJAX)
    logs = WebLogHandler.get_logs()
    return render(request, "terminal.html", {"logs": logs, "process": True})
def first_page(request):
    return render(request,"index.html")




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
from django.db.models import Count
from datetime import datetime

# @login_required(login_url="/login/")
from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth, Concat
from django.contrib.auth import get_user_model
from .models import Metadata, Measurements
import glob
import csv
import os
from django.db.models import Value

from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth, Concat
from django.contrib.auth import get_user_model
from .models import Metadata, Measurements
from django.db.models import Value, CharField
from django.db import connection

def get_table_count(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row = cursor.fetchone()
    return row[0] if row else 0
def index(request):
    # Calcul de l'espace total utilisé
    qs1 = Metadata.objects.all()
    sum_size = qs1.aggregate(Sum('Size_ko'))['Size_ko__sum'] or 0  # Éviter les erreurs si aucune donnée n'existe
    sum_size = int(sum_size / 1000000)  # Conversion en Mo
    
    # Calcul du nombre de fichiers uniques (Ref_trip distincts)
    unique_ref_trips = Measurements.objects.values_list('Ref_trip', flat=True).distinct()
    nbr_files = len(unique_ref_trips)
    
    # Nombre d'utilisateurs
    User = get_user_model()
    nbr_users = User.objects.count()
    
    # Répartition des données par mois
    monthly_data = (
        Measurements.objects.annotate(
            year_month=Concat(
                ExtractYear('Date'),
                Value('-'),
                ExtractMonth('Date'),
                output_field=CharField()  # Spécifier le type de sortie comme CharField
            )
        )
        .values('year_month')  # Grouper par année-mois
        .annotate(count=Count('id'))  # Compter le nombre d'enregistrements
        .order_by('year_month')  # Trier par année-mois
    )
    
    # Calculer le nombre total d'enregistrements pour déterminer les pourcentages
    total_records = Measurements.objects.count()
    
    # Convertir les résultats en une liste de dictionnaires pour le template
    # Ajouter le pourcentage pour chaque mois
    repartition = []
    sum_percentage = 0  # Variable pour stocker la somme des pourcentages
    
    if total_records > 0:  # Éviter la division par zéro
        for entry in monthly_data:
            percentage = (entry['count'] / total_records) * 100
            rounded_percentage = round(percentage, 2)  # Arrondir à 2 décimales
            
            repartition.append({
                'month': entry['year_month'],
                'count': entry['count'],
                'percentage': rounded_percentage
            })
            
            sum_percentage += rounded_percentage  # Ajouter à la somme
    
    # Arrondir la somme finale à 2 décimales
    sum_percentage = round(sum_percentage, 2)
    
    # Détection si l'utilisateur est admin
    try:
        is_admin = str(request.user.groups.all()[0]) == "admin"
    except IndexError:
        is_admin = False
    nb_tronques = get_table_count('ferry_plot_binary_truncated_files')
    nb_corrects = get_table_count('ferry_plot_binary_email')
    total_fichiers = nb_tronques + nb_corrects

    if total_fichiers > 0:
        pourcentage_tronques = round((nb_tronques / total_fichiers) * 100, 2)
    else:
        pourcentage_tronques = 0
    # Contexte à passer au template
    context = {
        'is_admin': is_admin,
        'nbr_files': nbr_files,
        'sum_size': sum_size,
        'nbr_users': nbr_users,
        'overview': True,
        'repartition': repartition,
        'sum_percentage': round((sum_percentage/nbr_files),2) if nbr_files > 0 else 0,
        'total_records': total_records,
        'pourcentage_tronques': pourcentage_tronques, 
    }
    
    # Rendre la page avec le contexte
    return render(request, "index.html", context)


def data_description(request):
    qs = Metadata.objects.all()
    template_name="data_description.html"

    #total space
    qs1=Metadata.objects.all()
    from django.db.models import Sum

    sum_size=qs1.aggregate(Sum('Size_ko'))
    sum_size = int(sum_size['Size_ko__sum'] / 1024)

    # nbr of files 

    unique_ref_trips = Measurements.objects.values_list('Ref_trip', flat=True).distinct()
    nbr_files = len(unique_ref_trips)

    

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
    # Cette ligne récupère déjà les téléchargements avec Status=False
    qs_actual = Download.objects.filter(Status=False)
    template_name = "ui-notifications.html"
    
    # Total space
    qs1 = Metadata.objects.all()
    from django.db.models import Sum
    
    sum_size = qs1.aggregate(Sum('Size_ko'))
    sum_size = int(sum_size['Size_ko__sum'] / 1024)
    
    # Nbr of files
    unique_ref_trips = Measurements.objects.values_list('Ref_trip', flat=True).distinct()
    nbr_files = len(unique_ref_trips)
    
    # Users
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    nbr_users = User.objects.count()
    
    # Liste des références de métadonnées
    list_of_metadata_references = list(Metadata.objects.values_list('Path_Reference', flat=True))
    
    # Le problème est ici : list_available_transects est vide mais utilisé dans le contexte
    list_available_transects = []
    
    # Get download requests list - uniquement avec Status=False
    qs_down = Download.objects.filter(Status=False)
    
    context = {
        'queryset': qs,
        "metadata": Metadata.objects.all(),
        "Measurements": Measurements.objects.all(),
        "parameter": Parameters.objects.all(),
        "av_transects": list_of_metadata_references, 
        "download": qs_actual,
        'is_admin': True, 
        "nbr_files": nbr_files,
        "sum_size": sum_size,
        "nbr_users": nbr_users,
        "interface": True,
        "qs_down": qs_down
    }
    
    return render(request, template_name, context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.db import connection
import json
import io

from .models import Download

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.db import connection
import json

@csrf_exempt
def update_request(request, id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        data = json.loads(request.body)
        action = data.get('action')

        try:
            request_obj = Download.objects.get(id=id)
        except Download.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Request not found'})

        if action == 'accept':
            return handle_accept_action(request_obj)
        elif action == 'reject':
            request_obj.delete()
            reject_request_email(request_obj.Email)
            return JsonResponse({'success': True, 'message': 'Request rejected'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


def handle_accept_action(request_obj):
    # Update the status of the request object
    request_obj.Status = True
    request_obj.save()

    # Get the transect value and convert it to lowercase
    transect_value = get_transect_value(request_obj)
    transect = str(transect_value).lower()

    # Determine the table name based on the transect value
    table_name = determine_table_name(transect)

    try:
        # Append ".csv" to the transect_value for querying
        libelle_with_csv = f"{transect_value}.csv"

        # Execute the query
        with connection.cursor() as cursor:
            query = f"SELECT fichier FROM {table_name} WHERE libelle = %s"
            cursor.execute(query, [libelle_with_csv])
            row = cursor.fetchone()

        # Check if a row was returned
        if not row:
            return JsonResponse({'success': False, 'error': 'Transect not found in the table'})

        # Extract binary data
        binary_data = row[0]
        if not binary_data:
            return JsonResponse({'success': False, 'error': 'No file content found'})

        # Convert memoryview to bytes and decode binary data into CSV content
        try:
            binary_data_bytes = bytes(binary_data)  # Convert memoryview to bytes
            csv_content = binary_data_bytes.decode('utf-8')  # Decode to string
        except UnicodeDecodeError:
            try:
                csv_content = binary_data_bytes.decode('latin-1')  # Try another encoding
            except Exception:
                return JsonResponse({'success': False, 'error': 'Unable to decode file content'})

        # Send email with the CSV attachment
        send_email_with_attachment(request_obj.Email, transect_value, csv_content)

        return JsonResponse({'success': True, 'message': 'File sent successfully'})

    except Exception as db_error:
        print(f"Database or email error: {str(db_error)}")
        return JsonResponse({'success': False, 'error': str(db_error)})


def get_transect_value(request_obj):
    transect_value = ""
    if isinstance(request_obj.Transects, list):
        transect_value = request_obj.Transects[0] if request_obj.Transects else ""
    elif isinstance(request_obj.Transects, str):
        transect_value = request_obj.Transects
    else:
        raise ValueError("Invalid Transects field")
    return transect_value


def determine_table_name(transect):
    if "genova" in transect:
        return "ferry_plot_binary_indexedgenova"
    elif "marseille" in transect:
        return "ferry_plot_binary_indexedmarseille"
    else:
        raise ValueError("Transect must contain 'genova' or 'marseille'")


def decode_binary_data(binary_data):
    try:
        return binary_data.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return binary_data.decode('latin-1')
        except Exception:
            raise ValueError("Unable to decode file content")


from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

def reject_request_email(email, logo_path="./Ferry_app/static/assets/img/instmLogo.jpg"):
    subject = 'Request Rejected - INSTM'
    from_email = 'ferryboxinstm@gmail.com'
    to = [email]

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="text-align: center;">
                    <img src="cid:instm_logo" alt="INSTM Logo" style="max-width: 120px; margin-bottom: 20px;">
                </div>
                <h2 style="color: #2E5C6E; text-align: center;">Rejection Notice</h2>
                <p style="font-size: 16px; color: #333;">
                    Dear Sir/Madam,
                </p>
                <p style="font-size: 16px; color: #333;">
                    We regret to inform you that your request has been <strong>rejected</strong> 
                </p>
            
                <p style="font-size: 16px; color: #333;">
                    Please feel free to contact us for more information or to submit a new request.
                </p>
                <p style="font-size: 16px; color: #333;">
                    Best regards,<br>The INSTM Team.
                </p>
            </div>
        </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, '', from_email, to)
    msg.attach_alternative(html_content, "text/html")

    # Attach INSTM logo inline
    with open(logo_path, 'rb') as img:
        logo = MIMEImage(img.read())
        logo.add_header('Content-ID', '<instm_logo>')
        logo.add_header('Content-Disposition', 'inline', filename='instm_logo.png')
        msg.attach(logo)

    msg.send()

def send_email_with_attachment(email, transect_value, csv_content):
    subject = 'Your CSV file from INSTM'
    from_email = 'ferryboxinstm@gmail.com'
    to = [email]

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                <div style="text-align: center;">
                    <img src="cid:instm_logo" alt="INSTM Logo" style="max-width: 150px; margin-bottom: 20px;">
                </div>
                <h2 style="color: #2E5C6E; text-align: center;">INSTM - Institut National des Sciences et Technologies de la Mer</h2>
                <p style="font-size: 16px; color: #333;">Please find attached the requested CSV file regarding the transect <strong>{transect_value}</strong>.</p>
                <p style="font-size: 16px; color: #333;">Thank you for your trust,<br>The INSTM team.</p>
            </div>
        </body>
    </html>
    """

    # Email setup
    msg = EmailMultiAlternatives(subject, '', from_email, to)
    msg.attach_alternative(html_content, "text/html")

    # Attaching the CSV file
    msg.attach(f"{transect_value}.csv", csv_content, 'text/csv')

    # Attaching the logo image inline
    logo_path = "./Ferry_app/static/assets/img/instmLogo.jpg"
    with open(logo_path, 'rb') as img:
        logo = MIMEImage(img.read())
        logo.add_header('Content-ID', '<instm_logo>')
        logo.add_header('Content-Disposition', 'inline', filename='instm_logo.png')
        msg.attach(logo)

    msg.send()
from django.http import HttpResponse
from django.db import connection
import csv
import io
import zipfile
def download_initial_file(request, file_name):
    import io

    with connection.cursor() as cursor:
        cursor.execute("SELECT file_data FROM ferry_plot_binary_email WHERE file_name = %s", [file_name])
        result = cursor.fetchone()

    if not result:
        return HttpResponse("Fichier introuvable", status=404)

    binary_data = result[0]
    binary_stream = io.BytesIO(binary_data)

    # Essai multi-encodage
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
        try:
            decoded = binary_stream.getvalue().decode(encoding)
            response = HttpResponse(decoded, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}.txt"'
            return response
        except UnicodeDecodeError:
            continue

    return HttpResponse("Erreur : impossible de décoder le fichier avec les encodages connus.", status=500)
def download_indexed_file(request, indexed_libelle):
    # Déterminer le nom de la table selon le libellé
    if 'genova' in indexed_libelle.lower():
        table_name = 'ferry_plot_binary_indexedgenova'
    elif 'marseille' in indexed_libelle.lower():
        table_name = 'ferry_plot_binary_indexedmarseille'
    else:
        return HttpResponse("Erreur : libellé non reconnu (genova ou marseille attendu).", status=400)

    # Récupérer le fichier binaire depuis la table
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT fichier FROM {table_name} WHERE libelle = %s", [indexed_libelle])
        result = cursor.fetchone()

    if not result:
        return HttpResponse("Fichier introuvable", status=404)

    binary_data = result[0]

    # Convertir memoryview en bytes si nécessaire et tenter plusieurs encodages
    raw_bytes = bytes(binary_data)

    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
        try:
            decoded = raw_bytes.decode(encoding)
            response = HttpResponse(decoded, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{indexed_libelle}.csv"'
            return response
        except UnicodeDecodeError:
            continue

    return HttpResponse("Erreur : impossible de décoder le fichier avec les encodages connus.", status=500)  
def download_classified_file(request,classified_libelle):
     # Déterminer le nom de la table selon le libellé
    if 'genova' in classified_libelle.lower():
        table_name = '"Ferry_plot_binary_classifiedgenova"'
    elif 'marseille' in classified_libelle.lower():
        table_name = '"Ferry_plot_binary_classifiedmarseille"'
    else:
        return HttpResponse("Erreur : libellé non reconnu (genova ou marseille attendu).", status=400)

    # Récupérer le fichier binaire depuis la table
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT fichier FROM {table_name} WHERE libelle = %s", [classified_libelle])
        result = cursor.fetchone()

    if not result:
        return HttpResponse("Fichier introuvable", status=404)

    binary_data = result[0]

    # Convertir memoryview en bytes si nécessaire et tenter plusieurs encodages
    raw_bytes = bytes(binary_data)

    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
        try:
            decoded = raw_bytes.decode(encoding)
            response = HttpResponse(decoded, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{classified_libelle}.csv"'
            return response
        except UnicodeDecodeError:
            continue

    return HttpResponse("Erreur : impossible de décoder le fichier avec les encodages connus.", status=500)  
def download_truncated_file(request, libelle):
    # Récupération du champ binaire
    with connection.cursor() as cursor:
        cursor.execute("SELECT fichier FROM ferry_plot_binary_truncated_files WHERE libelle = %s", [libelle])
        result = cursor.fetchone()

    if not result:
        return HttpResponse("Fichier introuvable", status=404)

    binary_data = result[0]  # c'est du BYTEA

    # On lit les données binaire dans un buffer
    binary_stream = io.BytesIO(binary_data)

    # Si c'est déjà un CSV : pas besoin de transformer
    try:
        # On tente de décoder comme CSV directement
        decoded = binary_stream.read().decode('utf-8')
        response = HttpResponse(decoded, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{libelle}.csv"'
        return response
    except UnicodeDecodeError:
        return HttpResponse("Erreur : le fichier n'est pas un CSV encodé en UTF-8.", status=500)


def fetch_truncated_files():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                libelle, 
                ROUND(OCTET_LENGTH(fichier) / 1024.0, 2) AS size 
            FROM 
                ferry_plot_binary_truncated_files
        """)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    
def download(request):
    qs = Measurements.objects.all()
    template_name = "download.html"

    # Total space
    qs1 = Metadata.objects.all()
    from django.db.models import Sum

    sum_size = qs1.aggregate(Sum('Size_ko'))
    sum_size = int(sum_size['Size_ko__sum'] / 1024)

    # Nbr of files 
    unique_ref_trips = Measurements.objects.values_list('Ref_trip', flat=True).distinct()
    nbr_files = len(unique_ref_trips)


    # Users
    from django.contrib.auth import get_user_model
    User = get_user_model()
    nbr_users = User.objects.count()

    # This part is to select the available transects in the database
    list_of_metadata_references = []
    for met in Metadata.objects.all():
        list_of_metadata_references.append(met.Path_Reference)
    list_available_transects = []

    # Check if we have POST data for downloading multiple transects
    if request.method == 'POST' and 'transect_select_download' in request.POST:
        selected_transects = request.POST.getlist('transect_select_download')
        
        if selected_transects:
            import io
            import zipfile
            from django.http import HttpResponse
            
            # Create a zip file in memory
            buffer = io.BytesIO()
            zip_file = zipfile.ZipFile(buffer, 'w')
            
            # Add each selected transect as a CSV file to the zip
            for transect in selected_transects:
                # Create a CSV for this transect
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)
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
                
                # Filter records for this transect
                ref_trip = transect.split('_')[0]
                chosen_transect = qs.filter(Ref_trip=ref_trip)
                
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
                
                # Add this CSV to the zip file
                filename = f"{transect}.csv"
                zip_file.writestr(filename, csv_buffer.getvalue())
                csv_buffer.close()
            
            # Close the zip file
            zip_file.close()
            
            # Prepare response with the zip file
            response = HttpResponse(buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="ferrybox_data.zip"'
            
            # Important: seek to the beginning of the buffer
            buffer.seek(0)
            return response
    
    # Handle the legacy GET parameter method (backward compatibility)
    transect_query_download_query = request.GET.get('transect_select_download')
    
    if is_valid_queryparam(transect_query_download_query):
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

        chosen_transect = qs.filter(Ref_trip=(transect_query_download_query.split('_')[0]))

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

        filename = str(transect_query_download_query) + ".csv"
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response
    truncated_files=fetch_truncated_files()
  # Alternative approach using raw SQL if you don't have a model
    # Alternative approach using raw SQL if you don't have a model
    email_files_genova = []
    email_files_marseille = []

    try:
      with connection.cursor() as cursor:
        cursor.execute("SELECT id, file_name, file_data FROM ferry_plot_binary_email")
        for row in cursor.fetchall():
            print("Processing email file...")
            file_info = {
                'id': row[0],
                'file_name': row[1],
                'file_data': row[2],
                'classified_libelle': '',
                'indexed_libelle': ''
            }

            libelle_lower = file_info['file_name'].lower() if file_info['file_name'] else ""
            file_name_csv = file_info['file_name'].replace('.txt', '.csv') if file_info['file_name'] else ""

            # GENOVA
            if "genova" in libelle_lower:
                try:
                    with connection.cursor() as class_cursor:
                        class_cursor.execute(
                            'SELECT libelle FROM "Ferry_plot_binary_classifiedgenova" WHERE libelle = %s',
                            [file_name_csv]
                        )
                        row_class = class_cursor.fetchone()
                        file_info['classified_libelle'] = row_class[0] if row_class else "Not found"
                except Exception as e:
                    file_info['classified_libelle'] = f"Error: {e}"

                try:
                    with connection.cursor() as index_cursor:
                        index_cursor.execute(
                            "SELECT libelle FROM ferry_plot_binary_indexedgenova WHERE libelle = %s",
                            [file_name_csv]
                        )
                        row_index = index_cursor.fetchone()
                        file_info['indexed_libelle'] = row_index[0] if row_index else "Not found"
                except Exception as e:
                    file_info['indexed_libelle'] = f"Error: {e}"

                email_files_genova.append(file_info)

            # MARSEILLE
            elif "marseille" in libelle_lower:
                try:
                    with connection.cursor() as class_cursor:
                        class_cursor.execute(
                            'SELECT libelle FROM "Ferry_plot_binary_classifiedmarseille" WHERE libelle = %s',
                            [file_name_csv]
                        )
                        row_class = class_cursor.fetchone()
                        file_info['classified_libelle'] = row_class[0] if row_class else "Not found"
                except Exception as e:
                    file_info['classified_libelle'] = f"Error: {e}"

                try:
                    with connection.cursor() as index_cursor:
                        index_cursor.execute(
                            "SELECT libelle FROM ferry_plot_binary_indexedmarseille WHERE libelle = %s",
                            [file_name_csv]
                        )
                        row_index = index_cursor.fetchone()
                        file_info['indexed_libelle'] = row_index[0] if row_index else "Not found"
                except Exception as e:
                    file_info['indexed_libelle'] = f"Error: {e}"

                email_files_marseille.append(file_info)

    except Exception as e:
      print(f"Error fetching email files: {e}")
    context = {
    'queryset': qs,
    "metadata": Metadata.objects.all(),
    "Measurements": Measurements.objects.all(),
    "parameter": Parameters.objects.all(),
    "av_transects": list_available_transects,
    'is_admin': True,
    "nbr_files": nbr_files,
    "sum_size": sum_size,
    "nbr_users": nbr_users,
    "interface": True,
    "truncated_files": truncated_files,
    'email_files_genova': email_files_genova,
    'email_files_marseille': email_files_marseille
}

    return render(request, template_name, context)


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

from django.shortcuts import render
from django.core.files.base import ContentFile

from django.db import connection

from django.shortcuts import render
from django.db import connection
import os

def upload(request):
    # Total space
    qs1 = Metadata.objects.all()
    from django.db.models import Sum

    sum_size = qs1.aggregate(Sum('Size_ko'))
    sum_size = int(sum_size['Size_ko__sum'] / 1024)

    # Nbr of files 
    unique_ref_trips = Measurements.objects.values_list('Ref_trip', flat=True).distinct()
    nbr_files = len(unique_ref_trips)


    # Users
    from django.contrib.auth import get_user_model
    User = get_user_model()
    nbr_users = User.objects.count()
    if request.method == 'POST':
        myfile = request.FILES.get('myfile')

        if not myfile:
            return render(request, 'upload.html', {'error': "No file selected."})

        # Vérifie le type MIME ou l'extension
        if myfile.content_type != 'text/plain' and not myfile.name.endswith('.txt'):
            return render(request, 'upload.html', {'error': "Only .txt files are allowed."})

        try:
            # Lecture du contenu en binaire
            file_data = myfile.read()  # Ceci est déjà du type bytes

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ferry_plot_binary_email (file_name, file_data) VALUES (%s, %s)",
                    [myfile.name, file_data]
                )

            return render(request, 'upload.html', {
                'message': f"File '{myfile.name}' uploaded successfully!"
            })

        except Exception as e:
            return render(request, 'upload.html', {
                'error': f"An error occurred while saving the file: {str(e)}"
            })
    context = {
    
    'is_admin': True,
    "nbr_files": nbr_files,
    "sum_size": sum_size,
    "nbr_users": nbr_users,
    "interface": True,
   
}
    # GET request : afficher la page vide
    return render(request, 'upload.html',context)




  
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
                                qs_genova = qs1.filter(Ref_trip=116) #genova
                                qs_marseille = qs1.filter(Ref_trip=102) #marseille
                                

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
    qs_genova = qs1.filter(Ref_trip=116)
    qs_marseille = qs1.filter(Ref_trip=102)

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



from django.shortcuts import render
from .models import Metadata, Measurements, Parameters

def heat_view(request):
    template_name = "heat.html"

    # Liste des noms uniques des métadonnées (transects disponibles)
    list_of_metadata_references = list(Metadata.objects.values_list('id_meta', 'Name','Path_Reference'))
    
    # Vérifie si l'utilisateur est admin
    is_admin = request.user.groups.filter(name="admin").exists()

    # Récupération des paramètres du formulaire avec valeurs par défaut
    ref_trip = request.GET.get("transect_selection_heat")
    parameter = request.GET.get("parameter_selection_heat", "Oxygen")  # Valeur par défaut
    qc_value = request.GET.get("qc_param_heat", "1 - Good")  # Valeur par défaut

    # Initialisation du contexte
    context = {
        'is_admin': is_admin,
        'av_transects': list_of_metadata_references,
        'metadata': Metadata.objects.all(),
        'parameters': Parameters.objects.all(),
        'down': "true" if is_admin else "false",
        'acces':True,
        'selected_transect': ref_trip,  # Stocke la valeur brute
        'selected_param': parameter,
        'selected_qc': qc_value,
        'filtered_data': []
    }

    # Traitement des données si tous les paramètres requis sont présents
    if ref_trip and parameter and qc_value:
        try:
            # Convertir ref_trip en entier
            try:
                ref_trip_int = int(ref_trip)
            except ValueError:
                context["error"] = f"ID Ref_trip invalide: {ref_trip}"
                return render(request, template_name, context)

            # Extraire la valeur numérique QC
            try:
                qc_value_numeric = int(qc_value.split('-')[0].strip())
            except (ValueError, IndexError):
                context["error"] = f"Format de valeur QC invalide: {qc_value}"
                return render(request, template_name, context)

            # Création des noms de colonnes pour le paramètre et QC
            param_column = parameter
            qc_column = f"QC_{parameter}"

            # Filtrer les données en fonction du ref_trip
            filters = {
                "Ref_trip": ref_trip_int,
            }

            # Ajouter le filtre QC seulement si différent de 0 (None)
            if qc_value_numeric > 0:
                filters[qc_column] = qc_value_numeric

            # Récupérer les données
            data_query = Measurements.objects.filter(**filters).exclude(**{param_column: None}).order_by("Date")

            # Debug: afficher le nombre de résultats
            data_count = data_query.count()
            context["debug_data_count"] = data_count

            # Récupérer les couples (Latitude, Longitude, valeur du paramètre)
            filtered_data = []
            for item in data_query:
                lat = getattr(item, "Latitude", None)
                lon = getattr(item, "Longitude", None)
                value = getattr(item, param_column, None)

                if lat is not None and lon is not None and value is not None:
                    filtered_data.append([lat, lon, value])

            # Obtenir les statistiques descriptives pour le paramètre
            param_stats = {
                "min": min([item[2] for item in filtered_data]) if filtered_data else None,
                "max": max([item[2] for item in filtered_data]) if filtered_data else None,
                "parameter": parameter
            }

            # Mise à jour du contexte avec les données filtrées
            context.update({
                "filtered_data": filtered_data,
                "selected_transect": ref_trip,  # Utiliser la valeur brute, pas convertie en string
                "selected_param": parameter,
                "selected_qc": qc_value,
                "data_count": len(filtered_data),
                "debug_filtered_count": len(filtered_data),
                "param_stats": param_stats
            })

        except Exception as e:
            import traceback
            context["error"] = f"Une erreur s'est produite: {str(e)}"
            context["traceback"] = traceback.format_exc()
    else:
        if request.method == "GET" and any([ref_trip, parameter, qc_value]):
            context["error"] = "Veuillez sélectionner un transect, un paramètre et une valeur QC."

    return render(request, template_name, context)





def popup_map(request):

    qs = Measurements.objects.all()
    template_name="popup_map.html"
        # plot the two segments for point picker
    qs1=Measurements.objects.all()
    qs_genova = qs1.filter(Ref_trip=116) #genova
    qs_marseille = qs1.filter(Ref_trip=102) #marseille


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



