"""
政策数据模型
"""
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, List
import json

@dataclass
class PolicyDocument:
    """政策文档数据模型"""
    
    # 核心字段
    policy_title: str = ""
    content: str = ""
    publish_date: Optional[str] = None
    publish_agency: str = ""
    document_type: str = ""
    
    # 扩展字段
    document_number: str = ""
    policy_level: str = ""  # 中央/省级/市级
    province: str = ""  # 省份（省级政策适用）
    keywords: List[str] = field(default_factory=list)
    source_url: str = ""
    crawl_date: str = ""
    file_format: str = "HTML"
    policy_status: str = "有效"
    
    # 内部字段
    doc_id: str = ""  # 文档唯一标识
    page_number: int = 0
    session_id: str = ""
    is_processed: bool = False
    
    def __post_init__(self):
        """初始化处理"""
        if self.crawl_date == "":
            self.crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        data = asdict(self)
        data['keywords'] = json.dumps(self.keywords, ensure_ascii=False)
        return data
    
    def to_excel_row(self) -> dict:
        """转换为Excel行格式"""
        return {
            "政策标题": self.policy_title,
            "正文内容": self.content,
            "发布时间": self.publish_date,
            "发布机构": self.publish_agency,
            "文件类型": self.document_type,
            "文件编号": self.document_number,
            "政策级别": self.policy_level,
            "省份": self.province,
            "关键词": ", ".join(self.keywords),
            "原文链接": self.source_url,
            "抓取时间": self.crawl_date,
            "文档格式": self.file_format,
            "政策状态": self.policy_status
        } 