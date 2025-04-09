import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import Ferry_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ferry_app.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Ferry_app.routing.websocket_urlpatterns
        )
    ),
})
