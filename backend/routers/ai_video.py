from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from base.security import UserContext
from fastapi import Depends
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from models import AIVideo
import os
import uuid
from loguru import logger
from utils.thread_pool import global_thread_pool
from utils.account_pool import account_pool
import time
from models import RunwaySession
import requests
from scripts.config import USER_AGENT
from typing import Dict, List
import json
import datetime
API_BASE_URL = "https://api.runwayml.com/v1"

# 内容类型映射
CONTENT_TYPE_MAP = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif'
}


class Resolution(str, Enum):
    LANDSCAPE = "1280x768"  # 横屏
    PORTRAIT = "768x1280"  # 竖屏


class CreateVideoResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[int] = None


class AIVideoItem(BaseModel):
    id: int
    user_id: int
    prompt: str
    resolution: str
    seconds: int
    seed: int
    status: int
    video_url: Optional[str]
    image_url: Optional[str]
    created_at: str


class AIVideoListResponse(BaseModel):
    total: int
    items: List[AIVideoItem]


router = APIRouter()

async def ai_video_generate(
    user_id: int,
    video_id: int,
    prompt: str,
    photo_path: str,
    seconds: int,
    seed: int,
    resolution: Resolution
):
    try:
        # 循环阻塞获取账号
        account = None
        while not account:
            account = account_pool.get_account()
            if not account:
                logger.info(f"[AIVideo-{video_id}] 未能获取到账号，3秒后重试...")
                time.sleep(3)
        # 获取Session
        session = RunwaySession.get(runway_id=account['id'])
        logger.info(f"[AIVideo-{video_id}] 获取到账号 ID: {account['id']}, 用户名: {account['username']}, Session ID: {session.session_id}")
        # 更新视频状态为生成中和账号
        AIVideo.update(status=1, runway_id=account['id']).where(AIVideo.id == video_id).execute()

        # 上传图片到runway
        image_url = upload_image_to_runway(video_id, session.session_id, photo_path, account)

        # 创建视频生成任务
        runway_task_id = create_video_task(video_id, image_url, prompt, session.session_id, seed, seconds, account)
        if not runway_task_id:
            logger.error(f"[AIVideo-{video_id}] 创建视频生成任务失败")
            raise HTTPException(status_code=500, detail="创建视频生成任务失败")

        while True:
            task_detail = get_task_detail(video_id, runway_task_id, account)
            if task_detail:
                status_info = parse_task_status(video_id, task_detail)
                if status_info:
                    logger.info(f"[AIVideo-{video_id}] 任务状态: {status_info['status']}")
                    logger.info(f"[AIVideo-{video_id}] 进度: {status_info['progress']}")
                    
                    # 如果任务完成或失败则退出循环
                    if status_info['status'] in ['SUCCEEDED']:
                        if status_info['video_url']:
                            logger.info(f"[AIVideo-{video_id}] 视频URL: {status_info['video_url']}")
                            logger.info(f"[AIVideo-{video_id}] 预览图片URLs: {json.dumps(status_info['preview_urls'], indent=2)}")
                            AIVideo.update(
                                status=2, 
                                video_url=status_info['video_url'],
                                image_url=image_url
                            ).where(AIVideo.id == video_id).execute()
                        break
                    if status_info['status'] in ['FAILED', 'CANCELED']:
                        logger.error(f"[AIVideo-{video_id}] 视频生成失败，任务ID: {runway_task_id}")
                        AIVideo.update(status=3).where(AIVideo.id == video_id).execute()
                        break
                        
            # 等待5秒后再次查询
            time.sleep(5)



    except Exception as e:
        logger.error(f"[AIVideo-{video_id}] AI视频生成失败: {e}")
        AIVideo.update(status=3).where(AIVideo.id == video_id).execute()
    except HTTPException as e:
        logger.error(f"[AIVideo-{video_id}] Runway账号失效: {str(e)}")
        if account:
            account_pool.remove_account(account['id'])
            logger.info(f"[AIVideo-{video_id}] 已删除失效账号 ID: {account['id']}")
            account = None
        AIVideo.update(status=3).where(AIVideo.id == video_id).execute()
        raise e
    finally:
        account_pool.release_account(account)

def create_video_task(
    aivideo_id: int,
    image_url: str,
    text_prompt: str,
    session_id: str,
    seed: int = 3259043548,
    seconds: int = 5,
    account: dict = None
) -> Optional[str]:
    """
    创建视频生成任务
    
    Args:
        image_url: 输入图片的URL
        text_prompt: 文本提示
        session_id: 会话ID
        seed: 随机种子
        seconds: 视频时长（秒）
        account: 账号信息
        
    Returns:
        str: 成功时返回任务ID，失败返回None
    """
    # 获取assetGroupId
    asset_group_id = get_asset_group_id(aivideo_id, session_id=session_id, account=account)
    if not asset_group_id:
        asset_group_id = get_asset_group(aivideo_id, session_id=session_id, account=account)
        if not asset_group_id:
            logger.error(f"[AIVideo-{aivideo_id}] 未能获取到assetGroupId")
            return None
    logger.info(f"[AIVideo-{aivideo_id}] 获取到assetGroupId: {asset_group_id}")
    headers = {
        "Authorization": f"Bearer {account['token']}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT
    }
    
    payload = {
        "taskType": "gen3a_turbo",
        "internal": False,
        "options": {
            "name": f"Gen-3 Alpha Turbo {seed}",
            "seed": seed,
            "exploreMode": True,
            "watermark": False,
            "enhance_prompt": True,
            "seconds": seconds,
            "keyframes": [
                {
                    "image": image_url,
                    "timestamp": 0
                }
            ],
            "text_prompt": text_prompt,
            "flip": True,
            "assetGroupId": asset_group_id
        },
        "asTeamId": account['as_team_id'],
        "sessionId": session_id
    }
    
    logger.info(f"[AIVideo-{aivideo_id}] 开始创建视频任务，提示词: {text_prompt[:30]}...")
    
    while True:
        response = requests.post(
            f"{API_BASE_URL}/tasks",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 401:
            logger.error(f"[AIVideo-{aivideo_id}] Runway账号token失效")
            raise HTTPException(status_code=401, detail="Runway账号失效")
            
        if response.status_code == 429:
            logger.warning(f"[AIVideo-{aivideo_id}] 请求频率限制(429)，3秒后重试...")
            time.sleep(3)
            continue
        
        response.raise_for_status()
        break
    
    data = response.json()
    task_id = parse_task_id(aivideo_id, data)
    if task_id:
        logger.info(f"[AIVideo-{aivideo_id}] 视频任务创建成功，任务ID: {task_id}")
        return task_id
    else:
        logger.error(f"[AIVideo-{aivideo_id}] 未能获取到任务ID")
        return None

def get_task_detail(aivideo_id: int, task_id: str, account: dict) -> Optional[Dict]:
    """
    获取任务详细信息
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 包含任务详细信息的字典，失败返回None
    """
    headers = {
        "Authorization": f"Bearer {account['token']}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    response = requests.get(
        f"{API_BASE_URL}/tasks/{task_id}",
        headers=headers,
        params={"asTeamId": account['as_team_id']}
    )
    
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    
    data = response.json()
    return data

def parse_task_id(aivideo_id: int, response_data: Dict) -> Optional[str]:
    """
    从任务响应数据中解析任务ID
    
    Args:
        response_data: 任务响应数据
        
    Returns:
        str: 任务ID，如果未找到则返回None
    """
    try:
        task_id = response_data.get('task', {}).get('id')
        if task_id:
            logger.debug(f"[AIVideo-{aivideo_id}] 解析到任务ID: {task_id}")
            return task_id
        else:
            logger.error(f"[AIVideo-{aivideo_id}] 未能在响应数据中找到任务ID")
            return None
    except Exception as e:
        logger.error(f"[AIVideo-{aivideo_id}] 解析任务ID失败: {e}")
        return None


def get_asset_group_id(aivideo_id: int, session_id: str, account: dict) -> Optional[str]:
    """
    获取assetGroupId
    
    Args:
        session_id: 会话ID
        account: 账号信息
        
    Returns:
        str: 成功时返回assetGroupId，失败返回None
    """
    headers = {
        "Authorization": f"Bearer {account['token']}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    logger.info(f"[AIVideo-{aivideo_id}] 获取assetGroupId，Session ID: {session_id}")
    response = requests.get(
        f"https://api.runwayml.com/v1/sessions/{session_id}",
        headers=headers,
        params={"asTeamId": account['as_team_id']}
    )

    if response.status_code == 401:
        logger.error(f"[AIVideo-{aivideo_id}] Runway账号token失效")
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    
    data = response.json()        
    # 从session对象中获取assetGroupId
    asset_group_id = data.get('session', {}).get('assetGroupId')
    if asset_group_id:
        return asset_group_id
    else:
        logger.error(f"[AIVideo-{aivideo_id}] 未能获取到assetGroupId")
        return None
def get_asset_group(aivideo_id: int, session_id: str, account: dict) -> Optional[str]:
    """
    获取assetGroupId
    
    Args:
        session_id: 会话ID
        account: 账号信息
        
    Returns:
        str: 成功时返回assetGroupId，失败返回None
    """
    headers = {
        "Authorization": f"Bearer {account['token']}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    logger.info(f"[AIVideo-{aivideo_id}] 获取assetGroupId，Session ID: {session_id}")
    response = requests.post(
        f"https://api.runwayml.com/v1/sessions/{session_id}/assetGroup",
        headers=headers,
        params={"asTeamId": account['as_team_id']}
    )

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    
    data = response.json()        
    # 从assetGroup对象中获取id
    asset_group_id = data.get('assetGroup', {}).get('id')
    if asset_group_id:
        return asset_group_id
    else:
        logger.error(f"[AIVideo-{aivideo_id}] 未能获取到assetGroupId")
        return None


def parse_task_status(aivideo_id: int, task_detail: Dict) -> Dict:
    """
    解析任务状态和视频URL
    
    Args:
        task_detail: 任务详细信息
        
    Returns:
        Dict: 包含状态信息的字典
        {
            'status': str,  # THROTTLED/RUNNING/SUCCEEDED等
            'progress': str,  # 进度比例
            'video_url': str,  # 成功时返回视频URL
            'preview_urls': List[str]  # 预览图片URL列表
        }
    """
    if task_detail.get('error', {}).get('code') == 401:
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    task = task_detail.get('task', {})
    status = task.get('status')
    progress = task.get('progressRatio')
    
    result = {
        'status': status,
        'progress': progress,
        'video_url': None,
        'preview_urls': []
    }
    
    # 如果任务成功完成，获取视频URL
    if status == 'SUCCEEDED' and task.get('artifacts'):
        artifact = task['artifacts'][0]  # 获取第一个制品
        result['video_url'] = artifact.get('url')
        result['preview_urls'] = artifact.get('previewUrls', [])
        
    logger.info(f"[AIVideo-{aivideo_id}] 任务状态: {status}, 进度: {progress}")
    if result['video_url']:
        logger.info(f"[AIVideo-{aivideo_id}] 视频URL: {result['video_url']}")
        
    return result

# 上传图片到runway
def upload_image_to_runway(aivideo_id: int, session_id: str, image_path: str, account: dict):
    # 获取上传链接
    logger.info(f"[AIVideo-{aivideo_id}] 上传图片到runway，Session ID: {session_id}, 图片路径: {image_path}, 账号: {account}")

    headers = {
        "Authorization": f"Bearer {account['token']}",
        "Content-Type": "application/json", 
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }

    # 获取文件名
    file_name = os.path.basename(image_path)
    logger.info(f"[AIVideo-{aivideo_id}] 准备上传文件: {file_name}")
    
    # 获取上传链接
    get_upload_url_payload = {
        "filename": file_name,
        "numberOfParts": 1,
        "type": "DATASET"
    }
    
    logger.info(f"[AIVideo-{aivideo_id}] 请求上传链接，payload: {get_upload_url_payload}")
    response = requests.post(
        f"{API_BASE_URL}/uploads",
        headers = headers,
        json = get_upload_url_payload
    )
    
    if response.status_code == 401:
        logger.error(f"[AIVideo-{aivideo_id}] Runway账号token失效")
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    data = response.json()

    upload_id = data.get('id')
    upload_url = data.get('uploadUrls')[0]
    logger.info(f"[AIVideo-{aivideo_id}] 获取上传链接成功: upload_id={upload_id}, upload_url={upload_url}")

    # 上传图片
    file_ext = os.path.splitext(image_path)[1].lower()
    content_type = CONTENT_TYPE_MAP.get(file_ext, 'application/octet-stream')
    logger.info(f"[AIVideo-{aivideo_id}] 文件类型: {file_ext}, 内容类型: {content_type}")
    
    headers = {
        "Accept": "*/*",
        "Content-Type": content_type,
        "sec-fetch-site": "cross-site",
        "User-Agent": USER_AGENT
    }
    
    file_size = os.path.getsize(image_path)
    headers["Content-Length"] = str(file_size)
    logger.info(f"[AIVideo-{aivideo_id}] 文件大小: {file_size} 字节")
    
    with open(image_path, 'rb') as f:
        logger.info(f"[AIVideo-{aivideo_id}] 开始上传文件到: {upload_url}")
        response = requests.put(upload_url, data=f, headers=headers)
        
        if response.status_code == 401:
            logger.error(f"[AIVideo-{aivideo_id}] Runway账号token失效")
            raise HTTPException(status_code=401, detail="Runway账号失效")
            
        response.raise_for_status()
        
        etag = response.headers.get('ETag')
        logger.info(f"[AIVideo-{aivideo_id}] 文件上传成功，获取到ETag: {etag}")

    if not etag:
        logger.error(f"[AIVideo-{aivideo_id}] 上传图片失败: 未获取到ETag")
        return None
    
    # 去除ETag两端的引号
    etag = etag.strip('"')
    logger.info(f"[AIVideo-{aivideo_id}] 处理后的ETag: {etag}")
    
    headers = {
        "Authorization": f"Bearer {account['token']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "parts": [
            {
                "PartNumber": 1,
                "ETag": etag
            }
        ]
    }
    
    logger.info(f"[AIVideo-{aivideo_id}] 完成上传请求，upload_id: {upload_id}, payload: {payload}")
    response = requests.post(
        f"{API_BASE_URL}/uploads/{upload_id}/complete",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 401:
        logger.error(f"[AIVideo-{aivideo_id}] Runway账号token失效")
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    
    data = response.json()
    image_url = data.get('url')
    logger.info(f"[AIVideo-{aivideo_id}] 完成上传成功，图片URL: {image_url}")
    
    return image_url


@router.post("/create_video", response_model=CreateVideoResponse)
async def create_video(
    prompt: str = Form(...),
    photo: UploadFile = File(...),
    seconds: int = Form(...),
    seed: int = Form(...),
    resolution: Resolution = Form(...),
    user_context: UserContext = Depends()
):
    # 验证分辨率
    if resolution not in Resolution:
        raise HTTPException(status_code=400, detail="分辨率只能是 1280x768(横屏) 或 768x1280(竖屏)")
    
    # 保存上传的图片
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    photo_content = await photo.read()
    photo_path = os.path.join(upload_dir, f"ai_video_{uuid.uuid4()}.jpg")
    with open(photo_path, "wb") as f:
        f.write(photo_content)
        
    # 创建AI视频记录
    video = AIVideo.create(
        user=user_context.user_id,
        prompt=prompt,
        resolution=resolution,
        seconds=seconds,
        seed=seed,
        status=0  # 排队中
    )

    global_thread_pool.submit(
        ai_video_generate, 
        user_context.user_id, 
        video.id, 
        prompt, 
        photo_path, 
        seconds, 
        seed, 
        resolution
    )

    return {
        "status": "success",
        "message": "视频生成任务已创建",
        "task_id": video.id
    }
@router.get("/list", response_model=AIVideoListResponse)
async def get_video_list(
    page: int = 1,
    page_size: int = 10,
    user_context: UserContext = Depends()
):
    """
    获取AI视频列表
    
    Args:
        page: 页码，从1开始
        page_size: 每页数量
        user: 用户上下文
        
    Returns:
        AIVideoListResponse: 包含总数和视频列表的响应
    """
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 计算24小时前的时间
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    
    # 获取总数（24小时内）
    total = AIVideo.select().where(
        (AIVideo.user == user_context.user_id) & 
        (AIVideo.created_at >= one_day_ago)
    ).count()
    
    # 获取分页数据（24小时内）
    videos = (AIVideo
             .select()
             .where(
                 (AIVideo.user == user_context.user_id) & 
                 (AIVideo.created_at >= one_day_ago)
             )
             .order_by(AIVideo.id.desc())
             .offset(offset)
             .limit(page_size))
             
    items = []
    for video in videos:
        items.append({
            "id": video.id,
            "user_id": video.user.id if hasattr(video.user, 'id') else video.user,  # 修复User对象转换问题
            "prompt": video.prompt,
            "resolution": video.resolution,
            "seconds": video.seconds,
            "seed": video.seed,
            "status": video.status,
            "video_url": video.video_url,
            "image_url": video.image_url,
            "created_at": video.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return {
        "total": total,
        "items": items
    }