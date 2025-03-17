from fastapi import APIRouter, HTTPException
from loguru import logger
from models import Task, User, VideoGeneration, RunwayAccount
from typing import Dict, Any, List
from datetime import datetime, timedelta
from utils.account_pool import account_pool
from peewee import fn, JOIN
from utils.thread_pool import global_thread_pool

router = APIRouter()


class DashboardStats:
    """仪表盘统计数据类"""
    
    @staticmethod
    def get_date_range(days_ago: int = 0) -> tuple:
        """
        获取指定天数前的日期范围（0点到24点）
        
        参数:
        - days_ago: 天数，0表示今天，1表示昨天，以此类推
        
        返回:
        - (开始时间, 结束时间) 元组
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=days_ago)
        end_date = start_date + timedelta(days=1)
        return start_date, end_date
    
    @staticmethod
    def get_user_stats() -> Dict[str, int]:
        """
        获取用户统计数据
        
        返回:
        - 包含总用户数、今日注册用户数和昨日注册用户数的字典
        """
        try:
            # 获取总用户数
            total_users = User.select().count()
            
            # 获取今日注册用户数
            today_start, today_end = DashboardStats.get_date_range(0)
            today_users = User.select().where(
                (User.created_at >= today_start) & 
                (User.created_at < today_end)
            ).count()
            
            # 获取昨日注册用户数
            yesterday_start, yesterday_end = DashboardStats.get_date_range(1)
            yesterday_users = User.select().where(
                (User.created_at >= yesterday_start) & 
                (User.created_at < yesterday_end)
            ).count()
            
            return {
                "total": total_users,
                "today": today_users,
                "yesterday": yesterday_users
            }
        except Exception as e:
            logger.error(f"获取用户统计数据失败: {str(e)}")
            logger.exception("详细错误")
            return {
                "total": 0,
                "today": 0,
                "yesterday": 0
            }
    
    @staticmethod
    def get_task_stats() -> Dict[str, int]:
        """
        获取任务统计数据
        
        返回:
        - 包含总任务数、今日任务数和昨日任务数的字典
        """
        try:
            # 获取总任务数
            total_tasks = Task.select().count()
            
            # 获取今日任务数
            today_start, today_end = DashboardStats.get_date_range(0)
            today_tasks = Task.select().where(
                (Task.created_at >= today_start) & 
                (Task.created_at < today_end)
            ).count()
            
            # 获取昨日任务数
            yesterday_start, yesterday_end = DashboardStats.get_date_range(1)
            yesterday_tasks = Task.select().where(
                (Task.created_at >= yesterday_start) & 
                (Task.created_at < yesterday_end)
            ).count()
            
            return {
                "total": total_tasks,
                "today": today_tasks,
                "yesterday": yesterday_tasks
            }
        except Exception as e:
            logger.error(f"获取任务统计数据失败: {str(e)}")
            logger.exception("详细错误")
            return {
                "total": 0,
                "today": 0,
                "yesterday": 0
            }
    
    @staticmethod
    def get_video_stats() -> Dict[str, int]:
        """
        获取视频统计数据
        
        返回:
        - 包含总视频数、今日视频数和昨日视频数的字典
        """
        try:
            # 获取总视频数
            total_videos = VideoGeneration.select().count()
            
            # 获取今日视频数
            today_start, today_end = DashboardStats.get_date_range(0)
            today_videos = VideoGeneration.select().where(
                (VideoGeneration.created_at >= today_start) & 
                (VideoGeneration.created_at < today_end)
            ).count()
            
            # 获取昨日视频数
            yesterday_start, yesterday_end = DashboardStats.get_date_range(1)
            yesterday_videos = VideoGeneration.select().where(
                (VideoGeneration.created_at >= yesterday_start) & 
                (VideoGeneration.created_at < yesterday_end)
            ).count()
            
            return {
                "total": total_videos,
                "today": today_videos,
                "yesterday": yesterday_videos
            }
        except Exception as e:
            logger.error(f"获取视频统计数据失败: {str(e)}")
            logger.exception("详细错误")
            return {
                "total": 0,
                "today": 0,
                "yesterday": 0
            }
    
    @staticmethod
    def get_account_stats() -> Dict[str, Any]:
        """
        获取账号统计数据
        
        返回:
        - 包含账号总数和账号池状态的字典
        """
        try:
            # 获取账号总数
            total_accounts = RunwayAccount.select().count()
            
            # 获取账号池状态
            pool_stats = account_pool.get_stats()
            
            return {
                "total": total_accounts,
                "pool": pool_stats
            }
        except Exception as e:
            logger.error(f"获取账号统计数据失败: {str(e)}")
            logger.exception("详细错误")
            return {
                "total": 0,
                "pool": {
                    "available_instances": 0,
                    "in_use_instances": 0,
                    "total_instances": 0
                }
            }
    
    @staticmethod
    def get_thread_pool_stats() -> Dict[str, Any]:
        """
        获取线程池统计数据
        
        返回:
        - 包含线程池状态的字典
        """
        try:
            return {
                "queue_size": global_thread_pool.get_queue_size(),
                "active_workers": global_thread_pool.get_active_workers(),
                "max_workers": global_thread_pool.max_workers,
                "running": global_thread_pool.running
            }
        except Exception as e:
            logger.error(f"获取线程池统计数据失败: {str(e)}")
            logger.exception("详细错误")
            return {
                "queue_size": 0,
                "active_workers": 0,
                "max_workers": 0,
                "running": False
            }
    
    @staticmethod
    def get_task_status_stats() -> Dict[str, int]:
        """
        获取任务状态统计数据
        
        返回:
        - 包含各状态任务数量的字典
        """
        try:
            # 获取各状态任务数量
            status_counts = (Task
                            .select(Task.status, fn.COUNT(Task.id).alias('count'))
                            .group_by(Task.status)
                            .dicts())
            
            result = {
                "queued": 0,  # 0-排队中
                "processing": 0,  # 1-生成中
                "completed": 0,  # 2-完成
                "failed": 0  # 3-失败
            }
            
            for item in status_counts:
                if item['status'] == 0:
                    result['queued'] = item['count']
                elif item['status'] == 1:
                    result['processing'] = item['count']
                elif item['status'] == 2:
                    result['completed'] = item['count']
                elif item['status'] == 3:
                    result['failed'] = item['count']
                elif item['status'] == 4:
                    result['deleted'] = item['count']
            
            return result
        except Exception as e:
            logger.error(f"获取任务状态统计数据失败: {str(e)}")
            logger.exception("详细错误")
            return {
                "queued": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0
            }
    
    @staticmethod
    def get_runway_account_stats() -> List[Dict[str, Any]]:
        """
        获取Runway账号使用统计数据
        
        返回:
        - 包含每个账号ID、用户名、总生成数、今日生成数和昨日生成数的列表
        """
        try:
            # 获取所有Runway账号
            accounts = RunwayAccount.select().dicts()
            
            # 获取日期范围
            today_start, today_end = DashboardStats.get_date_range(0)
            yesterday_start, yesterday_end = DashboardStats.get_date_range(1)
            
            # 获取每个账号的视频生成数量
            result = []
            
            for account in accounts:
                account_id = account['id']
                
                # 获取总生成数
                total_count = VideoGeneration.select().where(
                    VideoGeneration.runway_id == account_id
                ).count()
                
                # 获取今日生成数
                today_count = VideoGeneration.select().where(
                    (VideoGeneration.runway_id == account_id) &
                    (VideoGeneration.created_at >= today_start) &
                    (VideoGeneration.created_at < today_end)
                ).count()
                
                # 获取昨日生成数
                yesterday_count = VideoGeneration.select().where(
                    (VideoGeneration.runway_id == account_id) &
                    (VideoGeneration.created_at >= yesterday_start) &
                    (VideoGeneration.created_at < yesterday_end)
                ).count()
                
                # 构建账号统计数据
                account_stats = {
                    "id": account_id,
                    "username": account['username'],
                    "plan_expires": account['plan_expires'],
                    "total_videos": total_count,
                    "today_videos": today_count,
                    "yesterday_videos": yesterday_count
                }
                
                result.append(account_stats)
            
            # 按总生成数降序排序
            result.sort(key=lambda x: x['total_videos'], reverse=True)
            
            return result
        except Exception as e:
            logger.error(f"获取Runway账号统计数据失败: {str(e)}")
            logger.exception("详细错误")
            return []


@router.get("/dashboard")
async def get_dashboard_data():
    """
    获取仪表盘数据
    
    返回:
    - 包含用户、任务、视频和账号统计数据的字典
    """
    try:
        logger.info("获取仪表盘数据")
        
        return {
            "users": DashboardStats.get_user_stats(),
            "tasks": DashboardStats.get_task_stats(),
            "videos": DashboardStats.get_video_stats(),
            "accounts": DashboardStats.get_account_stats(),
            "task_status": DashboardStats.get_task_status_stats(),
            "thread_pool": DashboardStats.get_thread_pool_stats()
        }
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="获取仪表盘数据失败")


@router.get("/runway_dashboard")
async def get_runway_dashboard_data():
    """
    获取Runway账号仪表盘数据
    
    返回:
    - 包含所有Runway账号使用统计的列表
    """
    try:
        logger.info("获取Runway账号仪表盘数据")
        
        return {
            "accounts": DashboardStats.get_runway_account_stats()
        }
    except Exception as e:
        logger.error(f"获取Runway账号仪表盘数据失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="获取Runway账号仪表盘数据失败")


@router.get("/runway_account_stats/{account_id}")
async def get_runway_account_detail(account_id: int):
    """
    获取指定Runway账号的详细统计数据
    
    参数:
    - account_id: Runway账号ID
    
    返回:
    - 包含账号详情和使用统计的字典
    """
    try:
        logger.info(f"获取Runway账号 {account_id} 的详细统计数据")
        
        # 获取账号信息
        account = RunwayAccount.get_or_none(RunwayAccount.id == account_id)
        if not account:
            raise HTTPException(status_code=404, detail=f"账号 {account_id} 不存在")
        
        # 获取日期范围
        today_start, today_end = DashboardStats.get_date_range(0)
        yesterday_start, yesterday_end = DashboardStats.get_date_range(1)
        
        # 获取总生成数
        total_count = VideoGeneration.select().where(
            VideoGeneration.runway_id == account_id
        ).count()
        
        # 获取今日生成数
        today_count = VideoGeneration.select().where(
            (VideoGeneration.runway_id == account_id) &
            (VideoGeneration.created_at >= today_start) &
            (VideoGeneration.created_at < today_end)
        ).count()
        
        # 获取昨日生成数
        yesterday_count = VideoGeneration.select().where(
            (VideoGeneration.runway_id == account_id) &
            (VideoGeneration.created_at >= yesterday_start) &
            (VideoGeneration.created_at < yesterday_end)
        ).count()
        
        # 获取最近10个视频生成记录
        recent_videos = (VideoGeneration
                        .select(VideoGeneration, Task)
                        .join(Task, on=(VideoGeneration.task == Task.id))
                        .where(VideoGeneration.runway_id == account_id)
                        .order_by(VideoGeneration.created_at.desc())
                        .limit(10)
                        .dicts())
        
        # 获取每日生成数量统计（最近7天）
        daily_stats = []
        for i in range(6, -1, -1):
            day_start, day_end = DashboardStats.get_date_range(i)
            day_count = VideoGeneration.select().where(
                (VideoGeneration.runway_id == account_id) &
                (VideoGeneration.created_at >= day_start) &
                (VideoGeneration.created_at < day_end)
            ).count()
            
            daily_stats.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": day_count
            })
        
        return {
            "account": {
                "id": account.id,
                "username": account.username,
                "plan_expires": account.plan_expires,
                "created_at": account.created_at
            },
            "stats": {
                "total_videos": total_count,
                "today_videos": today_count,
                "yesterday_videos": yesterday_count,
                "daily_stats": daily_stats
            },
            "recent_videos": list(recent_videos)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Runway账号详细统计数据失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="获取Runway账号详细统计数据失败")


@router.post("/cleanup_stalled_tasks")
async def cleanup_stalled_tasks():
    """
    清理卡住的任务
    
    查询Task表，如果status==1（生成中），并且创建时间大于1小时的，把status修改为3（失败）
    
    返回:
    - 包含清理任务数量的字典
    """
    try:
        logger.info("开始清理卡住的任务")
        
        # 计算一小时前的时间点
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        # 查询所有状态为1且创建时间超过1小时的任务
        stalled_tasks = Task.select().where(
            (Task.status == 1) & 
            (Task.created_at < one_hour_ago)
        )
        
        # 获取符合条件的任务数量
        count = stalled_tasks.count()
        
        if count > 0:
            # 更新这些任务的状态为3（失败）
            Task.update(status=3).where(
                (Task.status == 1) & 
                (Task.created_at < one_hour_ago)
            ).execute()
            
            logger.info(f"成功清理 {count} 个卡住的任务")
        else:
            logger.info("没有发现卡住的任务")
        
        return {
            "success": True,
            "cleaned_count": count,
            "message": f"成功清理 {count} 个卡住的任务"
        }
    except Exception as e:
        logger.error(f"清理卡住的任务失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="清理卡住的任务失败")
