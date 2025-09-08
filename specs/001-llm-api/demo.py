#!/usr/bin/env python3
"""
Demo script for LLM API Gateway

This script demonstrates the basic functionality of the gateway without requiring
actual LLM provider API keys.
"""

import sqlite3
import json
import uuid
from datetime import datetime

DB_PATH = "gateway.db"

def demo_database_operations():
    """Demonstrate database operations."""
    print("=== LLM API Gateway Demo ===\n")
    
    print("1. Database Structure:")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Show virtual keys
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"   Tables: {[table[0] for table in tables]}")
    
    # Show virtual keys
    cursor.execute("SELECT id, project_name, created_at, is_active FROM virtual_keys")
    keys = cursor.fetchall()
    print(f"   Virtual Keys: {len(keys)} found")
    
    for key in keys:
        print(f"   - {key[1]}: {key[0]} (Active: {key[3]})")
    
    print()
    
    print("2. Creating Additional Demo Data:")
    
    # Create more virtual keys for demo
    demo_projects = ["Frontend App", "Backend Service", "Analytics Pipeline"]
    created_keys = []
    
    for project in demo_projects:
        key_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT OR IGNORE INTO virtual_keys (id, project_name) VALUES (?, ?)",
            (key_id, project)
        )
        created_keys.append((key_id, project))
        print(f"   Created key for '{project}': {key_id}")
    
    # Add some mock usage data
    print("\n3. Adding Mock Usage Data:")
    for i, (key_id, project) in enumerate(created_keys):
        # Add some mock usage records
        for j in range((i + 1) * 3):  # Different usage per project
            cursor.execute("""
                INSERT INTO usage_records 
                (virtual_key_id, provider, endpoint, request_tokens, response_tokens, estimated_cost)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                key_id,
                "openai" if j % 2 == 0 else "anthropic",
                "chat/completions",
                50 + j * 10,  # Request tokens
                30 + j * 5,   # Response tokens
                0.001 * (50 + j * 10 + 30 + j * 5)  # Mock cost
            ))
        print(f"   Added {(i + 1) * 3} usage records for '{project}'")
    
    conn.commit()
    
    print("\n4. Usage Statistics:")
    cursor.execute("""
        SELECT 
            vk.project_name,
            COUNT(ur.id) as total_requests,
            COALESCE(SUM(ur.request_tokens + ur.response_tokens), 0) as total_tokens,
            COALESCE(SUM(ur.estimated_cost), 0) as estimated_cost
        FROM virtual_keys vk
        LEFT JOIN usage_records ur ON vk.id = ur.virtual_key_id
        GROUP BY vk.id, vk.project_name
        ORDER BY total_requests DESC
    """)
    
    stats = cursor.fetchall()
    print("   Project              | Requests | Tokens | Est. Cost")
    print("   --------------------|----------|--------|----------")
    
    total_requests = 0
    total_tokens = 0
    total_cost = 0.0
    
    for project, requests, tokens, cost in stats:
        total_requests += requests
        total_tokens += tokens
        total_cost += cost
        print(f"   {project:<19} | {requests:>8} | {tokens:>6} | ${cost:>7.4f}")
    
    print("   --------------------|----------|--------|----------")
    print(f"   {'TOTAL':<19} | {total_requests:>8} | {total_tokens:>6} | ${total_cost:>7.4f}")
    
    conn.close()
    
    print("\n5. API Gateway Workflow Demo:")
    print("   ┌─────────────────┐")
    print("   │  Client App     │")
    print("   │ (Virtual Key)   │")
    print("   └─────────┬───────┘")
    print("             │ HTTP Request")
    print("             ▼")
    print("   ┌─────────────────┐")
    print("   │ LLM API Gateway │")
    print("   │ • Auth Check    │")
    print("   │ • Key Mapping   │")
    print("   │ • Usage Log     │")
    print("   └─────────┬───────┘")
    print("             │ Proxied Request")
    print("             ▼")
    print("   ┌─────────────────┐")
    print("   │ LLM Provider    │")
    print("   │ (Real API Key)  │")
    print("   └─────────────────┘")
    
    print("\n=== Demo Complete ===")
    print("\nTo start the gateway server:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Configure real API keys: python cli.py config set-key openai 'your-key'")
    print("  3. Start server: python cli.py serve")
    print("  4. Test endpoint: curl -H 'Authorization: Bearer VIRTUAL_KEY' http://localhost:8000/v1/chat/completions")

if __name__ == "__main__":
    demo_database_operations()