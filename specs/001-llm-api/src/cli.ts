#!/usr/bin/env bun
/**
 * LLM API Gateway CLI
 * 
 * Command-line interface for managing the LLM API Gateway.
 */

import { Command } from 'commander';
import { Database } from 'bun:sqlite';
import { randomUUID } from 'crypto';
import { writeFileSync, existsSync } from 'fs';
import YAML from 'yaml';

const DB_PATH = 'gateway.db';
const CONFIG_PATH = 'config.yaml';

// Database setup
const db = new Database(DB_PATH);

function initDb() {
  // Virtual API keys table
  db.exec(`
    CREATE TABLE IF NOT EXISTS virtual_keys (
      id TEXT PRIMARY KEY,
      project_name TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      is_active BOOLEAN DEFAULT TRUE
    )
  `);

  // Real API keys table
  db.exec(`
    CREATE TABLE IF NOT EXISTS real_keys (
      provider TEXT PRIMARY KEY,
      api_key TEXT NOT NULL,
      base_url TEXT
    )
  `);

  // Usage records table
  db.exec(`
    CREATE TABLE IF NOT EXISTS usage_records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      virtual_key_id TEXT,
      provider TEXT,
      endpoint TEXT,
      request_tokens INTEGER,
      response_tokens INTEGER,
      estimated_cost REAL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (virtual_key_id) REFERENCES virtual_keys (id)
    )
  `);
}

const program = new Command();

program
  .name('llm-gateway')
  .description('LLM API Gateway CLI - Manage virtual keys and configuration')
  .version('1.0.0');

// Init command
program
  .command('init')
  .description('Initialize the gateway database and configuration')
  .action(() => {
    console.log('Initializing LLM API Gateway...');
    
    // Create database
    initDb();
    console.log('✓ Database initialized');
    
    // Create default config if it doesn't exist
    if (!existsSync(CONFIG_PATH)) {
      const defaultConfig = {
        server: {
          host: '0.0.0.0',
          port: 8000
        },
        providers: {
          openai: {
            base_url: 'https://api.openai.com',
            api_key: ''
          },
          anthropic: {
            base_url: 'https://api.anthropic.com',
            api_key: ''
          }
        }
      };
      
      writeFileSync(CONFIG_PATH, YAML.stringify(defaultConfig));
      console.log(`✓ Configuration file created at ${CONFIG_PATH}`);
      console.log('  Please edit the configuration file to add your real API keys.');
    } else {
      console.log(`✓ Configuration file already exists at ${CONFIG_PATH}`);
    }
    
    console.log('Gateway initialization complete!');
  });

// Keys management commands
const keysCommand = program
  .command('keys')
  .description('Manage virtual API keys');

keysCommand
  .command('create')
  .description('Create a new virtual API key for a project')
  .argument('<project_name>', 'Name of the project')
  .option('-o, --output <format>', 'Output format (table|json)', 'table')
  .action((projectName: string, options) => {
    const virtualKeyId = randomUUID();
    
    try {
      const insertStmt = db.prepare(`
        INSERT INTO virtual_keys (id, project_name) VALUES (?, ?)
      `);
      insertStmt.run(virtualKeyId, projectName);
      
      const selectStmt = db.prepare(`
        SELECT id, project_name, created_at, is_active 
        FROM virtual_keys 
        WHERE id = ?
      `);
      const result = selectStmt.get(virtualKeyId) as any;
      
      if (options.output === 'json') {
        console.log(JSON.stringify({
          id: result.id,
          project_name: result.project_name,
          created_at: result.created_at,
          is_active: Boolean(result.is_active)
        }, null, 2));
      } else {
        console.log('✓ Virtual API key created successfully!');
        console.log(`  Project: ${result.project_name}`);
        console.log(`  Key ID: ${result.id}`);
        console.log(`  Created: ${result.created_at}`);
      }
    } catch (error) {
      console.error('✗ Error: Key creation failed', error);
      process.exit(1);
    }
  });

keysCommand
  .command('list')
  .description('List all virtual API keys')
  .option('-o, --output <format>', 'Output format (table|json)', 'table')
  .action((options) => {
    const stmt = db.prepare(`
      SELECT id, project_name, created_at, is_active 
      FROM virtual_keys 
      ORDER BY created_at DESC
    `);
    const results = stmt.all() as any[];
    
    if (options.output === 'json') {
      const keysData = results.map(row => ({
        id: row.id,
        project_name: row.project_name,
        created_at: row.created_at,
        is_active: Boolean(row.is_active)
      }));
      console.log(JSON.stringify(keysData, null, 2));
    } else {
      if (results.length === 0) {
        console.log('No virtual keys found.');
        return;
      }
      
      console.log('Virtual API Keys:');
      console.log('-'.repeat(80));
      console.log(`${'Project Name'.padEnd(20)} ${'Key ID'.padEnd(36)} ${'Created'.padEnd(20)} Active`);
      console.log('-'.repeat(80));
      
      results.forEach(row => {
        const status = row.is_active ? '✓' : '✗';
        console.log(`${row.project_name.padEnd(20)} ${row.id.padEnd(36)} ${row.created_at.padEnd(20)} ${status}`);
      });
    }
  });

keysCommand
  .command('revoke')
  .description('Revoke a virtual API key')
  .argument('<key_id>', 'ID of the key to revoke')
  .action((keyId: string) => {
    const stmt = db.prepare('UPDATE virtual_keys SET is_active = FALSE WHERE id = ?');
    const result = stmt.run(keyId);
    
    if (result.changes === 0) {
      console.error('✗ Virtual key not found');
      process.exit(1);
    } else {
      console.log('✓ Virtual key revoked successfully');
    }
  });

// Config management commands
const configCommand = program
  .command('config')
  .description('Manage gateway configuration');

configCommand
  .command('set-key')
  .description('Set real API key for a provider')
  .argument('<provider>', 'Provider name (openai|anthropic)')
  .argument('<api_key>', 'API key value')
  .action((provider: string, apiKey: string) => {
    if (!['openai', 'anthropic'].includes(provider)) {
      console.error('✗ Invalid provider. Use: openai, anthropic');
      process.exit(1);
    }
    
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO real_keys (provider, api_key) VALUES (?, ?)
    `);
    stmt.run(provider, apiKey);
    
    console.log(`✓ API key for ${provider} updated successfully`);
  });

configCommand
  .command('list-keys')
  .description('List configured real API keys (masked)')
  .action(() => {
    const stmt = db.prepare('SELECT provider, api_key FROM real_keys');
    const results = stmt.all() as any[];
    
    if (results.length === 0) {
      console.log('No API keys configured.');
      return;
    }
    
    console.log('Configured API Keys:');
    console.log('-'.repeat(40));
    console.log(`${'Provider'.padEnd(15)} API Key (masked)`);
    console.log('-'.repeat(40));
    
    results.forEach(({ provider, api_key }) => {
      const maskedKey = api_key.length > 8 ? `${api_key.slice(0, 8)}...` : '***';
      console.log(`${provider.padEnd(15)} ${maskedKey}`);
    });
  });

// Stats command
program
  .command('stats')
  .description('Show usage statistics')
  .option('-o, --output <format>', 'Output format (table|json)', 'table')
  .action((options) => {
    const stmt = db.prepare(`
      SELECT 
        vk.id as virtual_key_id,
        vk.project_name,
        COUNT(ur.id) as total_requests,
        COALESCE(SUM(ur.request_tokens + ur.response_tokens), 0) as total_tokens,
        COALESCE(SUM(ur.estimated_cost), 0) as estimated_cost
      FROM virtual_keys vk
      LEFT JOIN usage_records ur ON vk.id = ur.virtual_key_id
      GROUP BY vk.id, vk.project_name
      ORDER BY vk.created_at DESC
    `);
    const results = stmt.all() as any[];
    
    if (options.output === 'json') {
      const statsData = results.map(row => ({
        virtual_key_id: row.virtual_key_id,
        project_name: row.project_name,
        total_requests: row.total_requests,
        total_tokens: row.total_tokens,
        estimated_cost: row.estimated_cost
      }));
      console.log(JSON.stringify(statsData, null, 2));
    } else {
      if (results.length === 0) {
        console.log('No usage statistics found.');
        return;
      }
      
      console.log('Usage Statistics:');
      console.log('-'.repeat(90));
      console.log(`${'Project'.padEnd(20)} ${'Requests'.padEnd(10)} ${'Tokens'.padEnd(15)} ${'Est. Cost ($)'.padEnd(15)}`);
      console.log('-'.repeat(90));
      
      let totalRequests = 0;
      let totalTokens = 0;
      let totalCost = 0;
      
      results.forEach(row => {
        totalRequests += row.total_requests;
        totalTokens += row.total_tokens;
        totalCost += row.estimated_cost;
        
        console.log(
          `${row.project_name.padEnd(20)} ${row.total_requests.toString().padEnd(10)} ${row.total_tokens.toString().padEnd(15)} $${row.estimated_cost.toFixed(4).padEnd(14)}`
        );
      });
      
      console.log('-'.repeat(90));
      console.log(
        `${'TOTAL'.padEnd(20)} ${totalRequests.toString().padEnd(10)} ${totalTokens.toString().padEnd(15)} $${totalCost.toFixed(4).padEnd(14)}`
      );
    }
  });

// Serve command
program
  .command('serve')
  .description('Start the gateway server')
  .option('--host <host>', 'Host to bind to', '0.0.0.0')
  .option('--port <port>', 'Port to bind to', '8000')
  .action(async (options) => {
    console.log(`Starting LLM API Gateway on ${options.host}:${options.port}...`);
    
    try {
      // Use Bun to run the gateway
      const proc = Bun.spawn(['bun', 'run', 'src/gateway.ts'], {
        stdio: ['inherit', 'inherit', 'inherit'],
        env: {
          ...process.env,
          HOST: options.host,
          PORT: options.port
        }
      });
      
      process.on('SIGINT', () => {
        console.log('\nGateway stopped.');
        proc.kill();
        process.exit(0);
      });
      
      await proc.exited;
    } catch (error) {
      console.error('Error starting gateway:', error);
      process.exit(1);
    }
  });

if (import.meta.main) {
  program.parse();
}