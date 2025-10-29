#!/usr/bin/env python3
"""
WiFi Network Scanner
Advanced scanning with airodump-ng integration
"""

import subprocess
import re
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import threading

@dataclass
class WiFiNetwork:
    """Data class for WiFi network information"""
    ssid: str
    bssid: str
    signal: int
    channel: int
    encryption: str
    security: str
    clients: int = 0

class WiFiScanner:
    """Advanced WiFi network scanner using airodump-ng"""
    
    def __init__(self, scan_time: int = 10):
        self.scan_time = scan_time
        self.networks = []
        self.scan_process = None
        
    def scan_networks(self, interface: str = "wlan0mon") -> List[WiFiNetwork]:
        """Scan for WiFi networks using airodump-ng"""
        try:
            print(f"🔍 Scanning with airodump-ng on {interface}...")
            
            # Run airodump-ng
            cmd = [
                "airodump-ng",
                "--write", "scan_results",
                "--output-format", "csv",
                "--write-interval", "2",
                interface
            ]
            
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Let it scan for specified time
            time.sleep(self.scan_time)
            self.scan_process.terminate()
            self.scan_process.wait()
            
            # Parse results
            return self._parse_airodump_results("scan_results-01.csv")
            
        except Exception as e:
            print(f"❌ Scan error: {e}")
            return []
    
    def _parse_airodump_results(self, csv_file: str) -> List[WiFiNetwork]:
        """Parse airodump-ng CSV results"""
        networks = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Find start of network data
            start_index = 0
            for i, line in enumerate(lines):
                if line.startswith('BSSID,'):
                    start_index = i + 1
                    break
            
            # Parse network entries
            for line in lines[start_index:]:
                if line.strip() == '':
                    break
                    
                parts = line.split(',')
                if len(parts) >= 14:
                    try:
                        network = WiFiNetwork(
                            bssid=parts[0].strip(),
                            signal=int(parts[8].strip()) if parts[8].strip() else 0,
                            channel=int(parts[3].strip()) if parts[3].strip() else 1,
                            ssid=parts[13].strip(),
                            encryption=parts[5].strip(),
                            security=self._determine_security(parts[5].strip())
                        )
                        networks.append(network)
                    except (ValueError, IndexError):
                        continue
                        
        except FileNotFoundError:
            print("❌ Scan results file not found")
            
        # Sort by signal strength
        networks.sort(key=lambda x: x.signal, reverse=True)
        return networks
    
    def _determine_security(self, encryption: str) -> str:
        """Determine security level from encryption string"""
        enc_lower = encryption.lower()
        
        if 'wpa3' in enc_lower:
            return 'WPA3'
        elif 'wpa2' in enc_lower:
            return 'WPA2'
        elif 'wpa' in enc_lower:
            return 'WPA'
        elif 'wep' in enc_lower:
            return 'WEP'
        elif 'open' in enc_lower:
            return 'OPEN'
        else:
            return 'UNKNOWN'
    
    def get_network_details(self, bssid: str) -> Optional[Dict]:
        """Get detailed information for specific network"""
        for network in self.networks:
            if network.bssid.lower() == bssid.lower():
                return {
                    'ssid': network.ssid,
                    'bssid': network.bssid,
                    'signal': network.signal,
                    'channel': network.channel,
                    'security': network.security,
                    'encryption': network.encryption
                }
        return None