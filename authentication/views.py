# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth import logout
from django.http import JsonResponse
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

User = get_user_model()

def login_view(request):
    logger.info("Tentative de connexion via JWT")
    token = request.GET.get("token")
    msg = None

    if token:
        try:
            # Décodage du token JWT
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"],options={"verify_exp": False})
            print(f"Token décodé avec succès: {payload}")
            
            username = payload.get("sub")
            full_name = payload.get("name", "Utilisateur")
            roles = payload.get("role", "")
            
            # Vérification que le username existe
            if not username:
                msg = "Token invalide : 'sub' manquant"
                logger.warning("Token sans username (sub)")
                return redirect("home")

            # Création ou récupération de l'utilisateur
            user, created = User.objects.get_or_create(username=username)
            
            if created:
                user.set_unusable_password()
                logger.info(f"Nouvel utilisateur créé: {username}")
            else:
                logger.info(f"Utilisateur existant: {username}")
            
            # Mise à jour des informations utilisateur
            user.first_name = full_name
            
            # Gestion des rôles
            if "ROLE_ADMIN" in roles:
                user.is_staff = True
                user.is_superuser = True  # Changé pour donner tous les droits admin
                logger.info(f"Droits admin accordés à {username}")
            else:
                user.is_staff = False
                user.is_superuser = False
                logger.info(f"Droits utilisateur standard pour {username}")

            user.save()

            # Connexion de l'utilisateur
            login(request, user)
            print("kbduiiiiiiiiiiiiiiiiiiiiii")
            print(f"Connexion réussie pour {username}")
            logger.info(f"Session après login : {dict(request.session)}")
            logger.info(f"Session key : {request.session.session_key}")
            logger.info(f"Connexion réussie pour {username}")
            
            return redirect("home")  # Assurez-vous que cette URL existe

        except jwt.ExpiredSignatureError:
            msg = "Token expiré"
            logger.warning("Tentative de connexion avec un token expiré")
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Erreur JWT: {str(e)}")
            msg = f"Token invalide : {str(e)}"
            
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la connexion: {str(e)}")
            msg = f"Erreur de connexion : {str(e)}"

    else:
        msg = "Aucun token fourni"
        logger.warning("Tentative de connexion sans token")

    return redirect("home")
def logout_view(request):
    print("=== DEBUT FONCTION LOGOUT ===")  # Pour être sûr qu'on entre dans la fonction
    logger.info("=== DEBUG LOGOUT ===")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request cookies: {request.COOKIES}")
    logger.info(f"Session key from request: {request.session.session_key}")
    
    user = request.user
    logger.info(f"Déconnexion de l'utilisateur : {user} (authentifié: {user.is_authenticated})")
    logger.info(f"Contenu de la session avant logout : {dict(request.session)}")

    if request.user.is_authenticated:
        logout(request)
        request.session.flush() 
        logger.info("Logout effectué")
    else:
        logger.warning("Utilisateur déjà déconnecté ou session invalide")

    print("=== AVANT RETURN ===")
    
    # Retourner JsonResponse au lieu de redirect pour les requêtes AJAX
    response = JsonResponse({"message": "Logout successful"})
    response.delete_cookie('sessionid', path='/')
    response.delete_cookie('csrftoken', path='/')
    
    print("=== APRES CREATION RESPONSE ===")
    return response

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg     = 'User created.'
            success = True
            
            #return redirect("/login/")

        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })
