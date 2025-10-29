from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport, SSETransport
import asyncio
import logging
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 通义 联网搜索
# sk-e1b4b3ce55ac474a942f86b4558d5907
# https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch
async def test_sse() -> None:
    """
    使用 SSETransport 连接到服务器，列出所有可用工具及其描述和参数。
    """
    # 请求头
    headers = {
        "Authorization": "Bearer sk-e1b4b3ce55ac474a942f86b4558d5907"
    }

   
    async with Client(SSETransport("https://dashscope.aliyuncs.com/api/v1/mcps/market-cmapi031573/mcp/sse",headers=headers)) as client:
        tools = await client.list_tools()
        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"Description: {tool.description}")
            if tool.inputSchema:
                print(f"Parameters: {tool.inputSchema}")
            print("-" * 50)
    
               
    



if __name__ == "__main__":
    result1 = asyncio.run(test_sse())
    print(result1)
    # result2 = asyncio.run(search_with_bailian("一元二次方程 图片 ",5))
    # print(result2)