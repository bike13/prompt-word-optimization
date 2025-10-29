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
        "Authorization": "Bearer sk-e1b4b3ce55ac474a942f86b4558d5907",
        "Content-Type": "application/json"
    }

   
    async with Client(SSETransport("https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/sse",headers=headers)) as client:
        tools = await client.list_tools()
        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"Description: {tool.description}")
            if tool.inputSchema:
                print(f"Parameters: {tool.inputSchema}")
            print("-" * 50)
    
def extract_images_from_url(url: str) -> list:
    """
    从网页URL中提取图片链接
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images = []
        
        # 查找所有图片标签
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-src')
            if src:
                # 处理相对URL
                full_url = urljoin(url, src)
                images.append({
                    'url': full_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
        
        return images
    except Exception as e:
        logger.error(f"获取图片失败 {url}: {e}")
        return []

def download_image(image_url: str, save_dir: str = "images") -> str:
    """
    下载图片到本地
    """
    try:
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 获取文件名
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            filename = f"image_{hash(image_url) % 10000}.jpg"
        
        filepath = os.path.join(save_dir, filename)
        
        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"图片已保存: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"下载图片失败 {image_url}: {e}")
        return None

async def search_with_bailian(query: str, count: int = 5) -> None:
    """
    使用 bailian_web_search 工具进行搜索，并提取网页图片
    """
    # 请求头
    headers = {
        "Authorization": "Bearer sk-e1b4b3ce55ac474a942f86b4558d5907",
        "Content-Type": "application/json"
    }

    logger.info(f"正在搜索: {query}")
    async with Client(SSETransport("https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/sse", headers=headers)) as client:
        # 调用 bailian_web_search 工具
        result = await client.call_tool("bailian_web_search", {
            "query": query,
            "count": count
        })
        
        print(f"搜索查询: {query}")
        print(f"搜索结果数量: {count}")
        print("=" * 60)
        
        if result and hasattr(result, 'content'):
            for i, content in enumerate(result.content, 1):
                print(f"结果 {i}:")
                content_text = content.text if hasattr(content, 'text') else str(content)
                print(content_text)
                
                # 尝试从结果中提取URL
                try:
                    # 如果结果是JSON格式，解析它
                    if isinstance(content_text, str) and content_text.strip().startswith('{'):
                        data = json.loads(content_text)
                        if 'pages' in data:
                            for page in data['pages']:
                                if 'url' in page:
                                    url = page['url']
                                    print(f"  发现网页URL: {url}")
                                    
                                    # 获取网页图片
                                    images = extract_images_from_url(url)
                                    if images:
                                        print(f"  找到 {len(images)} 张图片:")
                                        for j, img in enumerate(images[:3], 1):  # 只显示前3张
                                            print(f"    图片 {j}: {img['url']}")
                                            if img['alt']:
                                                print(f"      描述: {img['alt']}")
                                            
                                            # 下载图片（可选）
                                            try:
                                                saved_path = download_image(img['url'], f"images/{query.replace(' ', '_')}")
                                                if saved_path:
                                                    print(f"      已保存到: {saved_path}")
                                            except Exception as e:
                                                print(f"      下载失败: {e}")
                                    else:
                                        print(f"  未找到图片")
                                    print("-" * 40)
                except json.JSONDecodeError:
                    # 如果不是JSON，尝试用正则表达式提取URL
                    import re
                    urls = re.findall(r'https?://[^\s<>"]+', content_text)
                    for url in urls[:3]:  # 只处理前3个URL
                        print(f"  发现URL: {url}")
                        images = extract_images_from_url(url)
                        if images:
                            print(f"  找到 {len(images)} 张图片:")
                            for j, img in enumerate(images[:3], 1):  # 只显示前3张
                                print(f"    图片 {j}: {img['url']}")
                        print("-" * 40)
                except Exception as e:
                    logger.error(f"处理结果时出错: {e}")
                
                print("-" * 40)
        else:
            print("搜索结果:", result)
                
    



if __name__ == "__main__":
    # result1 = asyncio.run(test_sse())
    # print(result1)
    result2 = asyncio.run(search_with_bailian("一元二次方程 图片 ",5))
    print(result2)