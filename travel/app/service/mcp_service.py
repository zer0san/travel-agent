from mcp.server.fastmcp import FastMCP
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

_mcp_client = None
_tools_cache = None

def get_mcp_client():
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MultiServerMCPClient(
            {
                "gaode": {
                    "transport" : "streamable_http",
                    "url":f"https://mcp.amap.com/mcp?key={os.getenv('GAODE_API_KEY')}"
                }
            }
        )
    return _mcp_client

async def get_mcp_tools():
    global _tools_cache
    if _tools_cache is None:
        client = get_mcp_client()
        _tools_cache = await client.get_tools()
    return _tools_cache

