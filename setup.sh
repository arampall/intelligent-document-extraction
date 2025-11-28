#!/bin/bash

# Setup script for Receipt Scanner
# This script installs all system and Python dependencies

set -e  # Exit on error

echo "🚀 Starting setup for Receipt Scanner..."
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "This script supports macOS and Linux only."
    exit 1
fi

echo "✅ Detected OS: $OS"
echo ""

# Install Poppler (still needed for pdf2image)
echo "📦 Installing system dependencies..."
if [[ "$OS" == "macos" ]]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew is not installed. Please install it first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    echo "  → Installing Poppler (for PDF conversion)..."
    brew install poppler || echo "  ⚠️  Poppler may already be installed"
    
elif [[ "$OS" == "linux" ]]; then
    # Detect Linux distribution
    if command -v apt-get &> /dev/null; then
        echo "  → Installing Poppler via apt-get..."
        sudo apt-get update
        sudo apt-get install -y poppler-utils
    elif command -v yum &> /dev/null; then
        echo "  → Installing Poppler via yum..."
        sudo yum install -y poppler-utils
    else
        echo "❌ Could not detect package manager (apt-get or yum)"
        exit 1
    fi
fi

echo "✅ System dependencies installed"
echo ""

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ -d "venv" ]; then
    echo "  ⚠️  Virtual environment already exists at ./venv"
    read -p "  Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "  → Removing existing venv..."
        rm -rf venv
        echo "  → Creating new virtual environment..."
        python3 -m venv venv
    else
        echo "  → Using existing virtual environment"
    fi
else
    echo "  → Creating virtual environment..."
    python3 -m venv venv
fi

echo "✅ Virtual environment ready"
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your Google API key:"
echo "   export GOOGLE_API_KEY='your-api-key-here'"
echo ""
echo "3. Run the Receipt Scanner app:"
echo "   streamlit run app.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
