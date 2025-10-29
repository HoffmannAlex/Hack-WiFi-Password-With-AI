#!/bin/bash
echo "🔧 Installing Hack WiFi AI..."

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Run as root: sudo ./install.sh"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install essential tools
echo "📥 Installing WiFi hacking tools..."
apt install -y \
    aircrack-ng \
    wireshark \
    tshark \
    hashcat \
    crunch \
    wordlists \
    macchanger \
    net-tools \
    wireless-tools \
    iw

# Install Python and dependencies
echo "🐍 Installing Python dependencies..."
apt install -y python3 python3-pip python3-venv

# Create virtual environment
echo "🏗️ Setting up Python environment..."
python3 -m venv wifi-ai-env
source wifi-ai-env/bin/activate

# Install Python packages
pip3 install scapy pandas numpy requests

# Install drivers for common WiFi adapters
echo "📡 Installing WiFi drivers..."
apt install -y \
    realtek-rtl88xxau-dkms \
    broadcom-sta-dkms \
    firmware-ath9k-htc \
    firmware-atheros

# Create necessary directories
echo "📁 Creating project structure..."
mkdir -p captures wordlists results reports

# Set permissions
echo "🔒 Setting permissions..."
chmod +x main.py
chmod +x core/*.py
chmod +x ai/*.py
chmod +x hardware/*.py
chmod +x utils/*.py

# Enable WiFi interface monitoring
echo "📶 Configuring network interfaces..."
systemctl stop NetworkManager
systemctl start NetworkManager

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Usage:"
echo "   sudo ./main.py"
echo ""
echo "📋 Next steps:"
echo "   1. Connect compatible WiFi adapter"
echo "   2. Run: sudo ./main.py"
echo "   3. Follow legal guidelines"
echo ""
echo "⚠️  Legal: Only use on networks you own or have permission to test!"