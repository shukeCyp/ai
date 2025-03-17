from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from models import Prompt
from loguru import logger
from peewee import fn
import random

router = APIRouter()


class CategoryResponse(BaseModel):
    name: str
    name_cn: str
    count: int


class CategoriesResponse(BaseModel):
    categories: List[CategoryResponse]


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """
    获取所有提示词分类
    
    返回:
    - categories: 分类列表，包含分类名称(英文和中文)和对应的提示词数量
    """
    try:
        logger.info("查询所有提示词分类")
        
        # 查询所有不同的分类及其数量
        query = (Prompt
                .select(Prompt.category, Prompt.category_cn, fn.COUNT(Prompt.id).alias('count'))
                .group_by(Prompt.category, Prompt.category_cn)
                .order_by(fn.COUNT(Prompt.id).desc()))
        
        categories = []
        for result in query:
            categories.append(CategoryResponse(
                name=result.category,
                name_cn=result.category_cn or result.category,  # 如果中文分类为空，则使用英文分类
                count=result.count
            ))
        
        return CategoriesResponse(categories=categories)
    
    except Exception as e:
        logger.error(f"查询提示词分类失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="查询提示词分类失败")


def get_random_prompt(category: str):
    """
    根据分类获取随机提示词
    
    参数:
    - category: 分类的英文名称
    
    返回:
    - 随机选择的提示词信息
    """
    try:
        logger.info(f"查询分类 '{category}' 的随机提示词")
        
        # 查询指定分类的所有提示词
        prompts = list(Prompt.select().where(Prompt.category == category))
        
        if not prompts:
            logger.warning(f"分类 '{category}' 没有找到提示词")
            raise HTTPException(status_code=404, detail=f"分类 '{category}' 没有找到提示词")
        
        # 随机选择一个提示词
        random_prompt = random.choice(prompts)
        
        return random_prompt.content
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取随机提示词失败: {str(e)}")
        logger.exception("详细错误")
        raise HTTPException(status_code=500, detail="获取随机提示词失败")


def get_category_cn_name(category: str) -> str:
    """
    根据英文分类名称获取对应的中文分类名称
    
    参数:
    - category: 分类的英文名称
    
    返回:
    - 分类的中文名称，如果不存在则返回英文名称
    """
    try:
        logger.info(f"查询分类 '{category}' 的中文名称")
        
        # 查询指定分类的中文名称
        prompt = Prompt.get_or_none(Prompt.category == category)
        
        if not prompt:
            logger.warning(f"分类 '{category}' 没有找到")
            return category
        
        return prompt.category_cn or category
    
    except Exception as e:
        logger.error(f"获取分类中文名称失败: {str(e)}")
        logger.exception("详细错误")
        return category
