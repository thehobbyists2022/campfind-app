#!/usr/bin/env python3
"""
CampFind — 一键打包 Android AAB（Flutter）

用法：
  python build_aab.py               # flutter analyze + 构建签名 AAB
  python build_aab.py --skip-analyze  # 跳过 flutter analyze，直接构建

产出：
  mobile/build/app/outputs/bundle/release/app-release.aab   （已签名，57MB 左右）
  复制一份到 mobile/campfind-app-release.aab

前置：本机已装 Flutter SDK + Android SDK + JDK（Android Studio 自带 jbr）。
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MOBILE = os.path.join(ROOT, "mobile")
FLUTTER = r"C:\flutter\bin\flutter.bat"
JBR = r"C:\Program Files\Android\Android Studio\jbr"


def run(cmd, cwd=MOBILE):
    print("  $ " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    print(out[-1500:])
    return r.returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-analyze", action="store_true")
    args = parser.parse_args()

    # 环境
    env = dict(os.environ)
    env["JAVA_HOME"] = JBR
    env["PATH"] = JBR + r"\bin;" + FLUTTER[: FLUTTER.rfind("\\bin")] + r"\bin;" + env["PATH"]

    print(f"[1/3] flutter analyze")
    if not args.skip_analyze:
        code = run([FLUTTER, "analyze"])
        # 有 error 则中止；只有 info/warning 可继续
        if code != 0:
            print("analyze 失败（请检查 error），中止")
            sys.exit(1)
    else:
        print("  跳过 analyze")

    print(f"[2/3] flutter build appbundle --release")
    code = run([FLUTTER, "build", "appbundle", "--release"])

    aab = os.path.join(MOBILE, "build", "app", "outputs", "bundle", "release", "app-release.aab")
    if code != 0 or not os.path.exists(aab):
        print("构建失败或未找到 AAB，请检查上方日志（常见：flutter_tools strip 后检查报错，但 AAB 实际已生成）")
        sys.exit(1)

    size_mb = os.path.getsize(aab) / 1e6
    print(f"[3/3] AAB 已生成: {aab} ({size_mb:.1f} MB)")

    # 复制一份方便上传
    dest = os.path.join(MOBILE, "campfind-app-release.aab")
    shutil.copyfile(aab, dest)
    print(f"已复制到: {dest}")
    print("上传 Google Play Console: 内部测试 -> 创建版本 -> 上传此 AAB")


if __name__ == "__main__":
    main()
