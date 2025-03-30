from .client import Client
import warnings
from typing import Dict, Any

__version__ = "3.6.1"
__author__ = "Ali Ganji zadeh"

class PatchedClient(Client):
    """کلاس اصلاح شده با متدهای ضروری"""
    
    def __init__(self, session: str = None, **kwargs):
        super().__init__(session, **kwargs)
        
        # تضمین وجود متدهای ضروری
        self._ensure_methods()
        
        # اتصال صحیح متدها
        self._connect_methods()
    
    def _ensure_methods(self):
        """اطمینان از وجود تمام متدهای ضروری"""
        required_methods = {
            'getChatInfo': self._get_chat_info,
            'logout': self._logout,
            'get_last_message': self.get_last_message,
            'resendMessage': self.resendMessage
        }
        
        for name, method in required_methods.items():
            if not hasattr(self, name):
                setattr(self, name, method)
    
    def _connect_methods(self):
        """اتصال متدها به شیء اصلی"""
        if not hasattr(self, 'methods'):
            self.methods = {}
        
        self.methods.update({
            'getChatInfo': self.getChatInfo,
            'logout': self.logout,
            'get_last_message': self.get_last_message,
            'resendMessage': self.resendMessage
        })
    
    def _get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """پیاده‌سازی جایگزین برای getChatInfo"""
        # اینجا باید پیاده‌سازی واقعی قرار گیرد
        return {"status": "OK", "chat_id": chat_id}
    
    async def _logout(self) -> Dict[str, Any]:
        """پیاده‌سازی جایگزین برای logout"""
        # اینجا باید پیاده‌سازی واقعی قرار گیرد
        return {"status": "OK"}

# جایگزینی کلاس اصلی
Client = PatchedClient

__all__ = ['Client']
