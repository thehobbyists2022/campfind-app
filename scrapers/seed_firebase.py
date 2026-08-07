#!/usr/bin/env python3
"""
CampFind Firebase Firestore Data Seeding Utility.
Populates 1,050 ACA Camps into Google Cloud Firestore.

Usage:
  1. Download serviceAccountKey.json from Firebase Console -> Project Settings -> Service Accounts.
  2. Place serviceAccountKey.json in scrapers/ directory.
  3. Run: python seed_firebase.py
"""
import json
import os
import sys

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("firebase-admin package is required. Run: pip install firebase-admin")
    sys.exit(1)

def seed_camps_to_firestore():
    service_key_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "app", "aca_camps.json")

    if not os.path.exists(service_key_path):
        print(f"❌ Error: {service_key_path} not found!")
        print("Please download serviceAccountKey.json from your Firebase Console and place it in the scrapers/ folder.")
        sys.exit(1)

    if not os.path.exists(dataset_path):
        print(f"❌ Error: {dataset_path} not found!")
        sys.exit(1)

    print("🔑 Initializing Firebase Admin SDK...")
    cred = credentials.Certificate(service_key_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    print(f"📂 Loading dataset from {dataset_path}...")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        camps = data.get("camps", [])

    print(f"🚀 Batch uploading {len(camps)} camps to Firestore collection 'camps'...")

    batch = db.batch()
    count = 0
    total = len(camps)

    for i, camp in enumerate(camps, start=1):
        camp_id = str(camp.get("id", f"camp_{i}"))
        doc_ref = db.collection("camps").document(camp_id)
        batch.set(doc_ref, camp)
        count += 1

        # Firestore batches support max 500 writes per batch
        if count == 400 or i == total:
            batch.commit()
            print(f"  ✓ Uploaded {i}/{total} camps...")
            batch = db.batch()
            count = 0

    print(f"🎉 Successfully seeded {total} camps into Firebase Firestore!")

if __name__ == "__main__":
    seed_camps_to_firestore()
