import os
from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
banner_path = os.environ.get("CAMPFIND_BANNER_SRC", os.path.join(ROOT_DIR, "store_assets", "feature_graphic_1024x500.png"))
output_path = os.environ.get("CAMPFIND_BANNER_OUT", os.path.join(ROOT_DIR, "store_assets", "feature_graphic_1024x500.png"))

if os.path.exists(banner_path):
    img = Image.open(banner_path)
    # Resize to exact 1024x500 resolution for Google Play Store
    img_resized = img.resize((1024, 500), Image.Resampling.LANCZOS)
    img_resized.save(output_path, "PNG")
    print(f"SUCCESS: Formatted banner to EXACT 1024x500 PNG at: {output_path}")
else:
    print("Banner file not found.")
