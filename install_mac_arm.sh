#!/bin/bash

# ============================================
# Video Translator - Mac ARM Installation
# ============================================
# Optimized for Apple Silicon (M1/M2/M3)
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║   Video Translator - Mac ARM Installation     ║"
echo "║   Optimized for Apple Silicon (M1/M2/M3)      ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running on Mac ARM
print_info "Checking system architecture..."
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    print_warning "This script is optimized for Apple Silicon (ARM64)"
    print_warning "Detected architecture: $ARCH"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
print_status "Running on Mac ARM64 (Apple Silicon)"

# Check for Homebrew
print_info "Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
    
    print_status "Homebrew installed"
else
    print_status "Homebrew already installed"
fi

# Update Homebrew
print_info "Updating Homebrew..."
brew update
print_status "Homebrew updated"

# Install Python 3.11 (best compatibility for Apple Silicon)
print_info "Installing Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    brew install python@3.11
    print_status "Python 3.11 installed"
else
    print_status "Python 3.11 already installed"
fi

# Install FFmpeg (optimized for ARM)
print_info "Installing FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    brew install ffmpeg
    print_status "FFmpeg installed"
else
    print_status "FFmpeg already installed"
fi

# Install Redis
print_info "Installing Redis..."
if ! command -v redis-server &> /dev/null; then
    brew install redis
    print_status "Redis installed"
else
    print_status "Redis already installed"
fi

# Start Redis service
print_info "Starting Redis service..."
brew services start redis
print_status "Redis service started"

# Create Python virtual environment
print_info "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip
print_status "pip upgraded"

# Install Python packages (ARM-optimized order)
print_info "Installing Python packages (this may take 5-10 minutes)..."

# Install NumPy first (ARM optimization)
print_info "Installing NumPy (ARM-optimized)..."
pip install numpy

# Install core dependencies
print_info "Installing core dependencies..."
pip install flask==3.0.0
pip install celery==5.3.4
pip install redis==5.0.1
pip install python-dotenv==1.0.0

# Install video processing tools
print_info "Installing video processing tools..."
pip install yt-dlp==2023.11.16
pip install ffmpeg-python==0.2.0

# Install Google AI packages
print_info "Installing Google AI (Gemini)..."
pip install google-generativeai==0.3.2

# Install Whisper (ARM-optimized with PyTorch)
print_info "Installing Whisper for Apple Silicon..."
# Install PyTorch for ARM first
pip install torch torchvision torchaudio

# Then install Whisper
pip install openai-whisper==20231117

# Install subtitle library
print_info "Installing subtitle tools..."
pip install pysrt==1.1.2

print_status "All Python packages installed"

# Create necessary directories
print_info "Creating project directories..."
mkdir -p temp
mkdir -p output
mkdir -p logs
print_status "Directories created"

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    print_info "Creating .env from .env.example..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status ".env file created"
        print_warning "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY"
    else
        print_error ".env.example not found"
        print_info "Please create .env file manually with your GEMINI_API_KEY"
    fi
else
    print_status ".env file already exists"
fi

# Test Redis connection
print_info "Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    print_status "Redis is running and accessible"
else
    print_error "Redis connection failed"
    print_info "Try: brew services restart redis"
fi

# Test FFmpeg
print_info "Testing FFmpeg..."
if ffmpeg -version > /dev/null 2>&1; then
    print_status "FFmpeg is working"
else
    print_error "FFmpeg test failed"
fi

# Test Python imports
print_info "Testing Python imports..."
python3 << 'EOF'
try:
    import flask
    import celery
    import redis
    import yt_dlp
    import whisper
    import google.generativeai as genai
    print("✓ All Python imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    print_status "All Python packages are working"
else
    print_error "Some Python packages failed to import"
fi

# Create launch scripts
print_info "Creating launch scripts..."

# Create start_redis.sh
cat > start_redis.sh << 'REDIS_SCRIPT'
#!/bin/bash
echo "Starting Redis..."
brew services start redis
echo "Redis started"
REDIS_SCRIPT
chmod +x start_redis.sh

# Create start_celery.sh
cat > start_celery.sh << 'CELERY_SCRIPT'
#!/bin/bash
source venv/bin/activate
echo "Starting Celery worker..."
celery -A tasks worker --loglevel=info
CELERY_SCRIPT
chmod +x start_celery.sh

# Create start_flask.sh
cat > start_flask.sh << 'FLASK_SCRIPT'
#!/bin/bash
source venv/bin/activate
echo "Starting Flask server..."
python app.py
FLASK_SCRIPT
chmod +x start_flask.sh

print_status "Launch scripts created"

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║         Installation Complete! 🎉             ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${YELLOW}📋 NEXT STEPS:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}1.${NC} Configure your API key:"
echo -e "   ${BLUE}nano .env${NC}"
echo -e "   Add your Gemini API key: ${YELLOW}GEMINI_API_KEY=your_key_here${NC}"
echo ""
echo -e "${GREEN}2.${NC} Start the services (in 3 separate terminals):"
echo ""
echo -e "   ${YELLOW}Terminal 1 - Redis:${NC}"
echo -e "   ${BLUE}./start_redis.sh${NC}"
echo ""
echo -e "   ${YELLOW}Terminal 2 - Celery Worker:${NC}"
echo -e "   ${BLUE}./start_celery.sh${NC}"
echo ""
echo -e "   ${YELLOW}Terminal 3 - Flask Server:${NC}"
echo -e "   ${BLUE}./start_flask.sh${NC}"
echo ""
echo -e "${GREEN}3.${NC} Open your browser:"
echo -e "   ${BLUE}http://localhost:5000${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}💡 TIP:${NC} Use the ${BLUE}./start.sh${NC} script to start all services at once!"
echo ""
echo -e "${GREEN}✨ Your Video Translator is ready to use!${NC}"
echo ""
