# -*- coding: utf-8 -*-
"""
统一日志输出工具类
提供结构化的日志记录功能，支持 Graylog 输出
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str = "susheng-ai-agent"):
        """
        初始化结构化日志记录器
        
        Args:
            name: 日志记录器名称
        """
        self.logger = logging.getLogger(name)
        self.service_name = "prompt-word-optimization"
        self.source = "prompt-word-optimization-logs"
        
        # 不添加额外的处理器，使用根日志记录器的配置
        # 这样可以确保所有日志都使用统一的格式
        self.logger.setLevel(logging.INFO)
        
        # 确保使用根日志记录器的处理器
        root_logger = logging.getLogger()
        if not self.logger.handlers:
            # 如果当前记录器没有处理器，则使用根记录器的处理器
            for handler in root_logger.handlers:
                self.logger.addHandler(handler)
        
        # 确保日志级别设置正确
        self.logger.setLevel(logging.INFO)
    
    def _get_base_extra(self, **kwargs) -> Dict[str, Any]:
        """
        获取基础额外字段
        
        Args:
            **kwargs: 额外的字段
            
        Returns:
            包含基础字段的字典
        """
        base_extra = {
            'app_name': 'prompt-word-optimization',
            'env': 'test',
            'level': 6,  # INFO level
            'level_name': 'INFO',
            'log_type': 'Python',
            'logger_name': f'{self.service_name}.logger',
            'marker': 'AI-AGENT',
            'thread_name': kwargs.get('thread_name', 'MainThread')
        }
        # 只添加特定的额外字段，避免添加过多信息
        if 'method' in kwargs:
            base_extra['method'] = kwargs['method']
        return base_extra
    
    def info(self, message: str, **kwargs):
        """记录 INFO 级别日志"""
        extra = self._get_base_extra(**kwargs)
        # 使用根日志记录器确保消息被正确发送到Graylog
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.info(f"{timestamp} [ss-log] [MainThread] INFO [{self.service_name}.logger] {message}", extra=extra)
    
    def debug(self, message: str, **kwargs):
        """记录 DEBUG 级别日志"""
        extra = self._get_base_extra(**kwargs)
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.debug(f"{timestamp} [ss-log] [MainThread] DEBUG [{self.service_name}.logger] {message}", extra=extra)
    
    def warning(self, message: str, **kwargs):
        """记录 WARNING 级别日志"""
        extra = self._get_base_extra(**kwargs)
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.warning(f"{timestamp} [ss-log] [MainThread] WARNING [{self.service_name}.logger] {message}", extra=extra)
    
    def error(self, message: str, **kwargs):
        """记录 ERROR 级别日志"""
        extra = self._get_base_extra(**kwargs)
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.error(f"{timestamp} [ss-log] [MainThread] ERROR [{self.service_name}.logger] {message}", extra=extra)
    
    def critical(self, message: str, **kwargs):
        """记录 CRITICAL 级别日志"""
        extra = self._get_base_extra(**kwargs)
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.critical(f"{timestamp} [ss-log] [MainThread] CRITICAL [{self.service_name}.logger] {message}", extra=extra)
    
    def api_request(self, endpoint: str, method: str, client_ip: str = None, 
                   request_data: Dict[str, Any] = None, **kwargs):
        """
        记录 API 请求日志
        
        Args:
            endpoint: API 端点
            method: HTTP 方法
            client_ip: 客户端 IP
            request_data: 请求数据
            **kwargs: 其他额外字段
        """
        extra = self._get_base_extra(
            log_type='api_request',
            endpoint=endpoint,
            method=method,
            client_ip=client_ip,
            request_data=request_data,
            **kwargs
        )
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.info(f"{timestamp} [ss-log] [MainThread] INFO [{self.service_name}.logger] ==> Preparing: {method} {endpoint}", extra=extra)
    
    def api_response(self, endpoint: str, method: str, status_code: int, 
                    response_time: float = None, **kwargs):
        """
        记录 API 响应日志
        
        Args:
            endpoint: API 端点
            method: HTTP 方法
            status_code: 响应状态码
            response_time: 响应时间（秒）
            **kwargs: 其他额外字段
        """
        extra = self._get_base_extra(
            log_type='api_response',
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            **kwargs
        )
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.info(f"{timestamp} [ss-log] [MainThread] INFO [{self.service_name}.logger] <== Total: {status_code} - {method} {endpoint}", extra=extra)
    
    def api_error(self, endpoint: str, method: str, error: str, 
                 error_type: str = None, **kwargs):
        """
        记录 API 错误日志
        
        Args:
            endpoint: API 端点
            method: HTTP 方法
            error: 错误信息
            error_type: 错误类型
            **kwargs: 其他额外字段
        """
        extra = self._get_base_extra(
            log_type='api_error',
            endpoint=endpoint,
            method=method,
            error=error,
            error_type=error_type,
            **kwargs
        )
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.error(f"{timestamp} [ss-log] [MainThread] ERROR [{self.service_name}.logger] ==> Parameters: {error}(String), {method}(String), {endpoint}(String)", extra=extra)
    
    def database_operation(self, operation: str, table: str = None, 
                          affected_rows: int = None, **kwargs):
        """
        记录数据库操作日志
        
        Args:
            operation: 操作类型（SELECT, INSERT, UPDATE, DELETE）
            table: 表名
            affected_rows: 影响的行数
            **kwargs: 其他额外字段
        """
        extra = self._get_base_extra(
            log_type='database_operation',
            operation=operation,
            table=table,
            affected_rows=affected_rows,
            **kwargs
        )
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.info(f"{timestamp} [ss-log] [MainThread] INFO [{self.service_name}.logger] ==> Preparing: {operation} {table or ''}", extra=extra)
    
    def model_inference(self, model_name: str, input_tokens: int = None, 
                       output_tokens: int = None, response_time: float = None, **kwargs):
        """
        记录模型推理日志
        
        Args:
            model_name: 模型名称
            input_tokens: 输入 token 数
            output_tokens: 输出 token 数
            response_time: 响应时间（秒）
            **kwargs: 其他额外字段
        """
        extra = self._get_base_extra(
            log_type='model_inference',
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time=response_time,
            **kwargs
        )
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.info(f"{timestamp} [ss-log] [MainThread] INFO [{self.service_name}.logger] ==> Preparing: {model_name}", extra=extra)
    
    def business_logic(self, operation: str, details: str = None, **kwargs):
        """
        记录业务逻辑日志
        
        Args:
            operation: 操作名称
            details: 详细信息
            **kwargs: 其他额外字段
        """
        extra = self._get_base_extra(
            log_type='business_logic',
            operation=operation,
            details=details,
            **kwargs
        )
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        details_info = f" - {details}" if details else ""
        root_logger.info(f"{timestamp} [ss-log] [MainThread] INFO [{self.service_name}.logger] ==> Preparing: {operation}{details_info}", extra=extra)
    
    def parameters(self, *params, **kwargs):
        """
        记录参数日志 - 格式：Parameters: 参数1(类型), 参数2(类型), ...
        
        Args:
            *params: 参数列表，每个参数可以是字符串或元组(值, 类型)
            **kwargs: 其他额外字段
        """
        extra = self._get_base_extra(
            log_type='parameters',
            **kwargs
        )
        
        # 格式化参数
        formatted_params = []
        for param in params:
            if isinstance(param, tuple) and len(param) == 2:
                value, param_type = param
                formatted_params.append(f"{value}({param_type})")
            else:
                formatted_params.append(f"{param}(String)")
        
        param_string = ", ".join(formatted_params)
        root_logger = logging.getLogger()
        # 手动添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        root_logger.debug(f"{timestamp} [ss-log] [MainThread] DEBUG [{self.service_name}.logger] ==> Parameters: {param_string}", extra=extra)


# 创建全局日志记录器实例
logger = StructuredLogger()

# 确保全局日志记录器使用根日志记录器的处理器
def ensure_logger_handlers():
    """确保全局日志记录器使用根日志记录器的处理器"""
    root_logger = logging.getLogger()
    if root_logger.handlers and not logger.logger.handlers:
        for handler in root_logger.handlers:
            logger.logger.addHandler(handler)
        logger.logger.setLevel(logging.INFO)

# 初始化处理器
ensure_logger_handlers()


def log_api_call(endpoint: str, method: str = "POST"):
    """
    API 调用日志装饰器 - 只记录核心接口调用信息
    
    Args:
        endpoint: API 端点
        method: HTTP 方法
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取请求对象
            request = None
            for arg in args:
                if hasattr(arg, 'client') and hasattr(arg, 'method'):
                    request = arg
                    break
            
            client_ip = "unknown"
            if request and hasattr(request, 'client') and request.client:
                client_ip = request.client.host
            
            start_time = datetime.now()
            
            # 记录API请求日志
            logger.api_request(
                endpoint=endpoint,
                method=method,
                client_ip=client_ip,
                status="processing"
            )
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 计算响应时间
                response_time = (datetime.now() - start_time).total_seconds()
                
                # 记录成功的API响应
                logger.api_response(
                    endpoint=endpoint,
                    method=method,
                    status_code=200,
                    response_time=response_time
                )
                
                return result
                
            except Exception as e:
                # 计算响应时间
                response_time = (datetime.now() - start_time).total_seconds()
                
                # 记录错误响应
                logger.api_error(
                    endpoint=endpoint,
                    method=method,
                    error=str(e),
                    error_type=type(e).__name__,
                    response_time=response_time
                )
                
                raise
        
        return wrapper
    return decorator
