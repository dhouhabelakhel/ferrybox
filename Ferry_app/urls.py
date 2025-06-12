
from django.contrib import admin
from django.urls import path, include  # add this
from django.conf.urls import url
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from Ferry_plot import views
from Ferry_plot.views import page_user_view


app_name = "Ferry_plot"


urlpatterns = [
    path('', include('Ferry_plot.urls')),
	path('index.html', views.index, name='home'),
      path('admin/', admin.site.urls),
    path('login/', include('authentication.urls')),
    path('', include('Ferry_plot.urls')),
]

# #table download part
# from Ferry_plot.views import PersonListView, PersonCreateView, PersonUpdateView


# urlpatterns += [
#     path('', PersonListView.as_view(), name='person_list'),
#     path('add/', PersonCreateView.as_view(), name='person_add'),
#     path('<int:pk>/edit/', PersonUpdateView.as_view(), name='person_edit'),
# ]



admin.site.site_header = "FerryBox administration"
admin.site.site_title = "FerryBox Admin"
admin.site.index_title = "Tunisian FerryBox database - Admin"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)









