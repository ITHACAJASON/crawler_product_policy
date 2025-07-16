"""
基础爬虫类
"""
import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

from loguru import logger
from config.crawler_config import config
from src.models.policy_model import PolicyDocument
from src.storage.excel_writer import ExcelWriter
from src.storage.database_handler import DatabaseHandler

class BaseCrawler(ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, crawler_name: str):
        self.crawler_name = crawler_name
        self.db_handler = DatabaseHandler()
        self.excel_writer = ExcelWriter()
        self.crawled_count = 0
        self.current_page = 1
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.batch_documents = []  # 批量文档缓存
        
        # 初始化日志
        self._setup_logging()
        
        # 初始化数据库
        self.db_handler.init_database()
        
        logger.info(f"初始化爬虫: {crawler_name}, 会话ID: {self.session_id}")
    
    def _setup_logging(self):
        """设置日志配置"""
        log_file = f"{config.LOG_DIR}/{self.crawler_name}_{self.session_id}.log"
        logger.add(log_file, rotation="10 MB", retention="30 days")
    
    def crawl(self):
        """主要爬取方法"""
        try:
            logger.info(f"开始爬取: {self.crawler_name}")
            
            # 恢复之前的进度
            self._restore_progress()
            
            # 开始爬取
            self._crawl_pages()
            
            # 最终保存
            self._final_save()
            
            logger.info(f"爬取完成，总共抓取 {self.crawled_count} 条数据")
            
        except Exception as e:
            logger.error(f"爬取过程中发生错误: {str(e)}")
            self._save_progress()
            # 保存已有的批量数据
            if self.batch_documents:
                self._save_batch_data(self.batch_documents)
            raise
    
    def _restore_progress(self):
        """恢复爬取进度"""
        progress = self.db_handler.get_crawler_progress(self.crawler_name)
        if progress:
            self.current_page = progress.get('current_page', 1)
            self.crawled_count = progress.get('crawled_count', 0)
            logger.info(f"恢复进度: 页面 {self.current_page}, 已抓取 {self.crawled_count} 条")
    
    def _save_progress(self):
        """保存爬取进度"""
        progress_data = {
            'current_page': self.current_page,
            'crawled_count': self.crawled_count,
            'last_update': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        self.db_handler.save_crawler_progress(self.crawler_name, progress_data)
        logger.info(f"保存进度: 页面 {self.current_page}, 已抓取 {self.crawled_count} 条")
    
    def _add_random_delay(self):
        """添加随机延迟"""
        delay = random.uniform(*config.RANDOM_DELAY_RANGE)
        time.sleep(delay)
    
    def _should_save_data(self) -> bool:
        """判断是否应该保存数据"""
        return len(self.batch_documents) >= config.SAVE_FREQUENCY
    
    def add_document(self, document: PolicyDocument):
        """添加文档到批量缓存"""
        # 设置会话ID
        document.session_id = self.session_id
        document.page_number = self.current_page
        
        self.batch_documents.append(document)
        self.crawled_count += 1
        
        # 检查是否需要保存
        if self._should_save_data():
            self._save_batch_data(self.batch_documents)
            self.batch_documents = []  # 清空缓存
    
    def _save_batch_data(self, documents: List[PolicyDocument]):
        """批量保存数据"""
        if not documents:
            return
        
        try:
            # 保存到Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"养老政策_{self.crawler_name}_{timestamp}.xlsx"
            self.excel_writer.save_documents(documents, filename)
            
            # 保存到数据库
            self.db_handler.save_documents(documents)
            
            # 保存进度
            self._save_progress()
            
            logger.info(f"保存 {len(documents)} 条数据到 {filename}")
            
        except Exception as e:
            logger.error(f"保存数据时发生错误: {str(e)}")
            raise
    
    def _final_save(self):
        """最终保存所有数据"""
        # 保存剩余的批量数据
        if self.batch_documents:
            self._save_batch_data(self.batch_documents)
        
        # 获取当前会话的所有数据
        all_documents = self.db_handler.get_session_documents(self.session_id)
        if all_documents:
            filename = f"养老政策_{self.crawler_name}_完整数据_{self.session_id}.xlsx"
            self.excel_writer.save_documents(all_documents, filename)
            logger.info(f"最终保存完整数据到 {filename}")
    
    @abstractmethod
    def _crawl_pages(self):
        """子类需要实现的页面爬取方法"""
        pass
    
    @abstractmethod
    def _parse_page_content(self, page_content: str) -> List[PolicyDocument]:
        """子类需要实现的页面解析方法"""
        pass 