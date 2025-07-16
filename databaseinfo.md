# 数据库信息记录

## 数据库配置

### SQLite数据库
- **文件路径**: `data/crawler_progress.db`
- **用途**: 存储爬取进度和文档缓存数据
- **创建时间**: 2024-12-15

## 数据表结构

### 1. policy_documents (政策文档表)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 主键，自增 | PRIMARY KEY |
| doc_id | TEXT | 文档唯一标识 | UNIQUE |
| policy_title | TEXT | 政策标题 | |
| content | TEXT | 正文内容 | |
| publish_date | TEXT | 发布时间 | |
| publish_agency | TEXT | 发布机构 | |
| document_type | TEXT | 文件类型 | |
| document_number | TEXT | 文件编号 | |
| policy_level | TEXT | 政策级别(中央/省级/市级) | |
| province | TEXT | 省份 | |
| keywords | TEXT | 关键词(JSON格式) | |
| source_url | TEXT | 原文链接 | |
| crawl_date | TEXT | 抓取时间 | |
| file_format | TEXT | 文档格式 | |
| policy_status | TEXT | 政策状态 | |
| page_number | INTEGER | 页面编号 | |
| session_id | TEXT | 会话ID | |
| is_processed | BOOLEAN | 是否已处理 | DEFAULT 0 |
| created_at | TIMESTAMP | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

### 2. crawler_progress (爬虫进度表)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 主键，自增 | PRIMARY KEY |
| crawler_name | TEXT | 爬虫名称 | UNIQUE |
| progress_data | TEXT | 进度数据(JSON格式) | |
| last_update | TIMESTAMP | 最后更新时间 | DEFAULT CURRENT_TIMESTAMP |

## 数据操作记录

### 2024-12-15
- 创建初始数据库结构
- 添加政策文档表和爬虫进度表
- 实现断点续传功能的数据支持

## 备份策略

- 每日自动备份数据库文件
- 备份文件命名格式: `crawler_progress_YYYYMMDD.db`
- 保留最近30天的备份文件

## 注意事项

1. 数据库文件较小，主要用于进度控制和临时缓存
2. 主要数据存储在Excel文件中
3. 定期清理已处理的临时数据，避免数据库文件过大
4. 文档ID使用源网站的唯一标识，避免重复抓取 