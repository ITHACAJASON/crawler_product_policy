"""
爬虫配置文件
"""
from typing import Dict, List
from dataclasses import dataclass
import os

@dataclass
class CrawlerConfig:
    """爬虫配置类"""
    
    # 基础配置
    BASE_DELAY: float = 2.0  # 请求间隔（秒）
    RANDOM_DELAY_RANGE: tuple = (1, 3)  # 随机延迟范围
    TIMEOUT: int = 30  # 请求超时时间
    
    # 重试配置
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 5.0
    BACKOFF_FACTOR: float = 2.0
    
    # 数据保存配置
    SAVE_FREQUENCY: int = 5  # 每N条数据保存一次
    BATCH_SIZE: int = 50     # 批处理大小
    
    # 文件配置
    DATA_DIR: str = "data"
    EXCEL_DIR: str = "data/excel"
    RAW_DIR: str = "data/raw"
    PROCESSED_DIR: str = "data/processed"
    LOG_DIR: str = "logs"
    
    # 数据库配置
    DB_PATH: str = "data/crawler_progress.db"
    
    # User-Agent轮换
    USER_AGENTS: List[str] = None
    
    # 中央政府网站配置
    NATIONAL_CONFIG: Dict = None
    
    # 省级政府网站配置（后续扩展）
    PROVINCIAL_CONFIGS: Dict = None
    
    def __post_init__(self):
        """初始化默认值"""
        if self.USER_AGENTS is None:
            self.USER_AGENTS = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        
        if self.NATIONAL_CONFIG is None:
            self.NATIONAL_CONFIG = {
                "base_url": "https://sousuo.www.gov.cn/zcwjk/policyDocumentLibrary",
                "search_params": {
                    "t": "zhengcelibrary",
                    "q": "养老"
                },
                "page_size": 10,
                "max_pages": 100  # 最大抓取页数，避免无限抓取
            }
        
        if self.PROVINCIAL_CONFIGS is None:
            self.PROVINCIAL_CONFIGS = {}

# 全局配置实例
config = CrawlerConfig() 