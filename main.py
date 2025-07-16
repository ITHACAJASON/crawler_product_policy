#!/usr/bin/env python3
"""
政策爬虫主程序
使用Playwright MCP进行网页抓取
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from loguru import logger
from src.crawlers.national_crawler import NationalCrawler

class PolicyCrawlerMain:
    """政策爬虫主程序"""
    
    def __init__(self):
        self.national_crawler = None
        self.setup_logging()
    
    def setup_logging(self):
        """设置全局日志"""
        logger.remove()  # 移除默认handler
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            "logs/main_{time:YYYYMMDD}.log",
            rotation="00:00",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG"
        )
        logger.info("政策爬虫程序启动")
    
    def run_with_playwright_mcp(self, page):
        """使用Playwright MCP页面对象运行爬虫"""
        try:
            logger.info("开始使用Playwright MCP爬取中央政府政策")
            
            # 初始化爬虫
            self.national_crawler = NationalCrawler()
            self.national_crawler.set_playwright_page(page)
            
            # 开始爬取
            self.national_crawler.crawl()
            
            logger.info("爬取任务完成")
            return True
            
        except Exception as e:
            logger.error(f"爬取过程中发生错误: {str(e)}")
            return False
    
    def get_start_url(self):
        """获取起始URL"""
        from config.crawler_config import config
        params = config.NATIONAL_CONFIG["search_params"]
        base_url = config.NATIONAL_CONFIG["base_url"]
        
        # 构建初始搜索URL
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        start_url = f"{base_url}?{param_string}&p=1&n=10"
        
        logger.info(f"起始URL: {start_url}")
        return start_url

def main():
    """主函数 - 独立运行模式"""
    logger.info("独立运行模式启动")
    crawler_main = PolicyCrawlerMain()
    
    print("=" * 50)
    print("🚀 政策爬虫程序")
    print("=" * 50)
    print("📋 使用说明：")
    print("1. 本程序需要配合Playwright MCP使用")
    print("2. 请使用以下URL开始爬取：")
    print(f"   {crawler_main.get_start_url()}")
    print("3. 数据将保存到data/excel/目录下")
    print("=" * 50)
    
    return crawler_main

if __name__ == "__main__":
    main_instance = main() 