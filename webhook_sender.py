"""
Модуль для отправки webhook уведомлений
"""
import aiohttp
import json
import logging
from datetime import datetime
from config import WEBHOOK_URL

logger = logging.getLogger(__name__)

class WebhookSender:
    """Класс для отправки webhook уведомлений"""
    
    @staticmethod
    async def send_invoice_webhook(invoice_data, result, user_info):
        """Отправка webhook для создания инвойса"""
        webhook_data = {
            "event_type": "invoice_created",
            "timestamp": datetime.now().isoformat(),
            "user_info": {
                "user_id": user_info.get("user_id"),
                "username": user_info.get("username"),
                "shop_id": user_info.get("shop_id")
            },
            "invoice_data": invoice_data,
            "api_result": result,
            "status": "success" if result.get('Success') else "error"
        }
        
        return await WebhookSender._send_webhook(webhook_data)
    
    @staticmethod
    async def send_payout_webhook(payout_data, result, user_info):
        """Отправка webhook для создания выплаты"""
        webhook_data = {
            "event_type": "payout_created",
            "timestamp": datetime.now().isoformat(),
            "user_info": {
                "user_id": user_info.get("user_id"),
                "username": user_info.get("username"),
                "shop_id": user_info.get("shop_id")
            },
            "payout_data": payout_data,
            "api_result": result,
            "status": "success" if result.get('Success') else "error"
        }
        
        return await WebhookSender._send_webhook(webhook_data)
    
    @staticmethod
    async def send_user_action_webhook(action_type, user_info, additional_data=None):
        """Отправка webhook для действий пользователя"""
        webhook_data = {
            "event_type": f"user_{action_type}",
            "timestamp": datetime.now().isoformat(),
            "user_info": {
                "user_id": user_info.get("user_id"),
                "username": user_info.get("username"),
                "shop_id": user_info.get("shop_id")
            },
            "action_data": additional_data or {}
        }
        
        return await WebhookSender._send_webhook(webhook_data)
    
    @staticmethod
    async def _send_webhook(data):
        """Отправка webhook данных"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    WEBHOOK_URL,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook отправлен успешно: {data.get('event_type')}")
                        return True
                    else:
                        logger.warning(f"Webhook вернул статус {response.status}: {data.get('event_type')}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка отправки webhook: {e}")
            return False
