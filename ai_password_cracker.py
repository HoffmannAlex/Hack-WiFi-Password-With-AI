import subprocess
import threading
from ai.password_generator import AIPasswordGenerator

class AICrackEngine:
    """Moteur de cracking AI intégré avec aircrack-ng"""
    
    def __init__(self):
        self.ai_generator = AIPasswordGenerator()
        self.is_cracking = False
        
    def crack_handshake_ai(self, capture_file: str, ssid: str, max_passwords: int = 100000):
        """Crack le handshake avec génération AI de mots de passe"""
        try:
            # Génère un fichier de mots de passe AI
            wordlist_file = self._generate_ai_wordlist(ssid, max_passwords)
            
            # Lance aircrack-ng avec la wordlist AI
            cmd = [
                "aircrack-ng",
                "-w", wordlist_file,
                "-b", self._get_bssid_from_capture(capture_file),
                capture_file
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
            
            for line in process.stdout:
                if "KEY FOUND" in line:
                    password = line.split("[")[1].split("]")[0]
                    return password
                    
            return None
            
        except Exception as e:
            print(f"❌ Erreur cracking: {e}")
            return None
    
    def _generate_ai_wordlist(self, ssid: str, count: int) -> str:
        """Génère une wordlist intelligente basée sur l'SSID"""
        passwords = set()
        
        for i in range(count):
            password = self.ai_generator.generate_context_password(ssid, i)
            passwords.add(password)
            
            if i % 1000 == 0:
                print(f"🤖 Génération AI: {i}/{count}")
        
        # Sauvegarde la wordlist
        filename = f"wordlists/ai_{ssid}_{int(time.time())}.txt"
        with open(filename, 'w') as f:
            f.write('\n'.join(passwords))
            
        return filename