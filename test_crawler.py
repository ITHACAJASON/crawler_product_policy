#!/usr/bin/env python3
"""
测试爬虫脚本 - 与Playwright MCP协同工作
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from src.crawlers.national_crawler import NationalCrawler
from src.models.policy_model import PolicyDocument
from bs4 import BeautifulSoup
from loguru import logger

class PlaywrightTestCrawler:
    """与Playwright MCP协同的测试爬虫"""
    
    def __init__(self):
        self.crawler = NationalCrawler()
        logger.info("测试爬虫初始化完成")
    
    def parse_current_page_html(self, html_content):
        """解析当前页面的HTML内容"""
        documents = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            logger.info(f"HTML内容长度: {len(html_content)}")
            
            # 查找政策文档项目
            # 从页面快照可以看到，政策项目在 generic 容器中
            policy_sections = soup.select('div.searchResult') or soup.select('.result-list')
            
            if not policy_sections:
                # 尝试查找具体的政策链接
                policy_links = soup.select('a[href*="content"]')
                logger.info(f"找到 {len(policy_links)} 个政策链接")
                
                for i, link in enumerate(policy_links[:10]):  # 限制前10个进行测试
                    try:
                        doc = PolicyDocument()
                        
                        # 提取标题
                        title_text = link.get_text(strip=True)
                        if title_text and len(title_text) > 5:
                            doc.policy_title = title_text
                            doc.source_url = link.get('href', '')
                            if doc.source_url and not doc.source_url.startswith('http'):
                                doc.source_url = f"http://www.gov.cn{doc.source_url}"
                            
                            # 设置基本信息
                            doc.policy_level = "中央"
                            doc.publish_agency = "中央政府"
                            doc.keywords = ["养老"]
                            doc.doc_id = f"test_{i}"
                            
                            # 从标题推断文件类型
                            if '通知' in title_text:
                                doc.document_type = '通知'
                            elif '意见' in title_text:
                                doc.document_type = '意见'
                            elif '办法' in title_text:
                                doc.document_type = '办法'
                            elif '规定' in title_text:
                                doc.document_type = '规定'
                            else:
                                doc.document_type = '政策文件'
                            
                            # 尝试从父元素获取发布时间
                            parent = link.parent
                            date_pattern = parent.get_text() if parent else ""
                            import re
                            date_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', date_pattern)
                            if date_match:
                                doc.publish_date = date_match.group(1)
                            
                            documents.append(doc)
                            logger.info(f"解析到政策: {doc.policy_title[:50]}...")
                    
                    except Exception as e:
                        logger.error(f"解析第{i}个政策项目失败: {str(e)}")
                        continue
            
            logger.info(f"总共解析到 {len(documents)} 个政策文档")
            return documents
            
        except Exception as e:
            logger.error(f"解析HTML失败: {str(e)}")
            return []
    
    def test_save_documents(self, documents):
        """测试保存文档功能"""
        if not documents:
            logger.warning("没有文档需要保存")
            return False
        
        try:
            # 使用爬虫的保存功能
            for doc in documents:
                self.crawler.add_document(doc)
            
            # 手动触发最终保存
            self.crawler._final_save()
            
            logger.info(f"成功保存 {len(documents)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"保存文档失败: {str(e)}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 政策爬虫测试程序")
    print("=" * 60)
    print("此程序将配合Playwright MCP测试爬虫功能")
    print("请确保已经在浏览器中打开了政策文件库页面")
    print("=" * 60)
    
    test_crawler = PlaywrightTestCrawler()
    return test_crawler

if __name__ == "__main__":
    test_instance = main() 