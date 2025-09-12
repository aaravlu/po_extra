import os
from dataclasses import dataclass

@dataclass
class BrowserConfig:
    headless: bool = True
    viewport_width: int = 375
    viewport_height: int = 667
    device_scale_factor: int = 2
    locale: str = 'zh-CN'
    timezone: str = 'Asia/Shanghai'
    timeout: int = 60000
    wait_timeout: int = 8000

@dataclass
class ScraperConfig:
    max_retries: int = 3
    base_backoff: int = 2
    extra_sleep: int = 2
    user_agent: str = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/120.0 Mobile/15E148 Safari/605.1.15'

@dataclass
class StorageConfig:
    base_image_dir: str = "assets/images"
    output_file: str = "wechat_article.md"
    default_header_image: str = "/assets/images/index.png"

# global configuration
BROWSER_CONFIG = BrowserConfig()
SCRAPER_CONFIG = ScraperConfig()
STORAGE_CONFIG = StorageConfig()
