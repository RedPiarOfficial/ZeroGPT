from abc import ABC, abstractmethod
from typing import Dict, Any
from .utils import CLIENT_TYPES, generate_headers, serialize_json_consistently, get_origin_token_captcha, get_writing_headers, generate_image_headers
from uuid import uuid4

class GPTTransport(ABC):
    def __init__(self, client_type: int | str):
        if isinstance(client_type, int):
            self.client_type = CLIENT_TYPES.get(client_type)
            if self.client_type is None:
                raise ValueError(f"Invalid client type id: {client_type}")
        elif isinstance(client_type, str):
            client_type = client_type.lower()
            if client_type.lower() not in CLIENT_TYPES.values():
                raise ValueError(f"Invalid client type name: {client_type}")
            self.client_type = client_type
        else:
            raise ValueError(f"Invalid client type: {client_type}")

    def get_req_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерирует корректные данные для каждого запроса
        Возвращает payload, headers и url для корректного запроса.
        """
        if self.client_type in ['client', 0]:
            headers = generate_headers(payload)
            payload_json = serialize_json_consistently(payload)
            return {
                'payload': payload_json,
                'headers': headers,
                'url': 'https://goldfish-app-fojmb.ondigitalocean.app//api/chat'
            }

        elif self.client_type in ['writing', 1]:
            context = ''.join(f"{msg['role'].lower().replace('assistant', 'ai')}: {msg['content']}\n" for msg in payload['messages'])
            session_id = str(uuid4())
            return {
                'payload': {
                    'text': context,
                    'capcha': get_origin_token_captcha(session_id),
                    'model': payload['model'],
                    'session_id': session_id
                },
                'headers': get_writing_headers(),
                'url': 'https://data.toolbaz.com/writing.php'
            }
    
    @abstractmethod
    def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass