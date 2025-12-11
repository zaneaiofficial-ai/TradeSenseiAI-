#!/usr/bin/env python
"""Test Supabase connection and auth."""
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client, Client

def test_supabase():
    print("Testing Supabase connection...")

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not set")
        return

    if url == "https://your-project.supabase.co":
        print("❌ SUPABASE_URL is still the placeholder. Please replace with your actual Supabase project URL.")
        return

    try:
        supabase: Client = create_client(url, key)
        print("✅ Supabase client created successfully")

        # Test a simple query (assuming you have a 'Users' table or similar)
        # For now, just check if we can connect
        response = supabase.table('Users').select('*').limit(1).execute()
        print("✅ Supabase query successful")
        print(f"Response: {response}")

    except Exception as e:
        print(f"❌ Supabase error: {e}")

if __name__ == '__main__':
    test_supabase()