"""
数据库处理模块
"""
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from loguru import logger
from config.crawler_config import config
from src.models.policy_model import PolicyDocument

class DatabaseHandler:
    """数据库操作处理类"""
    
    def __init__(self):
        self.db_path = config.DB_PATH
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建文档表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS policy_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT UNIQUE,
                    policy_title TEXT,
                    content TEXT,
                    publish_date TEXT,
                    publish_agency TEXT,
                    document_type TEXT,
                    document_number TEXT,
                    policy_level TEXT,
                    province TEXT,
                    keywords TEXT,
                    source_url TEXT,
                    crawl_date TEXT,
                    file_format TEXT,
                    policy_status TEXT,
                    page_number INTEGER,
                    session_id TEXT,
                    is_processed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建爬虫进度表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawler_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crawler_name TEXT UNIQUE,
                    progress_data TEXT,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("数据库初始化完成")
    
    def save_documents(self, documents: List[PolicyDocument]) -> bool:
        """保存文档列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for doc in documents:
                    doc_data = doc.to_dict()
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO policy_documents (
                            doc_id, policy_title, content, publish_date, publish_agency,
                            document_type, document_number, policy_level, province, keywords,
                            source_url, crawl_date, file_format, policy_status, page_number,
                            session_id, is_processed
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        doc_data['doc_id'], doc_data['policy_title'], doc_data['content'],
                        doc_data['publish_date'], doc_data['publish_agency'], doc_data['document_type'],
                        doc_data['document_number'], doc_data['policy_level'], doc_data['province'],
                        doc_data['keywords'], doc_data['source_url'], doc_data['crawl_date'],
                        doc_data['file_format'], doc_data['policy_status'], doc_data['page_number'],
                        doc_data.get('session_id', ''), doc_data['is_processed']
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"保存文档到数据库失败: {str(e)}")
            return False
    
    def get_crawler_progress(self, crawler_name: str) -> Optional[Dict]:
        """获取爬虫进度"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT progress_data FROM crawler_progress WHERE crawler_name = ?",
                    (crawler_name,)
                )
                result = cursor.fetchone()
                
                if result:
                    return json.loads(result[0])
                return None
                
        except Exception as e:
            logger.error(f"获取爬虫进度失败: {str(e)}")
            return None
    
    def save_crawler_progress(self, crawler_name: str, progress_data: Dict):
        """保存爬虫进度"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO crawler_progress (crawler_name, progress_data, last_update)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (crawler_name, json.dumps(progress_data)))
                conn.commit()
                
        except Exception as e:
            logger.error(f"保存爬虫进度失败: {str(e)}")
    
    def get_session_documents(self, session_id: str) -> List[PolicyDocument]:
        """获取会话的所有文档"""
        documents = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM policy_documents WHERE session_id = ? ORDER BY created_at",
                    (session_id,)
                )
                
                for row in cursor.fetchall():
                    doc = PolicyDocument(
                        doc_id=row[1],
                        policy_title=row[2],
                        content=row[3],
                        publish_date=row[4],
                        publish_agency=row[5],
                        document_type=row[6],
                        document_number=row[7],
                        policy_level=row[8],
                        province=row[9],
                        keywords=json.loads(row[10]) if row[10] else [],
                        source_url=row[11],
                        crawl_date=row[12],
                        file_format=row[13],
                        policy_status=row[14],
                        page_number=row[15],
                        session_id=row[16],
                        is_processed=bool(row[17])
                    )
                    documents.append(doc)
                    
        except Exception as e:
            logger.error(f"获取会话文档失败: {str(e)}")
            
        return documents 