from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from typing import Optional
import time
import random

from src.config.settings import BROWSER_CONFIG, SCRAPER_CONFIG

class BrowserManager:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
    def __enter__(self):
        self.setup_browser()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown_browser()
        
    def setup_browser(self):
        """初始化浏览器实例"""
        playwright = sync_playwright().start()
        
        self.browser = playwright.firefox.launch(
            headless=BROWSER_CONFIG.headless,
            args=[
                f'--width={BROWSER_CONFIG.viewport_width}',
                f'--height={BROWSER_CONFIG.viewport_height}',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        self.setup_context()
        
    def setup_context(self):
        """设置浏览器上下文"""
        self.context = self.browser.new_context(
            user_agent=SCRAPER_CONFIG.user_agent,
            viewport={
                'width': BROWSER_CONFIG.viewport_width,
                'height': BROWSER_CONFIG.viewport_height
            },
            device_scale_factor=BROWSER_CONFIG.device_scale_factor,
            locale=BROWSER_CONFIG.locale,
            timezone_id=BROWSER_CONFIG.timezone
        )
        
        # 设置HTTP头
        self.context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })
        
    def create_page(self) -> Page:
        """创建新页面"""
        if not self.context:
            self.setup_context()
        return self.context.new_page()
    
    def teardown_browser(self):
        """清理浏览器资源"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
            
    def navigate_with_retry(self, page: Page, url: str, max_retries: int = 3) -> bool:
        """页面导航"""
        for attempt in range(max_retries):
            try:
                # 随机延迟避免检测
                time.sleep(random.uniform(1, 3))
                
                print(f"尝试导航到: {url} (尝试 {attempt + 1}/{max_retries})")
                page.goto(url, wait_until='networkidle', timeout=BROWSER_CONFIG.timeout)
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(SCRAPER_CONFIG.base_backoff * (2 ** attempt))
                
        return False
