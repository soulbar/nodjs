"""
节点存储模块
"""
import json
import yaml
import logging
from typing import List, Dict
from config import OUTPUT_NODES_TXT, OUTPUT_NODES_JSON

logger = logging.getLogger(__name__)


class NodeStorage:
    """节点存储"""
    
    @staticmethod
    def save_to_txt(nodes: List[Dict], filename: str = OUTPUT_NODES_TXT):
        """保存为文本格式（Clash 格式）"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 免费节点列表 - 自动更新\n")
                f.write("# 来源: GitHub 自动爬取\n\n")
                
                for node in nodes:
                    if 'raw' in node:
                        f.write(f"{node['raw']}\n")
                    elif node.get('type') == 'ss':
                        # 生成 SS 链接
                        server = node.get('server', '')
                        port = node.get('port', '')
                        method = node.get('method', '')
                        password = node.get('password', '')
                        if server and port:
                            f.write(f"# {node.get('name', server)}\n")
                            f.write(f"ss://{method}:{password}@{server}:{port}\n")
                    elif node.get('type') == 'vmess':
                        if 'raw' in node:
                            f.write(f"{node['raw']}\n")
            
            logger.info(f"已保存 {len(nodes)} 个节点到 {filename}")
        except Exception as e:
            logger.error(f"保存文本文件失败: {e}")
    
    @staticmethod
    def save_to_json(nodes: List[Dict], filename: str = OUTPUT_NODES_JSON):
        """保存为 JSON 格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(nodes, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存 {len(nodes)} 个节点到 {filename}")
        except Exception as e:
            logger.error(f"保存 JSON 文件失败: {e}")
    
    @staticmethod
    def save_to_clash_yaml(nodes: List[Dict], filename: str = "clash_config.yaml"):
        """保存为 Clash YAML 格式"""
        try:
            proxies = []
            for node in nodes:
                if 'config' in node and isinstance(node['config'], dict):
                    proxy = node['config'].copy()
                    # 添加速度信息
                    if 'speed' in node:
                        proxy['speed'] = node['speed']
                    proxies.append(proxy)
            
            config = {
                'port': 7890,
                'socks-port': 7891,
                'allow-lan': False,
                'mode': 'rule',
                'log-level': 'info',
                'external-controller': '127.0.0.1:9090',
                'proxies': proxies,
                'proxy-groups': [
                    {
                        'name': '自动选择',
                        'type': 'select',
                        'proxies': [p.get('name', '') for p in proxies]
                    }
                ],
                'rules': [
                    'DOMAIN-SUFFIX,local,DIRECT',
                    'IP-CIDR,127.0.0.0/8,DIRECT',
                    'GEOIP,CN,DIRECT',
                    'MATCH,自动选择'
                ]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            
            logger.info(f"已保存 Clash 配置到 {filename}")
        except Exception as e:
            logger.error(f"保存 Clash 配置失败: {e}")
    
    @staticmethod
    def save_all(nodes: List[Dict]):
        """保存所有格式"""
        NodeStorage.save_to_txt(nodes)
        NodeStorage.save_to_json(nodes)
        NodeStorage.save_to_clash_yaml(nodes)

