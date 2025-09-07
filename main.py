from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# url = input('请输入连接：')
url = "https://mp.weixin.qq.com/s/5BRqbmsE9lfhai7mjt1gRQ"

# browser configuration
options = Options()
options.add_argument("--headless")  # 无头模式, 减少程序损耗
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# 可调参数
MAX_RETRIES = 3           # 最大重试次数
BASE_BACKOFF = 2          # 初始退避秒数
WAIT_TIMEOUT = 10         # 显式等待超时秒数
EXTRA_SLEEP = 2           # 页面额外等待秒数


def fetch_p_contents(driver, target_url: str):
    driver.get(target_url)
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "rich_media_content"))
    )
    time.sleep(EXTRA_SLEEP)
    p_tags = driver.find_elements(By.TAG_NAME, "p")
    p_contents = [p.text.strip() for p in p_tags if p.text.strip()]
    return p_contents


driver = webdriver.Chrome(options=options)

try:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            p_contents = fetch_p_contents(driver, url)
            with open("wechat_article_p_contents.md", "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write("title: {title}\n")
                f.write("layout: splash\n")
                f.write("excerpt: {time}\n")
                f.write("header:\n overlay_image:{img_path} \n overlay_filter:0.25\n---\n")
                for content in p_contents:
                    print(f"{content}")
                    f.write(f"\n{content}\n\n")
            break
        except Exception as e:
            if attempt < MAX_RETRIES:
                backoff = BASE_BACKOFF * (2 ** (attempt - 1))
                print(f"Attempt {attempt} failed: {e}. Retrying in {backoff}s ...")
                time.sleep(backoff)
                try:
                    driver.delete_all_cookies()
                except Exception:
                    pass
            else:
                raise RuntimeError(f"All {MAX_RETRIES} attempts failed during fetching and parsing") from e
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    driver.quit()
