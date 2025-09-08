#!/bin/bash
# Quick start script for LLM API Gateway

set -e

echo "🚀 LLM API Gateway Quick Start"
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "gateway.py" ]; then
    echo "❌ Please run this script from the LLM API Gateway directory"
    exit 1
fi

echo "✅ Python 3 found"

# Initialize if not already done
if [ ! -f "gateway.db" ]; then
    echo "🔧 Initializing gateway..."
    python3 cli.py init
else
    echo "✅ Gateway already initialized"
fi

# Check if any virtual keys exist
KEY_COUNT=$(python3 cli.py keys list --output json 2>/dev/null | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$KEY_COUNT" -eq 0 ]; then
    echo "🔑 Creating demo virtual key..."
    python3 cli.py keys create "Quick Start Demo"
    echo "✅ Demo virtual key created"
fi

# Show current status
echo ""
echo "📊 Current Status:"
python3 cli.py keys list
echo ""
python3 cli.py stats

echo ""
echo "🎯 Next Steps:"
echo "1. Configure real API keys:"
echo "   python3 cli.py config set-key openai 'your-openai-api-key'"
echo "   python3 cli.py config set-key anthropic 'your-anthropic-api-key'"
echo ""
echo "2. Start the gateway:"
echo "   python3 cli.py serve"
echo ""
echo "3. Test with your virtual key:"
FIRST_KEY=$(python3 cli.py keys list --output json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null || echo "")
if [ -n "$FIRST_KEY" ]; then
    echo "   curl -H 'Authorization: Bearer $FIRST_KEY' \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"model\":\"gpt-3.5-turbo\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}' \\"
    echo "        http://localhost:8000/v1/chat/completions"
fi

echo ""
echo "📚 For more info: cat README.md"