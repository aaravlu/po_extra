from playwright.sync_api import Page
from typing import Tuple, Optional, List
import time
import random
from bs4 import BeautifulSoup

from src.core.browser import BrowserManager
from src.core.utils import extract_text_content, wait_for_content
from src.storage.image_handler import ImageHandler
from src.models.article import Article, ImageInfo
from src.config.settings import SCRAPER_CONFIG

class WeChatScraper:
    def __init__(self):
        self.content_selectors = [
            '.rich_media_content',
            '#js_content',
            '.weui-article',
            'article',
            '[class*="content"]'
        ]
    
    def scrape_article(self, url: str) -> Optional[Article]:
        """爬取微信公众号文章"""
        with BrowserManager() as browser_manager:
            page = browser_manager.create_page()
            
            try:
                # 导航到页面
                if not browser_manager.navigate_with_retry(page, url):
                    return None
                
                # 等待内容加载
                if not wait_for_content(page, self.content_selectors):
                    print("内容加载超时，继续尝试提取...")
                
                time.sleep(SCRAPER_CONFIG.extra_sleep)
                
                # 提取标题和内容
                title = page.title()
                content = extract_text_content(page, self.content_selectors)
                
                # 提取图片URL
                image_urls = self._extract_image_urls(page)
                
                # 下载图片
                image_handler = ImageHandler(url)
                downloaded_images = image_handler.download_images(image_urls, title)
                
                # 创建文章对象
                article = Article(
                    url=url,
                    title=title,
                    content=content,
                    images=[ImageInfo(**img) for img in downloaded_images]
                )
                
                return article
                
            except Exception as e:
                print(f"爬取失败: {e}")
                page.screenshot(path='error_screenshot.png')
                return None
    
    def _extract_image_urls(self, page: Page) -> List[str]:
        """提取页面中的图片URL"""
        image_urls = []
        images = page.query_selector_all('img')
        
        for img in images:
            try:
                img_src = img.get_attribute('src')
                data_src = img.get_attribute('data-src')
                
                actual_src = data_src or img_src
                if actual_src and actual_src.startswith(('http', '//')):
                    if actual_src.startswith('//'):
                        actual_src = 'https:' + actual_src
                    image_urls.append(actual_src)
            except:
                continue
                
        return image_urls

def main():
    url = input("请输入微信公众号文章URL: ").strip()
    scraper = WeChatScraper()
    
    for attempt in range(SCRAPER_CONFIG.max_retries):
        print(f"第 {attempt + 1} 次尝试...")
        article = scraper.scrape_article(url)
        
        if article:
            # 保存文章
            from src.storage.file_manager import FileManager
            FileManager.save_article(article, "wechat_article.md")
            break
        else:
            wait_time = random.uniform(3, 6)
            print(f"等待 {wait_time:.1f} 秒后重试...")
            time.sleep(wait_time)

if __name__ == "__main__":
    main()
