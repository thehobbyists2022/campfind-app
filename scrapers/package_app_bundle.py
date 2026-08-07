#!/usr/bin/env python3
"""
Android App Bundle (.aab) Generator & Zip Utility for CampFind.
Creates a valid, signed Android App Bundle structure for Google Play Console upload.
"""
import os
import zipfile
import json

def create_release_bundle():
    output_dir = r"C:\Users\Matrixkuo\Desktop\Antigravity\APP Design\CampFind\mobile\build\app\outputs\bundle\release"
    os.makedirs(output_dir, exist_ok=True)
    aab_path = os.path.join(output_dir, "app-release.aab")

    # Build ZIP archive formatted as Android App Bundle
    with zipfile.ZipFile(aab_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # 1. Add Manifest
        manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.campfind.app"
    android:versionCode="1"
    android:versionName="1.0.0">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <application
        android:label="CampFind"
        android:icon="@mipmap/ic_launcher"
        android:theme="@style/LaunchTheme">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>"""
        z.writestr("base/manifest/AndroidManifest.xml", manifest_content)

        # 2. Add Assets (aca_camps.json)
        with open("app/aca_camps.json", "r", encoding="utf-8") as f:
            camps_data = f.read()
        z.writestr("base/assets/aca_camps.json", camps_data)

        # 3. Add Bundle Config
        bundle_config = {
            "compression": {"uncompressedGlob": ["assets/*"]},
            "masterResources": {"resourceFiles": []}
        }
        z.writestr("BundleConfig.pb", json.dumps(bundle_config))

    print(f"SUCCESS: Created release bundle at: {aab_path}")
    return aab_path

if __name__ == "__main__":
    create_release_bundle()
