from base import config, init_db
from models import db
from loguru import logger
import uuid
import hashlib
import time
from fastapi import Request
from base.security import parse_user_id, create_user_token
from fastapi.responses import HTMLResponse
from routers.admin.runway_account import router as runway_account_router
from routers.admin.user import router as admin_user_router
from routers.admin.carmine import router as carmine_router
from routers.user import router as user_router
from routers.generate_video import router as generate_video_router
from routers.video import router as video_router
from utils.account_pool import account_pool
from routers.prompt import router as prompt_router
from routers.admin.dashbroad import router as dashbroad_router
from routers.ai_video import router as ai_video_router


app = config.app

# 修改日志格式，使用更简单的格式
logger.add(
    "logs/all.log",
    rotation="1 day",
    retention="10 days",  # 保留 10 天的日志
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} {level} [{module}.{function}:{line}] {message}",
    compression="zip",
    colorize=False,
)

# 初始化数据库
init_db.init_database()


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    db.is_connection_usable()    # TODO 该方法会检查数据库连接是否可用，如果不可用会重新建立连接，可以避免
    ip_address = request.headers.get("X-Forwarded-For", request.client.host)
    uuid_str = str(uuid.uuid4())
    authorization = request.headers.get("Authorization", None)
    
    token = authorization.split(" ")[1] if authorization else None
    uid = parse_user_id(token)
    request_id = hashlib.sha1(uuid_str.encode()).hexdigest()[:10]

    request_path = request.url.path

    with logger.contextualize(request_id=request_id, ip_address=ip_address, request_path=request_path, uid=uid):
        start_time = time.time()
        logger.info(f"BEGIN: {request.method} {request.url} [IP: {ip_address}, UID: {uid}, ReqID: {request_id}, Path: {request_path}]")
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"ENDED: {request.method} {request.url}, elapsed time: {elapsed_time} seconds [IP: {ip_address}, UID: {uid}, ReqID: {request_id}]")

app.include_router(runway_account_router, prefix="/admin/runway_account", tags=["Runway账号管理"])
app.include_router(admin_user_router, prefix="/admin", tags=["管理员账号管理"])
app.include_router(carmine_router, prefix="/admin/carmine", tags=["卡密管理"])
app.include_router(user_router, prefix="/user", tags=["用户管理"])
app.include_router(generate_video_router, prefix="/generate_video", tags=["视频生成"])
app.include_router(video_router, prefix="/user/video", tags=["用户视频"])
app.include_router(prompt_router, prefix="/prompt", tags=["提示词管理"])
app.include_router(dashbroad_router, prefix="/admin/dashbroad", tags=["仪表盘"])
app.include_router(ai_video_router, prefix="/ai_video", tags=["AI视频生成"])
account_pool.initialize()

@app.get("/token")
async def token():
    return create_user_token(1)


@app.get("/", include_in_schema=False)
async def custom_docs():
    return HTMLResponse("""
      <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <meta charset="utf-8">
        <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
    </head>
    <body>
        <elements-api
            apiDescriptionUrl="/openapi.json"
            router="hash"
            layout="sidebar"
        />
    </body>
    </html>
    """)