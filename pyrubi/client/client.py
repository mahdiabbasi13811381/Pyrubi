# -*- coding: utf-8 -*-
# فایل: pyrubi/client/client.py
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Union, Any
from functools import wraps
import warnings

logger = logging.getLogger(__name__)

class Client:
    """کلاس اصلی با حفظ 100% سازگاری با نسخه قبلی"""
    
    def __init__(self, session: str = None, **kwargs):
        """
        مقداردهی اولیه با پارامترهای مشابه نسخه قبلی
        
        :param session: نام سشن (اختیاری)
        :param kwargs: سایر پارامترهای اختیاری
        """
        self.session = session
        self._session = None
        self._auth_token = None
        self._is_connected = False
        
        # حفظ متغیرهای مورد استفاده در نسخه قبلی
        self.methods = {
            'getInfo': self.getInfo,
            'getMessages': self.getMessages,
            'sendMessage': self.sendMessage,
            'forwardMessages': self.forwardMessages,
            'logout': self.logout
        }
        
        # راه‌اندازی اتصال
        self._setup_connection()

    def _setup_connection(self):
        """تنظیمات اولیه اتصال"""
        self._session = aiohttp.ClientSession()
            timeout=aiohttp.ClientTimeout(total=30)
        self._is_connected = True

    # ==================== متدهای قدیمی با پیاده‌سازی جدید ====================
    
    async def getInfo(self, object_guid: str) -> Dict[str, Any]:
        """متد قدیمی با پیاده‌سازی جدید"""
        try:
            response = await self._make_request(
                "GET", 
                f"v1/chats/{object_guid}/info"
            )
            return {'status': 'OK', 'data': response}
        except Exception as e:
            logger.error(f"Error in getInfo: {str(e)}")
            return {'status': 'ERROR', 'message': str(e)}

    async def getMessages(self, object_guid: str, count: int = 10) -> Dict[str, Any]:
        """متد قدیمی با پیاده‌سازی جدید"""
        try:
            messages = await self._get_messages_v2(object_guid, count)
            return {
                'status': 'OK',
                'messages': messages,
                'count': len(messages)
            }
        except Exception as e:
            logger.error(f"Error in getMessages: {str(e)}")
            return {'status': 'ERROR'}

    async def sendMessage(self, object_guid: str, text: str, **kwargs) -> Dict[str, Any]:
        """متد قدیمی با پیاده‌سازی جدید"""
        try:
            message_id = await self._send_message_v2(object_guid, text)
            return {
                'status': 'OK',
                'message_id': message_id
            }
        except Exception as e:
            logger.error(f"Error in sendMessage: {str(e)}")
            return {'status': 'ERROR'}

    async def forwardMessages(self, from_guid: str, message_ids: List[str], to_guid: str) -> Dict[str, Any]:
        """متد قدیمی با پیاده‌سازی جدید"""
        try:
            results = await asyncio.gather(
                *[self._forward_message_v2(from_guid, msg_id, to_guid) for msg_id in message_ids]
            )
            return {
                'status': 'OK',
                'results': results
            }
        except Exception as e:
            logger.error(f"Error in forwardMessages: {str(e)}")
            return {'status': 'ERROR'}

    async def logout(self) -> Dict[str, Any]:
        """متد قدیمی با پیاده‌سازی جدید"""
        try:
            await self._session.close()
            self._is_connected = False
            return {'status': 'OK'}
        except Exception as e:
            logger.error(f"Error in logout: {str(e)}")
            return {'status': 'ERROR'}

    # ==================== متدهای جدید با معماری بهبودیافته ====================
    
    async def _get_messages_v2(self, chat_id: str, count: int) -> List[Dict]:
        """نسخه جدید دریافت پیام‌ها"""
        response = await self._make_request(
            "GET",
            f"v2/chats/{chat_id}/messages",
            params={'count': count}
        )
        return response.get('messages', [])

    async def _send_message_v2(self, chat_id: str, text: str) -> str:
        """نسخه جدید ارسال پیام"""
        response = await self._make_request(
            "POST",
            f"v2/chats/{chat_id}/messages",
            json={'text': text}
        )
        return response['message_id']

    async def _forward_message_v2(self, from_chat: str, message_id: str, to_chat: str) -> Dict:
        """نسخه جدید ارسال مجدد"""
        response = await self._make_request(
            "POST",
            f"v2/chats/{from_chat}/messages/{message_id}/forward",
            json={'target_chat_id': to_chat}
        )
        return response

    # ==================== متدهای کمکی ====================
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """مدیریت درخواست‌های HTTP"""
        if not self._is_connected:
            raise ConnectionError("اتصال برقرار نشده است")
            
        try:
            async with self._session.request(
                method,
                f"{self.BASE_URL}/{endpoint}",
                **kwargs
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    def __del__(self):
        if self._is_connected:
            asyncio.create_task(self.logout())
