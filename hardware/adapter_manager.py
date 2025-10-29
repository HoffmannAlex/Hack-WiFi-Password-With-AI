#!/usr/bin/env python3
"""
WiFi Adapter Manager
Detect and manage WiFi adapters for penetration testing
"""

import subprocess
import re
from typing import List, Dict, Optional

class AdapterManager:
    """Manage WiFi adapters and their capabilities"""
    
    def __init__(self):
        self.adapters = []
        self.required_tools = [
            'aircrack-ng', 'airodump-ng', 'aireplay-ng', 
            'iwconfig', 'iwlist', 'ifconfig'
        ]
        
    def detect_wifi_adapters(self) -> List[Dict]:
        """Detect available WiFi adapters"""
        self.adapters = []
        
        try:
            # Use iwconfig to find wireless interfaces
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            
            current_adapter = None
            for line in result.stdout.split('\n'):
                # Look for interface names (no spaces at start of line)
                if line and not line.startswith(' ') and 'no wireless' not in line:
                    if 'IEEE 802.11' in line:
                        adapter_name = line.split()[0]
                        current_adapter = {
                            'interface': adapter_name,
                            'driver': 'unknown',
                            'chipset': 'unknown',
                            'monitor_support': False,
                            'injection_support': False
                        }
                        self.adapters.append(current_adapter)
                        
                elif current_adapter and 'Mode:' in line:
                    if 'Monitor' in line:
                        current_adapter['monitor_support'] = True
                        
            # Get detailed info for each adapter
            for adapter in self.adapters:
                self._get_adapter_details(adapter)
                
            return self.adapters
            
        except Exception as e:
            print(f"❌ Adapter detection error: {e}")
            return []
    
    def _get_adapter_details(self, adapter: Dict):
        """Get detailed information about adapter"""
        try:
            # Get driver info
            cmd = ['ethtool', '-i', adapter['interface']]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'driver:' in line:
                    adapter['driver'] = line.split(':')[1].strip()
                elif 'bus-info:' in line:
                    adapter['bus_info'] = line.split(':')[1].strip()
                    
            # Check injection capability
            injection_test = subprocess.run([
                'aireplay-ng', '-9', adapter['interface']
            ], capture_output=True, text=True)
            
            adapter['injection_support'] = 'Injection is working' in injection_test.stdout
            
        except:
            adapter['driver'] = 'unknown'
            adapter['injection_support'] = False
    
    def check_required_tools(self) -> bool:
        """Check if all required tools are installed"""
        missing_tools = []
        
        for tool in self.required_tools:
            try:
                subprocess.run(['which', tool], capture_output=True)
            except:
                missing_tools.append(tool)
                
        if missing_tools:
            print(f"❌ Missing tools: {', '.join(missing_tools)}")
            return False
            
        return True
    
    def get_best_adapter(self) -> Optional[str]:
        """Get the best available adapter for penetration testing"""
        if not self.adapters:
            self.detect_wifi_adapters()
            
        # Prefer adapters with monitor and injection support
        for adapter in self.adapters:
            if adapter.get('monitor_support') and adapter.get('injection_support'):
                return adapter['interface']
                
        # Fallback to first adapter
        if self.adapters:
            return self.adapters[0]['interface']
            
        return None