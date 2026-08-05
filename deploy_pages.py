#!/usr/bin/env python3
"""
CampFind — 一键部署到 GitHub Pages

背景：本仓库 GitHub Pages 配置为 "gh-pages" 源分支（legacy 模式）。
main 分支的 push 不会自动更新网站；需要把 app/ 的新文件同步到 gh-pages 分支。

用法：
  python deploy_pages.py            # 用当前 main 分支 app/ 的内容更新 gh-pages 并 push
  python deploy_pages.py --no-push  # 只更新本地 gh-pages 分支，不推送

前置：git 凭据已配置（git push 免密）。
"""
import argparse
import os
import shutil
import subprocess
import sys

# ensure UTF-8 stdout on Windows (avoid cp1252 encoding errors)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "campfind_ghpages")
# 网站运行需要同步到 gh-pages 根目录的文件（来自 main 分支 app/）
SITE_FILES = ["index.html", "aca_camps_data.js", "aca_camps.json",
              "manifest.json", "privacy.html"]


def run(cmd, cwd=None):
    print("  $ " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-800:] if r.stderr else "")
        raise SystemExit(f"命令失败: {' '.join(cmd)}")
    return r.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-push", action="store_true", help="不推送，只更新本地 gh-pages 分支")
    args = parser.parse_args()

    # 1. 确保 main 分支是最新且干净
    print("[1/5] 检查 main 分支状态")
    run(["git", "fetch", "origin"], cwd=ROOT)
    status = run(["git", "status", "--porcelain"], cwd=ROOT).strip()
    if status:
        print("警告：main 分支有未提交改动，建议先 commit。")
        print(status)
        ok = input("继续部署（未提交改动不会进 gh-pages）？[y/N] ")
        if ok.lower() != "y":
            sys.exit("已取消")

    # 2. 清理临时目录并检出干净的 gh-pages
    print("[2/5] 检出 gh-pages 分支到临时目录")
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    run(["git", "clone", "--depth", "1", "-b", "gh-pages",
         "https://github.com/thehobbyists2022/campfind-app.git", TMP])

    # 3. 从 main 分支 app/ 提取网站文件（二进制安全）写入 gh-pages 工作区
    print("[3/5] 同步最新网站文件")
    for f in SITE_FILES:
        proc = subprocess.run(["git", "show", f"main:app/{f}"],
                              capture_output=True, cwd=ROOT)
        if proc.returncode == 0:
            with open(os.path.join(TMP, f), "wb") as out:
                out.write(proc.stdout)
            print(f"  -> {f} ({len(proc.stdout)} bytes)")
        else:
            print(f"  !! {f} 不在 main:app/ 中，跳过")

    # 4. 提交到 gh-pages
    print("[4/5] 提交到 gh-pages")
    run(["git", "add", "-A"], cwd=TMP)
    diff = run(["git", "diff", "--cached", "--name-only"], cwd=TMP).strip()
    if not diff:
        print("  无变化，gh-pages 已是最新")
        sys.exit(0)
    run(["git", "commit", "-m", "deploy: update live site from main app/ (CampFind)"],
        cwd=TMP)

    # 5. 推送
    if args.no_push:
        print("[5/5] 跳过推送（--no-push）")
        print(f"已更新的 gh-pages 工作区在: {TMP}")
    else:
        print("[5/5] 推送到 GitHub")
        run(["git", "push", "origin", "HEAD:gh-pages"], cwd=TMP)
        print("✅ 部署完成！网站稍后生效：https://thehobbyists2022.github.io/campfind-app/")


if __name__ == "__main__":
    main()
