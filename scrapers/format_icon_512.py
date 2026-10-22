import os
from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
uploaded_path = os.environ.get("CAMPFIND_ICON_SRC", os.path.join(ROOT_DIR, "store_assets", "original_google_play_icon_512x512.png"))
output_path = os.environ.get("CAMPFIND_ICON_OUT", os.path.join(ROOT_DIR, "store_assets", "play_store_icon_512x512.png"))

if os.path.exists(uploaded_path):
    img = Image.open(uploaded_path)
    # Resize to exact 512x512 resolution for Google Play Store
    img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_resized.save(output_path, "PNG")
    print(f"SUCCESS: Formatted icon to EXACT 512x512 PNG at: {output_path}")
else:
    print("Uploaded image file not found.")
