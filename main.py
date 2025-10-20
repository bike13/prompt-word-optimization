from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from dotenv import load_dotenv
import logging
from pygelf import GelfUdpHandler
from datetime import datetime

# 导入日志配置和中间件
from utils.logger_utils import log_api_call

# 加载环境变量
load_dotenv()


# 创建FastAPI应用
app = FastAPI(title="Prompt Word Optimization", version="1.0.0")

def setup_logging():
    """设置日志配置，包括控制台和Graylog输出"""
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 设置Uvicorn和FastAPI的日志级别，过滤启动信息
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    # 禁用HTTP客户端库的默认日志输出，避免格式不一致
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai._client").setLevel(logging.WARNING)
    
    # 创建日志格式 - 格式：时间戳.毫秒 [ss-log] [线程名] 级别 [源文件:行号] 消息
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d [ss-log] [%(threadName)s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s', 
                                 datefmt='%Y-%m-%d %H:%M:%S')
    
    # 控制台处理器 - 注释掉，避免重复日志
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.INFO)
    # console_handler.setFormatter(formatter)
    # root_logger.addHandler(console_handler)
    
    # Graylog处理器 - 使用标准GelfUdpHandler
    try:
        graylog_handler = GelfUdpHandler(
            host='38.55.97.233',
            port=12201,
            debug=True,
            include_extra_fields=True
        )
        graylog_handler.setLevel(logging.INFO)
        # 为Graylog处理器设置简单格式器，不包含时间戳（因为logger_utils中已手动添加）
        graylog_formatter = logging.Formatter('%(message)s')
        graylog_handler.setFormatter(graylog_formatter)
        
        # 设置根日志记录器的传播属性，确保所有子记录器都使用相同的处理器
        root_logger.propagate = True
        root_logger.addHandler(graylog_handler)

    except Exception as e:
        print(f"错误详情: {type(e).__name__}: {e}")
    
    return root_logger

# 初始化日志系统
root_logger = setup_logging()

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
root_logger.info(f"{timestamp} [ss-log] [MainThread] INFO [prompt-word-optimization.logger] 应用启动，测试Graylog日志输出", extra={
    'app_name': 'prompt-word-optimization',
    'env': 'test',
    'level': 6,
    'level_name': 'INFO',
    'log_type': 'Python',
    'logger_name': 'prompt-word-optimization.logger',
    'marker': 'AI-AGENT',
    'thread_name': 'MainThread',
    'timestamp': timestamp
})



# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from api.opt_controller import router as opt_router
from api.html_controller import router as html_router
from api.doc_controller import router as doc_router

# 注册路由
app.include_router(opt_router, prefix="/api", tags=["optimization"])
app.include_router(html_router, prefix="/api", tags=["html"])
app.include_router(doc_router, prefix="/api/doc", tags=["document"])

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
@log_api_call('/', 'GET')
async def read_root():
    """返回主页面"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/html-fix", response_class=HTMLResponse)
@log_api_call('/html-fix', 'GET')
async def html_fix_page():
    """返回HTML修复页面"""
    with open("static/html_fix.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/prompt", response_class=HTMLResponse)
@log_api_call('/prompt', 'GET')
async def prompt_page():
    """返回提示词优化页面"""
    with open("static/prompt.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/doc", response_class=HTMLResponse)
@log_api_call('/doc', 'GET')
async def doc_page():
    """返回文档分析页面"""
    with open("static/doc.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9080)
