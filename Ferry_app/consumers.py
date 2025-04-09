from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

# Get a Django logger
logger = logging.getLogger('django')

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("✅ WebSocket connecté : %s", self.channel_name)
        await self.channel_layer.group_add("notifications", self.channel_name)
        logger.info("✅ Client ajouté au groupe 'notifications' : %s", self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        logger.info("❌ WebSocket déconnecté : %s", self.channel_name)
        await self.channel_layer.group_discard("notifications", self.channel_name)
    
    async def receive(self, text_data):
        logger.info("✅ Nouvelle notification reçue : %s", text_data)
        # Traitement facultatif ici
    
    async def send_notification(self, event):
     try:
        message = event["message"]
        logger.info("📨 Notification envoyée au client : %s", message)
        await self.send(text_data=json.dumps({"message": message}))
     except Exception as e:
        logger.error("❌ Erreur lors de l'envoi de la notification: %s", str(e))