#!/usr/bin/env python3
"""
Wordlist Manager
Generate and manage AI-powered password wordlists
"""

import os
import random
import string
from typing import List, Set
import sys

# Add AI module path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ai"))
from ai.password_generator import AIPasswordGenerator

class WordlistManager:
    """Manage AI-generated and traditional wordlists"""
    
    def __init__(self):
        self.ai_generator = AIPasswordGenerator()
        self.wordlist_dir = "wordlists"
        os.makedirs(self.wordlist_dir, exist_ok=True)
        
    def generate_ai_wordlist(self, ssid: str, count: int = 100000) -> str:
        """Generate AI-powered wordlist based on SSID analysis"""
        print(f"🧠 Generating AI wordlist for '{ssid}' ({count} passwords)...")
        
        passwords = set()
        generated = 0
        
        while generated < count:
            # Generate passwords using AI strategies
            password = self.ai_generator.generate_context_password(ssid, generated)
            
            if password and password not in passwords:
                passwords.add(password)
                generated += 1
                
            if generated % 10000 == 0:
                print(f"   Generated {generated}/{count} passwords...")
                
            # Safety break
            if generated >= count * 1.1:  # Allow 10% overrun for uniqueness
                break
        
        # Add common WiFi passwords
        common_passwords = self._get_common_wifi_passwords()
        passwords.update(common_passwords)
        
        # Save to file
        filename = f"{self.wordlist_dir}/ai_{ssid.replace(' ', '_')}_{count}.txt"
        self._save_wordlist(passwords, filename)
        
        print(f"✅ AI wordlist generated: {filename} ({len(passwords)} passwords)")
        return filename
    
    def _get_common_wifi_passwords(self) -> List[str]:
        """Get list of common WiFi passwords"""
        return [
            'password', '12345678', '1234567890', 'admin', 'wifi', 'internet',
            'password123', '123456789', 'qwerty', 'abc123', 'default', '1234',
            '12345', '123456', '1234567', '1234567890', '00000000', '11111111',
            '123123123', 'password1', 'password!', 'wifi123', 'admin123',
            'letmein', 'monkey', 'dragon', 'master', 'qwertyuiop', 'baseball',
            'football', 'jordan', 'harley', 'ranger', 'mustang', 'shadow',
            'ashley', 'michael', 'charlie', 'andrew', 'superman', 'batman'
        ]
    
    def _save_wordlist(self, passwords: Set[str], filename: str):
        """Save wordlist to file"""
        with open(filename, 'w') as f:
            for password in passwords:
                f.write(f"{password}\n")
    
    def combine_wordlists(self, files: List[str], output_file: str):
        """Combine multiple wordlist files"""
        all_passwords = set()
        
        for file in files:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    for line in f:
                        password = line.strip()
                        if password:
                            all_passwords.add(password)
        
        self._save_wordlist(all_passwords, output_file)
        return output_file
    
    def optimize_wordlist(self, input_file: str, output_file: str):
        """Optimize wordlist by removing duplicates and sorting"""
        if not os.path.exists(input_file):
            return input_file
            
        passwords = set()
        with open(input_file, 'r') as f:
            for line in f:
                passwords.add(line.strip())
                
        # Sort by length and commonality
        sorted_passwords = sorted(passwords, key=lambda x: (len(x), x))
        
        with open(output_file, 'w') as f:
            for password in sorted_passwords:
                f.write(f"{password}\n")
                
        return output_file