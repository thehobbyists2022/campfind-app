import os
from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
icon_src = os.environ.get("CAMPFIND_ICON_SRC", os.path.join(ROOT_DIR, "store_assets", "play_store_icon_512x512.png"))
res_dir = os.path.join(ROOT_DIR, "mobile", "android", "app", "src", "main", "res")

sizes = {
    "mipmap-mdpi": (48, 48),
    "mipmap-hdpi": (72, 72),
    "mipmap-xhdpi": (96, 96),
    "mipmap-xxhdpi": (144, 144),
    "mipmap-xxxhdpi": (192, 192)
}

if os.path.exists(icon_src):
    img = Image.open(icon_src)
    for folder, size in sizes.items():
        folder_path = os.path.join(res_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        target_file = os.path.join(folder_path, "ic_launcher.png")
        img.resize(size, Image.Resampling.LANCZOS).save(target_file, "PNG")
        print(f"Generated {folder}/ic_launcher.png ({size[0]}x{size[1]})")

# Create minimal styles.xml if not existing
values_dir = os.path.join(res_dir, "values")
os.makedirs(values_dir, exist_ok=True)
styles_xml = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="LaunchTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <item name="android:windowBackground">@android:color/white</item>
    </style>
</resources>"""
with open(os.path.join(values_dir, "styles.xml"), "w", encoding="utf-8") as f:
    f.write(styles_xml)

print("SUCCESS: Created all Android mipmap launcher icons and styles.xml.")
