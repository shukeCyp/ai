import datetime
from peewee import *

import logging

from loguru import logger
# from database import Base

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

logging.basicConfig(handlers=[InterceptHandler()], level=0)

db = MySQLDatabase('ai', user='root', password='abc@123456',
                         host='rm-f8zh0u32x2cb40fqb3o.mysql.rds.aliyuncs.com', port=3306)

class BaseModel(Model):
    class Meta:
        database = db

# 添加新的模型，对应 schema.sql 中的表

class RunwayAccount(BaseModel):
    username = CharField(max_length=255)
    password = CharField(max_length=255)
    as_team_id = CharField(max_length=255)
    token = CharField(max_length=255)
    plan_expires = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'runway_account'

class RunwaySession(BaseModel):
    runway = ForeignKeyField(RunwayAccount, backref='sessions')
    session_id = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'runway_session'

class User(BaseModel):
    username = CharField(max_length=255)
    password = CharField(max_length=255)
    mac = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'user'

class Admin(BaseModel):
    user = ForeignKeyField(User, backref='admins')
    username = CharField(max_length=255)
    password = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'admin'

class UserCarmine(BaseModel):
    user = ForeignKeyField(User, backref='carmines', null=True)
    carmine = CharField(max_length=255)
    duration = IntegerField(help_text='时长（单位：天）')
    created_at = DateTimeField(default=datetime.datetime.now, help_text='创建时间')
    activated_at = DateTimeField(null=True, help_text='激活时间')
    expired_at = DateTimeField(null=True, help_text='过期时间')

    class Meta:
        table_name = 'user_carmine'

class Task(BaseModel):
    user = ForeignKeyField(User, backref='tasks')
    status = IntegerField(default=0, help_text='0-排队中,1-生成中,2-完成')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'task'

class VideoGeneration(BaseModel):
    task = ForeignKeyField(Task, backref='video_generations')
    type = IntegerField(default=0, help_text='0-人物,1-产品')
    user_prompt = TextField(help_text='用户提示词')
    system_prompt = TextField(null=True, help_text='系统提示词')
    category = CharField(max_length=255, null=True, help_text='分类')
    image_url = CharField(max_length=1024, help_text='输入图片URL')
    video_url = CharField(max_length=1024, null=True, help_text='生成视频URL')
    runway_id = CharField(max_length=255, null=True, help_text='Runway任务ID')
    session_id = CharField(max_length=255, null=True, help_text='Runway会话ID')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'video_generation'

class Prompt(BaseModel):
    category = CharField(max_length=255, help_text='分类')
    category_cn = CharField(max_length=255, null=True, help_text='中文分类')
    content = TextField(help_text='提示词')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'prompt'

class ExceptionRequest(BaseModel):
    user = ForeignKeyField(User, backref='exception_requests', null=True, help_text='用户ID')
    ip_address = CharField(max_length=50, null=True, help_text='IP地址')
    request_url = CharField(max_length=1024, help_text='请求URL')
    request_method = CharField(max_length=10, help_text='请求方法')
    request_params = TextField(null=True, help_text='请求参数')
    request_body = TextField(null=True, help_text='请求体')
    error_message = TextField(help_text='错误信息')
    stack_trace = TextField(null=True, help_text='堆栈跟踪')
    http_status = IntegerField(null=True, help_text='HTTP状态码')
    created_at = DateTimeField(default=datetime.datetime.now, help_text='创建时间')

    class Meta:
        table_name = 'exception_request'
class AIVideo(BaseModel):
    user = ForeignKeyField(User, backref='ai_videos', help_text='用户ID')
    prompt = TextField(help_text='提示词')
    resolution = CharField(max_length=20, help_text='分辨率')
    seconds = IntegerField(help_text='视频时长')
    seed = BigIntegerField(help_text='随机种子')
    image_url = CharField(max_length=1024, null=True, help_text='输入图片URL')
    video_url = CharField(max_length=1024, null=True, help_text='生成视频URL')
    status = IntegerField(default=0, help_text='状态:0-排队中,1-生成中,2-完成,3-失败')
    is_deleted = IntegerField(default=0, help_text='是否删除:0-否,1-是')
    runway_id = CharField(max_length=255, null=True, help_text='Runway任务ID')
    created_at = DateTimeField(default=datetime.datetime.now, help_text='创建时间')
    updated_at = DateTimeField(default=datetime.datetime.now, help_text='更新时间')

    class Meta:
        table_name = 'ai_video'