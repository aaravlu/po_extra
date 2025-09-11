"""
post_scraper 
raw crawler idea script
------------------------
基于playwright实现，如果使用selenium会在几次访问后被拦截，且被检测行为，包括更换ip、header,浏览器特征都无法规避
但pw无法完美规避，开发成熟后可以给pw添加指纹伪装增强等功能
------------------------
"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from datetime import datetime

def create_image_directory(article_url):
    """创建图片保存目录，基于文章日期"""
    date_match = re.search(r'/(\d{4})(\d{2})(\d{2})/', article_url)
    if date_match:
        year, month, day = date_match.groups()
        date_str = f"{year}{month}{day}"
    
    # 在assets/images里创建本文的图片目录
    base_dir = "assets/images"
    article_dir = os.path.join(base_dir, date_str)
    os.makedirs(article_dir, exist_ok=True)

    return article_dir

def download_image(img_url, save_dir, filename=None):
    """下载图片到指定目录"""
    try:
        if not filename:
            # 从URL中提取文件名
            parsed_url = urlparse(img_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                filename = f"image_{int(time.time())}_{random.randint(1000, 9999)}.jpg"

        save_path = os.path.join(save_dir, filename)

        # 下载图片, 遇到验证页时请调整header和运行环境的ip
        response = requests.get(img_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 图片下载
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

def fetch_wechat_with_firefox(url):
    # 创建图片保存目录
    image_dir = create_image_directory(url)
    image_counter = 1

    with sync_playwright() as p:
        # 配置Firefox选项,可调整
        browser = p.firefox.launch(
            headless=True,
            args=[
                '--width=375',
                '--height=667',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        # 设置移动端上下文
        context = browser.new_context(
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/120.0 Mobile/15E148 Safari/605.1.15',
            viewport={'width': 375, 'height': 667},
            device_scale_factor=2,
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
        )

        # 设置HTTP头
        context.set_extra_http_headers({
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

        page = context.new_page()

        try:
            # 随机延迟避免检测
            time.sleep(random.uniform(1, 3))

            print(f"Firefox正在访问: {url}")
            page.goto(url, wait_until='networkidle', timeout=60000)

            # 多种等待策略
            content_selectors = [
                '.rich_media_content',
                '#js_content',
                '.weui-article',
                'article',
                '[class*="content"]'
            ]

            for selector in content_selectors:
                try:
                    page.wait_for_selector(selector, timeout=8000)
                    break
                except:
                    continue

            # 额外等待确保JavaScript执行完成
            time.sleep(2)

            # 获取文章标题（用于命名图片）
            title = page.title()
            safe_title = re.sub(r'[\\/*?:"<>|]', '', title)[:50]  # 清理非法字符

            # 提取文本内容（段落和span）
            paragraphs = page.query_selector_all('p')
            spans = page.query_selector_all('span')
            h_tags = page.query_selector_all('h1, h2, h3, h4, h5, h6')

            all_text_elements = paragraphs + spans + h_tags
            p_contents = []
            seen_texts = set()  # 避免重复内容

            for element in all_text_elements:
                try:
                    text = element.evaluate('el => el.textContent')
                    if text and text.strip():
                        clean_text = text.strip()
                        # 去重并过滤过短的内容
                        if (clean_text not in seen_texts and
                            len(clean_text) > 2 and
                            not clean_text.startswith('<!--') and
                            not clean_text.endswith('-->')):
                            seen_texts.add(clean_text)
                            p_contents.append(clean_text)
                except:
                    continue

            # 提取并下载图片
            images = page.query_selector_all('img')
            image_urls = []

            for img in images:
                try:
                    img_src = img.get_attribute('src')
                    data_src = img.get_attribute('data-src')  # 微信常用的懒加载属性

                    actual_src = data_src or img_src
                    if actual_src and actual_src.startswith(('http', '//')):
                        if actual_src.startswith('//'):
                            actual_src = 'https:' + actual_src

                        # 下载图片
                        filename = f"{safe_title}_{image_counter:03d}.jpg"
                        image_path = download_image(actual_src, image_dir, filename)

                        if image_path:
                            image_urls.append({
                                'original_url': actual_src,
                                'local_path': image_path,
                                'filename': filename
                            })
                            image_counter += 1

                except Exception as e:
                    print(f"图片处理错误: {e}")
                    continue

            # 如果直接获取失败，使用页面内容解析
            if not p_contents:
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # 尝试多种内容选择器
                content_areas = []
                for selector in content_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content_areas.extend(elements)

                if content_areas:
                    for area in content_areas:
                        # 提取段落
                        paragraphs = area.find_all('p')
                        for p in paragraphs:
                            text = p.get_text().strip()
                            if text and text not in seen_texts:
                                seen_texts.add(text)
                                p_contents.append(text)

                        # 提取span
                        spans = area.find_all('span')
                        for span in spans:
                            text = span.get_text().strip()
                            if text and text not in seen_texts:
                                seen_texts.add(text)
                                p_contents.append(text)

            # 如果还是没有内容，获取整个页面文本
            if not p_contents:
                full_text = page.evaluate('() => document.body.textContent')
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                for line in lines:
                    if line not in seen_texts and len(line) > 2:
                        seen_texts.add(line)
                        p_contents.append(line)

            return p_contents, image_urls, title

        except Exception as e:
            print(f"Firefox抓取错误: {e}")
            # 保存截图和HTML来调试
            page.screenshot(path='firefox_error.png')
            with open('firefox_page.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            return None, None, None

        finally:
            browser.close()

def main():
    url = input("请输入微信公众号文章URL: ").strip()

    # 尝试多次
    for attempt in range(3):
        print(f"第 {attempt + 1} 次尝试...")
        content, images, title = fetch_wechat_with_firefox(url)

        if content:
            # 获取当前时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 设置封面图片路径（如果有图片的话）
            img_path = "/assets/images/default-header.jpg"  # 默认图片
            if images:
                # 使用第一张图片作为封面
                first_image_path = images[0]['local_path']
                # 转换为相对路径（根据你的网站结构调整）
                img_path = first_image_path.replace('assets/images/', '/assets/images/')

            # 保存文本内容为markdown
            with open("wechat_firefox.md", "w", encoding="utf-8") as f:
                # jekyll模板使用
                #f.write("---\n")
                #f.write(f"title: {title or '微信公众号文章'}\n")
                #f.write("layout: splash\n")
                #f.write(f"excerpt: {current_time}\n")
                #f.write("header:\n")
                #f.write(f"  overlay_image: {img_path}\n")
                #f.write("  overlay_filter: 0.25\n")
                #f.write("categories:\n")
                #f.write("  - 微信公众号\n")
                #f.write("tags:\n")
                #f.write("  - 转载\n")
                #f.write("  - 技术文章(后期用大模型识别类型)\n")
                #f.write("---\n\n")

                # 写入文章内容,会有不可避免的信息，需要人工处理（span标签造成）
                for paragraph in content:
                    f.write(f"{paragraph}\n\n")

                # 添加图片信息
                if images:
                    f.write("\n## 文章图片\n\n")
                    for img_info in images:
                        f.write(f"![{img_info['filename']}]({img_info['local_path'].replace('assets/images/', '/assets/images/')})\n\n")

            print(f"成功保存 {len(content)} 个文本段落到 wechat_firefox.md")

            if images:
                print(f"成功下载 {len(images)} 张图片到 assets/images/")

            break
        else:
            wait_time = random.uniform(3, 6)
            print(f"等待 {wait_time:.1f} 秒后重试...")
            time.sleep(wait_time)

if __name__ == "__main__":
    main()
