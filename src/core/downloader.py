import requests
from typing import Optional
import os
import time
import random
from urllib.parse import urlparse

from src.config.settings import SCRAPER_CONFIG

class ImageDownloader:
    @staticmethod
    def download_image(img_url: str, save_dir: str, filename: Optional[str] = None) -> Optional[str]:
        """下载图片到指定目录"""
        try:
            if not filename:
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"image_{int(time.time())}_{random.randint(1000, 9999)}.jpg"

            save_path = os.path.join(save_dir, filename)

            response = requests.get(img_url, timeout=10, headers={
                'User-Agent': SCRAPER_CONFIG.user_agent
            })

            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                print(f"图片下载成功: {save_path}")
                return save_path
            else:
                print(f"图片下载失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"图片下载错误: {e}")
            return None
