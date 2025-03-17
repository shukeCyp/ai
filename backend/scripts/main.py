import requests
import json
import time
from typing import Dict, Optional
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QFrame)
from PyQt5.QtCore import Qt

# 会话ID常量
SESSION_ID = "61049279-c1c4-4b4a-bf0b-28d91187caf6"
# 团队ID常量
TEAM_ID = 31168330
# RUNWAY_TOKEN
RUNWAY_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzExNjgzMzAsImVtYWlsIjoibDhkM2kwdHJAY3Yuc2luZ2Fwb3JwZS5vcmciLCJleHAiOjE3NDMzMjU2MTAuNzI2LCJpYXQiOjE3NDA3MzM2MTAuNzI2LCJzc28iOmZhbHNlfQ.qgGVz1ZotBA7GzyX361siXYj2Z2i0mEhggTtn-nT1k0"

class VideoGenerator:
    def __init__(self, session_id: str, team_id: str = None):
        self.session_id = session_id
        self.team_id = team_id
        self.base_url = "https://api.example.com/video"  # 请替换为实际的API地址
        self.headers = {
            "Content-Type": "application/json",
            "Session-ID": session_id
        }
        if team_id:
            self.headers["Team-ID"] = team_id

    def generate_video(self, params: Dict) -> Optional[str]:
        """
        发起视频生成请求
        
        Args:
            params: 视频生成所需的参数字典
            
        Returns:
            str: 视频任务ID，如果失败则返回None
        """
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=params
            )
            response.raise_for_status()
            return response.json().get("task_id")
        except requests.exceptions.RequestException as e:
            print(f"视频生成请求失败: {e}")
            return None

    def check_status(self, task_id: str) -> Dict:
        """
        检查视频生成状态
        
        Args:
            task_id: 视频任务ID
            
        Returns:
            Dict: 包含状态信息的字典
        """
        try:
            response = requests.get(
                f"{self.base_url}/status/{task_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"状态检查失败: {e}")
            return {"status": "error", "message": str(e)}

class VideoGeneratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_generator = VideoGenerator(SESSION_ID, TEAM_ID)
        self.initUI()
        
    def initUI(self):
        # 设置窗口基本属性
        self.setWindowTitle('视频生成器')
        self.setGeometry(300, 300, 600, 400)  # 设置窗口位置和大小
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 创建状态显示区域
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton('开始生成')
        self.start_button.clicked.connect(self.start_generation)
        
        self.clear_button = QPushButton('清除日志')
        self.clear_button.clicked.connect(self.clear_status)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)

    def update_status(self, message):
        """更新状态信息"""
        self.status_text.append(message)

    def start_generation(self):
        """开始生成视频（示例）"""
        self.update_status("开始生成视频...")
        params = {"team_id": TEAM_ID}
        task_id = self.video_generator.generate_video(params)
        if task_id:
            self.update_status(f"任务ID: {task_id}")
            self.update_status("当前状态: 处理中...")
        else:
            self.update_status("视频生成失败，请检查网络连接或API配置")

    def clear_status(self):
        """清除状态信息"""
        self.status_text.clear()

def main():
    app = QApplication(sys.argv)
    window = VideoGeneratorGUI()
    window.show()  # 确保调用 show() 方法
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
