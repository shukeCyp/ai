from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dbutils.pooled_db import PooledDB
import os
import mysql.connector
from datetime import datetime, timedelta
from jose import JWTError, jwt


# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # 建议使用环境变量设置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# 提示词配置
PERSONAL_PROMPT = "The person in the picture is attracted by the true surprise and naturally covers their mouth with their hands, opens their eyes wide, and shows a real expression of surprise. It is necessary to strictly ensure that the finger shape is normal and reasonable, and the fingernails are normal red and not too long"

app = FastAPI()

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据库连接池配置
db_pool = PooledDB(
    creator=mysql.connector,
    host=os.getenv("DB_HOST", "rm-f8zh0u32x2cb40fqb3o.mysql.rds.aliyuncs.com"),
    user=os.getenv("DB_USER", "root"), 
    password=os.getenv("DB_PASSWORD", "abc@123456"),
    database=os.getenv("DB_NAME", "ai"),
    port=os.getenv("DB_PORT", 3306),
    autocommit=True,
    maxconnections=10,
    mincached=2,
)
