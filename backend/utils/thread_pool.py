import threading
import queue
import time
import traceback
import asyncio
from typing import Callable, Any, List, Optional
from concurrent.futures import Future
from loguru import logger

class Task:
    """表示要在线程池中执行的任务"""
    def __init__(self, func: Callable, args: tuple = (), kwargs: dict = None):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.future = Future()
    
    def execute(self):
        """执行任务并设置结果到future"""
        try:
            logger.info(f"执行任务，函数: {self.func.__name__}, 参数: {self.args}, {self.kwargs}")
            # 确保函数被实际调用
            if asyncio.iscoroutinefunction(self.func):
                # 如果是异步函数，使用同步方式运行
                result = asyncio.run(self.func(*self.args, **self.kwargs))
            else:
                # 普通函数直接调用
                result = self.func(*self.args, **self.kwargs)
            logger.info(f"任务执行结果: {result}")
            self.future.set_result(result)
        except Exception as e:
            logger.error(f"任务执行异常: {str(e)}")
            logger.error(traceback.format_exc())
            self.future.set_exception(e)

class Worker(threading.Thread):
    """工作线程，从任务队列获取任务并执行"""
    def __init__(self, task_queue: queue.Queue, name: str = None):
        super().__init__(name=name)
        self.task_queue = task_queue
        self.daemon = True  # 设置为守护线程，主线程结束时自动退出
        self._stop_event = threading.Event()
    
    def run(self):
        """线程主循环，不断从队列获取任务执行"""
        while not self._stop_event.is_set():
            try:
                # 从队列获取任务，最多等待1秒
                task = self.task_queue.get(timeout=1)
                try:
                    logger.debug(f"线程 {self.name} 开始执行任务")
                    task.execute()
                    logger.debug(f"线程 {self.name} 完成任务")
                finally:
                    # 无论任务是否成功，都标记为完成
                    self.task_queue.task_done()
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                logger.error(f"工作线程异常: {str(e)}")
                logger.error(traceback.format_exc())
    
    def stop(self):
        """停止工作线程"""
        self._stop_event.set()

class ThreadPool:
    """线程池，管理工作线程并分配任务"""
    def __init__(self, max_workers: int = 10, queue_size: int = 100, thread_name_prefix: str = "Worker"):
        """
        初始化线程池
        
        Args:
            max_workers: 最大工作线程数
            queue_size: 任务队列最大长度，0表示无限
            thread_name_prefix: 工作线程名称前缀
        """
        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        self.task_queue = queue.Queue(maxsize=queue_size)
        self.workers: List[Worker] = []
        self.running = False
        self._lock = threading.RLock()
    
    def start(self):
        """启动线程池"""
        with self._lock:
            if self.running:
                return
            
            self.running = True
            # 创建并启动工作线程
            for i in range(self.max_workers):
                worker = Worker(self.task_queue, name=f"{self.thread_name_prefix}-{i+1}")
                self.workers.append(worker)
                worker.start()
            
            logger.info(f"线程池已启动，工作线程数: {self.max_workers}")
    
    def submit(self, func: Callable, *args, **kwargs) -> Future:
        """
        提交任务到线程池
        
        Args:
            func: 要执行的函数
            args: 位置参数
            kwargs: 关键字参数
            
        Returns:
            Future对象，可用于获取任务结果
            
        Raises:
            RuntimeError: 如果线程池未启动
            queue.Full: 如果队列已满且设置了最大队列长度
        """
        logger.info(f"提交任务到线程池，函数: {func.__name__}, 参数: {args}, {kwargs}")
        if not self.running:
            # 如果线程池未启动，先启动线程池
            logger.warning("线程池未启动，正在自动启动")
            self.start()
        
        task = Task(func, args, kwargs)
        self.task_queue.put(task)
        logger.debug(f"任务已提交到队列，当前队列长度: {self.task_queue.qsize()}")
        return task.future
    
    def submit_nowait(self, func: Callable, *args, **kwargs) -> Optional[Future]:
        """
        提交任务到线程池，如果队列已满则立即返回None而不阻塞
        
        Args:
            func: 要执行的函数
            args: 位置参数
            kwargs: 关键字参数
            
        Returns:
            Future对象，可用于获取任务结果；如果队列已满则返回None
        """
        if not self.running:
            # 如果线程池未启动，先启动线程池
            logger.warning("线程池未启动，正在自动启动")
            self.start()
        
        task = Task(func, args, kwargs)
        try:
            self.task_queue.put_nowait(task)
            logger.debug(f"任务已提交到队列，当前队列长度: {self.task_queue.qsize()}")
            return task.future
        except queue.Full:
            logger.warning("任务队列已满，任务被丢弃")
            return None
    
    def shutdown(self, wait: bool = True):
        """
        关闭线程池
        
        Args:
            wait: 是否等待所有任务完成
        """
        with self._lock:
            if not self.running:
                return
            
            self.running = False
            
            # 停止所有工作线程
            for worker in self.workers:
                worker.stop()
            
            if wait:
                # 等待队列中的任务完成
                self.task_queue.join()
            
            # 清空工作线程列表
            self.workers.clear()
            
            logger.info("线程池已关闭")
    
    def wait_completion(self, timeout: Optional[float] = None) -> bool:
        """
        等待所有任务完成
        
        Args:
            timeout: 超时时间（秒），None表示无限等待
            
        Returns:
            是否所有任务都已完成
        """
        if not self.running:
            return True
        
        try:
            start_time = time.time()
            while not self.task_queue.empty():
                if timeout is not None and time.time() - start_time > timeout:
                    return False
                time.sleep(0.1)
            return True
        except:
            return False
    
    def get_queue_size(self) -> int:
        """获取当前队列中的任务数量"""
        return self.task_queue.qsize()
    
    def get_active_workers(self) -> int:
        """获取当前活动的工作线程数量"""
        return sum(1 for worker in self.workers if worker.is_alive())
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

# 创建一个全局线程池实例
global_thread_pool = ThreadPool(max_workers=20, queue_size=1000)
# 确保线程池在创建时就启动
global_thread_pool.start()

# 在应用退出时关闭线程池
import atexit
atexit.register(global_thread_pool.shutdown) 