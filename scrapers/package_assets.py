import os
import shutil

src_dir = r"C:\Users\Matrixkuo\Desktop\Antigravity\APP Design\CampFind\app"
assets_dir = r"C:\Users\Matrixkuo\Desktop\Antigravity\APP Design\CampFind\mobile\android\app\src\main\assets"

os.makedirs(assets_dir, exist_ok=True)

for root, dirs, files in os.walk(src_dir):
    rel_path = os.path.relpath(root, src_dir)
    target_root = os.path.join(assets_dir, rel_path) if rel_path != "." else assets_dir
    os.makedirs(target_root, exist_ok=True)
    for f in files:
        src_file = os.path.join(root, f)
        target_file = os.path.join(target_root, f)
        shutil.copy2(src_file, target_file)

print(f"SUCCESS: Packaged web app assets into {assets_dir}")
