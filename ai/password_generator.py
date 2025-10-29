#!/usr/bin/env python3
"""
AI Password Generator
Advanced AI-powered WiFi password generation
"""

import random
import string
import re
from typing import List, Dict, Set
import hashlib

class AIPasswordGenerator:
    """AI-powered password generation with context awareness"""
    
    def __init__(self):
        self.common_patterns = self._load_common_patterns()
        self.generated_passwords = set()
        
    def _load_common_patterns(self) -> Dict[str, List[str]]:
        """Load common WiFi password patterns"""
        return {
            'common_words': [
                'password', 'admin', 'wifi', 'internet', 'home', 'office',
                'default', 'wireless', 'network', 'secure', 'security'
            ],
            'common_suffixes': ['123', '1234', '12345', '!', '@', '#', '2024', '2025'],
            'common_prefixes': ['!', '#', '$', 'admin', 'wifi', 'wireless', 'secure'],
            'keyboard_patterns': [
                'qwerty', 'asdfgh', 'zxcvbn', '1q2w3e', '1qaz2wsx', 'qazwsx',
                'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
            ],
            'special_chars': ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')'],
            'leet_replacements': {
                'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7',
                'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5', 'T': '7'
            }
        }
    
    def generate_context_password(self, ssid: str, attempt: int) -> str:
        """Generate context-aware password based on SSID and attempt number"""
        
        # Phase-based generation strategy
        if attempt < 1000:
            return self._phase1_generation(ssid)
        elif attempt < 5000:
            return self._phase2_generation(ssid)
        elif attempt < 20000:
            return self._phase3_generation(ssid)
        else:
            return self._phase4_generation(ssid)
    
    def _phase1_generation(self, ssid: str) -> str:
        """Phase 1: Common passwords and simple variations"""
        patterns = []
        
        # Common passwords
        patterns.extend(self.common_patterns['common_words'])
        
        # Simple SSID variations
        ssid_clean = self._clean_ssid(ssid)
        if ssid_clean:
            for suffix in self.common_patterns['common_suffixes']:
                patterns.extend([
                    ssid_clean + suffix,
                    ssid_clean.lower() + suffix,
                    ssid_clean.upper() + suffix
                ])
        
        return random.choice(patterns) if patterns else self._generate_random(8)
    
    def _phase2_generation(self, ssid: str) -> str:
        """Phase 2: Keyboard patterns and leet speak"""
        patterns = []
        
        # Keyboard patterns
        patterns.extend(self.common_patterns['keyboard_patterns'])
        
        # Leet speak variations
        ssid_clean = self._clean_ssid(ssid)
        if ssid_clean:
            leet_version = self._to_leet_speak(ssid_clean)
            patterns.extend([
                leet_version,
                leet_version + '123',
                leet_version + '!'
            ])
        
        # Mixed case variations
        for pattern in patterns[:10]:  # First 10 patterns
            patterns.extend([
                pattern.capitalize(),
                pattern.upper(),
                pattern.lower()
            ])
        
        return random.choice(patterns) if patterns else self._generate_random(10)
    
    def _phase3_generation(self, ssid: str) -> str:
        """Phase 3: Advanced pattern combinations"""
        base = self._clean_ssid(ssid) or 'WiFi'
        
        # Complex combinations
        strategies = [
            lambda: base + ''.join(random.choices(string.digits, k=4)),
            lambda: base.capitalize() + random.choice(self.common_patterns['special_chars']),
            lambda: random.choice(self.common_patterns['common_prefixes']) + base + '123',
            lambda: self._to_leet_speak(base) + random.choice(self.common_patterns['common_suffixes']),
            lambda: base + random.choice(self.common_patterns['special_chars']) + 
                   ''.join(random.choices(string.digits, k=3))
        ]
        
        password = random.choice(strategies)()
        return password if 8 <= len(password) <= 16 else self._generate_random(12)
    
    def _phase4_generation(self, ssid: str) -> str:
        """Phase 4: Maximum complexity and randomness"""
        # Generate completely random but structured passwords
        structures = [
            "wwwwddddss",  # word word word word digit digit digit digit special
            "wwwddssww",   # word word word digit digit special special word word
            "ddwwwwssdd",  # digit digit word word word word special special digit digit
        ]
        
        structure = random.choice(structures)
        password = []
        
        for char_type in structure:
            if char_type == 'w':  # word character
                password.append(random.choice(string.ascii_letters))
            elif char_type == 'd':  # digit
                password.append(random.choice(string.digits))
            elif char_type == 's':  # special
                password.append(random.choice(self.common_patterns['special_chars']))
        
        return ''.join(password)
    
    def _clean_ssid(self, ssid: str) -> str:
        """Clean SSID for password generation"""
        # Remove special characters and spaces
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', ssid)
        return cleaned if cleaned else 'WiFi'
    
    def _to_leet_speak(self, text: str) -> str:
        """Convert text to leet speak"""
        result = []
        for char in text:
            result.append(self.common_patterns['leet_replacements'].get(char, char))
        return ''.join(result)
    
    def _generate_random(self, length: int) -> str:
        """Generate random password"""
        chars = string.ascii_letters + string.digits + '!@#$%'
        return ''.join(random.choice(chars) for _ in range(length))