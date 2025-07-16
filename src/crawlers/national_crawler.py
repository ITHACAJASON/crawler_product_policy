"""
中央政府政策爬虫
"""
import hashlib
import time
from typing import List
from urllib.parse import urljoin, urlparse

from loguru import logger
from bs4 import BeautifulSoup

from config.crawler_config import config
from src.crawlers.base_crawler import BaseCrawler
from src.models.policy_model import PolicyDocument

class NationalCrawler(BaseCrawler):
    """中央政府政策爬虫"""
    
    def __init__(self):
        super().__init__("中央政府")
        self.base_url = config.NATIONAL_CONFIG["base_url"]
        self.search_params = config.NATIONAL_CONFIG["search_params"]
        self.max_pages = config.NATIONAL_CONFIG["max_pages"]
        self.page_size = config.NATIONAL_CONFIG["page_size"]
        
        # Playwright页面对象将在运行时设置
        self.page = None
    
    def set_playwright_page(self, page):
        """设置Playwright页面对象"""
        self.page = page
    
    def _crawl_pages(self):
        """爬取页面主方法"""
        if not self.page:
            raise ValueError("Playwright页面对象未设置，请先调用set_playwright_page")
        
        logger.info(f"开始从第 {self.current_page} 页爬取中央政府政策")
        
        while self.current_page <= self.max_pages:
            try:
                logger.info(f"正在爬取第 {self.current_page} 页")
                
                # 导航到搜索页面
                search_url = self._build_search_url(self.current_page)
                logger.info(f"访问URL: {search_url}")
                
                # 这里将由外部调用者处理页面导航
                # 我们只处理解析逻辑
                
                # 页面将由外部设置，我们直接解析
                documents = self._parse_current_page()
                
                if not documents:
                    logger.warning(f"第 {self.current_page} 页没有找到政策文档，停止爬取")
                    break
                
                # 添加文档到批量处理
                for doc in documents:
                    self.add_document(doc)
                
                logger.info(f"第 {self.current_page} 页完成，获取到 {len(documents)} 条政策")
                
                # 进入下一页
                self.current_page += 1
                
                # 添加延迟
                self._add_random_delay()
                
            except Exception as e:
                logger.error(f"爬取第 {self.current_page} 页时出错: {str(e)}")
                
                # 重试机制
                retry_count = 0
                while retry_count < config.MAX_RETRIES:
                    try:
                        logger.info(f"重试第 {retry_count + 1} 次...")
                        time.sleep(config.RETRY_DELAY * (config.BACKOFF_FACTOR ** retry_count))
                        
                        # 重新尝试当前页面
                        documents = self._parse_current_page()
                        if documents:
                            for doc in documents:
                                self.add_document(doc)
                            logger.info(f"重试成功，第 {self.current_page} 页获取到 {len(documents)} 条政策")
                            break
                        
                    except Exception as retry_e:
                        logger.error(f"重试失败: {str(retry_e)}")
                        retry_count += 1
                
                if retry_count >= config.MAX_RETRIES:
                    logger.error(f"第 {self.current_page} 页重试失败，跳过该页")
                
                self.current_page += 1
    
    def _build_search_url(self, page_num: int) -> str:
        """构建搜索URL"""
        params = self.search_params.copy()
        params['p'] = str(page_num)
        params['n'] = str(self.page_size)
        
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{param_string}"
    
    def _parse_current_page(self) -> List[PolicyDocument]:
        """解析当前页面内容"""
        try:
            # 获取页面HTML内容
            html_content = self.page.content()
            return self._parse_page_content(html_content)
            
        except Exception as e:
            logger.error(f"解析页面内容失败: {str(e)}")
            return []
    
    def _parse_page_content(self, page_content: str) -> List[PolicyDocument]:
        """解析页面内容获取政策文档"""
        documents = []
        
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # 查找政策文档列表
            # 根据实际网站结构调整选择器
            policy_items = soup.select('.searchResult .result-item') or soup.select('.policy-item') or soup.select('.result-list li')
            
            if not policy_items:
                # 尝试其他可能的选择器
                policy_items = soup.select('.list-item') or soup.select('.content-item') or soup.select('tr[onclick]')
            
            logger.info(f"在页面中找到 {len(policy_items)} 个政策项目")
            
            for item in policy_items:
                try:
                    doc = self._parse_policy_item(item)
                    if doc and doc.policy_title:  # 确保有标题
                        documents.append(doc)
                except Exception as e:
                    logger.error(f"解析单个政策项目失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"解析页面HTML失败: {str(e)}")
        
        return documents
    
    def _parse_policy_item(self, item) -> PolicyDocument:
        """解析单个政策项目"""
        doc = PolicyDocument()
        
        try:
            # 提取标题
            title_elem = (item.select_one('a[title]') or 
                         item.select_one('.title a') or 
                         item.select_one('h3 a') or 
                         item.select_one('a'))
            
            if title_elem:
                doc.policy_title = title_elem.get('title') or title_elem.get_text(strip=True)
                # 提取链接
                href = title_elem.get('href')
                if href:
                    doc.source_url = urljoin(self.base_url, href)
            
            # 提取发布时间
            date_elem = (item.select_one('.date') or 
                        item.select_one('.time') or 
                        item.select_one('.publish-date'))
            
            if date_elem:
                doc.publish_date = date_elem.get_text(strip=True)
            
            # 提取发布机构
            agency_elem = (item.select_one('.agency') or 
                          item.select_one('.source') or 
                          item.select_one('.department'))
            
            if agency_elem:
                doc.publish_agency = agency_elem.get_text(strip=True)
            else:
                doc.publish_agency = "中央政府"
            
            # 提取文件类型
            type_elem = (item.select_one('.type') or 
                        item.select_one('.category'))
            
            if type_elem:
                doc.document_type = type_elem.get_text(strip=True)
            else:
                # 从标题推断类型
                title_lower = doc.policy_title.lower()
                if '通知' in title_lower:
                    doc.document_type = '通知'
                elif '意见' in title_lower:
                    doc.document_type = '意见'
                elif '办法' in title_lower:
                    doc.document_type = '办法'
                elif '规定' in title_lower:
                    doc.document_type = '规定'
                else:
                    doc.document_type = '政策文件'
            
            # 提取文档编号
            number_elem = item.select_one('.number') or item.select_one('.doc-number')
            if number_elem:
                doc.document_number = number_elem.get_text(strip=True)
            
            # 设置其他字段
            doc.policy_level = "中央"
            doc.province = ""
            doc.keywords = ["养老"]
            
            # 生成文档ID
            doc.doc_id = self._generate_doc_id(doc.policy_title, doc.source_url)
            
            # 如果有链接，尝试获取正文内容
            if doc.source_url and self.page:
                try:
                    content = self._fetch_document_content(doc.source_url)
                    if content:
                        doc.content = content
                except Exception as e:
                    logger.warning(f"获取文档正文失败: {str(e)}")
                    doc.content = doc.policy_title  # 使用标题作为备选内容
            
        except Exception as e:
            logger.error(f"解析政策项目详情失败: {str(e)}")
        
        return doc
    
    def _generate_doc_id(self, title: str, url: str) -> str:
        """生成文档唯一ID"""
        content = f"{title}_{url}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _fetch_document_content(self, url: str) -> str:
        """获取文档正文内容"""
        try:
            # 导航到文档页面
            self.page.goto(url, wait_until='networkidle')
            
            # 等待页面加载
            time.sleep(2)
            
            # 获取页面内容
            html_content = self.page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找正文内容
            content_elem = (soup.select_one('.content') or 
                           soup.select_one('.article-content') or 
                           soup.select_one('.policy-content') or 
                           soup.select_one('#content') or
                           soup.select_one('.main-content'))
            
            if content_elem:
                # 清理HTML标签并提取文本
                content = content_elem.get_text(separator=' ', strip=True)
                # 简单清理
                content = ' '.join(content.split())  # 移除多余空白
                return content[:5000]  # 限制长度
            
            return ""
            
        except Exception as e:
            logger.error(f"获取文档内容失败 {url}: {str(e)}")
            return "" 