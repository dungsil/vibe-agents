#!/bin/bash
# Quick start script for LLM API Gateway

set -e

echo "🚀 LLM API Gateway Quick Start"
echo "=============================="

# Check if Bun is available
if ! command -v bun &> /dev/null; then
    echo "❌ Bun is required but not installed"
    echo "   Install from: https://bun.sh/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "src/gateway.ts" ]; then
    echo "❌ Please run this script from the LLM API Gateway directory"
    exit 1
fi

echo "✅ Bun found"

# Install dependencies
echo "📦 Installing dependencies..."
bun install

# Initialize if not already done
if [ ! -f "gateway.db" ]; then
    echo "🔧 Initializing gateway..."
    bun run src/cli.ts init
else
    echo "✅ Gateway already initialized"
fi

# Check if any virtual keys exist
KEY_COUNT=$(bun run src/cli.ts keys list --output json 2>/dev/null | bun -e "console.log(JSON.parse(await Bun.stdin.text()).length)" 2>/dev/null || echo "0")

if [ "$KEY_COUNT" -eq 0 ]; then
    echo "🔑 Creating demo virtual key..."
    bun run src/cli.ts keys create "Quick Start Demo"
    echo "✅ Demo virtual key created"
fi

# Show current status
echo ""
echo "📊 Current Status:"
bun run src/cli.ts keys list
echo ""
bun run src/cli.ts stats

echo ""
echo "🎯 Next Steps:"
echo "1. Configure real API keys:"
echo "   bun run src/cli.ts config set-key openai 'your-openai-api-key'"
echo "   bun run src/cli.ts config set-key anthropic 'your-anthropic-api-key'"
echo ""
echo "2. Start the gateway:"
echo "   bun run src/cli.ts serve"
echo ""
echo "3. Test with your virtual key:"
FIRST_KEY=$(bun run src/cli.ts keys list --output json 2>/dev/null | bun -e "const data=JSON.parse(await Bun.stdin.text()); console.log(data[0]?.id || '')" 2>/dev/null || echo "")
if [ -n "$FIRST_KEY" ]; then
    echo "   curl -H 'Authorization: Bearer $FIRST_KEY' \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"model\":\"gpt-3.5-turbo\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}' \\"
    echo "        http://localhost:8000/v1/chat/completions"
fi

echo ""
echo "📚 For more info: cat README.md"