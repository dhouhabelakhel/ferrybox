

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
from Ferry_plot.views import transect_plotting, data_description, popup_map

app_name = "Ferry_plot"
# from django.urls import include

urlpatterns = [

    #the most important one
    path('', transect_plotting, name=''),

    # filters : this is the main filter
    
    #path('page-user.html', views.page_user_view, name='dataredirect'),
    # these are supporting the main filter functioning
    # path('data_access.html', views.data_access,  name='data_access'),
    path('map', views.map_view, name='map'),
    path('time_series', views.time_series, name='time_series'),
    path('scatter', views.scatter_view, name='scatter'),
    # path('heat.html', views.heat_view, name='heat'),

    #these are the general pages

    path('data', views.data, name='data3'),    
        #these are replacing pages funtion
    path('transect_plotting', views.transect_plotting, name='transect_plotting'),
    path('page-user', views.page_user_view, name='data'),
    # path('', page_user_view, name='datatest'),


 
    # path('', RedirectView.as_view(url='/index/', permanent=True)),

] 

urlpatterns += [

    # The home page
    # path('', views.index, name='home'),
    # path('index.html', views.index, name='home'),

    #the upload part
    path('popup_map.html', views.popup_map, name='up'),
    path('upload.html', views.upload, name='up'),
    path('download.html', views.download, name='down'),
    path('ui-notifications.html', views.ui_notifications_view, name='data2'),
    path('data_description.html', views.data_description, name='description'),

]


