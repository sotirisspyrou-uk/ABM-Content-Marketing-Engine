# HubSpot API Integration Functions
# Version: 08-09-2025 15:15:00
# File Path: /app/integrations/hubspot_client.py

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import json
from dataclasses import dataclass
from enum import Enum

class JourneyStage(Enum):
    PROBLEM_AWARENESS = "problem_awareness"
    SOLUTION_EXPLORATION = "solution_exploration"
    VENDOR_EVALUATION = "vendor_evaluation"
    DECISION_FINALIZATION = "decision_finalization"
    POST_PURCHASE_EXPANSION = "post_purchase_expansion"

class PersonaType(Enum):
    C_SUITE_EXECUTIVE = "c_suite_executive"
    TECHNICAL_DIRECTOR = "technical_director"
    OPERATIONS_MANAGER = "operations_manager"
    FINANCIAL_DECISION_MAKER = "financial_decision_maker"

@dataclass
class ABMInsights:
    journey_stage: JourneyStage
    persona_type: PersonaType
    engagement_score: int
    last_interaction: datetime
    preferred_content_format: str
    account_tier: str

class HubSpotABMClient:
    """
    Enhanced HubSpot client for ABM-specific operations
    """
    
    def __init__(self, api_key: str, portal_id: str):
        self.api_key = api_key
        self.portal_id = portal_id
        self.base_url = "https://api.hubapi.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        self.rate_limit_delay = 0.1  # 10 requests per second max
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make rate-limited API request with error handling
        """
        url = f"{self.base_url}{endpoint}"
        time.sleep(self.rate_limit_delay)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RateLimitError:
            # Exponential backoff for rate limiting
            time.sleep(min(300, self.rate_limit_delay * 2))
            self.rate_limit_delay *= 2
            return self._make_request(method, endpoint, data)
        
        except requests.exceptions.RequestException as e:
            print(f"HubSpot API Error: {e}")
            raise e
    
    def update_contact_abm_data(self, contact_id: str, abm_insights: ABMInsights) -> Dict:
        """
        Update contact with ABM intelligence data
        """
        properties = {
            "abm_journey_stage": abm_insights.journey_stage.value,
            "abm_persona_classification": abm_insights.persona_type.value,
            "abm_content_engagement_score": str(abm_insights.engagement_score),
            "abm_last_content_interaction": abm_insights.last_interaction.isoformat(),
            "abm_preferred_content_format": abm_insights.preferred_content_format
        }
        
        data = {"properties": properties}
        endpoint = f"/crm/v3/objects/contacts/{contact_id}"
        
        result = self._make_request("PATCH", endpoint, data)
        
        # Log the update
        self._log_abm_update(contact_id, properties)
        
        return result
    
    def get_account_contacts(self, company_id: str) -> List[Dict]:
        """
        Retrieve all contacts associated with a company account
        """
        endpoint = f"/crm/v3/objects/companies/{company_id}/associations/contacts"
        
        response = self._make_request("GET", endpoint)
        contact_ids = [assoc["id"] for assoc in response.get("results", [])]
        
        # Batch retrieve contact details
        return self.batch_get_contacts(contact_ids)
    
    def batch_get_contacts(self, contact_ids: List[str]) -> List[Dict]:
        """
        Efficiently retrieve multiple contacts with ABM properties
        """
        if not contact_ids:
            return []
        
        # HubSpot batch API allows up to 100 records per request
        batch_size = 100
        all_contacts = []
        
        for i in range(0, len(contact_ids), batch_size):
            batch_ids = contact_ids[i:i + batch_size]
            
            data = {
                "inputs": [{"id": contact_id} for contact_id in batch_ids],
                "properties": [
                    "email", "firstname", "lastname", "jobtitle", "company",
                    "abm_journey_stage", "abm_persona_classification", 
                    "abm_content_engagement_score", "abm_last_content_interaction"
                ]
            }
            
            endpoint = "/crm/v3/objects/contacts/batch/read"
            response = self._make_request("POST", endpoint, data)
            
            all_contacts.extend(response.get("results", []))
        
        return all_contacts
    
    def create_abm_workflow_trigger(self, workflow_config: Dict) -> Dict:
        """
        Create automated workflow based on ABM insights
        """
        workflow_data = {
            "name": workflow_config["name"],
            "enabled": True,
            "triggers": [{
                "type": "contact_property_change",
                "propertyName": workflow_config["trigger_property"],
                "operator": workflow_config.get("operator", "HAS_CHANGED")
            }],
            "actions": workflow_config["actions"]
        }
        
        endpoint = "/automation/v4/workflows"
        return self._make_request("POST", endpoint, workflow_data)
    
    def create_sales_task(self, contact_id: str, task_config: Dict) -> Dict:
        """
        Create sales task based on ABM signal
        """
        # Get contact owner
        contact = self.get_contact(contact_id)
        owner_id = contact.get("properties", {}).get("hubspot_owner_id")
        
        if not owner_id:
            raise ValueError(f"No owner assigned to contact {contact_id}")
        
        task_data = {
            "properties": {
                "hs_task_subject": task_config["subject"],
                "hs_task_body": task_config["notes"],
                "hs_task_status": "NOT_STARTED",
                "hs_task_priority": task_config.get("priority", "MEDIUM"),
                "hs_task_type": task_config.get("task_type", "TODO"),
                "hs_timestamp": self._calculate_due_date(task_config.get("due_date", "+24_hours")),
                "hubspot_owner_id": owner_id
            },
            "associations": [{
                "to": {"id": contact_id},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 204}]
            }]
        }
        
        endpoint = "/crm/v3/objects/tasks"
        return self._make_request("POST", endpoint, task_data)
    
    def get_contact_engagement_history(self, contact_id: str, days: int = 30) -> List[Dict]:
        """
        Retrieve engagement history for ABM analysis
        """
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        endpoint = f"/crm/v3/objects/contacts/{contact_id}/associations/activities"
        params = {
            "limit": 100,
            "since": since_date
        }
        
        response = self._make_request("GET", endpoint, params)
        return response.get("results", [])
    
    def update_lead_score(self, contact_id: str, score_adjustment: int) -> Dict:
        """
        Update contact lead score with ABM insights
        """
        # Get current score
        contact = self.get_contact(contact_id, ["hubspotscore"])
        current_score = int(contact.get("properties", {}).get("hubspotscore", 0))
        
        new_score = max(0, min(100, current_score + score_adjustment))
        
        data = {
            "properties": {
                "hubspotscore": str(new_score),
                "abm_score_contribution": str(score_adjustment)
            }
        }
        
        endpoint = f"/crm/v3/objects/contacts/{contact_id}"
        return self._make_request("PATCH", endpoint, data)
    
    def get_contact(self, contact_id: str, properties: Optional[List[str]] = None) -> Dict:
        """
        Get single contact with specified properties
        """
        endpoint = f"/crm/v3/objects/contacts/{contact_id}"
        params = {}
        
        if properties:
            params["properties"] = ",".join(properties)
        
        return self._make_request("GET", endpoint, params)
    
    def create_abm_list(self, list_name: str, filters: Dict) -> Dict:
        """
        Create dynamic list for ABM targeting
        """
        list_data = {
            "name": list_name,
            "dynamic": True,
            "filters": self._convert_filters_to_hubspot_format(filters)
        }
        
        endpoint = "/contacts/v1/lists"
        return self._make_request("POST", endpoint, list_data)
    
    def track_content_engagement(self, contact_id: str, content_data: Dict) -> Dict:
        """
        Track content engagement event in HubSpot
        """
        event_data = {
            "eventName": "abm_content_engagement",
            "objectType": "contact",
            "objectId": contact_id,
            "properties": {
                "content_id": content_data["content_id"],
                "content_type": content_data["content_type"],
                "engagement_duration": str(content_data["duration_seconds"]),
                "completion_rate": str(content_data["completion_percentage"]),
                "engagement_quality": content_data["quality_score"]
            }
        }
        
        endpoint = "/events/v3/send"
        return self._make_request("POST", endpoint, event_data)
    
    def _calculate_due_date(self, due_date_str: str) -> str:
        """
        Calculate timestamp for task due date
        """
        if due_date_str.startswith("+"):
            # Parse relative date like "+24_hours", "+2_days"
            parts = due_date_str[1:].split("_")
            amount = int(parts[0])
            unit = parts[1]
            
            if unit.startswith("hour"):
                delta = timedelta(hours=amount)
            elif unit.startswith("day"):
                delta = timedelta(days=amount)
            else:
                delta = timedelta(hours=24)  # Default
            
            due_date = datetime.now() + delta
        else:
            # Assume ISO format
            due_date = datetime.fromisoformat(due_date_str)
        
        return str(int(due_date.timestamp() * 1000))  # HubSpot expects milliseconds
    
    def _convert_filters_to_hubspot_format(self, filters: Dict) -> List[Dict]:
        """
        Convert simplified filters to HubSpot list filter format
        """
        hubspot_filters = []
        
        for property_name, condition in filters.items():
            filter_def = {
                "property": property_name,
                "operator": condition.get("operator", "EQ"),
                "value": condition.get("value")
            }
            hubspot_filters.append(filter_def)
        
        return hubspot_filters
    
    def _log_abm_update(self, contact_id: str, properties: Dict) -> None:
        """
        Log ABM data updates for audit trail
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "contact_id": contact_id,
            "updated_properties": properties,
            "source": "abm_engine"
        }
        
        # In production, this would write to a proper logging system
        print(f"ABM Update Log: {json.dumps(log_entry, indent=2)}")

# Usage Example
if __name__ == "__main__":
    # Initialize client
    client = HubSpotABMClient(
        api_key=os.getenv("HUBSPOT_API_KEY"),
        portal_id=os.getenv("HUBSPOT_PORTAL_ID")
    )
    
    # Example ABM insights update
    insights = ABMInsights(
        journey_stage=JourneyStage.SOLUTION_EXPLORATION,
        persona_type=PersonaType.TECHNICAL_DIRECTOR,
        engagement_score=75,
        last_interaction=datetime.now(),
        preferred_content_format="whitepaper",
        account_tier="tier_1_strategic"
    )
    
    # Update contact with ABM data
    contact_id = "12345"
    result = client.update_contact_abm_data(contact_id, insights)
    print(f"Updated contact {contact_id}: {result}")
