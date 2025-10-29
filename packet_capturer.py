import subprocess
import threading
import time
from typing import Optional

class HandshakeCapturer:
    """Capture les handshakes WPA/WPA2 pour le cracking"""
    
    def __init__(self, interface: str = "wlan0mon"):
        self.interface = interface
        self.capture_file = "capture/handshake.cap"
        self.is_capturing = False
        
    def start_capture(self, target_bssid: str, channel: int) -> bool:
        """Démarre la capture du handshake WPA"""
        try:
            # Lance airodump-ng pour capturer le handshake
            cmd = [
                "airodump-ng",
                "--bssid", target_bssid,
                "--channel", str(channel),
                "--write", "capture/handshake",
                self.interface
            ]
            
            self.capture_process = subprocess.Popen(cmd)
            self.is_capturing = True
            return True
            
        except Exception as e:
            print(f"❌ Erreur capture: {e}")
            return False
    
    def check_handshake_captured(self) -> bool:
        """Vérifie si un handshake a été capturé"""
        try:
            # Utilise aircrack-ng pour vérifier le handshake
            cmd = ["aircrack-ng", "-J", "capture/handshake-01.cap"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return "WPA handshake" in result.stdout
        except:
            return False