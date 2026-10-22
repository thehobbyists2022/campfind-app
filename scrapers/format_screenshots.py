import os
from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sc_home = os.environ.get("CAMPFIND_SC_HOME_SRC", os.path.join(ROOT_DIR, "store_assets", "screenshots", "raw_1.png"))
sc_compare = os.environ.get("CAMPFIND_SC_COMPARE_SRC", os.path.join(ROOT_DIR, "store_assets", "screenshots", "raw_4.png"))

out_home = os.environ.get("CAMPFIND_SC_HOME_OUT", os.path.join(ROOT_DIR, "store_assets", "screenshots", "01_playstore_search_map.png"))
out_compare = os.environ.get("CAMPFIND_SC_COMPARE_OUT", os.path.join(ROOT_DIR, "store_assets", "screenshots", "04_playstore_compare.png"))

if os.path.exists(sc_home):
    img = Image.open(sc_home)
    img.resize((1080, 1920), Image.Resampling.LANCZOS).save(out_home, "PNG")
    print("Formatted screenshot home to 1080x1920 PNG.")

if os.path.exists(sc_compare):
    img = Image.open(sc_compare)
    img.resize((1080, 1920), Image.Resampling.LANCZOS).save(out_compare, "PNG")
    print("Formatted screenshot compare to 1080x1920 PNG.")
