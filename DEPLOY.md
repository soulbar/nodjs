# 部署说明

## 部署到 GitHub

### 方法一：使用 GitHub CLI（推荐）

1. 安装 GitHub CLI（如果还没有安装）：
   ```bash
   # Windows (使用 Chocolatey)
   choco install gh
   
   # 或从 https://cli.github.com/ 下载安装
   ```

2. 登录 GitHub：
   ```bash
   gh auth login
   ```

3. 创建新仓库并推送代码：
   ```bash
   # 初始化 git（如果还没有）
   git init
   git add .
   git commit -m "Initial commit: 免费节点自动爬取系统"
   
   # 创建 GitHub 仓库并推送
   gh repo create free-nodes-crawler --public --source=. --remote=origin --push
   ```

### 方法二：手动创建仓库

1. 在 GitHub 上创建一个新仓库（例如：`free-nodes-crawler`）

2. 初始化并推送代码：
   ```bash
   git init
   git add .
   git commit -m "Initial commit: 免费节点自动爬取系统"
   git branch -M main
   git remote add origin https://github.com/你的用户名/free-nodes-crawler.git
   git push -u origin main
   ```

### 启用 GitHub Actions

1. 推送代码后，GitHub Actions 会自动启用
2. 定时任务会在每 2 小时自动运行一次
3. 你也可以在 GitHub 仓库的 Actions 标签页手动触发

### 查看运行结果

- 在 GitHub 仓库的 Actions 标签页查看运行日志
- 运行成功后，`nodes.txt`、`nodes.json` 和 `clash_config.yaml` 会自动更新
- 查看 `log.txt` 了解详细运行日志

## 本地测试

在部署前，建议先在本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py

# 查看结果
cat nodes.txt
cat nodes.json
```

## 注意事项

1. **GitHub API 限制**：GitHub API 有速率限制（未认证用户每小时 60 次请求）。如果需要爬取更多仓库，建议：
   - 使用 GitHub Personal Access Token
   - 在 GitHub Actions 的 Secrets 中添加 `GITHUB_TOKEN`

2. **节点来源**：默认配置的仓库可能不存在或已更改，请在 `config.py` 中更新 `GITHUB_REPOS` 列表

3. **代理测试**：由于 GitHub Actions 运行环境限制，某些代理测试可能无法完全执行。建议在本地环境进行完整测试

4. **安全性**：请遵守相关法律法规，仅用于学习和测试目的

