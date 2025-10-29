from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport, SSETransport
import asyncio


async def test_sse() -> None:
    """
    使用 SSETransport 连接到服务器，列出所有可用工具及其描述和参数。
    """
    async with Client(SSETransport("http://127.0.0.1:9081/sse")) as client:
        tools = await client.list_tools()
        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"Description: {tool.description}")
            if tool.inputSchema:
                print(f"Parameters: {tool.inputSchema}")


# 调用 execute_neo4j_command 工具 ，进行创建节点
async def test_create_neo4j_node() -> None:
    """
    使用 SSETransport 连接到服务器，调用 execute_neo4j_command 工具。
    """
    async with Client(SSETransport("http://127.0.0.1:9081/sse")) as client:
        result = await client.call_tool("execute_neo4j_command", {"query": "CREATE (n:Person {name: 'John', age: 30})"})
        print(result)

# 调用 execute_neo4j_command 工具 ，进行删除节点
async def test_delete_neo4j_node() -> None:
    """
    使用 SSETransport 连接到服务器，调用 execute_neo4j_command 工具。
    """
    async with Client(SSETransport("http://127.0.0.1:9081/sse")) as client:
        result = await client.call_tool("execute_neo4j_command", {"query": "MATCH (n:Person {name: 'John'}) DETACH DELETE n"})
        print(result)

# 调用 execute_neo4j_command 工具 ，进行更新节点
async def test_update_neo4j_node() -> None:
    """
    使用 SSETransport 连接到服务器，调用 execute_neo4j_command 工具。
    """
    async with Client(SSETransport("http://127.0.0.1:9081/sse")) as client:
        result = await client.call_tool("execute_neo4j_command", {"query": "MATCH (n:Person {name: 'John'}) SET n.age = 31"})
        print(result)

# 调用 execute_neo4j_command 工具 ，进行查询
async def test_query_neo4j_node() -> None:
    """
    使用 SSETransport 连接到服务器，调用 execute_neo4j_command 工具。
    """
    async with Client(SSETransport("http://127.0.0.1:9081/sse")) as client:
        result = await client.call_tool("execute_neo4j_command", {"query": "MATCH (n) RETURN n"})
        print(result)



if __name__ == "__main__":
    # result1 = asyncio.run(test_sse())
    # print(result1)
    result2 = asyncio.run(test_create_neo4j_node())
    print(result2)
    # result3 = asyncio.run(test_delete_neo4j_node())
    # print(result3)
    # result4 = asyncio.run(test_update_neo4j_node())
    # print(result4)
    # result5 = asyncio.run(test_query_neo4j_node())
    # print(result5)
