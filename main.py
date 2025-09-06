from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# 目标URL
url = "https://mp.weixin.qq.com/s/5BRqbmsE9lfhai7mjt1gRQ"

# 配置 headless 浏览器
options = Options()
options.add_argument("--headless")  # 无头模式
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# 初始化浏览器
driver = webdriver.Chrome(options=options)

try:
    # 访问页面
    driver.get(url)
    
    # 等待页面主要内容加载（最多等待10秒）
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "rich_media_content"))
    )
    
    # 额外的等待，确保动态内容加载完成
    time.sleep(2)
    
    # 提取所有 <p> 标签的文本内容
    p_tags = driver.find_elements(By.TAG_NAME, "p")
    p_contents = [p.text.strip() for p in p_tags if p.text.strip()]  # 去除空文本
    
    # 打印并保存结果
    with open("wechat_article_p_contents.md", "w", encoding="utf-8") as f:
        f.write("# 微信公众号文章 <p> 标签内容\n\n")
        for i, content in enumerate(p_contents, 1):
            print(f"{content}")
            f.write(f"\n{content}\n\n")

except Exception as e:
    print(f"发生错误: {e}")

finally:
    driver.quit()
