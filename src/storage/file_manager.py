from typing import List
from src.models.article import Article

class FileManager:
    @staticmethod
    def save_article(article: Article, filename: str, header_image: str = None):
        """保存文章到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(article.to_markdown(header_image))
        print(f"文章已保存到: {filename}")
