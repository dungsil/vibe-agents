#!/usr/bin/env bun
/**
 * Simple test script for the LLM API Gateway.
 */

const GATEWAY_URL = "http://localhost:8000";

interface VirtualKey {
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

async function testHealth(): Promise<boolean> {
  console.log("Testing health endpoint...");
  try {
    const response = await fetch(`${GATEWAY_URL}/health`);
    if (response.ok) {
      console.log("✓ Health check passed");
      return true;
    } else {
      console.log("✗ Health check failed");
      return false;
    }
  } catch (error) {
    console.log("✗ Health check failed:", error);
    return false;
  }
}

async function testAdminEndpoints(): Promise<{ success: boolean; virtualKey?: string }> {
  console.log("\nTesting admin endpoints...");
  
  try {
    // Create a virtual key
    console.log("Creating virtual key...");
    const createResponse = await fetch(`${GATEWAY_URL}/admin/virtual-keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: "Test Project" })
    });
    
    if (!createResponse.ok) {
      console.log("✗ Failed to create virtual key");
      return { success: false };
    }
    
    const keyData: VirtualKey = await createResponse.json();
    const virtualKey = keyData.id;
    console.log(`✓ Virtual key created: ${virtualKey}`);
    
    // List virtual keys
    const listResponse = await fetch(`${GATEWAY_URL}/admin/virtual-keys`);
    if (!listResponse.ok) {
      console.log("✗ Failed to list virtual keys");
      return { success: false, virtualKey };
    }
    
    const keys: VirtualKey[] = await listResponse.json();
    console.log(`✓ Listed ${keys.length} virtual keys`);
    
    // Get usage stats
    const statsResponse = await fetch(`${GATEWAY_URL}/admin/usage-stats`);
    if (!statsResponse.ok) {
      console.log("✗ Failed to get usage stats");
      return { success: false, virtualKey };
    }
    
    const stats: UsageStats[] = await statsResponse.json();
    console.log(`✓ Retrieved usage stats for ${stats.length} projects`);
    
    return { success: true, virtualKey };
  } catch (error) {
    console.log("✗ Admin endpoints test failed:", error);
    return { success: false };
  }
}

async function testLLMProxy(virtualKey: string): Promise<boolean> {
  console.log("\nTesting LLM proxy endpoint...");
  console.log("Note: This test will fail without a real OpenAI API key configured");
  
  try {
    const response = await fetch(`${GATEWAY_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${virtualKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: "Say hello!" }],
        max_tokens: 10
      })
    });
    
    if (response.status === 502) {
      console.log("⚠ LLM proxy test skipped (no API key configured)");
      return true; // Expected without real API key
    } else if (response.ok) {
      console.log("✓ LLM proxy test passed");
      return true;
    } else {
      console.log(`✗ LLM proxy test failed with status: ${response.status}`);
      const text = await response.text();
      console.log("Response:", text);
      return false;
    }
  } catch (error) {
    console.log("✗ LLM proxy test failed:", error);
    return false;
  }
}

async function cleanup(virtualKey?: string): Promise<void> {
  if (!virtualKey) return;
  
  console.log("\nCleaning up test data...");
  try {
    const response = await fetch(`${GATEWAY_URL}/admin/virtual-keys/${virtualKey}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      console.log("✓ Test virtual key cleaned up");
    } else {
      console.log("⚠ Failed to clean up test virtual key");
    }
  } catch (error) {
    console.log("⚠ Cleanup failed:", error);
  }
}

async function main(): Promise<void> {
  console.log("🧪 LLM API Gateway Test Suite");
  console.log("===============================");
  
  const tests: boolean[] = [];
  let virtualKey: string | undefined;
  
  // Test health endpoint
  tests.push(await testHealth());
  
  // Test admin endpoints
  const adminResult = await testAdminEndpoints();
  tests.push(adminResult.success);
  virtualKey = adminResult.virtualKey;
  
  // Test LLM proxy if we have a virtual key
  if (virtualKey) {
    tests.push(await testLLMProxy(virtualKey));
  }
  
  // Cleanup
  await cleanup(virtualKey);
  
  // Summary
  const passed = tests.filter(Boolean).length;
  const total = tests.length;
  
  console.log("\n📊 Test Results:");
  console.log(`Passed: ${passed}/${total}`);
  
  if (passed === total) {
    console.log("🎉 All tests passed!");
    process.exit(0);
  } else {
    console.log("❌ Some tests failed");
    process.exit(1);
  }
}

if (import.meta.main) {
  main().catch(error => {
    console.error("Test suite failed:", error);
    process.exit(1);
  });
}