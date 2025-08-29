from typing import Any
import httpx
from .utils.image import ZeroImage
from .utils.prompt import Dummy
from uuid import uuid4
import time
from pathlib import Path
import fake_useragent
import os
import mimetypes

class ImageClient:
    def __init__(self, http2=False, timeout=30):
        self.http2 = http2
        self.timeout = timeout
        self.auth_token = str(uuid4())

        try:
            self.UA = fake_useragent.UserAgent()
        except:
            self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        self._removebg_client = httpx.Client(http2=self.http2, timeout=self.timeout, headers={
            'user-agent': self.UA.random if not isinstance(self.UA, str) else self.UA,
            'referer': 'https://removebg.pictures/',
            'origin': 'https://removebg.pictures'
        })

    def create(self, prompt: str, nsfw: bool = False, samples: int = 1, resolution: tuple[int, int] = (512, 768), seed: int = -1, steps: int = 50,
                     negative_prompt: str = 'painting, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, deformed, ugly, blurry, bad anatomy, bad proportions, extra limbs, cloned face, skinny, glitchy, double torso, extra arms, extra hands, mangled fingers, missing lips, ugly face, distorted face, extra legs'):

        if isinstance(prompt, Dummy):
            data = prompt.get_data()
            prompt = data[0]['prompt']
            samples = data[0]['samples']
            resolution = data[0]['resolution']
            negative_prompt = data[0]['negative_prompt']
            seed = data[0]['seed']
            steps = data[0]['steps']

        with httpx.Client(http2=self.http2, timeout=self.timeout) as client:
            response = client.post(
                'https://api.arting.ai/api/cg/text-to-image/create',
                headers={'authorization': self.auth_token},
                json={
                    "prompt": prompt,
                    "model_id": "fuwafuwamix_v15BakedVae",
                    "is_nsfw": nsfw,
                    "samples": int(samples),
                    "height": int(resolution[1]),
                    "width": int(resolution[0]),
                    "negative_prompt": negative_prompt,
                    "seed": seed,
                    "lora_ids": "",
                    "lora_weight": "0.7",
                    "sampler": "DPM2",
                    "steps": int(steps),
                    "guidance": 7,
                    "clip_skip": 2
                },
            )
            response.raise_for_status()
            return response.json()

    def get(self, request_id: Any, trying: int = 10):
        for _ in range(trying):
            time.sleep(3)
            with httpx.Client(http2=self.http2, timeout=self.timeout) as client:
                response = client.post(
                    'https://api.arting.ai/api/cg/text-to-image/get',
                    headers={'authorization': self.auth_token},
                    json={'request_id': request_id})
                response.raise_for_status()
                if response.json()['code'] == 100000 and response.json()['data']['output']:
                    return ZeroImage(response.json()['data']['output'])
        else:
            raise TimeoutError("Processing did not finish, try again later!")

    def enhance(self, image: str, scale: int = 2):
        self.auth_token = str(uuid4())
        signed_urls = self.__get_signed_urls(image)
        __urls = {
            'put': signed_urls['data']['oss_signed_urls'][0]['put'],
            'get': signed_urls['data']['oss_signed_urls'][0]['get']
        }

        self.__upload_image_to_server(image, __urls)
        task_id = self.__create_task('api/image/image-enhance/create-task', __urls, scale)['data']['task_id']

        task = self.__get_task_result('api/image/image-enhance/get-task-result', task_id)

        return ZeroImage([task['data']['task_result']['file_oss_path']])

    def remove_watermark(self, image_path: str, image_name: str = "result.jpg"):
        dir_name = os.path.dirname(image_name)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(image_path, "rb") as src:
            mime_type = mimetypes.guess_type(image_path)[0]
            files = {
                "original_image_file": (os.path.basename(image_path), src, mime_type if mime_type else 'application/octet-stream')
            }
            resp = httpx.post(
                "https://api.unwatermark.ai/api/magiceraser/v2/ai-image-watermark-remove-auto/create-job",
                files=files,
                timeout=self.timeout,
                headers={
                    "product-code": "067003",
                    "product-serial": str(uuid4().hex),
                    "user-agent": self.UA.random if not isinstance(self.UA, str) else self.UA
                },
            )
            resp.raise_for_status()

            if resp.json()["code"] != 100000:
                raise RuntimeError(resp.json()["message"]["en"] if resp.json()['message'].get('en') else resp.json()['message'])

            image_url = resp.json()["result"]["output_image_url"]

        resp_img = httpx.get(image_url, timeout=self.timeout)
        resp_img.raise_for_status()

        with open(image_name, "wb") as dst:
            dst.write(resp_img.content)

        return image_name

    def remove_background(self, image_path: str, processor: str = "fast", image_name: str = "./__zerogpt__/result.jpg"):
        # Validate file existence
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File {image_path} not found")

        dir_name = os.path.dirname(image_name)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # Validate size (<= 10 MB)
        size_bytes = os.path.getsize(image_path)
        size_mb = size_bytes / 1048576
        if size_mb > 10:
            raise ValueError("File size exceeds 10 MB")

        # Validate type
        allowed_types = ['image/png', 'image/jpeg']
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type not in allowed_types:
            raise ValueError("Supported file types: PNG, JPG")

        # Helpers
        def _format_size(v: float) -> str:
            if v == 0:
                return "0-1MB"
            elif v <= 1:
                return "0-1MB"
            elif v <= 2:
                return "1-2MB"
            elif v <= 4:
                return "2-4MB"
            elif v <= 7:
                return "4-7MB"
            elif v <= 10:
                return "7-10MB"
            else:
                return "0MB"

        file_id = str(uuid4())
        original_size = _format_size(size_mb)

        # Prepare removebg session
        self.__renew_session()

        # Upload image
        self.__upload_image_to_removebg(image_path, mime_type, file_id)

        # Send metadata
        metadata = {
            "id": file_id,
            "name": os.path.basename(image_path),
            "originalSize": original_size,
            "processor": processor,
            "timestamp": int(time.time() * 1000)
        }
        self.__upload_metadata_to_removebg(metadata)

        # Initial delay then poll and download
        time.sleep(5)
        return self.__images(file_id, image_name)

    """
        Функции ниже используются для работы с API arting.ai
    """
    def __get_signed_urls(self, image_path: str):
        with httpx.Client(http2=self.http2, timeout=self.timeout) as client:
            response = client.post(
                'https://api.arting.ai/api/cg/get_oss_signed_urls',
                headers={'authorization': self.auth_token, 'user-agent': self.UA.random if not isinstance(self.UA, str) else self.UA},
                json={'f_suffixs': [Path(image_path).suffix.split('.')[-1]]})
            response.raise_for_status()
            return response.json()

    def __upload_image_to_server(self, image_path: str, urls: dict):
        with httpx.Client(http2=self.http2, timeout=self.timeout) as client:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            response = client.put(
                urls['put'],
                headers={'user-agent': self.UA.random if not isinstance(self.UA, str) else self.UA},
                data=image_data)

            response.raise_for_status()
            return True

    def __create_task(self, path, urls, scale=2):
        with httpx.Client(http2=self.http2, timeout=self.timeout) as client:
            response = client.post(
                'https://api.arting.ai/' + path,
                headers={'authorization': self.auth_token, 'user-agent': self.UA.random if not isinstance(self.UA, str) else self.UA},
                json={
                    'image_url': urls['get'],
                    'scale': scale,
                    'version': 'v1.4' 
                })
            response.raise_for_status()
            return response.json()

    def __get_task_result(self, path, task_id, trying=10):
        for _ in range(trying):
            time.sleep(3)
            with httpx.Client(http2=self.http2, timeout=self.timeout) as client:
                response = client.get(
                    'https://api.arting.ai/' + path,
                    headers={'authorization': self.auth_token, 'user-agent': self.UA.random if not isinstance(self.UA, str) else self.UA},
                    params={'task_id': task_id})
                response.raise_for_status()
                if response.json()['code'] == 100000 and response.json()['data']['status'] == 1:
                    return response.json()
        else:
            raise TimeoutError("Processing did not finish, try again later!")

    """
        Функции ниже используются для работы с API removebg.pictures
    """
    def __renew_session(self):
        self._removebg_client.cookies.clear()
        resp = self._removebg_client.get("https://removebg.pictures/")
        resp.raise_for_status()

    def __upload_image_to_removebg(self, path, mime_type, file_id):
        with open(path, "rb") as f:
            files = {"file": (os.path.basename(path), f, mime_type)}
            resp = self._removebg_client.post(
                "https://removebg.pictures/api/upload",
                data={"id": file_id},
                files=files
            )
            resp.raise_for_status()
            return True

    def __upload_metadata_to_removebg(self, metadata):
        resp = self._removebg_client.post(
            "https://removebg.pictures/api/images",
            json=metadata
        )
        resp.raise_for_status()
        return True

    def __images(self, file_id, image_name):
        max_attempts = 60
        for attempt in range(max_attempts):
            time.sleep(5)
            resp = self._removebg_client.get(f"https://removebg.pictures/api/images/{file_id}")
            resp.raise_for_status()
            data = resp.json()

            if data.get("erased"):
                image_resp = self._removebg_client.get(
                    f"https://removebg.pictures/api/images/{file_id}/download-processed?p=y"
                )
                image_resp.raise_for_status()
                with open(image_name, "wb") as f:
                    f.write(image_resp.content)
                return image_name
            elif "error" in data:
                raise RuntimeError(f"Error in status: {data['error']}")

        raise TimeoutError("Processing did not finish within 5 minutes")