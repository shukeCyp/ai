from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from loguru import logger
from models import RunwayAccount, RunwaySession
import requests
from typing import Optional, List
import datetime as dt
from base.security import AdminContext

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str
    machineId: Optional[str] = None

class LoginResponse(BaseModel):
    token: str

class UserProfile(BaseModel):
    id: int
    createdAt: datetime
    updatedAt: datetime
    planExpires: datetime

class Session(BaseModel):
    id: str
    name: str
    createdAt: datetime
    updatedAt: datetime

class RunwayAccountResponse(BaseModel):
    id: int
    username: str
    password: str
    as_team_id: str
    plan_expires: datetime
    created_at: datetime
    updated_at: datetime

class RunwayAccountListResponse(BaseModel):
    total: int
    accounts: List[RunwayAccountResponse]

class RunwaySessionResponse(BaseModel):
    id: int
    runway_id: int
    session_id: str
    created_at: datetime

class RunwaySessionListResponse(BaseModel):
    total: int
    sessions: List[RunwaySessionResponse]

@router.post("/account/add")
async def add_runway_account(
    username: str, 
    password: str,
    admin: AdminContext = Depends()
):
    """
    添加Runway账号
    """
    logger.info(f"添加Runway账号: username={username}")
    
    # 登录获取token
    token = runway_login(username, password)
    
    # 获取用户信息
    user_info = get_runway_user_info(token)
    
    # 创建账号记录
    account = RunwayAccount(
        username=username,
        password=password,
        as_team_id=user_info.id,
        token=token,
        plan_expires=user_info.planExpires
    )
    
    # 保存到数据库
    account.save()
    
    logger.info(f"Runway账号添加成功: {account}")
    return {"message": "Runway账号添加成功"}

@router.get("/account/list")
async def list_runway_accounts(
    page: int = 1, 
    page_size: int = 10,
    admin: AdminContext = Depends()
):
    """
    获取Runway账号列表，支持分页
    """
    logger.info(f"获取Runway账号列表: page={page}, page_size={page_size}")
    
    # 计算总数
    total = RunwayAccount.select().count()
    
    # 获取分页数据
    accounts = RunwayAccount.select().order_by(RunwayAccount.created_at.desc()).paginate(page, page_size)
    
    # 转换为响应格式
    account_list = []
    for account in accounts:
        account_list.append(RunwayAccountResponse(
            id=account.id,
            username=account.username,
            password=account.password,
            as_team_id=account.as_team_id,
            plan_expires=account.plan_expires,
            created_at=account.created_at,
            updated_at=account.updated_at
        ))
    
    logger.info(f"成功获取Runway账号列表，总数: {total}")
    return RunwayAccountListResponse(
        total=total,
        accounts=account_list
    )

@router.post("/session/create")
async def create_session(
    runway_id: int,
    admin: AdminContext = Depends()
):
    """
    为指定的Runway账号创建一个新会话
    """
    logger.info(f"为Runway账号创建会话: runway_id={runway_id}")
    
    # 获取账号信息
    try:
        account = RunwayAccount.get_by_id(runway_id)
    except Exception as e:
        logger.error(f"获取Runway账号失败: {str(e)}")
        raise Exception(f"获取Runway账号失败: {str(e)}")
    
    # 创建会话
    session_id = create_runway_session(account.token, account.as_team_id)
    
    # 保存会话记录
    session = RunwaySession(
        runway_id=runway_id,
        session_id=session_id
    )
    session.save()
    
    logger.info(f"Runway会话创建成功: runway_id={runway_id}, session_id={session_id}")
    return {"message": "会话创建成功", "session_id": session_id}

@router.get("/session/list")
async def list_runway_sessions(
    page: int = 1, 
    page_size: int = 10, 
    runway_id: Optional[int] = Query(None, description="Runway账号ID，不传则获取所有会话"),
    admin: AdminContext = Depends()
):
    """
    获取Runway会话列表，支持分页和按账号ID过滤
    """
    logger.info(f"获取Runway会话列表: page={page}, page_size={page_size}, runway_id={runway_id}")
    
    # 构建查询
    query = RunwaySession.select()
    
    # 如果指定了runway_id，则按账号过滤
    if runway_id is not None:
        query = query.where(RunwaySession.runway_id == runway_id)
    
    # 计算总数
    total = query.count()
    
    # 获取分页数据
    sessions = query.order_by(RunwaySession.created_at.desc()).paginate(page, page_size)
    
    # 转换为响应格式
    session_list = []
    for session in sessions:
        session_list.append(RunwaySessionResponse(
            id=session.id,
            runway_id=session.runway_id,
            session_id=session.session_id,
            created_at=session.created_at
        ))
    
    logger.info(f"成功获取Runway会话列表，总数: {total}")
    return RunwaySessionListResponse(
        total=total,
        sessions=session_list
    )

def runway_login(username: str, password: str) -> str:
    """
    调用 Runway API 进行登录并获取 token
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        str: JWT token
        
    Raises:
        Exception: 当登录失败时抛出异常
    """
    url = "https://api.runwayml.com/v1/login"
    
    logger.info(f"尝试登录Runway账号: username={username}")
    
    payload = LoginRequest(
        username=username,
        password=password,
        machineId=None
    )
    
    try:
        logger.debug(f"发送登录请求到: {url}")
        response = requests.post(url, json=payload.dict())
        logger.info(f"登录响应: {response.json()}")
        response.raise_for_status()  # 处理其他非200状态码
        
        login_response = LoginResponse(**response.json())
        logger.info(f"Runway账号 {username} 登录成功")
        return login_response.token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"登录请求失败: {str(e)}")
        raise Exception(f"登录请求失败: {str(e)}")
    except Exception as e:
        logger.error(f"处理登录响应时出错: {str(e)}")
        raise Exception(f"处理登录响应时出错: {str(e)}")


def get_runway_user_info(token: str) -> UserProfile:
    """
    获取Runway用户资料信息
    
    Args:
        token: JWT token
        
    Returns:
        UserProfile: 包含用户ID和时间信息的对象
        
    Raises:
        Exception: 当请求失败时抛出异常
    """
    url = "https://api.runwayml.com/v1/profile"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    logger.info("获取Runway用户资料信息")
    
    try:
        logger.debug(f"发送获取用户资料请求到: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        user_data = data["user"]
        
        logger.info("成功获取Runway用户资料")
        return UserProfile(
            id=user_data["id"],
            createdAt=user_data["createdAt"],
            updatedAt=user_data["updatedAt"],
            planExpires=user_data["planExpires"]
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        raise Exception(f"获取用户资料失败: {str(e)}")
    except Exception as e:
        logger.error(f"处理用户资料响应时出错: {str(e)}")
        raise Exception(f"处理用户资料响应时出错: {str(e)}")


def create_runway_session(token: str, team_id: str) -> str:
    """
    创建新的Runway会话
    
    Args:
        token: JWT token
        team_id: 团队ID
        
    Returns:
        str: 会话ID
        
    Raises:
        Exception: 当创建会话失败时抛出异常
    """
    url = "https://api.runwayml.com/v1/sessions"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "asTeamId": team_id,
        "taskIds": []
    }
    
    logger.info(f"尝试创建Runway会话，团队ID: {team_id}")
    
    try:
        logger.debug(f"发送创建会话请求到: {url}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        session_data = data["session"]
        
        logger.info(f"成功创建Runway会话，会话ID: {session_data['id']}")
        
        session = Session(
            id=session_data["id"],
            name=session_data["name"],
            createdAt=session_data["createdAt"],
            updatedAt=session_data["updatedAt"]
        )
        return session.id
        
    except requests.exceptions.RequestException as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise Exception(f"创建会话失败: {str(e)}")
    except Exception as e:
        logger.error(f"处理会话响应时出错: {str(e)}")
        raise Exception(f"处理会话响应时出错: {str(e)}")
