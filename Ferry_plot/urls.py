from django.urls import path, re_path
# from Ferry_plot import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView
from Ferry_plot import views
 
try:
    from Ferry_plot.views import importExcel, transect_plotting, data_description, popup_map, mails, import_mails
except ImportError:
    from Ferry_plot.views import importExcel, transect_plotting, data_description, popup_map
    print("⚠️ ImportError ignoré : mails et import_mails non trouvés")

app_name = "Ferry_plot"
# from django.urls import include

urlpatterns = [

    #the most important one
    path('', transect_plotting, name='try'),

    # filters : this is the main filter
    
    # path('page-user.html', views.page_user_view, name='dataredirect'),
    # these are supporting the main filter functioning
    # path('data_access.html', views.data_access,  name='data_access'),
    path('map', views.map_view, name='map'),
    path('notifications', views.notifications_view, name='notifications'),
    path('api/notifications/', views.get_latest_notifications, name='get_latest_notifications'),

    path('time_series/', views.time_series, name='time_series'),
    path('scatter', views.scatter_view, name='scatter'),
    path('heat', views.heat_view, name='heat'),
    path('update_request/<int:id>/', views.update_request, name='update_request'),

    # path('succes.html', succes_view, name='succes'),  # Ajoutez une vue pour le succès
    #path('importExcel/', importExcel, name='importExcel'),  # Ajoutez une vue pour le succès
    #path('mails/', mails, name='mails'),
    #path('import_mails/<int:id_meta>/', import_mails, name='import_mails'),
    path('process',views.terminal_view),
    #these are the general pages

    path('data.html', views.data, name='data3'),   
    path('download_truncated_file/<str:libelle>/', views.download_truncated_file, name='download_truncated_file'),
    path('download_indexed_file/<str:indexed_libelle>/', views.download_indexed_file, name='download_indexed_file'),
    path('download_classified_file/<str:classified_libelle>/', views.download_classified_file, name='download_classified_file'),
    path('download_intial_file/<str:file_name>/', views.download_initial_file, name='download_initial_file'),



        #these are replacing pages funtion
    path('transect_plotting', views.transect_plotting, name='transect_plotting'),
    path('page-user', views.page_user_view, name='data'),
    # path('', page_user_view, name='datatest'),
 

 
    # path('', RedirectView.as_view(url='/index/', permanent=True)),

] 

urlpatterns += [

    # The home page
    # path('', views.index, name='home'),
    path('index.html', views.index, name='home'),

    #the upload part
    path('popup_map.html', views.popup_map, name='up'),
    path('upload.html', views.upload, name='up'),
    path('download.html', views.download, name='down'),
    path('ui-notifications.html', views.ui_notifications_view, name='data2'),
    path('data_description.html', views.data_description, name='description'),
    #path('import_data.html', views.importer_data, name='import_data'),

]


