import hmac
import hashlib
import time
import json
import httpx
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from uuid import uuid4
import fake_useragent

from typing import Dict, Any
import random
import string
import base64

CLIENT_TYPES = {
    0: "client",
    1: "writing",
}

def get_server_time(url="https://goldfish-app-fojmb.ondigitalocean.app"):
    try:
        start_time = time.time()
        response = httpx.get(url, timeout=10)
        end_time = time.time()
        
        server_date = response.headers.get("Date")
        if server_date:
            dt = parsedate_to_datetime(server_date)
            server_timestamp = int(dt.timestamp())

            network_delay = max(0, end_time - start_time)
            buffer_seconds = 2  
            adjusted_timestamp = server_timestamp + int(network_delay) + buffer_seconds
            
            return adjusted_timestamp
            
    except Exception as e:
        """Error"""
        raise Exception(e)
    
    return int(time.time()) + 2

def serialize_json_consistently(data):
    return json.dumps(data, ensure_ascii=True, separators=(',', ':'))

def generate_headers(data):
    secret_key = "your-super-secret-key-replace-in-production"
    timestamp = str(get_server_time())
    data_json = serialize_json_consistently(data)

    message = timestamp + data_json
    key_bytes = secret_key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha256)
    signature = hmac_obj.hexdigest()

    headers = {
        "X-API-Key": "62852b00cb9e44bca86f0ec7e7455dc6",
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Accept-Encoding": "gzip, deflate",
        "Content-Encoding": "gzip",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.aiuncensored.info",
        "Referer": "https://www.aiuncensored.info/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36",
    }

    return headers


def generate_image_headers():
    return {
        'accept': 'application/json',
        'content-type': 'application/json',
        'authorization': str(uuid4()),
        'origin': 'https://arting.ai',
        'referer': 'https://arting.ai/',
        'user-agent': fake_useragent.UserAgent().random
    }

"""

WritingClient Sections

"""
def get_writing_headers():
    return {
                "User-Agent": fake_useragent.UserAgent().random,
                "Referer": "https://toolbaz.com/",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Content-Encoding": "gzip",
            }

def get_origin_token_captcha(session_id):
        request_data = get_request_data(session_id)

        response = httpx.post(
            "https://data.toolbaz.com/token.php",
            data=request_data,
            headers=get_writing_headers()
        )

        if 'token' in response.json():
            return response.json()['token']
        else:
            raise Exception('[Fatal Error] Error fetching Captcha token')

def generate_random_string(length: int = 42) -> str:
        """Генерирует случайную строку из букв и цифр (как в примере)"""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(chars) for _ in range(length))
    
def encode_data(data: Dict) -> str:
        """Кодирует данные в base64 (аналог gH7wN функции)"""
        json_str = json.dumps(data, separators=(',', ':'))
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
        return encoded
    
    
def generate_token(tdf_value: str = "-4") -> str:
        token_data = {
            "bR6wF": {
                        "nV5kP": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                        "lQ9jX": "ru-RU", 
                        "sD2zR": "1536x864",
                        "tY4hL": "Europe/Kiev", 
                        "pL8mC": "Win32",
                        "cQ3vD": 24,
                        "hK7jN": 12
                    },
            "uT4bX": {
                        "mM9wZ": [],  # Пустой массив движений мыши
                        "kP8jY": []   # Пустой массив нажатий клавиш
                    },
            "tuTcS": int(time.time()),
            "tDfxy": tdf_value,
            "RtyJt": ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for _ in range(36))
        }

        encoded_data = encode_data(token_data)
        final_token = generate_random_string(6) + encoded_data
        
        return final_token
    
def get_request_data(session_id) -> Dict[str, str]:
        return {
            "session_id": session_id,
            "token": generate_token()
        }