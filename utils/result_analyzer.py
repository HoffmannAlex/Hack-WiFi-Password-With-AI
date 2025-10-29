#!/usr/bin/env python3
"""
Result Analyzer
Analyze and report cracking results
"""

import json
import time
from typing import Dict, Any
import os

class ResultAnalyzer:
    """Analyze and report password cracking results"""
    
    def __init__(self):
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def save_cracking_result(self, ssid: str, password: str, 
                           attempts: int, duration: float, method: str):
        """Save successful cracking result"""
        result = {
            'ssid': ssid,
            'password': password,
            'attempts': attempts,
            'duration_seconds': duration,
            'method': method,
            'timestamp': time.time(),
            'date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        filename = f"{self.results_dir}/cracked_{ssid.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"💾 Result saved: {filename}")
        return result
    
    def generate_report(self, results: Dict[str, Any]):
        """Generate comprehensive cracking report"""
        timestamp = int(time.time())
        report_file = f"{self.results_dir}/full_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"📊 Full report saved: {report_file}")
        
        # Print summary
        self._print_summary(results)
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print results summary"""
        print(f"\n📈 CRACKING SUMMARY")
        print(f"   SSID: {results.get('ssid', 'Unknown')}")
        
        if results.get('password'):
            print(f"   🔓 PASSWORD FOUND: {results['password']}")
            print(f"   ⏱️  Time: {results.get('duration_seconds', 0):.2f}s")
            print(f"   🔢 Attempts: {results.get('attempts', 0)}")
            print(f"   🎯 Method: {results.get('method', 'AI')}")
        else:
            print(f"   ❌ PASSWORD NOT FOUND")
            print(f"   ⏱️  Time spent: {results.get('duration_seconds', 0):.2f}s")
            print(f"   🔢 Attempts made: {results.get('attempts', 0)}")
    
    def load_previous_results(self) -> Dict[str, Any]:
        """Load previous cracking results"""
        results = {}
        
        if os.path.exists(self.results_dir):
            for file in os.listdir(self.results_dir):
                if file.endswith('.json') and file.startswith('cracked_'):
                    try:
                        with open(os.path.join(self.results_dir, file), 'r') as f:
                            result = json.load(f)
                            results[result['ssid']] = result
                    except:
                        continue
                        
        return results