import os
from pathlib import Path
from .config import db_pool
from loguru import logger

def init_database():
    """初始化数据库，创建必要的表结构"""
    conn = db_pool.connection()
    cursor = conn.cursor()
    try:
        # 读取schema.sql文件
        schema_path = Path(__file__).parent.parent / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # 按语句分割并执行SQL
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        logger.info('数据库表初始化完成')
    except Exception as e:
        logger.error(f'数据库初始化失败: {str(e)}')
        raise e
    finally:
        cursor.close()
        conn.close()