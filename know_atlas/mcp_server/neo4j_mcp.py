from fastmcp import FastMCP
from neo4j import GraphDatabase
import os
import json
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="neo4j_query_tool",
    dependencies=["requests"],
    host="0.0.0.0",
    port=9081
)

class Neo4jQueryTool:
    """Neo4j数据库查询工具类"""
    
    def __init__(self):
        """初始化Neo4j连接"""
        # bolt 是 Neo4j 数据库默认的二进制通讯协议名称，这里表示连接到本地的 Neo4j 数据库实例。
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            logger.info(f"成功连接到Neo4j数据库: {self.uri}")
            return True
        except Exception as e:
            logger.error(f"连接Neo4j数据库失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j数据库连接已关闭")
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """执行Cypher查询"""
        if not self.driver:
            if not self.connect():
                return {"error": "无法连接到Neo4j数据库"}
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                
                # 处理查询结果
                records = []
                for record in result:
                    record_dict = {}
                    for key, value in record.items():
                        # 处理Neo4j的特殊数据类型
                        if hasattr(value, 'labels'):
                            # 节点对象
                            record_dict[key] = {
                                "type": "node",
                                "labels": list(value.labels),
                                "properties": dict(value)
                            }
                        elif hasattr(value, 'type'):
                            # 关系对象
                            record_dict[key] = {
                                "type": "relationship",
                                "type_name": value.type,
                                "properties": dict(value)
                            }
                        elif isinstance(value, list):
                            # 列表类型
                            record_dict[key] = [self._serialize_value(item) for item in value]
                        else:
                            record_dict[key] = self._serialize_value(value)
                    records.append(record_dict)
                
                return {
                    "success": True,
                    "records": records,
                    "count": len(records),
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _serialize_value(self, value):
        """序列化Neo4j值"""
        if hasattr(value, 'labels'):
            return {
                "type": "node",
                "labels": list(value.labels),
                "properties": dict(value)
            }
        elif hasattr(value, 'type'):
            return {
                "type": "relationship", 
                "type_name": value.type,
                "properties": dict(value)
            }
        elif isinstance(value, (str, int, float, bool)) or value is None:
            return value
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        else:
            return str(value)


# 创建全局查询工具实例
neo4j_tool = Neo4jQueryTool()

@mcp.tool(description="执行Neo4j 指令，可用于查询、创建、删除节点和关系")
def execute_neo4j_command(query: str, parameters: Optional[Dict] = None) -> str:
    """
    执行Neo4j 查询、创建、删除节点和关系
    
    Args:
        query: 查询、创建、删除节点和关系语句
        parameters: 查询、创建、删除节点和关系参数（可选）
    
    Returns:
        查询结果的JSON字符串
    """
    try:
        result = neo4j_tool.execute_query(query, parameters)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"查询工具执行失败: {e}")
        return json.dumps({
            "success": False,
            "error": f"查询工具执行失败: {str(e)}",
            "query": query
        }, ensure_ascii=False, indent=2)





if __name__ == "__main__":
    mcp.run(
        transport="sse",
    )