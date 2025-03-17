from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import string
from typing import Optional, List
from loguru import logger
from models import UserCarmine, User
from base.security import AdminContext

router = APIRouter()

# 卡密类型定义
CARMINE_TYPES = {
    "day": {"name": "天卡", "days": 1},
    "week": {"name": "周卡", "days": 7},
    "month": {"name": "月卡", "days": 30},
    "year": {"name": "年卡", "days": 365},
    "forever": {"name": "永久卡", "days": 36500}  # 约100年，视为永久
}

class CarmineResponse(BaseModel):
    id: int
    user_id: Optional[int]
    carmine: str
    duration: int
    created_at: datetime
    activated_at: Optional[datetime]
    expired_at: Optional[datetime]
    type_name: str  # 卡密类型名称（天卡、周卡等）

class CarmineListResponse(BaseModel):
    total: int
    carmines: List[CarmineResponse]

class CarmineActivateRequest(BaseModel):
    carmine: str
    user_id: int

@router.post("/generate")
async def generate_carmines(
    type: str = Query(..., description="卡密类型: day(天卡), week(周卡), month(月卡), year(年卡), forever(永久卡)"),
    count: int = Query(1, description="生成数量，默认为1，最大100"),
    admin: AdminContext = Depends()
):
    """
    生成指定类型和数量的卡密
    """
    if type not in CARMINE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的卡密类型，可选值: {', '.join(CARMINE_TYPES.keys())}")
    
    if count <= 0 or count > 100:
        raise HTTPException(status_code=400, detail="卡密数量必须在1-100之间")
    
    logger.info(f"生成卡密: 类型={type}, 数量={count}")
    
    carmine_type = CARMINE_TYPES[type]
    duration = carmine_type["days"]
    
    generated_carmines = []
    
    for _ in range(count):
        # 生成32位随机卡密
        carmine_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
        
        # 创建卡密记录
        carmine = UserCarmine(
            carmine=carmine_code,
            duration=duration,
        )
        carmine.save()
        
        generated_carmines.append(carmine_code)
    
    logger.info(f"成功生成{count}张{carmine_type['name']}")
    return {
        "message": f"成功生成{count}张{carmine_type['name']}",
        "carmines": generated_carmines
    }

@router.get("/list")
async def list_carmines(
    page: int = 1, 
    page_size: int = 10,
    type: Optional[str] = Query(None, description="卡密类型，不传则获取所有类型"),
    status: Optional[str] = Query(None, description="卡密状态: unused(未使用), used(已使用), expired(已过期), all(全部)"),
    search: Optional[str] = Query(None, description="搜索卡密代码，支持部分匹配"),
    admin: AdminContext = Depends()
):
    """
    获取卡密列表，支持分页、按类型和状态过滤，以及搜索卡密代码
    """
    logger.info(f"获取卡密列表: page={page}, page_size={page_size}, type={type}, status={status}, search={search}")
    
    # 构建查询
    query = UserCarmine.select()
    
    # 按类型过滤
    if type and type in CARMINE_TYPES:
        duration = CARMINE_TYPES[type]["days"]
        query = query.where(UserCarmine.duration == duration)
    
    # 按状态过滤
    now = datetime.now()
    if status == "unused":
        query = query.where(UserCarmine.activated_at.is_null())
    elif status == "used":
        query = query.where(
            (UserCarmine.activated_at.is_null(False)) & 
            ((UserCarmine.expired_at > now) | (UserCarmine.expired_at.is_null()))
        )
    elif status == "expired":
        query = query.where(
            (UserCarmine.activated_at.is_null(False)) & 
            (UserCarmine.expired_at <= now)
        )
    
    # 搜索卡密代码
    if search:
        query = query.where(UserCarmine.carmine.contains(search))
    
    # 计算总数
    total = query.count()
    
    # 获取分页数据，按ID倒序排序
    carmines = query.order_by(UserCarmine.id.desc()).paginate(page, page_size)
    
    # 转换为响应格式
    carmine_list = []
    for carmine in carmines:
        try:
            # 确定卡密类型名称
            type_name = "未知"
            for key, value in CARMINE_TYPES.items():
                if value["days"] == carmine.duration:
                    type_name = value["name"]
                    break
            
            # 安全地获取用户ID
            user_id = None
            if carmine.user:
                try:
                    user_id = carmine.user.id
                except:
                    pass
            
            carmine_response = CarmineResponse(
                id=carmine.id,
                user_id=user_id,
                carmine=carmine.carmine,
                duration=carmine.duration,
                created_at=carmine.created_at,
                activated_at=carmine.activated_at,
                expired_at=carmine.expired_at,
                type_name=type_name
            )
            carmine_list.append(carmine_response)
        except Exception as e:
            logger.error(f"处理卡密数据时出错: {str(e)}, carmine_id={carmine.id}")
            continue
    
    logger.info(f"成功获取卡密列表，总数: {total}")
    return CarmineListResponse(
        total=total,
        carmines=carmine_list
    )

@router.post("/activate")
async def activate_carmine(
    request: CarmineActivateRequest,
    admin: AdminContext = Depends()
):
    """
    激活卡密
    """
    logger.info(f"激活卡密: carmine={request.carmine}, user_id={request.user_id}")
    
    # 查找卡密
    try:
        carmine = UserCarmine.get(UserCarmine.carmine == request.carmine)
    except UserCarmine.DoesNotExist:
        logger.error(f"卡密不存在: {request.carmine}")
        raise HTTPException(status_code=404, detail="卡密不存在")
    
    # 检查卡密是否已激活
    if carmine.activated_at is not None:
        logger.error(f"卡密已被激活: {request.carmine}")
        raise HTTPException(status_code=400, detail="卡密已被激活")
    
    # 查找用户
    try:
        user = User.get_by_id(request.user_id)
    except User.DoesNotExist:
        logger.error(f"用户不存在: {request.user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 激活卡密
    now = datetime.now()
    
    # 如果是永久卡，设置过期日期为2099年12月31日
    if carmine.duration == CARMINE_TYPES["forever"]["days"]:
        expired_at = datetime(2099, 12, 31, 23, 59, 59)
    else:
        expired_at = now + timedelta(days=carmine.duration)
    
    carmine.user = user
    carmine.activated_at = now
    carmine.expired_at = expired_at
    carmine.save()
    
    # 确定卡密类型名称
    type_name = "未知"
    for key, value in CARMINE_TYPES.items():
        if value["days"] == carmine.duration:
            type_name = value["name"]
            break
    
    logger.info(f"卡密激活成功: carmine={request.carmine}, user_id={request.user_id}, type={type_name}")
    return {
        "message": "卡密激活成功",
        "carmine": request.carmine,
        "user_id": request.user_id,
        "type": type_name,
        "expired_at": expired_at
    }

@router.delete("/{carmine_id}")
async def delete_carmine(
    carmine_id: int,
    admin: AdminContext = Depends()
):
    """
    删除卡密
    """
    logger.info(f"删除卡密: id={carmine_id}")
    
    try:
        carmine = UserCarmine.get_by_id(carmine_id)
    except UserCarmine.DoesNotExist:
        logger.error(f"卡密不存在: id={carmine_id}")
        raise HTTPException(status_code=404, detail="卡密不存在")
    
    # 检查卡密是否已激活
    if carmine.activated_at is not None:
        logger.error(f"已激活的卡密不能删除: id={carmine_id}")
        raise HTTPException(status_code=400, detail="已激活的卡密不能删除")
    
    carmine.delete_instance()
    
    logger.info(f"卡密删除成功: id={carmine_id}")
    return {"message": "卡密删除成功"}

@router.get("/check/{carmine_code}")
async def check_carmine(
    carmine_code: str,
    admin: AdminContext = Depends()
):
    """
    检查卡密状态
    """
    logger.info(f"检查卡密状态: carmine={carmine_code}")
    
    try:
        carmine = UserCarmine.get(UserCarmine.carmine == carmine_code)
    except UserCarmine.DoesNotExist:
        logger.error(f"卡密不存在: {carmine_code}")
        raise HTTPException(status_code=404, detail="卡密不存在")
    
    # 确定卡密类型名称
    type_name = "未知"
    for key, value in CARMINE_TYPES.items():
        if value["days"] == carmine.duration:
            type_name = value["name"]
            break
    
    # 确定卡密状态
    status = "未使用"
    if carmine.activated_at:
        if carmine.expired_at and carmine.expired_at <= datetime.now():
            status = "已过期"
        else:
            status = "已使用"
    
    logger.info(f"卡密状态: carmine={carmine_code}, status={status}")
    return {
        "carmine": carmine_code,
        "type": type_name,
        "duration": carmine.duration,
        "status": status,
        "user_id": carmine.user.id if carmine.user else None,
        "activated_at": carmine.activated_at,
        "expired_at": carmine.expired_at
    }
