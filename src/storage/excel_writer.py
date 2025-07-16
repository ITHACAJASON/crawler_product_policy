"""
Excel文件写入模块
"""
import pandas as pd
from pathlib import Path
from typing import List
from datetime import datetime

from loguru import logger
from config.crawler_config import config
from src.models.policy_model import PolicyDocument

class ExcelWriter:
    """Excel文件写入类"""
    
    def __init__(self):
        self._ensure_excel_dir()
    
    def _ensure_excel_dir(self):
        """确保Excel目录存在"""
        Path(config.EXCEL_DIR).mkdir(parents=True, exist_ok=True)
    
    def save_documents(self, documents: List[PolicyDocument], filename: str) -> bool:
        """保存文档到Excel文件"""
        try:
            if not documents:
                logger.warning("没有文档需要保存")
                return False
            
            # 转换为DataFrame格式
            excel_data = [doc.to_excel_row() for doc in documents]
            df = pd.DataFrame(excel_data)
            
            # 保存到Excel文件
            filepath = Path(config.EXCEL_DIR) / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='政策文档', index=False)
                
                # 设置列宽
                worksheet = writer.sheets['政策文档']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # 最大宽度50
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"成功保存 {len(documents)} 条文档到 {filename}")
            return True
            
        except Exception as e:
            logger.error(f"保存Excel文件失败: {str(e)}")
            return False
    
    def append_documents(self, documents: List[PolicyDocument], filename: str) -> bool:
        """追加文档到现有Excel文件"""
        try:
            filepath = Path(config.EXCEL_DIR) / filename
            
            # 检查文件是否存在
            if filepath.exists():
                # 读取现有数据
                existing_df = pd.read_excel(filepath, sheet_name='政策文档')
                
                # 新数据
                new_data = [doc.to_excel_row() for doc in documents]
                new_df = pd.DataFrame(new_data)
                
                # 合并数据
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                # 文件不存在，直接创建
                combined_data = [doc.to_excel_row() for doc in documents]
                combined_df = pd.DataFrame(combined_data)
            
            # 保存合并后的数据
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name='政策文档', index=False)
            
            logger.info(f"成功追加 {len(documents)} 条文档到 {filename}")
            return True
            
        except Exception as e:
            logger.error(f"追加Excel文件失败: {str(e)}")
            return False 