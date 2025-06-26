"""
Система логирования и мониторинга для PyRobot backend
Обеспечивает structured logging, метрики производительности и health checks
"""

import logging
import logging.config
import json
import time
import traceback
import psutil
import os
from functools import wraps
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g, jsonify


class StructuredFormatter(logging.Formatter):
    """
    Форматтер для structured logging в JSON формате
    """
    
    def format(self, record):
        # Базовые поля
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Добавляем exception info если есть
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Добавляем extra fields если есть
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
            
        # Добавляем request context если доступен
        if hasattr(g, 'request_id'):
            log_data['request_id'] = g.request_id
            
        return json.dumps(log_data, ensure_ascii=False)


class MetricsCollector:
    """
    Коллектор метрик производительности
    """
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_error': 0,
            'execution_times': [],
            'memory_usage': [],
            'code_executions': 0,
            'robot_operations': 0,
            'errors_by_type': {}
        }
        self.start_time = time.time()
    
    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Записать метрику запроса"""
        self.metrics['requests_total'] += 1
        
        if 200 <= status_code < 400:
            self.metrics['requests_success'] += 1
        else:
            self.metrics['requests_error'] += 1
        
        self.metrics['execution_times'].append({
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'timestamp': time.time()
        })
        
        # Ограничиваем размер списка
        if len(self.metrics['execution_times']) > 1000:
            self.metrics['execution_times'] = self.metrics['execution_times'][-500:]
    
    def record_code_execution(self, duration: float, lines_count: int):
        """Записать метрику выполнения кода"""
        self.metrics['code_executions'] += 1
        # Можно добавить более подробные метрики выполнения кода
    
    def record_robot_operation(self, operation: str):
        """Записать операцию робота"""
        self.metrics['robot_operations'] += 1
    
    def record_error(self, error_type: str, error_message: str):
        """Записать ошибку"""
        if error_type not in self.metrics['errors_by_type']:
            self.metrics['errors_by_type'][error_type] = 0
        self.metrics['errors_by_type'][error_type] += 1
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Получить системные метрики"""
        process = psutil.Process()
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'process_memory_mb': process.memory_info().rss / 1024 / 1024,
            'process_cpu_percent': process.cpu_percent(),
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'uptime_seconds': time.time() - self.start_time
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Получить сводку всех метрик"""
        system_metrics = self.get_system_metrics()
        
        # Вычисляем средние времена выполнения
        recent_executions = [
            ex for ex in self.metrics['execution_times'] 
            if time.time() - ex['timestamp'] < 300  # последние 5 минут
        ]
        
        avg_response_time = 0
        if recent_executions:
            avg_response_time = sum(ex['duration'] for ex in recent_executions) / len(recent_executions)
        
        return {
            'system': system_metrics,
            'application': {
                'requests_total': self.metrics['requests_total'],
                'requests_success': self.metrics['requests_success'],
                'requests_error': self.metrics['requests_error'],
                'success_rate': (
                    self.metrics['requests_success'] / max(self.metrics['requests_total'], 1) * 100
                ),
                'avg_response_time_ms': avg_response_time * 1000,
                'code_executions': self.metrics['code_executions'],
                'robot_operations': self.metrics['robot_operations'],
                'errors_by_type': self.metrics['errors_by_type'],
                'recent_errors_count': sum(self.metrics['errors_by_type'].values())
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# Глобальный экземпляр коллектора метрик
metrics_collector = MetricsCollector()


def setup_logging(app):
    """
    Настройка системы логирования
    """
    
    # Определяем формат логирования в зависимости от окружения
    environment = os.environ.get('ENVIRONMENT', 'development')
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    if environment == 'production':
        # В production используем structured JSON logging
        formatter = StructuredFormatter()
    else:
        # В development используем человеко-читаемый формат
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'
        )
    
    # Основной обработчик
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Настраиваем логгеры приложения
    app_logger = logging.getLogger('PyRobot')
    app_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Приглушаем логи внешних библиотек
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('redis').setLevel(logging.WARNING)
    
    app_logger.info(f"Logging configured for {environment} environment, level: {log_level}")
    
    return app_logger


def request_logging_middleware(app):
    """
    Middleware для логирования запросов и метрик
    """
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = f"{int(time.time() * 1000)}-{id(request)}"
        
        logger = logging.getLogger('PyRobot.Request')
        logger.info(
            "Request started",
            extra={'extra_data': {
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'request_id': g.request_id
            }}
        )
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        
        logger = logging.getLogger('PyRobot.Request')
        
        # Записываем метрики
        metrics_collector.record_request(
            endpoint=request.endpoint or 'unknown',
            method=request.method,
            status_code=response.status_code,
            duration=duration
        )
        
        # Логируем завершение запроса
        log_level = logging.INFO
        if response.status_code >= 400:
            log_level = logging.ERROR
        elif response.status_code >= 300:
            log_level = logging.WARNING
            
        logger.log(
            log_level,
            "Request completed",
            extra={'extra_data': {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration * 1000,
                'response_size': response.calculate_content_length() or 0,
                'request_id': g.request_id
            }}
        )
        
        return response


def log_code_execution(func):
    """
    Декоратор для логирования выполнения кода
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('PyRobot.CodeExecution')
        start_time = time.time()
        
        try:
            logger.info("Code execution started")
            result = func(*args, **kwargs)
            
            duration = time.time() - start_time
            metrics_collector.record_code_execution(duration, 0)  # TODO: добавить подсчет строк
            
            logger.info(
                "Code execution completed successfully",
                extra={'extra_data': {
                    'duration_ms': duration * 1000,
                    'success': True
                }}
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            
            metrics_collector.record_error(error_type, str(e))
            
            logger.error(
                "Code execution failed",
                extra={'extra_data': {
                    'duration_ms': duration * 1000,
                    'error_type': error_type,
                    'error_message': str(e),
                    'success': False
                }},
                exc_info=True
            )
            raise
    
    return wrapper


def log_robot_operation(operation_name: str):
    """
    Декоратор для логирования операций робота
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('PyRobot.Robot')
            
            try:
                logger.debug(f"Robot operation started: {operation_name}")
                result = func(*args, **kwargs)
                
                metrics_collector.record_robot_operation(operation_name)
                logger.debug(f"Robot operation completed: {operation_name}")
                
                return result
                
            except Exception as e:
                logger.error(
                    f"Robot operation failed: {operation_name}",
                    extra={'extra_data': {
                        'operation': operation_name,
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }},
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def create_health_endpoints(app):
    """
    Создание endpoints для мониторинга здоровья системы
    """
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Базовая проверка здоровья"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',  # TODO: получать из конфигурации
            'environment': os.environ.get('ENVIRONMENT', 'development')
        })
    
    @app.route('/health/detailed', methods=['GET'])
    def detailed_health_check():
        """Подробная проверка здоровья с метриками"""
        try:
            # Проверяем различные компоненты системы
            checks = {
                'redis': check_redis_health(),
                'interpreter': check_interpreter_health(),
                'filesystem': check_filesystem_health()
            }
            
            # Определяем общий статус
            overall_status = 'healthy' if all(
                check['status'] == 'healthy' for check in checks.values()
            ) else 'degraded'
            
            return jsonify({
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'checks': checks,
                'metrics': metrics_collector.get_summary()
            })
            
        except Exception as e:
            logger = logging.getLogger('PyRobot.Health')
            logger.error("Health check failed", exc_info=True)
            
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': str(e)
            }), 500
    
    @app.route('/metrics', methods=['GET'])
    def metrics_endpoint():
        """Endpoint для получения метрик (для мониторинговых систем)"""
        return jsonify(metrics_collector.get_summary())


def check_redis_health() -> Dict[str, Any]:
    """Проверка здоровья Redis"""
    try:
        import redis
        redis_client = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=int(os.environ.get('REDIS_PORT', 6379)),
            socket_timeout=2
        )
        redis_client.ping()
        return {'status': 'healthy', 'message': 'Redis connection successful'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Redis connection failed: {str(e)}'}


def check_interpreter_health() -> Dict[str, Any]:
    """Проверка здоровья интерпретатора"""
    try:
        # Простая проверка - можем ли создать интерпретатор с пустым кодом
        from .kumir_interpreter.interpreter import KumirLanguageInterpreter
        interpreter = KumirLanguageInterpreter("")
        return {'status': 'healthy', 'message': 'Interpreter initialization successful'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Interpreter check failed: {str(e)}'}


def check_filesystem_health() -> Dict[str, Any]:
    """Проверка здоровья файловой системы"""
    try:
        # Проверяем доступность для записи
        test_file = '/tmp/pyrobot_health_check.txt'
        with open(test_file, 'w') as f:
            f.write('health check')
        os.remove(test_file)
        
        return {'status': 'healthy', 'message': 'Filesystem access successful'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Filesystem check failed: {str(e)}'}
