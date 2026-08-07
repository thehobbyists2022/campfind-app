import os
from PIL import Image

banner_path = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\campfind_feature_banner_1785351508933.jpg"
output_path = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\campfind_feature_banner_1024x500.png"

if os.path.exists(banner_path):
    img = Image.open(banner_path)
    # Resize to exact 1024x500 resolution for Google Play Store
    img_resized = img.resize((1024, 500), Image.Resampling.LANCZOS)
    img_resized.save(output_path, "PNG")
    print(f"SUCCESS: Formatted banner to EXACT 1024x500 PNG at: {output_path}")
else:
    print("Banner file not found.")
