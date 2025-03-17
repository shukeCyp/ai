import requests
import json
import logging
import time
from typing import Optional, Dict, List
from config import RUNWAY_TOKEN, USER_AGENT, SESSION_ID, AS_TEAM_ID

# API基础URL
API_BASE_URL = "https://api.runwayml.com/v1"

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_video_task(
    image_url: str,
    text_prompt: str,
    session_id: str,
    seed: int = 3259043548,
    seconds: int = 5
) -> Optional[str]:
    """
    创建视频生成任务
    
    Args:
        image_url: 输入图片的URL
        text_prompt: 文本提示
        session_id: 会话ID
        seed: 随机种子
        seconds: 视频时长（秒）
        team_id: 团队ID
        
    Returns:
        str: 成功时返回任务ID，失败返回None
    """
    try:
        # 获取assetGroupId
        asset_group_id = get_asset_group_id(SESSION_ID, AS_TEAM_ID)
        if not asset_group_id:
            return None
            
        headers = {
            "Authorization": f"Bearer {RUNWAY_TOKEN}",
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
                "seconds": 5,
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
            "asTeamId": AS_TEAM_ID,
            "sessionId": SESSION_ID
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tasks",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        task_id = parse_task_id(data)
        if task_id:
            logger.info(f"视频任务创建成功，任务ID: {task_id}")
            return task_id
        else:
            logger.error("未能获取到任务ID")
            return None
            
    except Exception as e:
        logger.error(f"创建视频任务失败: {e}")
        return None

def get_asset_group_id(session_id: str, team_id: int) -> Optional[str]:
    """
    获取assetGroupId
    
    Args:
        session_id: 会话ID
        team_id: 团队ID
        
    Returns:
        str: 成功时返回assetGroupId，失败返回None
    """
    try:
        headers = {
            "Authorization": f"Bearer {RUNWAY_TOKEN}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT
        }
        
        response = requests.get(
            f"https://api.runwayml.com/v1/sessions/{session_id}",
            headers=headers,
            params={"asTeamId": team_id}
        )
        response.raise_for_status()
        
        data = response.json()        
        # 从session对象中获取assetGroupId
        asset_group_id = data.get('session', {}).get('assetGroupId')
        if asset_group_id:
            logger.info(f"获取assetGroupId成功: {asset_group_id}")
            return asset_group_id
        else:
            logger.error("未能获取到assetGroupId")
            return None
            
    except Exception as e:
        logger.error(f"获取assetGroupId失败: {e}")
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
            logger.info(f"解析到任务ID: {task_id}")
            return task_id
        else:
            logger.error("未能在响应数据中找到任务ID")
            return None
    except Exception as e:
        logger.error(f"解析任务ID失败: {e}")
        return None

def get_task_detail(task_id: str) -> Optional[Dict]:
    """
    获取任务详细信息
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 包含任务详细信息的字典，失败返回None
    """
    try:
        headers = {
            "Authorization": f"Bearer {RUNWAY_TOKEN}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT
        }
        
        response = requests.get(
            f"{API_BASE_URL}/tasks/{task_id}",
            headers=headers,
            params={"asTeamId": AS_TEAM_ID}
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"获取任务详细信息成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
        
    except Exception as e:
        logger.error(f"获取任务详细信息失败: {e}")
        return None

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
    try:
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
        
    except Exception as e:
        logger.error(f"解析任务状态失败: {e}")
        return None

if __name__ == "__main__":
    # 测试示例
    image_url = "https://d2jqrm6oza8nb6.cloudfront.net/datasets/add52f10-3703-4f54-9b91-4ac27fce2e81.jpg?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiN2RhYzViZDk3YTEyMTY2NyIsImJ1Y2tldCI6InJ1bndheS1kYXRhc2V0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc0MTEzMjgwMH0.5Pab5I28uW9Z7IwW3xG6AEeG7fs0Vm7WGc-Eh2ENJbo"
    text_prompt = "Show a person inside a car doing an exaggerated surprised expression"
    session_id = SESSION_ID
    
    # 创建任务
    task_id = create_video_task(
        image_url=image_url,
        text_prompt=text_prompt,
        session_id=session_id
    )
    
    if task_id:
        # 循环获取任务状态直到完成
        while True:
            task_detail = get_task_detail(task_id)
            if task_detail:
                status_info = parse_task_status(task_detail)
                if status_info:
                    print(f"任务状态: {status_info['status']}")
                    print(f"进度: {status_info['progress']}")
                    
                    # 如果任务完成或失败则退出循环
                    if status_info['status'] in ['SUCCEEDED', 'FAILED', 'CANCELED']:
                        if status_info['video_url']:
                            print(f"视频URL: {status_info['video_url']}")
                            print(f"预览图片URLs: {json.dumps(status_info['preview_urls'], indent=2)}")
                        break
                        
            # 等待5秒后再次查询
            time.sleep(5)
