from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from typing import List
from pydantic import BaseModel
from fastapi import Depends
from base.security import UserContext
from loguru import logger
from scripts.config import USER_AGENT
import uuid
import os
from utils.thread_pool import global_thread_pool
from models import Task, VideoGeneration, User, RunwaySession
from utils.account_pool import account_pool
from utils.thread_pool import Task as ThreadPoolTask
from utils.image_util import pad_image, crop_image
import requests
import json
import time
from typing import Optional, Dict
from base.config import PERSONAL_PROMPT
from routers.prompt import get_random_prompt, get_category_cn_name
from datetime import datetime, timedelta
import random


class GenerateVideoRequest(BaseModel):
    person_prompt: str
    product_prompt: str
    person_categories: List[str]
    product_categories: List[str]


class GenerateVideoLimitResponse(BaseModel):
    status: str
    message: str
    count: int
    limit: int = 5
    task_id: Optional[int] = None
    person_prompt: Optional[str] = None
    product_prompt: Optional[str] = None
    person_categories: Optional[List[str]] = None
    product_categories: Optional[List[str]] = None


API_BASE_URL = "https://api.runwayml.com/v1"

# 内容类型映射
CONTENT_TYPE_MAP = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif'
}


router = APIRouter()

async def process_video_generation(
    user_id: int,
    task_id: int,
    person_prompt: str,
    product_prompt: str,
    person_categories: List[str],
    product_categories: List[str],
    person_photo_path: str,
    product_photo_path: str
):
    
    try:
        """
        处理视频生成的后台任务
        """
        logger.info(f"开始处理视频生成任务 {task_id}")
        
        # 更新任务状态为生成中
        task = Task.get_by_id(task_id)
        task.status = 1  # 1-生成中
        task.save()
        
        # 获取账号，如果没有可用账号则死循环阻塞等待
        account = None
        # 尝试创建人物视频任务，最多尝试5次
        runway_task_id = None
        retry_count = 0
        while retry_count < 5:
            while account is None:
                account = account_pool.get_account()
                if account is None:
                    logger.warning("没有可用账号，等待5秒后重试...")
                    time.sleep(5)
            # 获取到账号，获取Session信息
            session = RunwaySession.get(runway_id=account['id'])
            logger.info(f"获取到账号 ID: {account['id']}, 用户名: {account['username']}, Session ID: {session.session_id}")

            # 获取账号后，开始处理
            # 上传图片到runway
            person_image_url = upload_image_to_runway(session.session_id, person_photo_path, account)
            
            runway_task_id = create_video_task(
                image_url=person_image_url,
                text_prompt=PERSONAL_PROMPT + "," + person_prompt,
                session_id=session.session_id,
                seconds=5,
                account=account
            )
            if runway_task_id:
                break
            # 释放账号
            if account:
                account_pool.release_account(account['id'])
                logger.info(f"已释放账号 ID: {account['id']}")
                account = None
            logger.warning(f"创建人物视频任务失败，第{retry_count+1}次重试...")
            time.sleep(60)  # 等待1分钟后重试
            retry_count += 1
            
        if not runway_task_id:
            logger.error("创建人物视频任务失败，已达到最大重试次数")
            # 更新任务状态为失败
            task = Task.get_by_id(task_id)
            task.status = 3  # 3-失败
            task.save()
            return
        
        video_url = None
        # 轮询任务状态
        while True:
            task_detail = get_task_detail(runway_task_id, account)
            if task_detail:
                status_info = parse_task_status(task_detail)
                if status_info:
                    logger.info(f"任务状态: {status_info['status']}")
                    logger.info(f"进度: {status_info['progress']}")
                    
                    # 如果任务完成或失败则退出循环
                    if status_info['status'] in ['SUCCEEDED']:
                        if status_info['video_url']:
                            logger.info(f"视频URL: {status_info['video_url']}")
                            logger.info(f"预览图片URLs: {json.dumps(status_info['preview_urls'], indent=2)}")
                            
                            # 添加VideoGeneration记录
                            VideoGeneration.create(
                                task=task_id,
                                type=0,  # 0-人物
                                user_prompt=person_prompt,
                                category=','.join(person_categories),
                                image_url=person_image_url,
                                video_url=status_info['video_url'],
                                runway_id=account['id'],
                                session_id=session.session_id
                            )
                            
                            
                        break
                    if status_info['status'] in ['FAILED', 'CANCELED']:
                        logger.error(f"人物视频生成失败，任务ID: {runway_task_id}")
                        # 更新任务状态为失败
                        task = Task.get_by_id(task_id)
                        task.status = 3  # 3-失败
                        task.save()
                        return 
                        
            # 等待5秒后再次查询
            time.sleep(5)
        
        if account:
            account_pool.release_account(account['id'])
            logger.info(f"已释放账号 ID: {account['id']}")
            account = None
        
        system_prompt = ""
        category_cn_name_list = []
        # 循环获取产品提示词
        for category in product_categories:
            # 拼接提示词
            prompt = get_random_prompt(category)
            # 获取中文分类名称
            category_cn_name = get_category_cn_name(category)
            category_cn_name_list.append(category_cn_name)
            if isinstance(prompt, str):
                system_prompt += prompt + ","
            else:
                # 如果get_random_prompt返回协程，需要等待它完成
                prompt_result = await prompt
                system_prompt += prompt_result + ","
        
        system_prompt += product_prompt
        # 尝试创建产品视频任务，最多尝试5次
        runway_task_id = None
        retry_count = 0
        while retry_count < 5:
            while account is None:
                account = account_pool.get_account()
                if account is None:
                    logger.warning("没有可用账号，等待5秒后重试...")
                    time.sleep(5)
            # 获取到账号，获取Session信息
            session = RunwaySession.get(runway_id=account['id'])
            logger.info(f"获取到账号 ID: {account['id']}, 用户名: {account['username']}, Session ID: {session.session_id}")

            # 获取账号后，开始处理
            # 上传图片到runway
            product_image_url = upload_image_to_runway(session.session_id, product_photo_path, account)
            runway_task_id = create_video_task(
                image_url=product_image_url,
                text_prompt=system_prompt,
                session_id=session.session_id,
                seconds=5,
                account=account
            )
            if runway_task_id:
                break
            # 释放账号
            if account:
                account_pool.release_account(account['id'])
                logger.info(f"已释放账号 ID: {account['id']}")
                account = None
            
            logger.warning(f"创建产品视频任务失败，第{retry_count+1}次重试...")
            time.sleep(60)  # 等待1分钟后重试
            retry_count += 1
            
        if not runway_task_id:
            logger.error("创建产品视频任务失败，已达到最大重试次数")
            # 更新任务状态为失败
            task = Task.get_by_id(task_id)
            task.status = 3  # 3-失败
            task.save()
            return
        
        video_url = None
        # 轮询任务状态
        while True:
            task_detail = get_task_detail(runway_task_id, account)
            if task_detail:
                status_info = parse_task_status(task_detail)
                if status_info:
                    logger.info(f"任务状态: {status_info['status']}")
                    logger.info(f"进度: {status_info['progress']}")
                    
                    # 如果任务完成或失败则退出循环
                    if status_info['status'] in ['SUCCEEDED', 'FAILED', 'CANCELED']:
                        if status_info['video_url']:
                            logger.info(f"视频URL: {status_info['video_url']}")
                            logger.info(f"预览图片URLs: {json.dumps(status_info['preview_urls'], indent=2)}")
                            
                            # 添加VideoGeneration记录
                            VideoGeneration.create(
                                task=task_id,
                                type=1,  
                                user_prompt=product_prompt,
                                category=','.join(category_cn_name_list),
                                image_url=product_image_url,
                                video_url=status_info['video_url'],
                                runway_id=account['id'],
                                session_id=session.session_id
                            )
                            
                            # 更新任务状态为完成
                            task = Task.get_by_id(task_id)
                            task.status = 2  # 2-完成
                            task.save()
                            
                        break
                    if status_info['status'] in ['FAILED', 'CANCELED']:
                        logger.error(f"产品视频生成失败，任务ID: {runway_task_id}")
                        # 更新任务状态为失败
                        task = Task.get_by_id(task_id)
                        task.status = 3  # 3-失败
                        task.save()
                        return 
                        
            # 等待5秒后再次查询
            time.sleep(5)
        
    except Exception as e:
        logger.error(f"视频生成任务 {task_id} 失败: {str(e)}")
        # 更新任务状态为失败
        try:
            task = Task.get_by_id(task_id)
            task.status = 3  # 3-失败
            task.save()
        except Exception as ex:
            logger.error(f"更新任务状态失败: {str(ex)}")
    finally:
        # 释放账号回到账号池
        if account:
            account_pool.release_account(account['id'])
            logger.info(f"已释放账号 ID: {account['id']}")
def get_task_detail(task_id: str, account: dict) -> Optional[Dict]:
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
def parse_task_status(task_detail: Dict) -> Dict:
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
        
    logger.info(f"任务状态: {status}, 进度: {progress}")
    if result['video_url']:
        logger.info(f"视频URL: {result['video_url']}")
        
    return result
def create_video_task(
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
    asset_group_id = get_asset_group_id(session_id=session_id, account=account)
    if not asset_group_id:
        asset_group_id = get_asset_group(session_id=session_id, account=account)
        if not asset_group_id:
            logger.error("未能获取到assetGroupId")
            return None
    logger.info(f"获取到assetGroupId: {asset_group_id}")
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
    
    logger.info(f"开始创建视频任务，提示词: {text_prompt[:30]}...")
    
    while True:
        response = requests.post(
            f"{API_BASE_URL}/tasks",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 401:
            logger.error("Runway账号token失效")
            raise HTTPException(status_code=401, detail="Runway账号失效")
            
        if response.status_code == 429:
            logger.warning("请求频率限制(429)，3秒后重试...")
            time.sleep(3)
            continue
        
        response.raise_for_status()
        break
    
    data = response.json()
    task_id = parse_task_id(data)
    if task_id:
        logger.info(f"视频任务创建成功，任务ID: {task_id}")
        return task_id
    else:
        logger.error("未能获取到任务ID")
        return None
                

def parse_task_id(response_data: Dict) -> Optional[str]:
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
            logger.debug(f"解析到任务ID: {task_id}")
            return task_id
        else:
            logger.error("未能在响应数据中找到任务ID")
            return None
    except Exception as e:
        logger.error(f"解析任务ID失败: {e}")
        return None

def get_asset_group_id(session_id: str, account: dict) -> Optional[str]:
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
    
    logger.info(f"获取assetGroupId，Session ID: {session_id}")
    response = requests.get(
        f"https://api.runwayml.com/v1/sessions/{session_id}",
        headers=headers,
        params={"asTeamId": account['as_team_id']}
    )

    if response.status_code == 401:
        logger.error("Runway账号token失效")
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    
    data = response.json()        
    # 从session对象中获取assetGroupId
    asset_group_id = data.get('session', {}).get('assetGroupId')
    if asset_group_id:
        return asset_group_id
    else:
        logger.error("未能获取到assetGroupId")
        return None
def get_asset_group(session_id: str, account: dict) -> Optional[str]:
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
    
    logger.info(f"获取assetGroupId，Session ID: {session_id}")
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
        logger.error("未能获取到assetGroupId")
        return None

# 上传图片到runway
def upload_image_to_runway(session_id: str, image_path: str, account: dict):
    # 获取上传链接
    logger.info(f"上传图片到runway，Session ID: {session_id}, 图片路径: {image_path}, 账号: {account}")

    headers = {
        "Authorization": f"Bearer {account['token']}",
        "Content-Type": "application/json", 
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }

    # 获取文件名
    file_name = os.path.basename(image_path)
    logger.info(f"准备上传文件: {file_name}")
    
    # 获取上传链接
    get_upload_url_payload = {
        "filename": file_name,
        "numberOfParts": 1,
        "type": "DATASET"
    }
    
    logger.info(f"请求上传链接，payload: {get_upload_url_payload}")
    response = requests.post(
        f"{API_BASE_URL}/uploads",
        headers = headers,
        json = get_upload_url_payload
    )
    
    if response.status_code == 401:
        logger.error("Runway账号token失效")
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    data = response.json()

    upload_id = data.get('id')
    upload_url = data.get('uploadUrls')[0]
    logger.info(f"获取上传链接成功: upload_id={upload_id}, upload_url={upload_url}")

    # 上传图片
    file_ext = os.path.splitext(image_path)[1].lower()
    content_type = CONTENT_TYPE_MAP.get(file_ext, 'application/octet-stream')
    logger.info(f"文件类型: {file_ext}, 内容类型: {content_type}")
    
    headers = {
        "Accept": "*/*",
        "Content-Type": content_type,
        "sec-fetch-site": "cross-site",
        "User-Agent": USER_AGENT
    }
    
    file_size = os.path.getsize(image_path)
    headers["Content-Length"] = str(file_size)
    logger.info(f"文件大小: {file_size} 字节")
    
    with open(image_path, 'rb') as f:
        logger.info(f"开始上传文件到: {upload_url}")
        response = requests.put(upload_url, data=f, headers=headers)
        
        if response.status_code == 401:
            logger.error("Runway账号token失效")
            raise HTTPException(status_code=401, detail="Runway账号失效")
            
        response.raise_for_status()
        
        etag = response.headers.get('ETag')
        logger.info(f"文件上传成功，获取到ETag: {etag}")

    if not etag:
        logger.error("上传图片失败: 未获取到ETag")
        return None
    
    # 去除ETag两端的引号
    etag = etag.strip('"')
    logger.info(f"处理后的ETag: {etag}")
    
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
    
    logger.info(f"完成上传请求，upload_id: {upload_id}, payload: {payload}")
    response = requests.post(
        f"{API_BASE_URL}/uploads/{upload_id}/complete",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 401:
        logger.error("Runway账号token失效")
        raise HTTPException(status_code=401, detail="Runway账号失效")
        
    response.raise_for_status()
    
    data = response.json()
    image_url = data.get('url')
    logger.info(f"完成上传成功，图片URL: {image_url}")
    
    return image_url

async def generate_video_task(
        user_id: int,
        task_id: int,
        type : int, # 0-人物，1-产品
        prompt: str,
        photo_path: str,
        categories: List[str]
):
    try:
        task_log_prefix = f"任务[{task_id}_{type}]"
        # 循环阻塞获取账号
        account = None
        while not account:
            account = account_pool.get_account()
            if not account:
                logger.info(f"{task_log_prefix} 用户 {user_id} 未能获取到账号，3秒后重试...")
                time.sleep(3)
        # 获取Session
        session = RunwaySession.get(runway_id=account['id'])
        logger.info(f"{task_log_prefix} user_id: {user_id}, 获取到账号 ID: {account['id']}, 用户名: {account['username']}, Session ID: {session.session_id}")

        # 上传图片到runway
        image_url = upload_image_to_runway(session.session_id, photo_path, account)
        # 创建视频任务
        logger.info(f"{task_log_prefix} 默认提示词是: {type} == {prompt}")
        my_prompt = ""
        # 输出分类
        logger.info(f"{task_log_prefix} 分类是: {categories[0]}")
        if type == 0:
            my_prompt = prompt if prompt != "默认人像提示词" else PERSONAL_PROMPT
        else:
            my_prompt = prompt if prompt != "默认商品提示词" else get_random_prompt(categories[0])
        logger.info(f"{task_log_prefix} 最终提示词是: {type} == {my_prompt}")
        runway_task_id = create_video_task(
                image_url=image_url,
                text_prompt=my_prompt,
                session_id=session.session_id,
                seconds=5,
                seed=random.randint(1, 1000000000),
                account=account
            )
        
        # 循环获取任务状态
        # 轮询任务状态
        while True:
            task_detail = get_task_detail(runway_task_id, account)
            if task_detail:
                status_info = parse_task_status(task_detail)
                if status_info:
                    logger.info(f"{task_log_prefix} 任务状态: {status_info['status']}")
                    logger.info(f"{task_log_prefix} 进度: {status_info['progress']}")
                    
                    # 如果任务完成或失败则退出循环
                    if status_info['status'] in ['SUCCEEDED']:
                        if status_info['video_url']:
                            logger.info(f"{task_log_prefix} 视频URL: {status_info['video_url']}")
                            logger.info(f"{task_log_prefix} 预览图片URLs: {json.dumps(status_info['preview_urls'], indent=2)}")
                            
                            # 添加VideoGeneration记录
                            VideoGeneration.create(
                                task=task_id,
                                type=type,  # 0-人物
                                user_prompt= prompt,
                                category=get_category_cn_name(categories[0]),
                                image_url=image_url,
                                video_url=status_info['video_url'],
                                runway_id=account['id'],
                                session_id=session.session_id
                            )
                            
                            
                        break
                    if status_info['status'] in ['FAILED', 'CANCELED']:
                        logger.error(f"{task_log_prefix} 视频生成失败，任务ID: {runway_task_id}")
                        task = Task.get_by_id(task_id)
                        task.status = 3  # 3-失败
                        task.save()
                        raise HTTPException(status_code=400, detail="视频生成失败")
                        
            # 等待5秒后再次查询
            time.sleep(5)
        
    except HTTPException as e:
        if e.status_code == 401 and e.detail == "Runway账号失效":
            logger.error(f"{task_log_prefix} Runway账号失效: {str(e)}")
            if account:
                # 从账号池中删除失效账号
                account_pool.remove_account(account['id'])
                logger.info(f"{task_log_prefix} 已删除失效账号 ID: {account['id']}")
                account = None
            # 生成失败
            task = Task.get_by_id(task_id)
            task.status = 3  # 3-失败
            task.save()
            raise
    except Exception as e:
        logger.error(f"{task_log_prefix} 生成视频任务失败: {str(e)}")
        # 生成失败
        task = Task.get_by_id(task_id)
        task.status = 3  # 3-失败
        task.save()
        raise
    finally:
        if account:
            account_pool.release_account(account['id'])
            logger.info(f"{task_log_prefix} 已释放账号 ID: {account['id']}")
            account = None
        # 判断任务流程是否结束
        if VideoGeneration.select().where(VideoGeneration.task == task_id).count() == 2:
            task = Task.get_by_id(task_id)
            task.status = 2  # 2-完成
            task.save()
            logger.info(f"任务[{task_id}] 全部完成，已更新状态")

@router.post("/generate_video", response_model=GenerateVideoLimitResponse)
async def generate_video(
    person_prompt: str = Form(...),
    product_prompt: str = Form(...),
    person_categories: List[str] = Form(...),
    product_categories: List[str] = Form(...),
    person_photo: UploadFile = File(...),
    product_photo: UploadFile = File(...),
    user_context: UserContext = Depends()
):
    """
    生成视频接口
    
    参数:
    - person_prompt: 人物提示词
    - product_prompt: 产品提示词
    - person_categories: 人物分类数组
    - product_categories: 产品分类数组
    - person_photo: 人物照片
    - product_photo: 产品照片
    """
    logger.info(f"请求生成视频，人物提示词: {person_prompt}, 产品提示词: {product_prompt}, 人物分类: {person_categories}, 产品分类: {product_categories}")
    
    # 获取用户ID
    user_id = user_context.user_id
    
    # 检查用户1小时内的生成次数
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    # 查询1小时内的任务数量
    count = Task.select().where(
        (Task.user == user_id) & 
        (Task.created_at >= one_hour_ago) & 
        (Task.status == 1)
    ).count()
    
    logger.info(f"用户 {user_id} 在过去1小时内已生成 {count} 个视频")
    
    # 如果超过限制，返回错误
    if count >= 5:
        logger.warning(f"用户 {user_id} 生成视频次数超过限制")
        return GenerateVideoLimitResponse(
            status="error",
            message="同时生成视频个数已达上限",
            count=count
        )
    
    # 创建任务记录
    task = Task.create(
        user_id=user_id,
        status=1  # 0-排队中
    )
    
    # 保存上传的照片
    upload_dir = os.path.join("uploads", str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存人物照片
    person_photo_content = await person_photo.read()
    person_photo_path = os.path.join(upload_dir, f"person_{task.id}_{uuid.uuid4()}.jpg")
    with open(person_photo_path, "wb") as f:
        f.write(person_photo_content) 
    # 裁剪人物照片
    person_photo_path = crop_image(person_photo_path, 'vertical')
    
    # 保存产品照片
    product_photo_content = await product_photo.read()
    product_photo_path = os.path.join(upload_dir, f"product_{task.id}_{uuid.uuid4()}.jpg")
    with open(product_photo_path, "wb") as f:
        f.write(product_photo_content)
    # 裁剪产品照片
    product_photo_path = pad_image(product_photo_path, 'vertical')
    
    global_thread_pool.submit(
        generate_video_task,
        user_id,
        task.id,
        0,
        person_prompt,
        person_photo_path,
        person_categories
    )
    
    global_thread_pool.submit(
        generate_video_task,
        user_id,
        task.id,
        1,
        product_prompt,
        product_photo_path,
        product_categories
    )
    

    return GenerateVideoLimitResponse(
        status="processing",
        message="视频生成请求已接收",
        count=count + 1,  # 包括当前这次请求
        task_id=task.id,
        person_prompt=person_prompt,
        product_prompt=product_prompt,
        person_categories=person_categories,
        product_categories=product_categories
    )
