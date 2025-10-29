#!/usr/bin/env python3
"""
Security Analyzer
Analyze WiFi network security and generate reports
"""

import json
import time
from typing import Dict, Any
from dataclasses import dataclass
import subprocess

@dataclass
class SecurityReport:
    """Security assessment report"""
    ssid: str
    bssid: str
    security_level: str
    encryption: str
    signal_strength: int
    channel: int
    recommendations: list
    risk_score: int
    vulnerabilities: list

class SecurityAnalyzer:
    """Analyze WiFi network security posture"""
    
    def __init__(self):
        self.reports = []
        
    def analyze_network(self, network) -> Dict[str, Any]:
        """Comprehensive security analysis of target network"""
        
        risk_score = 0
        vulnerabilities = []
        recommendations = []
        
        # Analyze encryption
        if network.security in ["WEP", "OPEN"]:
            risk_score += 80
            vulnerabilities.append("Weak encryption")
            recommendations.append("Upgrade to WPA2/WPA3")
        elif network.security == "WPA":
            risk_score += 60
            vulnerabilities.append("Deprecated WPA encryption")
            recommendations.append("Upgrade to WPA2/WPA3")
        elif network.security == "WPA2":
            risk_score += 30
            vulnerabilities.append("Potential KRACK vulnerability")
            recommendations.append("Consider WPA3 upgrade")
        elif network.security == "WPA3":
            risk_score += 10
            recommendations.append("Good security practice")
            
        # Analyze signal strength
        if network.signal > 80:
            risk_score += 5
            recommendations.append("Consider reducing transmit power")
        elif network.signal < 20:
            risk_score += 20
            vulnerabilities.append("Weak signal may indicate distance issues")
            
        # Analyze channel
        if 1 <= network.channel <= 11:
            risk_score += 5  # 2.4GHz crowded spectrum
        elif network.channel >= 36:
            risk_score += 0  # 5GHz less crowded
            
        # SSID analysis
        if self._is_default_ssid(network.ssid):
            risk_score += 25
            vulnerabilities.append("Default SSID detected")
            recommendations.append("Change default SSID")
            
        if self._contains_sensitive_info(network.ssid):
            risk_score += 30
            vulnerabilities.append("SSID contains sensitive information")
            recommendations.append("Change SSID to remove sensitive info")
            
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        return {
            'ssid': network.ssid,
            'bssid': network.bssid,
            'security_level': risk_level,
            'encryption': network.security,
            'signal_strength': network.signal,
            'channel': network.channel,
            'risk_score': risk_score,
            'vulnerabilities': vulnerabilities,
            'recommendations': recommendations,
            'timestamp': time.time()
        }
    
    def _is_default_ssid(self, ssid: str) -> bool:
        """Check if SSID is a default/router brand"""
        default_patterns = [
            'linksys', 'netgear', 'dlink', 'tp-link', 'asus', 
            'belkin', 'cisco', 'arris', 'default', 'wireless',
            'router', 'modem'
        ]
        return any(pattern in ssid.lower() for pattern in default_patterns)
    
    def _contains_sensitive_info(self, ssid: str) -> bool:
        """Check if SSID contains sensitive information"""
        sensitive_patterns = [
            'admin', 'password', 'security', 'wifi', 'internet',
            'company', 'corp', 'inc', 'office', 'home'
        ]
        return any(pattern in ssid.lower() for pattern in sensitive_patterns)
    
    def generate_report(self, analysis: Dict[str, Any]):
        """Generate comprehensive security report"""
        print(f"\n📊 SECURITY ANALYSIS REPORT")
        print(f"   SSID: {analysis['ssid']}")
        print(f"   BSSID: {analysis['bssid']}")
        print(f"   Risk Level: {analysis['security_level']}")
        print(f"   Risk Score: {analysis['risk_score']}/100")
        print(f"   Encryption: {analysis['encryption']}")
        print(f"   Signal: {analysis['signal_strength']}%")
        
        if analysis['vulnerabilities']:
            print(f"\n   🔴 VULNERABILITIES:")
            for vuln in analysis['vulnerabilities']:
                print(f"      • {vuln}")
                
        if analysis['recommendations']:
            print(f"\n   ✅ RECOMMENDATIONS:")
            for rec in analysis['recommendations']:
                print(f"      • {rec}")
                
        # Save to file
        self._save_report(analysis)
    
    def _save_report(self, analysis: Dict[str, Any]):
        """Save report to JSON file"""
        timestamp = int(time.time())
        filename = f"reports/security_analysis_{analysis['ssid']}_{timestamp}.json"
        
        os.makedirs("reports", exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
            
        print(f"   📄 Report saved: {filename}")