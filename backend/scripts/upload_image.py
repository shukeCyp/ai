import requests
import json
import os
import logging
from typing import Optional, Dict
from config import RUNWAY_TOKEN
from config import USER_AGENT
from PIL import Image

# API基础URL
API_BASE_URL = "https://api.runwayml.com/v1"

# 请求头常量
HEADERS = {
    "Origin": "https://app.runwayml.com",
    "Referer": "https://app.runwayml.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

# 内容类型映射
CONTENT_TYPE_MAP = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif'
}

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取文件上传路径
def init_upload(filename: str) -> Optional[Dict]:
    """
    初始化上传请求
    
    Args:
        token: Runway API token
        filename: 要上传的文件名
        
    Returns:
        Dict: 包含上传信息的字典，失败返回None
        {
            'uploadUrl': str,
            'uploadId': str,
            'uploadHeaders': Dict
        }
    """
    try:
        headers = {
            "Authorization": f"Bearer {RUNWAY_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT
        }
        
        payload = {
            "filename": filename,
            "numberOfParts": 1,
            "type": "DATASET"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/uploads",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        return {
            'uploadUrl': data['uploadUrls'][0],
            'uploadId': data['id'],
            'uploadHeaders': data['uploadHeaders']
        }
    except Exception as e:
        logger.error(f"初始化上传失败: {e}")
        return None

# 通过文件上传路径，返回Etag
def upload_file_to_url(file_path: str, upload_url: str) -> Optional[str]:
    """
    上传文件到预签名URL
    
    Args:
        token: Runway API token
        file_path: 本地文件路径
        upload_url: 预签名的上传URL
        upload_headers: 上传需要的特定头信息
        
    Returns:
        str: 上传成功时返回ETag，失败返回None
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        content_type = CONTENT_TYPE_MAP.get(file_ext, 'application/octet-stream')
        
        headers = {
            "Accept": "*/*",
            "Content-Type": content_type,
            "sec-fetch-site": "cross-site",
            "User-Agent": USER_AGENT
        }
        
        file_size = os.path.getsize(file_path)
        headers["Content-Length"] = str(file_size)
        
        with open(file_path, 'rb') as f:
            response = requests.put(upload_url, data=f, headers=headers)
            response.raise_for_status()
            
            etag = response.headers.get('ETag')
            return etag.strip('"') if etag else None
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return None

# 完成上传过程，获取图片链接
def complete_upload(upload_id: str, etag: str) -> Optional[str]:
    """
    完成上传过程
    
    Args:
        token: Runway API token
        upload_id: 上传ID
        etag: 文件上传后返回的ETag
        
    Returns:
        str: 成功时返回上传图片的URL，失败返回None
    """
    try:
        headers = {
            **HEADERS,
            "Authorization": f"Bearer {RUNWAY_TOKEN}",
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
        
        response = requests.post(
            f"{API_BASE_URL}/uploads/{upload_id}/complete",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"完成上传成功: {data}")
        
        # 返回上传图片的URL
        return data.get('url')
    except Exception as e:
        logger.error(f"完成上传失败: {e}")
        return None

def crop_image(image_path: str, orientation: str = 'horizontal') -> str:
    """
    裁剪图片为指定尺寸，居中裁剪
    
    Args:
        image_path: 图片路径
        orientation: 方向，'horizontal'为横屏(1280x768)，'vertical'为竖屏(768x1280)
        
    Returns:
        str: 裁剪后的图片路径
    """
    try:
        # 打开图片
        img = Image.open(image_path)
        
        # 设置目标尺寸
        if orientation.lower() == 'horizontal':
            target_width, target_height = 1280, 768
        else:
            target_width, target_height = 768, 1280
        
        # 获取原始尺寸
        orig_width, orig_height = img.size
        
        # 计算裁剪区域
        # 计算宽高比
        target_ratio = target_width / target_height
        orig_ratio = orig_width / orig_height
        
        if orig_ratio > target_ratio:
            # 原图过宽，需要在宽度上裁剪
            new_width = int(orig_height * target_ratio)
            new_height = orig_height
            left = (orig_width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = orig_height
        else:
            # 原图过高，需要在高度上裁剪
            new_width = orig_width
            new_height = int(orig_width / target_ratio)
            left = 0
            top = (orig_height - new_height) // 2
            right = orig_width
            bottom = top + new_height
        
        # 裁剪
        cropped_img = img.crop((left, top, right, bottom))
        
        # 调整大小到目标尺寸
        resized_img = cropped_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # 生成新文件名
        file_name, file_ext = os.path.splitext(image_path)
        new_path = f"{file_name}_crop{file_ext}"
        
        # 保存裁剪后的图片
        resized_img.save(new_path, quality=95)
        print(f"图片裁剪成功，保存至: {new_path}")
        
        return new_path
    except Exception as e:
        logger.error(f"图片裁剪失败: {e}")
        return None

# 修改upload_image函数，添加裁剪功能
def upload_image(image_path: str, orientation: str = 'horizontal') -> Optional[str]:
    print(f"开始处理图片: {image_path}")
    
    # 先裁剪图片
    cropped_path = crop_image(image_path, orientation)
    if not cropped_path:
        print("图片裁剪失败")
        return None
        
    print(f"开始上传裁剪后的图片: {cropped_path}")
    # 获取文件名
    file_name = os.path.basename(cropped_path)
    upload_info = init_upload(file_name)
    if upload_info:
        etag = upload_file_to_url(cropped_path, upload_info['uploadUrl'])
        if etag:
            url = complete_upload(upload_info['uploadId'], etag)
            if url:
                print(f"上传成功: {url}")
                return url
            else:
                print("上传失败")
                return None
        else:
            print("文件上传失败")
            return None
    else:
        print("初始化上传失败")
        return None

if __name__ == "__main__":
    # 测试完整上传流程
    image_path = "/Users/chaiyapeng/Downloads/照片/OIP.jpg"
    # 横屏裁剪并上传
    # upload_image(image_path, 'horizontal')
    # 竖屏裁剪并上传
    upload_image(image_path, 'vertical')

"""
第一步：通过init_upload获取上传路径
第二步：通过upload_file_to_url上传文件
第三步：通过complete_upload完成上传
"""