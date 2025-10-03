"""
API клиент для работы с Konvert2pay
"""
import aiohttp
import logging
from config import INVOICE_CREATE_URL, WITHDRAWAL_CREATE_URL
from webhook_sender import WebhookSender

logger = logging.getLogger(__name__)

class Konvert2payAPI:
    """Клиент для работы с API Konvert2pay"""
    
    @staticmethod
    async def create_invoice(shop_id, shop_api_key, order_id, client_id, amount, user_info=None):
        """Создание инвойса через API Konvert2pay"""
        data = {
            "shop_id": shop_id,
            "method": "oneclickpay",
            "order_id": order_id,
            "client_id": client_id,
            "amount": amount
        }
        
        headers = {
            "Authorization": shop_api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(INVOICE_CREATE_URL, data=data, headers=headers) as response:
                    result = await response.json()
                    
                    # Отправляем webhook
                    if user_info:
                        await WebhookSender.send_invoice_webhook(data, result, user_info)
                    
                    return result
        except Exception as e:
            logger.error(f"Ошибка API запроса инвойса: {e}")
            error_result = {"Success": False, "Error": {"Code": 500, "Message": str(e)}}
            
            # Отправляем webhook с ошибкой
            if user_info:
                await WebhookSender.send_invoice_webhook(data, error_result, user_info)
            
            return error_result

    @staticmethod
    async def create_payout(shop_id, shop_api_key, order_id, client_id, iban_account, iban_inn, 
                          cardholder_surname, cardholder_name, cardholder_middlename, 
                          iban_purpose, amount, user_info=None):
        """Создание выплаты через API Konvert2pay"""
        data = {
            "shop_id": shop_id,
            "order_id": f"{order_id} {client_id}",  # Для выплат order_id = ID заявки + ID клиента
            "ibanAccount": iban_account,
            "ibanInn": iban_inn,
            "cardholderSurname": cardholder_surname,
            "cardholderName": cardholder_name,
            "cardholderMiddlename": cardholder_middlename,
            "ibanPurpose": iban_purpose,
            "amount": amount
        }
        
        headers = {
            "Authorization": shop_api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(WITHDRAWAL_CREATE_URL, data=data, headers=headers) as response:
                    result = await response.json()
                    
                    # Отправляем webhook
                    if user_info:
                        await WebhookSender.send_payout_webhook(data, result, user_info)
                    
                    return result
        except Exception as e:
            logger.error(f"Ошибка API запроса выплаты: {e}")
            error_result = {"Success": False, "Error": {"Code": 500, "Message": str(e)}}
            
            # Отправляем webhook с ошибкой
            if user_info:
                await WebhookSender.send_payout_webhook(data, error_result, user_info)
            
            return error_result
