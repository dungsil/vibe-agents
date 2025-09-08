/**
 * LLM API Gateway
 * 
 * A proxy service for LLM API calls that tracks usage per project using virtual API keys.
 */

import { Elysia, t } from 'elysia';
import { bearer } from '@elysiajs/bearer';
import { Database } from 'bun:sqlite';
import { randomUUID } from 'crypto';

const DB_PATH = 'gateway.db';

// Database setup
const db = new Database(DB_PATH);

// Initialize database with required tables
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

// Types
interface VirtualKeyCreate {
  project_name: string;
}

interface VirtualKeyResponse {
  id: string;
  project_name: string;
  created_at: string;
  is_active: boolean;
}

interface UsageStats {
  virtual_key_id: string;
  project_name: string;
  total_requests: number;
  total_tokens: number;
  estimated_cost: number;
}

interface KeyInfo {
  id: string;
  project_name: string;
  is_active: boolean;
}

// Database operations
const getVirtualKeyInfo = (virtualKey: string): KeyInfo | null => {
  const stmt = db.prepare(`
    SELECT id, project_name, is_active 
    FROM virtual_keys 
    WHERE id = ? AND is_active = TRUE
  `);
  return stmt.get(virtualKey) as KeyInfo | null;
};

const getRealApiKey = (provider: string): string | null => {
  const stmt = db.prepare('SELECT api_key FROM real_keys WHERE provider = ?');
  const result = stmt.get(provider) as { api_key: string } | undefined;
  return result?.api_key || null;
};

const logUsage = (
  virtualKeyId: string,
  provider: string,
  endpoint: string,
  requestTokens: number,
  responseTokens: number,
  estimatedCost: number
) => {
  const stmt = db.prepare(`
    INSERT INTO usage_records (virtual_key_id, provider, endpoint, request_tokens, response_tokens, estimated_cost)
    VALUES (?, ?, ?, ?, ?, ?)
  `);
  stmt.run(virtualKeyId, provider, endpoint, requestTokens, responseTokens, estimatedCost);
};

// Initialize database
initDb();

const app = new Elysia()
  .use(bearer())
  .onBeforeHandle(({ bearer, path, request }) => {
    // Skip authentication for admin endpoints and health check
    if (path.startsWith('/admin') || path === '/health') {
      return;
    }

    // For LLM API proxy endpoints, validate virtual key
    if (path.startsWith('/v1/')) {
      if (!bearer) {
        return new Response('Missing Authorization header', { status: 401 });
      }

      const keyInfo = getVirtualKeyInfo(bearer);
      if (!keyInfo) {
        return new Response('Invalid or inactive virtual API key', { status: 401 });
      }

      // Store key info in context for later use
      (request as any).keyInfo = keyInfo;
    }
  })

  // Admin endpoints
  .post('/admin/virtual-keys', ({ body }: { body: VirtualKeyCreate }) => {
    // Validate project name
    if (!body.project_name || !body.project_name.trim()) {
      return new Response('Project name cannot be empty', { status: 400 });
    }

    if (body.project_name.trim().length > 100) {
      return new Response('Project name too long (max 100 characters)', { status: 400 });
    }

    const virtualKeyId = randomUUID();
    const projectName = body.project_name.trim();

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
      const result = selectStmt.get(virtualKeyId) as VirtualKeyResponse;

      return result;
    } catch (error) {
      return new Response(`Database error: ${error}`, { status: 500 });
    }
  }, {
    body: t.Object({
      project_name: t.String()
    })
  })

  .get('/admin/virtual-keys', (): VirtualKeyResponse[] => {
    const stmt = db.prepare(`
      SELECT id, project_name, created_at, is_active 
      FROM virtual_keys 
      ORDER BY created_at DESC
    `);
    return stmt.all() as VirtualKeyResponse[];
  })

  .delete('/admin/virtual-keys/:keyId', ({ params }) => {
    const stmt = db.prepare('UPDATE virtual_keys SET is_active = FALSE WHERE id = ?');
    const result = stmt.run(params.keyId);
    
    if (result.changes === 0) {
      return new Response('Virtual key not found', { status: 404 });
    }

    return { message: 'Virtual key revoked successfully' };
  })

  .get('/admin/usage-stats', (): UsageStats[] => {
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
    return stmt.all() as UsageStats[];
  })

  // LLM API proxy endpoints
  .all('/v1/*', async ({ request, path }) => {
    const keyInfo = (request as any).keyInfo as KeyInfo;
    const llmPath = path.replace('/v1/', '');

    // Determine provider based on path
    let provider = 'openai'; // Default to OpenAI
    if (llmPath.toLowerCase().includes('anthropic')) {
      provider = 'anthropic';
    }

    // Get real API key for provider
    const realApiKey = getRealApiKey(provider);
    if (!realApiKey) {
      return new Response(`No API key configured for provider: ${provider}`, { status: 502 });
    }

    // Determine base URL based on provider
    const baseUrls: Record<string, string> = {
      openai: 'https://api.openai.com',
      anthropic: 'https://api.anthropic.com'
    };
    const baseUrl = baseUrls[provider] || 'https://api.openai.com';

    // Prepare request
    const url = `${baseUrl}/v1/${llmPath}`;
    const headers = new Headers(request.headers);

    // Replace authorization header with real API key
    if (provider === 'openai') {
      headers.set('Authorization', `Bearer ${realApiKey}`);
    } else if (provider === 'anthropic') {
      headers.set('x-api-key', realApiKey);
    }

    // Remove host header to avoid conflicts
    headers.delete('host');

    try {
      const response = await fetch(url, {
        method: request.method,
        headers: headers,
        body: request.method !== 'GET' ? await request.text() : undefined,
      });

      // Parse response to extract token usage (simplified)
      let requestTokens = 0;
      let responseTokens = 0;
      let estimatedCost = 0.0;

      const responseText = await response.text();
      
      if (response.headers.get('content-type')?.startsWith('application/json')) {
        try {
          const responseData = JSON.parse(responseText);
          if (responseData.usage) {
            const usage = responseData.usage;
            requestTokens = usage.prompt_tokens || 0;
            responseTokens = usage.completion_tokens || 0;
            // Simplified cost calculation (would need actual pricing)
            estimatedCost = (requestTokens * 0.0015 + responseTokens * 0.002) / 1000;
          }
        } catch {
          // Ignore parsing errors
        }
      }

      // Log usage
      logUsage(
        keyInfo.id,
        provider,
        llmPath,
        requestTokens,
        responseTokens,
        estimatedCost
      );

      // Return response
      return new Response(responseText, {
        status: response.status,
        headers: response.headers
      });

    } catch (error) {
      return new Response(`Error connecting to LLM provider: ${error}`, { status: 502 });
    }
  })

  .get('/health', () => ({
    status: 'healthy',
    timestamp: new Date().toISOString()
  }))

  .listen(8000);

console.log(`🦊 LLM API Gateway is running at ${app.server?.hostname}:${app.server?.port}`);

export default app;