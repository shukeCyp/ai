import os
import json
import random
import threading
import time
from typing import List, Optional, Dict, Any
from loguru import logger
from models import RunwayAccount
from datetime import datetime

class AccountPool:
    """
    账号池类，用于管理多线程环境下的账号分配和回收
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AccountPool, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._lock = threading.RLock()  # 使用可重入锁
        self._available_accounts: List[Dict[str, Any]] = []  # 可用账号列表
        self._in_use_accounts: Dict[str, Dict[str, Any]] = {}  # 正在使用的账号，键为账号ID和实例ID的组合
        self._removed_accounts: Dict[int, str] = {}  # 被移除的账号，键为账号ID，值为移除原因
        self._initialized = True
        self._refresh_interval = 60  # 刷新间隔，单位秒
        self._last_refresh_time = 0
        self._instances_per_account = 2  # 每个账号的实例数量

        # 从数据库加载账号
        self._load_accounts()

    @classmethod
    def initialize(cls):
        """初始化账号池，从数据库加载账号"""
        # 使用全局单例实例调用实例方法
        account_pool.initialize_instance()
            
    def initialize_instance(self):
        """实例初始化方法"""
        with self._lock:
            if self._initialized:
                return
            
            self._refresh_accounts()
            self._initialized = True
            logger.info(f"账号池初始化完成，共加载 {len(self._available_accounts)} 个账号实例")
    def _load_accounts(self):
        """从数据库加载账号"""
        try:
            # 获取所有账号
            accounts = list(RunwayAccount.select().dicts())
            
            # 更新可用账号列表，保留已经在使用的账号
            in_use_keys = set(self._in_use_accounts.keys())
            
            # 清空可用账号列表
            self._available_accounts = []
            
            # 创建所有可能的账号实例组合
            all_instances = []
            for account in accounts:
                for instance_id in range(self._instances_per_account):
                    account_instance = account.copy()
                    account_instance['instance_id'] = instance_id
                    account_key = f"{account['id']}_{instance_id}"
                    if account_key not in in_use_keys:
                        all_instances.append(account_instance)
            
            # 随机打乱所有实例的顺序
            random.shuffle(all_instances)
            
            # 将打乱后的实例添加到可用列表
            self._available_accounts = all_instances
            
            self._last_refresh_time = time.time()
            logger.debug(f"账号池刷新完成，可用账号实例: {len(self._available_accounts)}，使用中账号实例: {len(self._in_use_accounts)}")
        except Exception as e:
            logger.error(f"刷新账号池失败: {str(e)}")
            self._available_accounts = []

    def _refresh_accounts(self):
        """从数据库刷新账号列表"""
        current_time = time.time()
        # 如果距离上次刷新时间不足刷新间隔，则不刷新
        if current_time - self._last_refresh_time < self._refresh_interval:
            return
            
        try:
            # 获取所有账号
            accounts = RunwayAccount.select().dicts()
            
            # 更新可用账号列表，保留已经在使用的账号
            in_use_keys = set(self._in_use_accounts.keys())
            
            # 清空可用账号列表
            self._available_accounts = []
            
            # 为每个账号创建多个实例
            for account in accounts:
                for instance_id in range(self._instances_per_account):
                    # 创建账号实例，添加实例ID
                    account_instance = account.copy()
                    account_instance['instance_id'] = instance_id
                    
                    # 生成唯一键
                    account_key = f"{account['id']}_{instance_id}"
                    
                    # 如果账号实例不在使用中，则添加到可用列表
                    if account_key not in in_use_keys:
                        self._available_accounts.append(account_instance)
            
            self._last_refresh_time = current_time
            logger.debug(f"账号池刷新完成，可用账号实例: {len(self._available_accounts)}，使用中账号实例: {len(self._in_use_accounts)}")
        except Exception as e:
            logger.error(f"刷新账号池失败: {str(e)}")

    def get_account(self) -> Optional[Dict[str, Any]]:
        """
        获取一个可用账号
        
        Returns:
            Dict[str, Any] | None: 账号信息字典，如果没有可用账号则返回None
        """
        with self._lock:
            if not self._initialized:
                self.initialize()
                
            # 如果没有可用账号，尝试刷新
            if not self._available_accounts:
                self._refresh_accounts()
                
            if not self._available_accounts:
                logger.warning("没有可用账号")
                return None
                
            # 从可用账号列表中取出一个账号
            account = self._available_accounts.pop(0)
            
            # 生成唯一键
            account_key = f"{account['id']}_{account['instance_id']}"
            
            # 将账号标记为使用中
            self._in_use_accounts[account_key] = account
            
            logger.debug(f"分配账号 ID: {account['id']}, 实例ID: {account['instance_id']}, 用户名: {account['username']}")
            return account

    def release_account(self, account_id: int):
        """
        释放一个账号，将其归还到可用账号池
        
        Args:
            account_id: 账号ID
        """
        with self._lock:
            if not self._initialized:
                logger.warning("账号池未初始化，无法释放账号")
                return
            
            # 查找所有匹配的账号实例
            matching_keys = [key for key in self._in_use_accounts.keys() if key.startswith(f"{account_id}_")]
            
            if not matching_keys:
                logger.warning(f"尝试释放不存在或未被使用的账号 ID: {account_id}")
                return
            
            # 释放第一个匹配的账号实例
            account_key = matching_keys[0]
            account = self._in_use_accounts.pop(account_key)
            self._available_accounts.append(account)
            logger.debug(f"释放账号 ID: {account_id}, 实例ID: {account['instance_id']}, 用户名: {account['username']}")

    def remove_account(self, account_id: int, reason: str = "未指定原因"):
        """
        从账号池中移除一个账号（不操作数据库）
        
        Args:
            account_id: 要移除的账号ID
            reason: 移除原因
        """
        with self._lock:
            # 记录是否找到并移除了账号
            removed = False
            
            # 从可用账号列表中移除所有匹配的账号实例
            for account in self._available_accounts[:]:
                if account['id'] == account_id:
                    self._available_accounts.remove(account)
                    removed = True
            
            # 从使用中账号列表中移除所有匹配的账号实例
            keys_to_remove = []
            for key, account in self._in_use_accounts.items():
                if account['id'] == account_id:
                    keys_to_remove.append(key)
                    removed = True
            
            for key in keys_to_remove:
                del self._in_use_accounts[key]
            
            if removed:
                # 记录移除原因
                self._removed_accounts[account_id] = reason
                logger.info(f"从账号池移除账号 ID: {account_id}, 原因: {reason}")
            else:
                logger.warning(f"账号 ID: {account_id} 不在账号池中，无法移除")

    def add_account(self, account_id: int):
        """
        将数据库中的账号添加到账号池（不操作数据库）
        
        Args:
            account_id: 要添加的账号ID
        
        Returns:
            bool: 添加是否成功
        """
        with self._lock:
            # 检查账号是否已在可用池中
            for account in self._available_accounts:
                if account['id'] == account_id:
                    logger.warning(f"账号 ID: {account_id} 已经在可用池中")
                    return False
            
            # 检查账号是否在使用中
            in_use = False
            for key, account in self._in_use_accounts.items():
                if account['id'] == account_id:
                    in_use = True
                    break
                
            if in_use:
                logger.warning(f"账号 ID: {account_id} 正在使用中，无法添加")
                return False
            
            # 从数据库获取账号信息
            try:
                # 从数据库获取账号信息
                account = RunwayAccount.get_or_none(RunwayAccount.id == account_id)
                
                if not account:
                    logger.error(f"账号 ID: {account_id} 在数据库中不存在")
                    return False
                
                # 将账号转换为字典
                account_dict = {
                    'id': account.id,
                    'username': account.username,
                    'password': account.password,
                    'team_id': account.team_id,
                    'status': account.status,
                    'created_at': account.created_at,
                    'updated_at': account.updated_at
                }
                
                # 为账号创建多个实例并添加到可用池
                for instance_id in range(self._instances_per_account):
                    account_instance = account_dict.copy()
                    account_instance['instance_id'] = instance_id
                    self._available_accounts.append(account_instance)
                
                # 如果账号在已移除列表中，则移除
                if account_id in self._removed_accounts:
                    del self._removed_accounts[account_id]
                
                logger.info(f"成功添加账号 ID: {account_id} 到可用池，创建了 {self._instances_per_account} 个实例")
                return True
            except Exception as e:
                logger.error(f"添加账号 ID: {account_id} 失败: {str(e)}")
                return False

    def get_stats(self) -> Dict[str, int]:
        """
        获取账号池统计信息
        
        Returns:
            Dict[str, int]: 包含可用账号数和使用中账号数的字典
        """
        with self._lock:
            # 计算唯一账号ID的数量
            unique_available_ids = set(account['id'] for account in self._available_accounts)
            unique_in_use_ids = set(int(key.split('_')[0]) for key in self._in_use_accounts.keys())
            
            return {
                "available_instances": len(self._available_accounts),
                "in_use_instances": len(self._in_use_accounts),
                "total_instances": len(self._available_accounts) + len(self._in_use_accounts),
                "unique_available": len(unique_available_ids),
                "unique_in_use": len(unique_in_use_ids),
                "unique_total": len(unique_available_ids.union(unique_in_use_ids))
            }

    def get_pool_status(self):
        """
        获取账号池状态
        
        Returns:
            Dict: 包含账号池状态信息的字典
        """
        with self._lock:
            return {
                "available": len(self._available_accounts),
                "in_use": len(self._in_use_accounts),
                "removed": len(self._removed_accounts),
                "total": len(self._available_accounts) + len(self._in_use_accounts) + len(self._removed_accounts)
            }

# 创建全局单例实例
account_pool = AccountPool() 