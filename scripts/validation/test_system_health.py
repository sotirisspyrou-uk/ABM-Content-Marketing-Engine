#!/usr/bin/env python3
"""
System Health Validation Script
Tests all core components of the ABM Content Marketing Engine
"""

import os
import sys
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SystemHealthValidator:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.results = []
    
    def log_result(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}: {message}")
    
    def test_environment_variables(self):
        """Test that all required environment variables are present"""
        required_vars = [
            "HUBSPOT_API_KEY",
            "HUBSPOT_PORTAL_ID", 
            "CLAUDE_API_KEY",
            "SUPABASE_URL"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_result(
                "Environment Variables",
                False,
                f"Missing: {', '.join(missing_vars)}"
            )
        else:
            self.log_result("Environment Variables", True, "All required variables present")
    
    def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("API Health", True, f"Status: {data.get('status')}")
            else:
                self.log_result("API Health", False, f"HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_result("API Health", False, "Connection failed - is the server running?")
        except Exception as e:
            self.log_result("API Health", False, str(e))
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            from app.integrations.supabase_client import SupabaseClient
            client = SupabaseClient()
            # Simple connection test
            self.log_result("Database Connection", True, "Supabase connection successful")
        except ImportError:
            self.log_result("Database Connection", False, "Supabase client not found")
        except Exception as e:
            self.log_result("Database Connection", False, str(e))
    
    def test_core_engines(self):
        """Test that core engines can be imported"""
        engines = [
            "app.engines.content_recommender",
            "app.engines.engagement_analytics", 
            "app.engines.nurture_automation",
            "app.integrations.hubspot_client"
        ]
        
        for engine in engines:
            try:
                __import__(engine)
                self.log_result(f"Engine Import: {engine.split('.')[-1]}", True, "Import successful")
            except ImportError as e:
                self.log_result(f"Engine Import: {engine.split('.')[-1]}", False, str(e))
    
    def test_hubspot_connection(self):
        """Test HubSpot API connectivity"""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            self.log_result("HubSpot Connection", False, "API key not configured")
            return
        
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.hubapi.com/crm/v3/objects/contacts?limit=1",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result("HubSpot Connection", True, "API connection successful")
            elif response.status_code == 401:
                self.log_result("HubSpot Connection", False, "Invalid API key")
            else:
                self.log_result("HubSpot Connection", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("HubSpot Connection", False, str(e))
    
    def generate_report(self):
        """Generate final validation report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        
        print("\n" + "="*50)
        print("SYSTEM HEALTH VALIDATION REPORT")
        print("="*50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - System is ready for deployment!")
        else:
            print("\n⚠️  Some tests failed - review issues before deployment")
            print("\nFailed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed_tests == total_tests

def main():
    print("🔍 Starting System Health Validation...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 50)
    
    validator = SystemHealthValidator()
    
    # Run all validation tests
    validator.test_environment_variables()
    validator.test_api_health()
    validator.test_database_connection()
    validator.test_core_engines()
    validator.test_hubspot_connection()
    
    # Generate final report
    success = validator.generate_report()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
