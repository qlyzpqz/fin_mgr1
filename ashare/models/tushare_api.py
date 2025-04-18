from functools import wraps
import time
import logging
from typing import Any, Callable
import tushare as ts
from ashare.logger.setup_logger import get_logger

class TushareAPI:
    def __init__(self, api_token: str, max_retries: int = 3, retry_delay: float = 60.0):
        """
        初始化 TushareAPI 包装类
        
        Args:
            api_token: Tushare API token
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间(秒)
        """
        self.api = ts.pro_api(api_token)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = get_logger()

    def __getattr__(self, name: str) -> Callable:
        """拦截所有对原始 pro_api 对象的方法调用"""
        original_method = getattr(self.api, name)
        
        @wraps(original_method)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(self.max_retries):
                try:
                    return original_method(*args, **kwargs)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        self.logger.error(f"调用 {name} 方法失败，已达到最大重试次数: {str(e)}")
                        raise
                    self.logger.warning(f"调用 {name} 方法失败，正在进行第 {attempt + 1} 次重试: {str(e)}")
                    time.sleep(self.retry_delay)
            
        return wrapper