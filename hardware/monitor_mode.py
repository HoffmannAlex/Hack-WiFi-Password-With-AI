#!/usr/bin/env python3
"""
Monitor Mode Manager
Enable/disable monitor mode for WiFi adapters
"""

import subprocess
import time
import re
from typing import Optional

class MonitorMode:
    """Manage monitor mode for WiFi adapters"""
    
    def __init__(self):
        self.original_interfaces = {}
        
    def enable_monitor_mode(self, interface: str) -> Optional[str]:
        """Enable monitor mode on specified interface"""
        try:
            print(f"🔧 Enabling monitor mode on {interface}...")
            
            # Kill conflicting processes
            self._kill_conflicting_processes()
            
            # Check if already in monitor mode
            if self._is_monitor_mode(interface):
                print(f"✅ {interface} already in monitor mode")
                return interface
                
            # Try airmon-ng first
            result = subprocess.run([
                'airmon-ng', 'start', interface
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find the new monitor interface
                monitor_iface = self._find_monitor_interface(interface)
                if monitor_iface:
                    print(f"✅ Monitor mode enabled: {monitor_iface}")
                    self.original_interfaces[monitor_iface] = interface
                    return monitor_iface
            
            # Fallback to iwconfig method
            print("🔄 Trying iwconfig method...")
            monitor_iface = f"{interface}mon"
            
            subprocess.run(['ip', 'link', 'set', interface, 'down'])
            subprocess.run(['iwconfig', interface, 'mode', 'monitor'])
            subprocess.run(['ip', 'link', 'set', interface, 'up'])
            
            if self._is_monitor_mode(interface):
                print(f"✅ Monitor mode enabled: {interface}")
                return interface
            else:
                print("❌ Failed to enable monitor mode")
                return None
                
        except Exception as e:
            print(f"❌ Monitor mode error: {e}")
            return None
    
    def disable_monitor_mode(self, interface: str):
        """Disable monitor mode and restore managed mode"""
        try:
            # Find original interface name
            original_iface = self.original_interfaces.get(interface, interface)
            
            print(f"🔧 Disabling monitor mode on {interface}...")
            
            # Use airmon-ng to stop monitor mode
            subprocess.run(['airmon-ng', 'stop', interface], 
                         capture_output=True)
            
            # Ensure interface is back to managed mode
            subprocess.run(['ip', 'link', 'set', original_iface, 'down'])
            subprocess.run(['iwconfig', original_iface, 'mode', 'managed'])
            subprocess.run(['ip', 'link', 'set', original_iface, 'up'])
            
            print(f"✅ Monitor mode disabled, {original_iface} in managed mode")
            
        except Exception as e:
            print(f"❌ Monitor mode disable error: {e}")
    
    def _is_monitor_mode(self, interface: str) -> bool:
        """Check if interface is in monitor mode"""
        try:
            result = subprocess.run(['iwconfig', interface], 
                                  capture_output=True, text=True)
            return 'Mode:Monitor' in result.stdout
        except:
            return False
    
    def _find_monitor_interface(self, original_interface: str) -> Optional[str]:
        """Find the monitor interface created by airmon-ng"""
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if original_interface in line and 'Mode:Monitor' in line:
                    return line.split()[0]
                    
        except:
            pass
            
        return None
    
    def _kill_conflicting_processes(self):
        """Kill processes that might interfere with monitor mode"""
        try:
            subprocess.run(['airmon-ng', 'check', 'kill'], 
                         capture_output=True, text=True)
        except:
            pass