from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
from base.security import UserContext
from models import Task, VideoGeneration, User
from loguru import logger
from peewee import JOIN, fn, DoesNotExist


class VideoResponse(BaseModel):
    task_id: int
    person_video_id: Optional[int] = None
    product_video_id: Optional[int] = None
    person_image_url: Optional[str] = None
    product_image_url: Optional[str] = None
    person_categories: Optional[str] = None
    product_categories: Optional[str] = None
    person_video_url: Optional[str] = None
    product_video_url: Optional[str] = None
    status: int
    created_at: datetime


class VideoListResponse(BaseModel):
    total: int
    videos: List[VideoResponse]


class DeleteVideoResponse(BaseModel):
    success: bool
    message: str


router = APIRouter()

@router.get("/videos", response_model=VideoListResponse)
async def get_user_videos(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_context: UserContext = Depends()
):
    """
    获取用户的视频列表
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页数量
    """
    try:
        user_id = user_context.user_id
        logger.info(f"查询用户 {user_id} 的视频列表，页码: {page}, 每页数量: {page_size}")
        
        # 计算24小时前的时间
        one_day_ago = datetime.now() - timedelta(days=1)
        
        # 查询所有任务，排除已删除的任务（状态为4）且只查询24小时内的
        tasks = (Task
                .select()
                .where(
                    (Task.user == user_id) & 
                    (Task.status != 4) & 
                    (Task.created_at >= one_day_ago)
                )
                .order_by(Task.created_at.desc())
                .paginate(page, page_size))
        
        # 计算总数，排除已删除的任务且只计算24小时内的
        total = Task.select().where(
            (Task.user == user_id) & 
            (Task.status != 4) & 
            (Task.created_at >= one_day_ago)
        ).count()
        
        # 获取任务ID列表
        task_ids = [task.id for task in tasks]
        
        # 查询每个任务对应的视频生成记录
        videos_by_task: Dict[int, Dict[int, VideoGeneration]] = {}
        if task_ids:
            video_query = (VideoGeneration
                          .select()
                          .where(VideoGeneration.task.in_(task_ids)))
            
            for video in video_query:
                if video.task_id not in videos_by_task:
                    videos_by_task[video.task_id] = {}
                videos_by_task[video.task_id][video.type] = video
        
        # 构建响应
        result = []
        for task in tasks:
            # 获取人物和产品视频（如果存在）
            person_video = videos_by_task.get(task.id, {}).get(0)  # 0-人物
            product_video = videos_by_task.get(task.id, {}).get(1)  # 1-产品
            
            # 创建响应对象
            response = VideoResponse(
                task_id=task.id,
                status=task.status,
                created_at=task.created_at
            )
            
            # 填充人物视频信息（如果存在）
            if person_video:
                response.person_video_id = person_video.id
                response.person_image_url = person_video.image_url
                response.person_categories = person_video.category
                response.person_video_url = person_video.video_url
            
            # 填充产品视频信息（如果存在）
            if product_video:
                response.product_video_id = product_video.id
                response.product_image_url = product_video.image_url
                response.product_categories = product_video.category
                response.product_video_url = product_video.video_url
            
            result.append(response)
        
        return VideoListResponse(
            total=total,
            videos=result
        )
    
    except Exception as e:
        logger.error(f"查询用户视频列表失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="查询视频列表失败")

@router.delete("/videos/{task_id}", response_model=DeleteVideoResponse)
async def delete_video(
    task_id: int,
    user_context: UserContext = Depends()
):
    """
    删除视频
    
    参数:
    - task_id: 任务ID
    """
    try:
        user_id = user_context.user_id
        logger.info(f"删除视频，任务ID: {task_id}, 用户ID: {user_id}")
        
        # 查询任务是否存在且属于当前用户
        try:
            task = Task.get((Task.id == task_id) & (Task.user == user_id))
        except DoesNotExist:
            logger.warning(f"任务不存在或不属于用户，任务ID: {task_id}, 用户ID: {user_id}")
            raise HTTPException(status_code=404, detail="视频不存在或无权删除")
        
        # 将任务状态更新为4（删除状态）
        logger.info(f"将任务状态更新为删除状态，任务ID: {task_id}")
        task.status = 4
        task.save()
        
        return DeleteVideoResponse(
            success=True,
            message="视频删除成功"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除视频失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="删除视频失败")
