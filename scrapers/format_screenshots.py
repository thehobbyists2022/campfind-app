import os
from PIL import Image

sc_home = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\campfind_screenshot_home_1785351525649.jpg"
sc_compare = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\campfind_screenshot_compare_1785351542890.jpg"

out_home = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\campfind_screenshot_home_1080x1920.png"
out_compare = r"C:\Users\Matrixkuo\.gemini\antigravity\brain\84c663b4-dccb-4a9f-bdef-9340979e07ee\campfind_screenshot_compare_1080x1920.png"

if os.path.exists(sc_home):
    img = Image.open(sc_home)
    img.resize((1080, 1920), Image.Resampling.LANCZOS).save(out_home, "PNG")
    print("Formatted screenshot home to 1080x1920 PNG.")

if os.path.exists(sc_compare):
    img = Image.open(sc_compare)
    img.resize((1080, 1920), Image.Resampling.LANCZOS).save(out_compare, "PNG")
    print("Formatted screenshot compare to 1080x1920 PNG.")
