from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class ImageInfo:
    original_url: str
    local_path: str
    filename: str
    download_time: datetime = field(default_factory=datetime.now)

@dataclass
class Article:
    url: str
    title: str
    content: List[str]
    images: List[ImageInfo] = field(default_factory=list)
    publish_date: Optional[str] = None
    scrape_time: datetime = field(default_factory=datetime.now)
    
    def to_markdown(self, header_image: str = None) -> str:
        """将文章转换为markdown格式"""
        lines = []
        
        # Front Matter头部
        lines.append("---")
        lines.append(f"title: {self.title}")
        lines.append("layout: splash")
        lines.append(f"excerpt: {self.scrape_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("header:")
        lines.append(f"  overlay_image: {header_image or '/assets/images/index.png'}")
        lines.append("  overlay_filter: 0.25")
        lines.append("categories:")
        lines.append("  - 微信公众号")
        lines.append("tags:")
        lines.append("  - 转载")
        lines.append("---\n")
        
        # 内容
        for paragraph in self.content:
            lines.append(f"{paragraph}\n")
        
        # 图片
        if self.images:
            lines.append("\n## 文章图片\n")
            for img in self.images:
                lines.append(f"![{img.filename}]({img.local_path.replace('assets/images/', '/assets/images/')})\n")
        
        return "\n".join(lines)
