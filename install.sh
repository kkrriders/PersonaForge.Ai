#!/bin/bash

# PersonaForge.AI Installation Script
# Sets up the local LinkedIn automation environment

set -e

echo "🚀 PersonaForge.AI Installation Script"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file..."
        cp .env.example .env
        echo "✅ .env file created from template"
    else
        echo "⚠️  .env.example not found, creating basic .env..."
        cat > .env << EOL
# PersonaForge.AI Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
DATABASE_PATH=data/linkedin_tool.db
LOCAL_STORAGE_ONLY=true
ENCRYPT_DATA=true
EOL
        echo "✅ Basic .env file created"
    fi
else
    echo "✅ .env file already exists"
fi

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p data/{images,posts,schedules,analytics,backups}
echo "✅ Directories created"

# Check Ollama installation
echo "🤖 Checking Ollama installation..."
if command -v ollama >/dev/null 2>&1; then
    echo "✅ Ollama is installed"
    
    # Check if llama3.2 model is available
    if ollama list | grep -q "llama3.2"; then
        echo "✅ llama3.2 model is available"
    else
        echo "📥 Downloading llama3.2 model..."
        ollama pull llama3.2
        echo "✅ llama3.2 model downloaded"
    fi
else
    echo "❌ Ollama not found!"
    echo "Please install Ollama from https://ollama.ai"
    echo "Then run: ollama pull llama3.2"
    echo ""
    echo "Installation will continue, but Ollama is required for operation."
fi

# Set permissions
echo "🔒 Setting file permissions..."
chmod +x startup.py
chmod +x main.py
echo "✅ Permissions set"

echo ""
echo "🎉 Installation Complete!"
echo "======================="
echo ""
echo "Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Start the application: python startup.py"
echo "   OR: python main.py (direct launch)"
echo ""
echo "For development:"
echo "- Activate venv: source venv/bin/activate"
echo "- Run tests: python -m pytest (if tests are added)"
echo ""
echo "Configuration:"
echo "- Edit .env file to customize settings"
echo "- All data stored in ./data/ directory"
echo ""
echo "Support:"
echo "- Check README.md for detailed documentation"
echo "- System status available in application menu"