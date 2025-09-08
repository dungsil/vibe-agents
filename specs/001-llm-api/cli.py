#!/usr/bin/env python3
"""
LLM API Gateway CLI

Command-line interface for managing the LLM API Gateway.
"""

import click
import sqlite3
import yaml
import json
import uuid
import requests
from datetime import datetime
from typing import Dict, Any

DB_PATH = "gateway.db"
CONFIG_PATH = "config.yaml"

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Virtual API keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS virtual_keys (
            id TEXT PRIMARY KEY,
            project_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Real API keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS real_keys (
            provider TEXT PRIMARY KEY,
            api_key TEXT NOT NULL,
            base_url TEXT
        )
    """)
    
    # Usage records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            virtual_key_id TEXT,
            provider TEXT,
            endpoint TEXT,
            request_tokens INTEGER,
            response_tokens INTEGER,
            estimated_cost REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (virtual_key_id) REFERENCES virtual_keys (id)
        )
    """)
    
    conn.commit()
    conn.close()

@click.group()
def cli():
    """LLM API Gateway CLI - Manage virtual keys and configuration."""
    pass

@cli.command()
def init():
    """Initialize the gateway database and configuration."""
    click.echo("Initializing LLM API Gateway...")
    
    # Create database
    init_db()
    click.echo("✓ Database initialized")
    
    # Create default config if it doesn't exist
    import os
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 8000
            },
            "providers": {
                "openai": {
                    "base_url": "https://api.openai.com",
                    "api_key": ""
                },
                "anthropic": {
                    "base_url": "https://api.anthropic.com",
                    "api_key": ""
                }
            }
        }
        
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        click.echo(f"✓ Configuration file created at {CONFIG_PATH}")
        click.echo("  Please edit the configuration file to add your real API keys.")
    else:
        click.echo(f"✓ Configuration file already exists at {CONFIG_PATH}")
    
    click.echo("Gateway initialization complete!")

@cli.group()
def keys():
    """Manage virtual API keys."""
    pass

@keys.command("create")
@click.argument("project_name")
@click.option("--output", "-o", type=click.Choice(["table", "json"]), default="table", help="Output format")
def create_key(project_name, output):
    """Create a new virtual API key for a project."""
    virtual_key_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO virtual_keys (id, project_name) VALUES (?, ?)",
            (virtual_key_id, project_name)
        )
        conn.commit()
        
        cursor.execute(
            "SELECT id, project_name, created_at, is_active FROM virtual_keys WHERE id = ?",
            (virtual_key_id,)
        )
        result = cursor.fetchone()
        
        if output == "json":
            click.echo(json.dumps({
                "id": result[0],
                "project_name": result[1],
                "created_at": result[2],
                "is_active": bool(result[3])
            }, indent=2))
        else:
            click.echo(f"✓ Virtual API key created successfully!")
            click.echo(f"  Project: {result[1]}")
            click.echo(f"  Key ID: {result[0]}")
            click.echo(f"  Created: {result[2]}")
            
    except sqlite3.IntegrityError:
        click.echo("✗ Error: Key already exists", err=True)
    finally:
        conn.close()

@keys.command("list")
@click.option("--output", "-o", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_keys(output):
    """List all virtual API keys."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, created_at, is_active FROM virtual_keys ORDER BY created_at DESC")
    results = cursor.fetchall()
    conn.close()
    
    if output == "json":
        keys_data = [
            {
                "id": row[0],
                "project_name": row[1],
                "created_at": row[2],
                "is_active": bool(row[3])
            } for row in results
        ]
        click.echo(json.dumps(keys_data, indent=2))
    else:
        if not results:
            click.echo("No virtual keys found.")
            return
            
        click.echo("Virtual API Keys:")
        click.echo("-" * 80)
        click.echo(f"{'Project Name':<20} {'Key ID':<36} {'Created':<20} {'Active'}")
        click.echo("-" * 80)
        
        for row in results:
            status = "✓" if row[3] else "✗"
            click.echo(f"{row[1]:<20} {row[0]:<36} {row[2]:<20} {status}")

@keys.command("revoke")
@click.argument("key_id")
def revoke_key(key_id):
    """Revoke a virtual API key."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE virtual_keys SET is_active = FALSE WHERE id = ?", (key_id,))
    
    if cursor.rowcount == 0:
        click.echo("✗ Virtual key not found", err=True)
    else:
        conn.commit()
        click.echo("✓ Virtual key revoked successfully")
    
    conn.close()

@cli.group()
def config():
    """Manage gateway configuration."""
    pass

@config.command("set-key")
@click.argument("provider", type=click.Choice(["openai", "anthropic"]))
@click.argument("api_key")
def set_api_key(provider, api_key):
    """Set real API key for a provider."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO real_keys (provider, api_key) VALUES (?, ?)",
        (provider, api_key)
    )
    conn.commit()
    conn.close()
    
    click.echo(f"✓ API key for {provider} updated successfully")

@config.command("list-keys")
def list_api_keys():
    """List configured real API keys (masked)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT provider, api_key FROM real_keys")
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        click.echo("No API keys configured.")
        return
    
    click.echo("Configured API Keys:")
    click.echo("-" * 40)
    click.echo(f"{'Provider':<15} {'API Key (masked)'}")
    click.echo("-" * 40)
    
    for provider, api_key in results:
        masked_key = f"{api_key[:8]}..." if len(api_key) > 8 else "***"
        click.echo(f"{provider:<15} {masked_key}")

@cli.command()
@click.option("--output", "-o", type=click.Choice(["table", "json"]), default="table", help="Output format")
def stats(output):
    """Show usage statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            vk.id,
            vk.project_name,
            COUNT(ur.id) as total_requests,
            COALESCE(SUM(ur.request_tokens + ur.response_tokens), 0) as total_tokens,
            COALESCE(SUM(ur.estimated_cost), 0) as estimated_cost
        FROM virtual_keys vk
        LEFT JOIN usage_records ur ON vk.id = ur.virtual_key_id
        GROUP BY vk.id, vk.project_name
        ORDER BY vk.created_at DESC
    """)
    results = cursor.fetchall()
    conn.close()
    
    if output == "json":
        stats_data = [
            {
                "virtual_key_id": row[0],
                "project_name": row[1],
                "total_requests": row[2],
                "total_tokens": row[3],
                "estimated_cost": row[4]
            } for row in results
        ]
        click.echo(json.dumps(stats_data, indent=2))
    else:
        if not results:
            click.echo("No usage statistics found.")
            return
            
        click.echo("Usage Statistics:")
        click.echo("-" * 90)
        click.echo(f"{'Project':<20} {'Requests':<10} {'Tokens':<15} {'Est. Cost ($)':<15}")
        click.echo("-" * 90)
        
        total_requests = 0
        total_tokens = 0
        total_cost = 0.0
        
        for row in results:
            total_requests += row[2]
            total_tokens += row[3]
            total_cost += row[4]
            
            click.echo(f"{row[1]:<20} {row[2]:<10} {row[3]:<15} ${row[4]:<14.4f}")
        
        click.echo("-" * 90)
        click.echo(f"{'TOTAL':<20} {total_requests:<10} {total_tokens:<15} ${total_cost:<14.4f}")

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def serve(host, port):
    """Start the gateway server."""
    import subprocess
    import sys
    
    click.echo(f"Starting LLM API Gateway on {host}:{port}...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "gateway:app", 
            "--host", host, 
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        click.echo("\nGateway stopped.")

if __name__ == "__main__":
    cli()