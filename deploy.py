"""
自动部署脚本 - 帮助将代码部署到 GitHub
"""
import subprocess
import sys
import os


def run_command(cmd, check=True):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"错误: {result.stderr}")
        sys.exit(1)
    return result


def main():
    """主函数"""
    print("=" * 50)
    print("开始部署到 GitHub")
    print("=" * 50)
    
    # 检查是否已初始化 git
    if not os.path.exists('.git'):
        print("初始化 Git 仓库...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit: 免费节点自动爬取系统"')
    else:
        print("Git 仓库已存在，检查更改...")
        run_command("git add .", check=False)
        result = run_command("git status --porcelain", check=False)
        if result.stdout.strip():
            run_command('git commit -m "更新代码"', check=False)
    
    # 检查是否已设置远程仓库
    result = run_command("git remote -v", check=False)
    if not result.stdout.strip():
        print("\n请先创建 GitHub 仓库，然后运行以下命令：")
        print("  git remote add origin https://github.com/你的用户名/仓库名.git")
        print("  git push -u origin main")
        print("\n或者使用 GitHub CLI：")
        print("  gh repo create 仓库名 --public --source=. --remote=origin --push")
        return
    
    # 推送代码
    print("\n推送到 GitHub...")
    run_command("git push", check=False)
    
    print("\n" + "=" * 50)
    print("部署完成！")
    print("=" * 50)
    print("\nGitHub Actions 将在每 2 小时自动运行一次")
    print("你也可以在 GitHub 仓库的 Actions 标签页手动触发")


if __name__ == "__main__":
    main()

