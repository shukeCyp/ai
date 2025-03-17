from fastapi import APIRouter, Query, Depends, HTTPException, Path
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from loguru import logger
from models import Admin, User
from models import UserCarmine as Carmine
from base.security import create_user_token, AdminContext, parse_user_id
from peewee import fn, JOIN, SQL

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    username: str
    mac_address: Optional[str] = None
    created_at: datetime
    expired_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]

class UserDetailResponse(BaseModel):
    id: int
    username: str
    mac_address: Optional[str] = None
    created_at: datetime
    carmine: Optional[dict] = None
    
    class Config:
        orm_mode = True

@router.post("/user/login")
async def login(username: str, password: str):
    """
    管理员登录
    """
    admin = Admin.get_or_none(Admin.username == username, Admin.password == password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_user_token(admin.id)
    return {"token": token}

@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词，可搜索用户名"),
    current_user: AdminContext = Depends()
):
    """
    获取用户列表
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页数量
    - keyword: 搜索关键词，可搜索用户名
    """
    try:
        # 检查当前用户是否为管理员
        admin = Admin.get_or_none(Admin.id == current_user.user_id)
        if not admin:
            raise HTTPException(status_code=403, detail="只有管理员才能访问此接口")
            
        logger.info(f"获取用户列表，页码: {page}, 每页数量: {page_size}, 关键词: {keyword}")
        
        # 构建查询，左连接卡密表以获取到期时间
        query = (User
                .select(User, Carmine.expired_at)
                .left_outer_join(Carmine, on=(User.id == Carmine.user))
                .order_by(User.id.desc()))
        
        # 如果有关键词，添加搜索条件
        if keyword:
            keyword = f"%{keyword}%"
            query = query.where(
                (fn.LOWER(User.username).contains(keyword.lower()))
            )
        
        # 获取总数
        total = User.select().count()
        if keyword:
            total = User.select().where(
                (fn.LOWER(User.username).contains(keyword.lower()))
            ).count()
        
        # 分页
        users_with_expires = query.paginate(page, page_size)
        
        # 转换为响应模型
        user_list = []
        for user_data in users_with_expires:
            user_list.append(
                UserResponse(
                    id=user_data.id,
                    username=user_data.username,
                    mac_address=user_data.mac if hasattr(user_data, 'mac') else None,
                    created_at=user_data.created_at,
                    expired_at=user_data.carmine.expired_at if hasattr(user_data, 'carmine') and user_data.carmine else None
                )
            )
        
        return UserListResponse(
            total=total,
            users=user_list
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="获取用户列表失败")

@router.get("/user/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: int = Path(..., description="用户ID"),
    current_user: AdminContext = Depends()
):
    """
    获取用户详细信息
    
    参数:
    - user_id: 用户ID
    """
    try:
        # 检查当前用户是否为管理员
        admin = Admin.get_or_none(Admin.id == current_user.user_id)
        if not admin:
            raise HTTPException(status_code=403, detail="只有管理员才能访问此接口")
            
        logger.info(f"获取用户详细信息，用户ID: {user_id}")
        
        # 获取用户信息
        user = User.get_or_none(User.id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取用户关联的卡密信息
        carmine = Carmine.get_or_none(Carmine.user == user_id)
        carmine_data = None
        
        if carmine:
            carmine_data = {
                "id": carmine.id,
                "code": carmine.code,
                "expired_at": carmine.expired_at,
                "created_at": carmine.created_at,
                "status": carmine.status
            }
        
        # 构建响应
        return UserDetailResponse(
            id=user.id,
            username=user.username,
            mac_address=user.mac if hasattr(user, 'mac') else None,
            created_at=user.created_at,
            carmine=carmine_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户详细信息失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="获取用户详细信息失败")
