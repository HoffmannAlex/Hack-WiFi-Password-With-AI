#!/usr/bin/env python3
"""
AI Password Cracker
AI-powered WPA password cracking with aircrack-ng
"""

import subprocess
import time
import os
from typing import Optional
import sys

# Add AI module path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ai"))
from ai.password_generator import AIPasswordGenerator

class AICrackEngine:
    """AI-powered WPA password cracking engine"""
    
    def __init__(self):
        self.ai_generator = AIPasswordGenerator()
        self.is_cracking = False
        self.crack_process = None
        
    def crack_handshake(self, capture_file: str, wordlist_file: str, ssid: str) -> Optional[str]:
        """Crack handshake using aircrack-ng with AI wordlist"""
        try:
            if not os.path.exists(capture_file):
                print(f"❌ Capture file not found: {capture_file}")
                return None
                
            if not os.path.exists(wordlist_file):
                print(f"❌ Wordlist file not found: {wordlist_file}")
                return None
            
            print(f"🔓 Cracking {ssid} with AI wordlist...")
            print(f"   Capture: {capture_file}")
            print(f"   Wordlist: {wordlist_file}")
            
            # Start aircrack-ng
            cmd = [
                "aircrack-ng",
                "-w", wordlist_file,
                "-b", self._extract_bssid(capture_file),
                capture_file
            ]
            
            self.is_cracking = True
            self.crack_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor output for password
            password = None
            for line in self.crack_process.stdout:
                if not self.is_cracking:
                    break
                    
                if "KEY FOUND" in line:
                    # Extract password from line like: "KEY FOUND! [ password123 ]"
                    try:
                        password = line.split("[")[1].split("]")[0].strip()
                        print(f"✅ KEY FOUND: {password}")
                        break
                    except IndexError:
                        continue
                        
                # Show progress
                if "Passphrase" in line or "Keys tested" in line:
                    print(f"   {line.strip()}")
            
            self.crack_process.terminate()
            return password
            
        except Exception as e:
            print(f"❌ Cracking error: {e}")
            return None
        finally:
            self.is_cracking = False
    
    def _extract_bssid(self, capture_file: str) -> str:
        """Extract BSSID from capture file"""
        try:
            cmd = ["aircrack-ng", "-J", capture_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse BSSID from output
            for line in result.stdout.split('\n'):
                if "BSSID" in line and len(line.split()) > 1:
                    return line.split()[1]
                    
        except:
            pass
            
        return "00:00:00:00:00:00"  # Fallback
    
    def stop_cracking(self):
        """Stop the cracking process"""
        self.is_cracking = False
        if self.crack_process:
            self.crack_process.terminate()