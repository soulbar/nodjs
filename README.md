# 免费节点自动爬取与验证系统

自动从 GitHub 爬取免费代理节点，验证可用性，测试流媒体访问，并自动测速。

## 功能特性

- 🔍 自动从 GitHub 爬取免费节点
- ✅ 自动验证节点可用性（TCP 连接测试）
- 🎬 测试流媒体访问（YouTube/GitHub/ChatGPT/Netflix）
- ⚡ 自动测速（100-300 KB/s 速度范围）
- 🔄 定时任务每 2 小时自动更新（GitHub Actions）
- 📊 自动生成可用节点列表（多种格式）

## 快速开始

### 1. 部署到 GitHub（推荐）

#### 方法一：使用 GitHub CLI

```bash
# 安装 GitHub CLI（如果还没有）
# Windows: choco install gh
# 或从 https://cli.github.com/ 下载

# 登录 GitHub
gh auth login

# 创建仓库并推送
git init
git add .
git commit -m "Initial commit"
gh repo create free-nodes-crawler --public --source=. --remote=origin --push
```

#### 方法二：手动创建

1. 在 GitHub 上创建新仓库
2. 运行以下命令：

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

### 2. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行爬虫
python main.py

# 查看结果
cat nodes.txt
cat nodes.json
```

## 输出文件

- `nodes.txt` - 所有可用节点列表（链接格式）
- `nodes.json` - 节点详细信息（JSON 格式）
- `clash_config.yaml` - Clash 配置文件
- `log.txt` - 运行日志

## 配置说明

编辑 `config.py` 可以自定义：

- `GITHUB_REPOS` - GitHub 仓库列表
- `TEST_URLS` - 流媒体测试网站
- `MIN_SPEED` / `MAX_SPEED` - 速度范围（KB/s）
- `MAX_CONCURRENT` - 并发数

## GitHub Actions

项目已配置 GitHub Actions，会自动：

1. 每 2 小时运行一次爬虫
2. 验证和测速节点
3. 自动提交更新到仓库

你可以在 GitHub 仓库的 **Actions** 标签页查看运行状态和手动触发。

## 项目结构

```
.
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── node_crawler.py      # GitHub 节点爬虫
├── node_validator.py    # 节点验证器
├── node_speedtest.py    # 节点测速器
├── node_storage.py      # 节点存储
├── proxy_helper.py       # 代理辅助工具
├── requirements.txt    # Python 依赖
├── .github/
│   └── workflows/
│       └── auto-update.yml  # GitHub Actions 配置
└── README.md
```

## 节点来源

系统会自动从配置的 GitHub 仓库爬取节点，支持：

- Clash 配置文件（YAML）
- SS/SSR/V2Ray 链接
- 自动识别和解析多种节点格式

## 注意事项

- ⚠️ 节点来源于公开仓库，请自行判断安全性
- ⚠️ 建议仅用于学习和测试目的
- ⚠️ 请遵守相关法律法规
- ⚠️ GitHub API 有速率限制，如需爬取更多仓库，建议使用 Personal Access Token

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request！

