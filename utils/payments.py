"""Обработка платежей через CryptoBot и ЮKassa"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict
from config import (
    CRYPTOBOT_TOKEN, CRYPTOBOT_API_URL,
    YOO_KASSA_SHOP_ID, YOO_KASSA_SECRET_KEY
)

logger = logging.getLogger(__name__)


class CryptoBotAPI:
    """API для CryptoBot"""
    
    def __init__(self, token: str):
        self.token = token
        self.api_url = CRYPTOBOT_API_URL
        
    async def create_invoice(
        self,
        amount: float,
        currency_type: str = "fiat",
        fiat: str = "RUB",
        description: str = ""
    ) -> Optional[Dict]:
        """Создание счета в CryptoBot"""
        headers = {
            "Crypto-Pay-API-Token": self.token,
            "Content-Type": "application/json"
        }
        
        data = {
            "amount": str(amount),
            "currency_type": currency_type,
            "fiat": fiat,
            "description": description
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/createInvoice",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        logger.info(f"✅ Счет создан: {result['result']['invoice_id']}")
                        return result["result"]
                    else:
                        logger.error(f"❌ Ошибка создания счета: {result}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка API CryptoBot: {e}")
            return None
    
    async def get_invoice(self, invoice_id: int) -> Optional[Dict]:
        """Получение информации о счете"""
        headers = {"Crypto-Pay-API-Token": self.token}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/getInvoices",
                    headers=headers,
                    params={"invoice_ids": str(invoice_id)}
                ) as response:
                    result = await response.json()
                    
                    if result.get("ok") and result["result"]["items"]:
                        return result["result"]["items"][0]
                    return None
        except Exception as e:
            logger.error(f"❌ Ошибка проверки счета: {e}")
            return None


class YooKassaAPI:
    """API для ЮKassa"""
    
    def __init__(self, shop_id: str, secret_key: str):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.api_url = "https://api.yookassa.ru/v3"
        
    async def create_payment(
        self,
        amount: float,
        description: str,
        return_url: str = "https://t.me/bot"
    ) -> Optional[Dict]:
        """Создание платежа в ЮKassa"""
        import uuid
        
        headers = {
            "Content-Type": "application/json",
            "Idempotence-Key": str(uuid.uuid4())
        }
        
        data = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description
        }
        
        auth = aiohttp.BasicAuth(self.shop_id, self.secret_key)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/payments",
                    headers=headers,
                    json=data,
                    auth=auth
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("status") == "pending":
                        logger.info(f"✅ Платеж создан: {result['id']}")
                        return result
                    else:
                        logger.error(f"❌ Ошибка создания платежа: {result}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка API ЮKassa: {e}")
            return None
    
    async def check_payment(self, payment_id: str) -> Optional[Dict]:
        """Проверка статуса платежа"""
        auth = aiohttp.BasicAuth(self.shop_id, self.secret_key)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/payments/{payment_id}",
                    auth=auth
                ) as response:
                    result = await response.json()
                    return result
        except Exception as e:
            logger.error(f"❌ Ошибка проверки платежа: {e}")
            return None


# Создание экземпляров API
crypto_bot = CryptoBotAPI(CRYPTOBOT_TOKEN) if CRYPTOBOT_TOKEN else None
yoo_kassa = YooKassaAPI(YOO_KASSA_SHOP_ID, YOO_KASSA_SECRET_KEY) if YOO_KASSA_SHOP_ID and YOO_KASSA_SECRET_KEY else None
