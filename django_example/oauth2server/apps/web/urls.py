from django.conf.urls import url

from apps.web.views import AuthorizeView

app_name='apps'
urlpatterns = [
    url('^authorize/?', AuthorizeView.as_view(), name='authorize'),
]