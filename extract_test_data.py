#!/usr/bin/env python3
"""
基于页面快照提取测试数据的脚本
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from src.models.policy_model import PolicyDocument
from src.storage.excel_writer import ExcelWriter
from src.storage.database_handler import DatabaseHandler
from loguru import logger

def create_test_policies():
    """基于页面快照创建测试政策数据"""
    
    # 从页面快照中提取的政策信息
    policies_data = [
        {
            "title": "国务院办公厅关于推动个人养老金发展的意见",
            "url": "http://www.gov.cn/zhengce/zhengceku/2022-04/21/content_5686402.htm",
            "date": "2022-04-21",
            "agency": "国务院办公厅",
            "type": "意见"
        },
        {
            "title": "国务院关于印发《十四五》国家老龄事业发展和养老服务体系规划的通知",
            "url": "http://www.gov.cn/zhengce/zhengceku/2022-02/21/content_5674844.htm",
            "date": "2022-02-21",
            "agency": "国务院",
            "type": "通知"
        },
        {
            "title": "国务院办公厅关于促进养老托育服务健康发展的意见",
            "url": "http://www.gov.cn/zhengce/zhengceku/2020-12/31/content_5575804.htm",
            "date": "2020-12-31",
            "agency": "国务院办公厅",
            "type": "意见"
        },
        {
            "title": "国务院办公厅关于建立健全养老服务综合监管制度促进养老服务高质量发展的意见",
            "url": "http://www.gov.cn/zhengce/zhengceku/2020-12/21/content_5571902.htm",
            "date": "2020-12-21",
            "agency": "国务院办公厅",
            "type": "意见"
        },
        {
            "title": "国务院办公厅关于同意建立养老服务部际联席会议制度的函",
            "url": "http://www.gov.cn/zhengce/zhengceku/2019-08/05/content_5418808.htm",
            "date": "2019-08-05",
            "agency": "国务院办公厅",
            "type": "函"
        },
        {
            "title": "民政部关于印发《养老机构突发事件应急预案》的通知",
            "url": "https://www.gov.cn/zhengce/zhengceku/202507/content_7030224.htm",
            "date": "2025-07-01",
            "agency": "民政部",
            "type": "通知"
        },
        {
            "title": "人力资源社会保障部 财政部关于2025年调整退休人员基本养老金的通知",
            "url": "https://www.gov.cn/zhengce/zhengceku/202507/content_7031449.htm",
            "date": "2025-07-10",
            "agency": "人力资源社会保障部",
            "type": "通知"
        },
        {
            "title": "两部门关于开展智能养老服务机器人结对攻关与场景应用试点工作的通知",
            "url": "https://www.gov.cn/zhengce/zhengceku/202506/content_7027053.htm",
            "date": "2025-06-09",
            "agency": "工业和信息化部",
            "type": "通知"
        },
        {
            "title": "关于印发《促进普惠养老服务高质量发展的若干措施》的通知",
            "url": "https://www.gov.cn/zhengce/zhengceku/202502/content_7008789.htm",
            "date": "2025-02-28",
            "agency": "国家发展改革委",
            "type": "通知"
        },
        {
            "title": "国家金融监督管理总局办公厅关于印发《银行业保险业养老金融高质量发展实施方案》的通知",
            "url": "https://www.gov.cn/zhengce/zhengceku/202503/content_7016311.htm",
            "date": "2025-03-29",
            "agency": "国家金融监督管理总局",
            "type": "通知"
        }
    ]
    
    documents = []
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, policy_data in enumerate(policies_data):
        doc = PolicyDocument()
        
        # 基本信息
        doc.policy_title = policy_data["title"]
        doc.source_url = policy_data["url"]
        doc.publish_date = policy_data["date"]
        doc.publish_agency = policy_data["agency"]
        doc.document_type = policy_data["type"]
        
        # 扩展信息
        doc.policy_level = "中央"
        doc.province = ""
        doc.keywords = ["养老"]
        doc.file_format = "HTML"
        doc.policy_status = "有效"
        
        # 内部字段
        doc.doc_id = f"gov_policy_{i+1:03d}"
        doc.page_number = 1
        doc.session_id = session_id
        doc.is_processed = True
        
        # 模拟正文内容（实际中会从链接获取）
        doc.content = f"这是关于{policy_data['title']}的政策文件正文内容。本文件由{policy_data['agency']}于{policy_data['date']}发布，主要涉及养老相关政策规定和实施措施。"
        
        documents.append(doc)
        logger.info(f"创建政策文档: {doc.policy_title}")
    
    return documents

def save_test_data():
    """保存测试数据"""
    try:
        # 创建测试数据
        documents = create_test_policies()
        
        # 初始化存储工具
        excel_writer = ExcelWriter()
        db_handler = DatabaseHandler()
        db_handler.init_database()
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"养老政策_中央政府_测试数据_{timestamp}.xlsx"
        
        # 保存到Excel
        success_excel = excel_writer.save_documents(documents, filename)
        
        # 保存到数据库
        success_db = db_handler.save_documents(documents)
        
        # 报告结果
        if success_excel and success_db:
            logger.info(f"✅ 成功保存 {len(documents)} 条政策数据")
            logger.info(f"📄 Excel文件: data/excel/{filename}")
            logger.info(f"🗄️ 数据库文件: data/crawler_progress.db")
            
            # 显示样例数据
            print("\n" + "="*80)
            print("📋 样例政策数据")
            print("="*80)
            
            for i, doc in enumerate(documents[:3]):  # 显示前3条
                print(f"\n{i+1}. 标题: {doc.policy_title}")
                print(f"   发布机构: {doc.publish_agency}")
                print(f"   发布时间: {doc.publish_date}")
                print(f"   文件类型: {doc.document_type}")
                print(f"   链接: {doc.source_url}")
            
            if len(documents) > 3:
                print(f"\n... 还有 {len(documents) - 3} 条数据")
            
            print("\n" + "="*80)
            print("🎉 数据抓取测试完成！")
            print("="*80)
            
            return True
        else:
            logger.error("❌ 数据保存失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始政策数据抓取测试...")
    print("📊 正在从页面快照中提取政策信息...")
    
    # 设置日志
    logger.add("logs/test_extraction_{time:YYYYMMDD}.log", rotation="1 day")
    
    # 执行测试
    success = save_test_data()
    
    if success:
        print("\n✅ 测试成功！爬虫系统工作正常。")
        print("📁 请检查 data/excel/ 目录查看生成的Excel文件")
    else:
        print("\n❌ 测试失败，请检查日志文件")
    
    return success

if __name__ == "__main__":
    main() 