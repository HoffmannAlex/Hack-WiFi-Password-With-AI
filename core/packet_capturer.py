#!/usr/bin/env python3
"""
WPA Handshake Capturer
Capture and validate WPA/WPA2 handshakes
"""

import subprocess
import threading
import time
import os
from typing import Optional
import re

class HandshakeCapturer:
    """Capture WPA handshakes using airodump-ng"""
    
    def __init__(self):
        self.capture_process = None
        self.is_capturing = False
        self.capture_file = None
        
    def start_capture(self, interface: str, target_bssid: str, channel: int) -> bool:
        """Start capturing handshake for target network"""
        try:
            # Create capture directory
            os.makedirs("captures", exist_ok=True)
            
            timestamp = int(time.time())
            self.capture_file = f"captures/handshake_{timestamp}"
            
            # Start airodump-ng for specific target
            cmd = [
                "airodump-ng",
                "--bssid", target_bssid,
                "--channel", str(channel),
                "--write", self.capture_file,
                "--output-format", "pcap",
                interface
            ]
            
            print(f"🎣 Starting capture: {' '.join(cmd)}")
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.is_capturing = True
            return True
            
        except Exception as e:
            print(f"❌ Capture start error: {e}")
            return False
    
    def check_handshake(self) -> bool:
        """Check if WPA handshake has been captured"""
        if not self.capture_file:
            return False
            
        try:
            # Use aircrack-ng to verify handshake
            cmd = ["aircrack-ng", "-J", f"{self.capture_file}-01.cap"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if "WPA handshake" in result.stdout:
                return True
                
            # Alternative check with cap files
            cap_file = f"{self.capture_file}-01.cap"
            if os.path.exists(cap_file):
                # Check file size and content
                stat = os.stat(cap_file)
                if stat.st_size > 1000:  # Reasonable minimum size
                    return self._analyze_cap_file(cap_file)
                    
        except Exception as e:
            print(f"❌ Handshake check error: {e}")
            
        return False
    
    def _analyze_cap_file(self, cap_file: str) -> bool:
        """Analyze cap file for handshake indicators"""
        try:
            # Use tshark to analyze packets
            cmd = [
                "tshark", "-r", cap_file, 
                "-Y", "eapol", 
                "-T", "fields", "-e", "wlan_mgt.fixed.cookie"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Count EAPOL packets (should have multiple for handshake)
            eapol_count = len([line for line in result.stdout.split('\n') if line.strip()])
            return eapol_count >= 4  # Complete handshake has 4 packets
            
        except:
            return False
    
    def stop_capture(self):
        """Stop the capture process"""
        if self.capture_process:
            self.capture_process.terminate()
            self.capture_process.wait()
            self.is_capturing = False
    
    def get_capture_file(self) -> Optional[str]:
        """Get the capture file path"""
        if self.capture_file:
            return f"{self.capture_file}-01.cap"
        return None