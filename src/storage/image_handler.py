import os
from typing import List, Optional
from src.core.utils import extract_date_from_url, create_directory
from src.core.downloader import ImageDownloader
from src.config.settings import STORAGE_CONFIG

class ImageHandler:
    def __init__(self, article_url: str):
        self.article_url = article_url
        self.image_dir = self._create_image_directory()
        self.image_counter = 1
        
    def _create_image_directory(self) -> str:
        """创建图片保存目录"""
        date_str = extract_date_from_url(self.article_url)
        article_dir = os.path.join(STORAGE_CONFIG.base_image_dir, date_str)
        return create_directory(article_dir)
    
    def download_images(self, image_urls: List[str], title: str) -> List[dict]:
        """下载所有图片"""
        downloaded_images = []
        safe_title = re.sub(r'[\\/*?:"<>|]', '', title)[:50] if title else "unknown"
        
        for img_url in image_urls:
            filename = f"{safe_title}_{self.image_counter:03d}.jpg"
            local_path = ImageDownloader.download_image(img_url, self.image_dir, filename)
            
            if local_path:
                downloaded_images.append({
                    'original_url': img_url,
                    'local_path': local_path,
                    'filename': filename
                })
                self.image_counter += 1
                
        return downloaded_images
