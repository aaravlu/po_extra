import re
import os
from datetime import datetime
from typing import List, Set
from playwright.sync_api import Page

def extract_date_from_url(url: str) -> str:
    """从URL中提取日期"""
    date_match = re.search(r'/(\d{4})(\d{2})(\d{2})/', url)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}{month}{day}"
    return datetime.now().strftime("%Y%m%d")

def create_directory(path: str) -> str:
    """创建目录并返回路径"""
    os.makedirs(path, exist_ok=True)
    return path

def extract_text_content(page: Page, selectors: List[str]) -> List[str]:
    """从页面中提取文本内容"""
    text_elements = []
    seen_texts: Set[str] = set()
    
    # 尝试多种元素选择器
    element_types = ['p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    for element_type in element_types:
        elements = page.query_selector_all(element_type)
        for element in elements:
            try:
                text = element.evaluate('el => el.textContent')
                if text and text.strip():
                    clean_text = text.strip()
                    if (clean_text not in seen_texts and
                        len(clean_text) > 2 and
                        not clean_text.startswith('<!--') and
                        not clean_text.endswith('-->')):
                        seen_texts.add(clean_text)
                        text_elements.append(clean_text)
            except:
                continue
                
    return text_elements

def wait_for_content(page: Page, selectors: List[str], timeout: int = 8000) -> bool:
    """等待内容加载"""
    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            continue
    return False
