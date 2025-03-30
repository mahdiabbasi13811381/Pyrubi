from .client import Client
import warnings

__version__ = "3.6.1"
__author__ = "Ali Ganji zadeh"

class PatchedClient(Client):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not hasattr(self, 'methods'):
            self.methods = {
                'get_last_message': self.get_last_message,
                'resendMessage': self.resendMessage,
                'forward_messages': self.forward_messages,
                'get_messages': self.get_messages,
                'logout': self.logout
            }
        
        warnings.warn(
            "Using patched version of Pyrubi Client. "
            "Some features may not work as expected.",
            RuntimeWarning
        )

Client = PatchedClient

__all__ = ['Client']
