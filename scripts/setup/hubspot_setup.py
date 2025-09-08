#!/usr/bin/env python3
"""
HubSpot Setup Script for ABM Content Marketing Engine
Creates custom properties and workflows in HubSpot
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class HubSpotSetup:
    def __init__(self):
        self.api_key = os.getenv("HUBSPOT_API_KEY")
        self.portal_id = os.getenv("HUBSPOT_PORTAL_ID")
        
        if not self.api_key:
            print("❌ HUBSPOT_API_KEY not found in environment variables")
            sys.exit(1)
            
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_contact_properties(self):
        """Create custom contact properties for ABM tracking"""
        
        properties = [
            {
                "name": "abm_journey_stage",
                "label": "ABM Journey Stage",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "Problem Awareness", "value": "problem_awareness"},
                    {"label": "Solution Exploration", "value": "solution_exploration"},
                    {"label": "Vendor Evaluation", "value": "vendor_evaluation"},
                    {"label": "Decision Finalization", "value": "decision_finalization"},
                    {"label": "Post-Purchase Expansion", "value": "post_purchase_expansion"}
                ]
            },
            {
                "name": "abm_persona_classification",
                "label": "ABM Persona Type",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "C-Suite Executive", "value": "c_suite_executive"},
                    {"label": "Technical Director", "value": "technical_director"},
                    {"label": "Operations Manager", "value": "operations_manager"},
                    {"label": "Financial Decision Maker", "value": "financial_decision_maker"}
                ]
            },
            {
                "name": "abm_content_engagement_score",
                "label": "Content Engagement Score",
                "type": "number",
                "fieldType": "number",
                "description": "0-100 score based on content interaction quality and depth"
            },
            {
                "name": "abm_last_content_interaction",
                "label": "Last Content Interaction",
                "type": "datetime",
                "fieldType": "date",
                "description": "Timestamp of most recent content engagement"
            },
            {
                "name": "abm_preferred_content_format",
                "label": "Preferred Content Format",
                "type": "enumeration",
                "fieldType": "checkbox",
                "options": [
                    {"label": "Whitepaper", "value": "whitepaper"},
                    {"label": "Case Study", "value": "case_study"},
                    {"label": "Demo/Video", "value": "demo_video"},
                    {"label": "Interactive Tool", "value": "interactive_tool"}
                ]
            }
        ]
        
        for prop in properties:
            try:
                response = requests.post(
                    f"{self.base_url}/crm/v3/properties/contacts",
                    headers=self.headers,
                    json=prop
                )
                
                if response.status_code == 201:
                    print(f"✅ Created contact property: {prop['name']}")
                elif response.status_code == 409:
                    print(f"⚠️  Contact property already exists: {prop['name']}")
                else:
                    print(f"❌ Failed to create contact property {prop['name']}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error creating contact property {prop['name']}: {e}")
    
    def create_company_properties(self):
        """Create custom company properties for ABM tracking"""
        
        properties = [
            {
                "name": "abm_account_tier",
                "label": "ABM Account Tier",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "Tier 1 - Strategic", "value": "tier_1_strategic"},
                    {"label": "Tier 2 - High Value", "value": "tier_2_high_value"},
                    {"label": "Tier 3 - Standard", "value": "tier_3_standard"}
                ]
            },
            {
                "name": "abm_industry_vertical",
                "label": "ABM Industry Vertical",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "Staffing & Recruitment", "value": "staffing_recruitment"},
                    {"label": "B2B Banking", "value": "b2b_banking"},
                    {"label": "Biotech CDMO", "value": "biotech_cdmo"},
                    {"label": "B2B Travel", "value": "b2b_travel"},
                    {"label": "Due Diligence", "value": "due_diligence"}
                ]
            },
            {
                "name": "abm_engagement_velocity",
                "label": "Account Engagement Velocity",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "High", "value": "high"},
                    {"label": "Medium", "value": "medium"},
                    {"label": "Low", "value": "low"},
                    {"label": "Stalled", "value": "stalled"}
                ]
            }
        ]
        
        for prop in properties:
            try:
                response = requests.post(
                    f"{self.base_url}/crm/v3/properties/companies",
                    headers=self.headers,
                    json=prop
                )
                
                if response.status_code == 201:
                    print(f"✅ Created company property: {prop['name']}")
                elif response.status_code == 409:
                    print(f"⚠️  Company property already exists: {prop['name']}")
                else:
                    print(f"❌ Failed to create company property {prop['name']}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error creating company property {prop['name']}: {e}")
    
    def test_api_connection(self):
        """Test HubSpot API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/crm/v3/objects/contacts?limit=1",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print("✅ HubSpot API connection successful")
                return True
            else:
                print(f"❌ HubSpot API connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ HubSpot API connection error: {e}")
            return False

def main():
    print("🚀 Starting HubSpot Setup...")
    print("================================")
    
    setup = HubSpotSetup()
    
    print("\n🔗 Testing API connection...")
    if not setup.test_api_connection():
        print("❌ Cannot proceed without valid HubSpot API connection")
        sys.exit(1)
    
    print("\n📝 Creating contact properties...")
    setup.create_contact_properties()
    
    print("\n🏢 Creating company properties...")
    setup.create_company_properties()
    
    print("\n✅ HubSpot setup completed!")
    print("\n📋 Next steps:")
    print("   1. Verify properties in HubSpot Settings > Properties")
    print("   2. Test system with: python scripts/validation/test_system_health.py")

if __name__ == "__main__":
    main()
