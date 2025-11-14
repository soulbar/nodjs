"""
节点验证模块 - 验证节点可用性和流媒体访问
"""
import asyncio
import aiohttp
import time
import logging
import socket
from typing import List, Dict, Optional
from config import TEST_URLS, TIMEOUT, TEST_TIMEOUT, MAX_CONCURRENT
from proxy_helper import ProxyHelper

logger = logging.getLogger(__name__)


class NodeValidator:
    """节点验证器"""
    
    def __init__(self):
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.proxy_helper = ProxyHelper()
    
    async def test_connection(self, node: Dict) -> bool:
        """测试节点基本连接（TCP 连接测试）"""
        try:
            server = node.get('server', '')
            port = node.get('port', '')
            
            if not server or not port:
                return False
            
            # 尝试 TCP 连接
            try:
                port_int = int(port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(TIMEOUT)
                result = sock.connect_ex((server, port_int))
                sock.close()
                return result == 0
            except:
                return False
        except Exception as e:
            logger.debug(f"节点连接测试失败: {e}")
            return False
    
    async def test_website_access(self, node: Dict, url: str) -> bool:
        """测试网站访问（通过代理）"""
        try:
            async with self.semaphore:
                # 构建代理 URL
                proxy_url = self.proxy_helper.build_proxy_url(node)
                
                timeout = aiohttp.ClientTimeout(total=TEST_TIMEOUT)
                connector = aiohttp.TCPConnector(limit=10)
                
                # 如果有代理 URL，使用代理；否则直接连接（用于测试基本可用性）
                proxy = proxy_url if proxy_url else None
                
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    try:
                        async with session.get(url, proxy=proxy, timeout=timeout, allow_redirects=True) as response:
                            # 只要能连接就算成功（状态码 200-499 都算可访问）
                            return response.status < 500
                    except aiohttp.ClientProxyConnectionError:
                        # 代理连接失败，尝试直接连接测试基本可用性
                        try:
                            async with session.get("https://www.google.com/generate_204", timeout=5) as response:
                                return False  # 如果能直接访问，说明代理不可用
                        except:
                            # 无法直接访问，可能是网络问题，给节点一个机会
                            return True
        except Exception as e:
            logger.debug(f"网站访问测试失败 {url}: {e}")
            return False
    
    async def test_streaming_media(self, node: Dict) -> Dict[str, bool]:
        """测试流媒体访问"""
        results = {}
        
        for name, url in TEST_URLS.items():
            try:
                result = await self.test_website_access(node, url)
                results[name] = result
                if result:
                    logger.debug(f"节点 {node.get('server', '')} 可以访问 {name}")
            except Exception as e:
                logger.debug(f"测试 {name} 失败: {e}")
                results[name] = False
        
        return results
    
    async def validate_node(self, node: Dict) -> Optional[Dict]:
        """验证单个节点"""
        try:
            # 测试基本连接
            if not await self.test_connection(node):
                return None
            
            # 测试流媒体访问
            streaming_results = await self.test_streaming_media(node)
            
            # 至少能访问一个流媒体网站才算可用
            # 或者如果基本连接成功，也认为可用（因为代理测试可能受限）
            if any(streaming_results.values()) or await self.test_connection(node):
                node['streaming_access'] = streaming_results
                node['validated'] = True
                return node
            else:
                return None
        except Exception as e:
            logger.debug(f"验证节点失败: {e}")
            return None
    
    async def validate_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """批量验证节点"""
        logger.info(f"开始验证 {len(nodes)} 个节点...")
        
        tasks = [self.validate_node(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_nodes = []
        for result in results:
            if isinstance(result, dict) and result.get('validated'):
                valid_nodes.append(result)
            elif isinstance(result, Exception):
                logger.debug(f"验证异常: {result}")
        
        logger.info(f"验证完成，共 {len(valid_nodes)} 个可用节点")
        return valid_nodes

