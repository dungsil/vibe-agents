# LLM API Gateway

A self-hosted proxy service for LLM API calls that tracks usage per project using virtual API keys.

## Features

- **API Proxying**: Routes requests to OpenAI, Anthropic, and other LLM providers
- **Virtual API Keys**: Manage project-specific keys separate from real provider keys
- **Usage Tracking**: Monitor token usage, costs, and request statistics per project
- **Self-Hosted**: Deploy on your own infrastructure with minimal dependencies
- **CLI Management**: Command-line tools for key management and administration
- **RESTful Admin API**: HTTP endpoints for programmatic management

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize the gateway
python cli.py init
```

### 2. Configuration

Edit `config.yaml` to add your real LLM provider API keys:

```yaml
providers:
  openai:
    api_key: "sk-your-openai-key-here"
  anthropic:
    api_key: "sk-ant-your-anthropic-key-here"
```

Or use the CLI:

```bash
python cli.py config set-key openai "sk-your-openai-key-here"
python cli.py config set-key anthropic "sk-ant-your-anthropic-key-here"
```

### 3. Create Virtual Keys

```bash
# Create a virtual key for your project
python cli.py keys create "My Project"

# List all virtual keys
python cli.py keys list
```

### 4. Start the Gateway

```bash
# Start the server
python cli.py serve

# Or run directly
python gateway.py
```

The gateway will be available at `http://localhost:8000`

## Usage

### Making API Calls

Use your virtual API key instead of your real API key when making requests:

```bash
# OpenAI API call via gateway
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Anthropic API call via gateway
curl http://localhost:8000/v1/messages \
  -H "Authorization: Bearer YOUR_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Administration

#### CLI Commands

```bash
# Virtual key management
python cli.py keys create "Project Name"    # Create new virtual key
python cli.py keys list                     # List all virtual keys
python cli.py keys revoke KEY_ID            # Revoke a virtual key

# Configuration management
python cli.py config set-key openai "sk-..."  # Set real API key
python cli.py config list-keys                # List configured keys (masked)

# Usage statistics
python cli.py stats                         # View usage statistics
python cli.py stats --output json          # JSON format
```

#### Admin API Endpoints

```bash
# Create virtual key
curl -X POST http://localhost:8000/admin/virtual-keys \
  -H "Content-Type: application/json" \
  -d '{"project_name": "My Project"}'

# List virtual keys
curl http://localhost:8000/admin/virtual-keys

# Get usage statistics
curl http://localhost:8000/admin/usage-stats

# Revoke virtual key
curl -X DELETE http://localhost:8000/admin/virtual-keys/KEY_ID
```

## Configuration

### Environment Variables

- `DB_PATH`: Path to SQLite database file (default: `gateway.db`)
- `CONFIG_PATH`: Path to configuration file (default: `config.yaml`)

### Configuration File

```yaml
server:
  host: "0.0.0.0"       # Server host
  port: 8000            # Server port

providers:
  openai:
    base_url: "https://api.openai.com"
    api_key: "your-key"
  anthropic:
    base_url: "https://api.anthropic.com"
    api_key: "your-key"

logging:
  level: "INFO"
  file: "gateway.log"

rate_limits:
  default: 100          # Requests per minute per virtual key
  premium: 1000
```

## Architecture

```
Client Application
       ↓
Virtual API Key Authentication
       ↓
LLM API Gateway
       ↓
Real API Key → LLM Provider (OpenAI/Anthropic/etc.)
       ↓
Usage Tracking & Statistics
```

## Database Schema

### Virtual Keys
- `id`: Unique virtual key identifier
- `project_name`: Project name for organization
- `created_at`: Creation timestamp
- `is_active`: Whether the key is active

### Real Keys
- `provider`: LLM provider name (openai, anthropic)
- `api_key`: Real API key for the provider
- `base_url`: Provider API base URL

### Usage Records
- `virtual_key_id`: Associated virtual key
- `provider`: LLM provider used
- `endpoint`: API endpoint called
- `request_tokens`: Input tokens used
- `response_tokens`: Output tokens generated
- `estimated_cost`: Calculated cost
- `timestamp`: Request timestamp

## Security Considerations

- **Store real API keys securely**: Use environment variables or encrypted configuration
- **Network security**: Deploy behind HTTPS and restrict access
- **Virtual key management**: Regularly rotate and audit virtual keys
- **Database security**: Secure the SQLite database file permissions
- **Admin endpoints**: Consider adding authentication for admin endpoints in production

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python cli.py init

EXPOSE 8000
CMD ["python", "gateway.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  llm-gateway:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DB_PATH=/app/data/gateway.db
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/
```

### Adding New Providers

1. Add provider configuration to `config.yaml`
2. Update the provider detection logic in `gateway.py`
3. Add provider-specific authentication headers
4. Update base URL mapping

## License

MIT License - see LICENSE file for details