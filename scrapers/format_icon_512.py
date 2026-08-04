import os
from PIL import Image

uploaded_path = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\.user_uploaded\media__1785352297871.jpg"
output_path = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\campfind_app_icon_512x512.png"

if os.path.exists(uploaded_path):
    img = Image.open(uploaded_path)
    # Resize to exact 512x512 resolution for Google Play Store
    img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_resized.save(output_path, "PNG")
    print(f"SUCCESS: Formatted icon to EXACT 512x512 PNG at: {output_path}")
else:
    print("Uploaded image file not found.")
