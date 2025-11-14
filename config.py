# 配置文件

# GitHub 节点仓库列表（示例，实际需要根据实际情况调整）
GITHUB_REPOS = [
    "freefq/free",
    "peasoft/NoMoreWalls",
    "ripaojiedian/free-ssr-ss-v2ray-vless-clash",
]

# 测试目标网站
TEST_URLS = {
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "chatgpt": "https://chat.openai.com",
    "netflix": "https://www.netflix.com",
}

# 测速配置
SPEED_TEST_URL = "https://www.google.com/generate_204"
MIN_SPEED = 100  # 最小速度 (KB/s)
MAX_SPEED = 300  # 最大速度 (KB/s)

# 超时设置
TIMEOUT = 10  # 连接超时（秒）
TEST_TIMEOUT = 15  # 测试超时（秒）

# 并发设置
MAX_CONCURRENT = 20  # 最大并发数

# 输出文件
OUTPUT_NODES_TXT = "nodes.txt"
OUTPUT_NODES_JSON = "nodes.json"
LOG_FILE = "log.txt"

