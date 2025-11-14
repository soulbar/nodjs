"""
主程序入口
"""
import asyncio
import logging
import sys
from datetime import datetime
from config import GITHUB_REPOS, LOG_FILE
from node_crawler import GitHubNodeCrawler
from node_validator import NodeValidator
from node_speedtest import NodeSpeedTest
from node_storage import NodeStorage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始节点爬取和验证流程")
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    try:
        # 1. 爬取节点
        logger.info("步骤 1: 开始爬取节点...")
        crawler = GitHubNodeCrawler()
        all_nodes = crawler.crawl_all(GITHUB_REPOS)
        logger.info(f"共爬取到 {len(all_nodes)} 个节点")
        
        if not all_nodes:
            logger.warning("未爬取到任何节点，请检查网络连接和仓库配置")
            return
        
        # 2. 验证节点可用性
        logger.info("步骤 2: 开始验证节点可用性...")
        validator = NodeValidator()
        valid_nodes = await validator.validate_nodes(all_nodes)
        logger.info(f"验证完成，共 {len(valid_nodes)} 个可用节点")
        
        if not valid_nodes:
            logger.warning("没有可用的节点")
            return
        
        # 3. 测速
        logger.info("步骤 3: 开始测速...")
        speedtest = NodeSpeedTest()
        speed_ok_nodes = await speedtest.test_nodes_speed(valid_nodes)
        logger.info(f"测速完成，共 {len(speed_ok_nodes)} 个节点速度在范围内")
        
        if not speed_ok_nodes:
            logger.warning("没有速度在范围内的节点")
            return
        
        # 4. 保存结果
        logger.info("步骤 4: 保存结果...")
        NodeStorage.save_all(speed_ok_nodes)
        
        # 5. 统计信息
        logger.info("=" * 50)
        logger.info("爬取和验证完成！")
        logger.info(f"总节点数: {len(all_nodes)}")
        logger.info(f"可用节点数: {len(valid_nodes)}")
        logger.info(f"速度合格节点数: {len(speed_ok_nodes)}")
        
        # 流媒体访问统计
        streaming_stats = {}
        for node in speed_ok_nodes:
            if 'streaming_access' in node:
                for site, accessible in node['streaming_access'].items():
                    if site not in streaming_stats:
                        streaming_stats[site] = 0
                    if accessible:
                        streaming_stats[site] += 1
        
        logger.info("流媒体访问统计:")
        for site, count in streaming_stats.items():
            logger.info(f"  {site}: {count} 个节点可访问")
        
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

