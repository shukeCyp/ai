import requests
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

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

def login(username: str, password: str) -> str:
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
    
    payload = LoginRequest(
        username=username,
        password=password,
        machineId=None
    )
    
    try:
        response = requests.post(url, json=payload.dict())
        response.raise_for_status()  # 如果响应状态码不是 200，抛出异常
        
        login_response = LoginResponse(**response.json())
        return login_response.token
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"登录请求失败: {str(e)}")
    except Exception as e:
        raise Exception(f"处理登录响应时出错: {str(e)}")

def get_user_profile(token: str) -> UserProfile:
    """
    获取用户资料信息
    
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
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        user_data = data["user"]
        
        return UserProfile(
            id=user_data["id"],
            createdAt=user_data["createdAt"],
            updatedAt=user_data["updatedAt"],
            planExpires=user_data["planExpires"]
        )
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"获取用户资料失败: {str(e)}")
    except Exception as e:
        raise Exception(f"处理用户资料响应时出错: {str(e)}")

def create_session(token: str, team_id: int) -> str:
    """
    创建新的会话
    
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
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        session_data = data["session"]
        
        session = Session(
            id=session_data["id"],
            name=session_data["name"],
            createdAt=session_data["createdAt"],
            updatedAt=session_data["updatedAt"]
        )
        return session.id
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"创建会话失败: {str(e)}")
    except Exception as e:
        raise Exception(f"处理会话响应时出错: {str(e)}")

# 使用示例
if __name__ == "__main__":
    try:
        # 测试登录
        token = login("l8d3i0tr", "yuxiang123456")
        print(f"登录成功！Token: {token}\n")
        
        # 测试获取用户资料
        profile = get_user_profile(token)
        print("用户资料：")
        print(f"ID: {profile.id}")
        print(f"创建时间: {profile.createdAt}")
        print(f"更新时间: {profile.updatedAt}")
        print(f"计划过期时间: {profile.planExpires}\n")
        
        # 测试创建会话
        session_id = create_session(token, profile.id)
        print(f"创建会话成功！Session ID: {session_id}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
