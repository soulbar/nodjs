"""
GitHub 节点爬虫模块
"""
import re
import requests
import base64
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class GitHubNodeCrawler:
    """从 GitHub 爬取节点"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_github_file_content(self, repo: str, file_path: str) -> str:
        """获取 GitHub 文件内容"""
        try:
            # 使用 GitHub API
            api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('encoding') == 'base64':
                    content = base64.b64decode(data['content']).decode('utf-8')
                    return content
            return ""
        except Exception as e:
            logger.error(f"获取文件内容失败 {repo}/{file_path}: {e}")
            return ""
    
    def search_github_files(self, repo: str, pattern: str = "*.yaml,*.yml,*.txt") -> List[str]:
        """搜索 GitHub 仓库中的文件"""
        try:
            api_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code != 200:
                # 尝试 master 分支
                api_url = f"https://api.github.com/repos/{repo}/git/trees/master?recursive=1"
                response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                files = []
                for item in data.get('tree', []):
                    if item['type'] == 'blob':
                        path = item['path']
                        if any(path.endswith(ext) for ext in ['.yaml', '.yml', '.txt', '.json']):
                            files.append(path)
                return files
            return []
        except Exception as e:
            logger.error(f"搜索文件失败 {repo}: {e}")
            return []
    
    def parse_clash_config(self, content: str) -> List[Dict]:
        """解析 Clash 配置文件"""
        nodes = []
        try:
            import yaml
            config = yaml.safe_load(content)
            
            if 'proxies' in config:
                for proxy in config['proxies']:
                    nodes.append({
                        'type': proxy.get('type', ''),
                        'name': proxy.get('name', ''),
                        'server': proxy.get('server', ''),
                        'port': proxy.get('port', ''),
                        'config': proxy
                    })
        except Exception as e:
            logger.error(f"解析 Clash 配置失败: {e}")
        
        return nodes
    
    def parse_ss_ssr_v2ray(self, content: str) -> List[Dict]:
        """解析 SS/SSR/V2Ray 链接"""
        nodes = []
        
        # SS 链接: ss://...
        ss_pattern = r'ss://([A-Za-z0-9+/=]+)'
        for match in re.finditer(ss_pattern, content):
            try:
                encoded = match.group(1)
                # 补齐 base64 padding
                padding = 4 - len(encoded) % 4
                if padding != 4:
                    encoded += '=' * padding
                
                decoded = base64.b64decode(encoded).decode('utf-8')
                # 解析 SS 链接格式
                if '@' in decoded:
                    parts = decoded.split('@')
                    method_password = parts[0]
                    server_port = parts[1]
                    if ':' in method_password:
                        method, password = method_password.split(':', 1)
                        if ':' in server_port:
                            server, port = server_port.rsplit(':', 1)
                            nodes.append({
                                'type': 'ss',
                                'server': server,
                                'port': int(port),
                                'method': method,
                                'password': password,
                                'raw': match.group(0)
                            })
            except Exception as e:
                logger.debug(f"解析 SS 链接失败: {e}")
                pass
        
        # V2Ray 链接: vmess://...
        vmess_pattern = r'vmess://([A-Za-z0-9+/=]+)'
        for match in re.finditer(vmess_pattern, content):
            try:
                encoded = match.group(1)
                # 补齐 base64 padding
                padding = 4 - len(encoded) % 4
                if padding != 4:
                    encoded += '=' * padding
                
                decoded = base64.b64decode(encoded).decode('utf-8')
                import json
                config = json.loads(decoded)
                nodes.append({
                    'type': 'vmess',
                    'server': config.get('add', ''),
                    'port': config.get('port', ''),
                    'uuid': config.get('id', ''),
                    'config': config,
                    'raw': match.group(0)
                })
            except Exception as e:
                logger.debug(f"解析 VMess 链接失败: {e}")
                pass
        
        # SSR 链接: ssr://...
        ssr_pattern = r'ssr://([A-Za-z0-9+/=]+)'
        for match in re.finditer(ssr_pattern, content):
            try:
                encoded = match.group(1)
                # 补齐 base64 padding
                padding = 4 - len(encoded) % 4
                if padding != 4:
                    encoded += '=' * padding
                
                decoded = base64.b64decode(encoded).decode('utf-8')
                # SSR 链接格式: server:port:protocol:method:obfs:password_base64/?obfsparam=xxx&protoparam=xxx&remarks=xxx
                # 这里简化处理，保存原始链接
                nodes.append({
                    'type': 'ssr',
                    'raw': match.group(0)
                })
            except Exception as e:
                logger.debug(f"解析 SSR 链接失败: {e}")
                pass
        
        # 也尝试从 proxy_helper 解析
        from proxy_helper import ProxyHelper
        helper = ProxyHelper()
        
        # 重新解析所有链接
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('ss://'):
                parsed = helper.parse_ss_link(line)
                if parsed:
                    nodes.append(parsed)
            elif line.startswith('vmess://'):
                parsed = helper.parse_vmess_link(line)
                if parsed:
                    nodes.append(parsed)
        
        return nodes
    
    def crawl_repo(self, repo: str) -> List[Dict]:
        """爬取指定仓库的所有节点"""
        all_nodes = []
        logger.info(f"开始爬取仓库: {repo}")
        
        # 搜索可能的配置文件
        files = self.search_github_files(repo)
        
        # 也尝试直接访问常见的配置文件路径
        common_paths = [
            "clash.yaml", "clash.yml", "config.yaml", "config.yml",
            "proxies.yaml", "proxies.yml", "sub.yaml", "sub.yml",
            "nodes.txt", "free.txt", "proxy.txt"
        ]
        
        for path in common_paths + files[:10]:  # 限制文件数量
            try:
                content = self.get_github_file_content(repo, path)
                if content:
                    # 尝试解析 Clash 配置
                    nodes = self.parse_clash_config(content)
                    if nodes:
                        all_nodes.extend(nodes)
                        logger.info(f"从 {path} 解析到 {len(nodes)} 个节点")
                    
                    # 尝试解析 SS/SSR/V2Ray 链接
                    nodes = self.parse_ss_ssr_v2ray(content)
                    if nodes:
                        all_nodes.extend(nodes)
                        logger.info(f"从 {path} 解析到 {len(nodes)} 个链接节点")
            except Exception as e:
                logger.debug(f"处理文件 {path} 失败: {e}")
        
        logger.info(f"仓库 {repo} 共爬取到 {len(all_nodes)} 个节点")
        return all_nodes
    
    def crawl_all(self, repos: List[str]) -> List[Dict]:
        """爬取所有仓库"""
        all_nodes = []
        for repo in repos:
            try:
                nodes = self.crawl_repo(repo)
                all_nodes.extend(nodes)
            except Exception as e:
                logger.error(f"爬取仓库 {repo} 失败: {e}")
        
        # 去重
        unique_nodes = []
        seen = set()
        for node in all_nodes:
            key = f"{node.get('server', '')}:{node.get('port', '')}"
            if key not in seen:
                seen.add(key)
                unique_nodes.append(node)
        
        logger.info(f"去重后共 {len(unique_nodes)} 个唯一节点")
        return unique_nodes

