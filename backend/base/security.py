from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from pydantic import BaseModel
from .config import db_pool, SECRET_KEY, ALGORITHM
from models import User, Admin
import logging as logger # 该模块中的logger格式化输出不支持extra参数，故改用logging模块
import time
import base64
from models import ExceptionRequest
import json
            

class RequestCredentials:
    """包装认证凭据和请求对象的类"""
    def __init__(self, credentials: HTTPAuthorizationCredentials, request: Request):
        self.credentials = credentials
        self.request = request

class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> RequestCredentials:
        # 调用父类方法获取认证凭据
        credentials = await super().__call__(request)
        # 返回包装了凭据和请求的对象
        return RequestCredentials(credentials, request)

oauth2_scheme = CustomHTTPBearer()

# 定义通用的认证异常
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="登录失效",
    headers={"WWW-Authenticate": "Bearer"},
)

class UserContext:
    user_id: int
    user: User
    def __init__(self, auth: RequestCredentials = Depends(oauth2_scheme)):
        logger.info(f"解析认证信息: auth={auth.credentials}")
        token = auth.credentials.credentials
        request = auth.request
        

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            logger.debug(f"Token解析结果: payload={payload}")
        except jwt.PyJWTError as e:
            logger.error(f"Token解析失败: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
            
        user_id = payload.get("sub")
        if user_id is None:
            logger.error("Token中缺少user_id")
            raise credentials_exception
        
        self.user_id = int(user_id)
        try:
            self.user = User.get_by_id(int(user_id))
        except User.DoesNotExist:
            logger.error(f"用户不存在: user_id={user_id}")
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # # 获取请求头中的MAC地址
        # client_mac = request.headers.get("Mac")
        # if not client_mac:
        #     logger.error(f"请求头中缺少MAC地址: user_id={self.user_id}")
        #     raise HTTPException(status_code=400, detail="设备未授权")
        
        # # 验证MAC地址
        # if client_mac != self.user.mac:
        #     logger.error(f"MAC地址不匹配: user_id={self.user_id}, expected={self.user.mac}, actual={client_mac}")
        #     raise HTTPException(status_code=403, detail="设备未授权")
            
        # logger.info(f"当前用户上下文: user_id={self.user_id}, mac={client_mac}")
                # 蜜罐检查
        # try:
        #     # 获取请求头
        #     request_time = request.headers.get('X-Request-Time')
        #     track_id = request.headers.get('X-Track-ID')
            
        #     logger.info(f"蜜罐检查开始: request_time={request_time}, track_id={track_id}")
            
        #     # 检查必要的请求头是否存在
        #     if not request_time or not track_id:
        #         logger.warning(f"蜜罐检查失败: request_time={request_time}, track_id={track_id}")
        #         self._log_suspicious_request_sync(request, "蜜罐检查失败：缺少必要的请求头", self.user_id)
        #         # 不应该返回，正常往下执行
            
        #     # 蜜罐检查 1：检查可疑请求头
        #     suspicious_headers = [
        #         'x-real-ip',
        #         'x-forwarded-for',
        #         'x-original-url',
        #         'x-rewrite-url'
        #     ]
            
        #     for header in suspicious_headers:
        #         if header in request.headers:
        #             logger.warning(f"检测到可疑请求头: {header}={request.headers.get(header)}")
        #             # 记录可疑请求到数据库
        #             self._log_suspicious_request_sync(request, "可疑请求头", self.user_id)
        #             # 不应该返回，正常往下执行
            
        #     # 蜜罐检查 2：验证时间戳合法性
        #     if request_time:
        #         current_time = int(time.time() * 1000)
        #         request_time = int(request_time)
        #         time_diff = abs(current_time - request_time)
        #         logger.info(f"时间戳检查: current_time={current_time}, request_time={request_time}, diff={time_diff}ms")
        #         if time_diff > 30000:  # 30秒时间窗口
        #             logger.warning(f"时间戳不合法: 差值={time_diff}ms, 超过30秒限制")
        #             self._log_suspicious_request_sync(request, "时间戳不合法", self.user_id)
        #             # 不应该返回，正常往下执行
            
        #     # 蜜罐检查 3：验证 track_id 格式
        #     if track_id and request_time:
        #         try:
        #             decoded_track = base64.b64decode(track_id).decode()
        #             track_timestamp = int(decoded_track.split('_')[0])
        #             logger.info(f"track_id检查: decoded={decoded_track}, timestamp={track_timestamp}")
        #             if track_timestamp != request_time:
        #                 logger.warning(f"track_id不匹配: track_timestamp={track_timestamp}, request_time={request_time}")
        #                 self._log_suspicious_request_sync(request, "track_id不匹配", self.user_id)
        #                 # 不应该返回，正常往下执行
        #         except Exception as decode_err:
        #             logger.warning(f"track_id格式错误: {str(decode_err)}")
        #             self._log_suspicious_request_sync(request, "track_id格式错误", self.user_id)
        #             # 不应该返回，正常往下执行
            
        #     logger.info("蜜罐检查完成")
        # except Exception as e:
        #     logger.error(f"蜜罐检查异常: {str(e)}")
    
    def _log_suspicious_request_sync(self, request: Request, error_message: str, user_id: int):
        """同步方式记录可疑请求到数据库"""
        try:
            logger.info(f"开始记录可疑请求: error_message={error_message}")
            
            # 获取请求信息
            url = str(request.url)
            method = request.method
            logger.debug(f"请求信息: url={url}, method={method}")
            
            # 尝试获取请求参数
            params = {}
            for key, value in request.query_params.items():
                params[key] = value
            logger.debug(f"请求参数: params={params}")
            
            # 获取IP地址
            ip_address = request.headers.get("X-Forwarded-For", request.client.host)
            logger.debug(f"IP地址: ip_address={ip_address}")
            
            # 创建异常请求记录
            record = ExceptionRequest.create(
                user_id=user_id,
                ip_address=ip_address,
                request_url=url,
                request_method=method,
                request_params=json.dumps(params) if params else None,
                request_body="无法在同步方法中获取请求体",
                error_message=error_message,
                stack_trace=None,
                http_status=403
            )
            logger.info(f"异常请求记录已创建: record_id={record.id}")
            
            logger.warning(f"记录可疑请求: IP={ip_address}, URL={url}, 错误={error_message}, 用户ID={user_id}")
        except Exception as e:
            logger.error(f"记录可疑请求失败: {str(e)}")
            logger.exception("记录可疑请求异常详情")

class AdminContext:
    user_id: int
    admin: Admin

    def __init__(self, auth: RequestCredentials = Depends(oauth2_scheme)):
        logger.info(f"解析管理员认证信息: auth={auth.credentials}")
        token = auth.credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            logger.debug(f"Token解析结果: payload={payload}")
        except jwt.PyJWTError as e:
            logger.error(f"Token解析失败: {str(e)}")
            raise credentials_exception
            
        user_id = payload.get("sub")
        if user_id is None:
            logger.error("Token中缺少user_id")
            raise credentials_exception
        
        self.user_id = int(user_id)
        try:
            self.admin = Admin.get_by_id(int(user_id))
        except Admin.DoesNotExist:
            logger.error(f"用户不是管理员: user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
            
        logger.info(f"当前管理员上下文: user_id={self.user_id}, admin_id={self.admin.id}")
    
def parse_user_id(token: str) -> int | None:
    """解析用户信息"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except jwt.PyJWTError:
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_user_token(user_id: int, expires_delta_minutes: int = 60*24*365*10) -> str:
    logger.info(f"生成用户Token: user_id={user_id}, expires_delta_minutes={expires_delta_minutes}")
    access_token_expires = timedelta(minutes=expires_delta_minutes)
    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=access_token_expires
    )
    return access_token
