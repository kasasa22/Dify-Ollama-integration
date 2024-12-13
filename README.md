# Dify-Ollama Integration

![cover-v5-optimized](https://github.com/langgenius/dify/assets/13230914/f9e19af5-61ba-4119-b926-d10c4c06ebab)

A complete guide for setting up Dify with Ollama integration for local LLM deployment.

## System Requirements

- CPU >= 2 Core
- RAM >= 4 GiB
- Python 3.8 or higher
- Docker and Docker Compose
- Git

## Detailed Installation Guide

### 1. Setting Up Dify

First, clone and set up the Dify repository:
```bash
# Clone the Dify repository
git clone https://github.com/langgenius/dify.git
cd dify

# Navigate to docker directory
cd docker

# Create environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with necessary configurations:
```bash
# Core settings
EDITION=community
CONSOLE_URL=http://localhost
API_URL=http://localhost/api
APP_URL=http://localhost

# Database settings
DB_HOST=postgres
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=difyai123456
DB_DATABASE=dify

# Redis settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=difyai123456

# Storage settings
STORAGE_TYPE=local
```

### 3. Start Dify with Docker

Launch the Dify services:
```bash
# Start all services
docker compose up -d

# Check if services are running
docker ps
```

### 4. Installing Ollama

Set up Ollama in parallel:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Pull a model (in a new terminal)
ollama pull llama2
```

### 5. Web Interface Configuration

1. Access Dify Setup:
   - Open your browser and go to `http://localhost/install`
   - Complete the initial setup process:
     - Create your admin account
     - Set your workspace name
     - Choose your preferred language

2. Configure Model Provider:
   - Log into Dify dashboard
   - Navigate to `Settings > Model Providers`
   - Click "Add Model Provider"
   - Choose "Custom Model Provider"

3. Add Ollama Configuration:
   ```
   Provider Name: Ollama
   Base URL: http://localhost:11434/v1
   Supported Models: llama2
   ```
   - Click "Test Connection" to verify
   - Save the configuration

4. Configure a Model:
   - Go to `Settings > Model Settings`
   - Click "Add New Model"
   - Select "Ollama" as provider
   - Choose your model (e.g., llama2)
   - Configure model parameters:
     ```
     Name: Llama 2
     Model: llama2
     Context Length: 4096
     Temperature: 0.7
     ```
   - Save the model configuration

5. Create an Application:
   - Go to "Applications" in sidebar
   - Click "Create New"
   - Choose application type (Chat or Text Generation)
   - Select your configured Ollama model
   - Configure prompt templates
   - Test the integration

## Testing the Integration

1. Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

2. Check available models:
```bash
ollama list
```

3. Test in Dify:
   - Open your created application
   - Try sending a test message
   - Check response generation
   - Verify model parameters

## Common Issues and Solutions

1. Dify Container Issues:
```bash
# Check container logs
docker logs dify-api
docker logs dify-web

# Restart containers
docker compose restart
```

2. Ollama Connection Problems:
```bash
# Verify Ollama is running
ps aux | grep ollama

# Restart Ollama
sudo systemctl restart ollama
```

3. Model Loading Issues:
```bash
# Remove and repull model
ollama rm llama2
ollama pull llama2
```

## Environment Variables Reference

Key variables in `.env` file:
```bash
# Model Settings
OLLAMA_HOST=http://localhost:11434
SERVER_PORT=8000

# Security Settings
CONSOLE_API_AUTH_SECRET_KEY=your-secret-key
CONSOLE_COOKIE_SECRET_KEY=your-cookie-key
```

## API Endpoints

- POST `/v1/chat/completions`: Chat completions
- POST `/v1/completions`: Text completions
- GET `/v1/models`: List available models

## Support

For support:
1. Check container logs: `docker logs dify-api`
2. Check Ollama logs: `journalctl -u ollama`
3. Create an issue with:
   - Error messages
   - Container logs
   - Configuration details

## License

This project is licensed under the MIT License - see the LICENSE file for details.
