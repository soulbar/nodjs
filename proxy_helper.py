"""
代理辅助模块 - 用于构建代理连接
"""
import base64
import json
from typing import Dict, Optional


class ProxyHelper:
    """代理辅助类"""
    
    @staticmethod
    def build_proxy_url(node: Dict) -> Optional[str]:
        """构建代理 URL"""
        node_type = node.get('type', '').lower()
        server = node.get('server', '')
        port = node.get('port', '')
        
        if not server or not port:
            return None
        
        if node_type == 'ss':
            method = node.get('method', '')
            password = node.get('password', '')
            if method and password:
                # SS 代理格式: ss://method:password@server:port
                auth = base64.b64encode(f"{method}:{password}".encode()).decode()
                return f"http://{auth}@{server}:{port}"
        
        elif node_type == 'socks5':
            username = node.get('username', '')
            password = node.get('password', '')
            if username and password:
                return f"socks5://{username}:{password}@{server}:{port}"
            else:
                return f"socks5://{server}:{port}"
        
        elif node_type == 'http' or node_type == 'https':
            username = node.get('username', '')
            password = node.get('password', '')
            if username and password:
                return f"{node_type}://{username}:{password}@{server}:{port}"
            else:
                return f"{node_type}://{server}:{port}"
        
        return None
    
    @staticmethod
    def parse_vmess_link(link: str) -> Optional[Dict]:
        """解析 VMess 链接"""
        try:
            if not link.startswith('vmess://'):
                return None
            
            encoded = link[8:]  # 移除 'vmess://' 前缀
            # 补齐 base64 padding
            padding = 4 - len(encoded) % 4
            if padding != 4:
                encoded += '=' * padding
            
            decoded = base64.b64decode(encoded).decode('utf-8')
            config = json.loads(decoded)
            
            return {
                'type': 'vmess',
                'server': config.get('add', ''),
                'port': config.get('port', ''),
                'uuid': config.get('id', ''),
                'alterId': config.get('aid', ''),
                'network': config.get('net', 'tcp'),
                'config': config,
                'raw': link
            }
        except Exception as e:
            return None
    
    @staticmethod
    def parse_ss_link(link: str) -> Optional[Dict]:
        """解析 SS 链接"""
        try:
            if not link.startswith('ss://'):
                return None
            
            encoded = link[5:]  # 移除 'ss://' 前缀
            
            # 处理带 @ 的格式
            if '@' in encoded:
                parts = encoded.split('@')
                if len(parts) == 2:
                    auth_part = parts[0]
                    server_part = parts[1]
                    
                    # 补齐 base64 padding
                    padding = 4 - len(auth_part) % 4
                    if padding != 4:
                        auth_part += '=' * padding
                    
                    try:
                        decoded_auth = base64.b64decode(auth_part).decode('utf-8')
                        if ':' in decoded_auth:
                            method, password = decoded_auth.split(':', 1)
                            if ':' in server_part:
                                server, port = server_part.rsplit(':', 1)
                                return {
                                    'type': 'ss',
                                    'server': server,
                                    'port': int(port),
                                    'method': method,
                                    'password': password,
                                    'raw': link
                                }
                    except:
                        pass
            
            return None
        except Exception as e:
            return None

