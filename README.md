## INTRO

为了提取华科俱乐部微信公众号文章内容做的爬虫工具，旨在更好地迁移文章到俱乐部主页，和俱乐部的项目[post_scraper](https://github.com/hust-open-atom-club/post_scraper) ，本项目成熟后，将迁移到该仓库。

以下是主页使用的文章管理模板，更多参考https://github.com/hust-open-atom-club/OpenAtomClub/blob/master/pages/_news/：

```
---
title: ""（h1标签）
layout: splash（固定）
excerpt: "2024-3-27"（参考脚本的处理）
header:
  overlay_image: /assets/images/index.jpg（基本固定）
  overlay_filter: 0.25（固定）
---

![image](本地文件路径)  -----图img标签
文章内容（p）

```

目前脚本结构简单，主要功能是爬取指定微信公众号文章（通过 URL 输入）的 <p> 标签内容，并将结果保存为 Markdown 文件（wechat_article_p_contents.md）。它使用 Selenium 模拟浏览器行为，适合动态加载的页面（如微信文章页）。具体功能包括：

1. **浏览器配置**：通过 Chrome 的无头模式（headless）和自定义用户代理（User-Agent）模拟真实浏览器访问。
2. **动态页面加载**：使用显式等待（WebDriverWait）确保目标元素（rich_media_content）加载完成。
3. **内容提取**：获取所有 <p> 标签的非空文本内容。
4. **错误重试机制**：支持最大重试次数（MAX_RETRIES），结合指数退避策略（exponential backoff）处理网络或加载失败。
5. **结果保存**：将爬取内容写入 Markdown 文件，包含固定格式的 YAML 前置元数据（front matter）。

需要添加的功能已写在issue中，欢迎贡献。待功能补全后，使用rust重写：







## ROADMAP
