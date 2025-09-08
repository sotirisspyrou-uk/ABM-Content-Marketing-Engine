# Automated Nurture Sequences Engine
# Version: 08-09-2025 15:45:00
# File Path: /app/engines/nurture_automation.py

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class TriggerType(Enum):
    JOURNEY_STAGE_CHANGE = "journey_stage_change"
    ENGAGEMENT_THRESHOLD = "engagement_threshold"
    CONTENT_INTERACTION = "content_interaction"
    TIME_BASED = "time_based"
    BEHAVIORAL_SIGNAL = "behavioral_signal"
    SALES_ACTIVITY = "sales_activity"

class ActionType(Enum):
    SEND_EMAIL = "send_email"
    DELIVER_CONTENT = "deliver_content"
    CREATE_TASK = "create_task"
    UPDATE_PROPERTIES = "update_properties"
    NOTIFY_SALES = "notify_sales"
    ADD_TO_LIST = "add_to_list"
    SCHEDULE_CALL = "schedule_call"

class SequenceStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class TriggerCondition:
    trigger_type: TriggerType
    property_name: str
    operator: str  # "equals", "greater_than", "less_than", "contains", "changed"
    value: Any
    metadata: Dict[str, Any]

@dataclass
class SequenceAction:
    action_id: str
    action_type: ActionType
    delay_hours: int
    conditions: List[TriggerCondition]
    parameters: Dict[str, Any]
    success_criteria: Dict[str, Any]

@dataclass
class NurtureSequence:
    sequence_id: str
    name: str
    description: str
    target_industry: str
    target_persona: str
    target_journey_stage: str
    triggers: List[TriggerCondition]
    actions: List[SequenceAction]
    sequence_duration_days: int
    success_metrics: Dict[str, float]
    status: SequenceStatus

@dataclass
class ContactSequenceEnrollment:
    enrollment_id: str
    contact_id: str
    sequence_id: str
    enrolled_date: datetime
    current_action_index: int
    next_action_due: datetime
    status: SequenceStatus
    completion_data: Dict[str, Any]

class AutomatedNurtureEngine:
    """
    Intelligent nurture sequence orchestration for ABM campaigns
    """
    
    def __init__(self, hubspot_client, content_engine, analytics_engine):
        self.hubspot_client = hubspot_client
        self.content_engine = content_engine
        self.analytics_engine = analytics_engine
        self.active_enrollments: Dict[str, ContactSequenceEnrollment] = {}
        self.sequence_library = self._initialize_sequence_library()
    
    def evaluate_sequence_triggers(
        self, 
        contact_id: str, 
        trigger_data: Dict[str, Any]
    ) -> List[str]:
        """
        Evaluate if any nurture sequences should be triggered for a contact
        """
        triggered_sequences = []
        
        for sequence in self.sequence_library.values():
            if self._should_trigger_sequence(sequence, contact_id, trigger_data):
                triggered_sequences.append(sequence.sequence_id)
        
        return triggered_sequences
    
    def enroll_contact_in_sequence(
        self, 
        contact_id: str, 
        sequence_id: str
    ) -> ContactSequenceEnrollment:
        """
        Enroll a contact in a nurture sequence
        """
        if contact_id in self.active_enrollments:
            # Check if already enrolled in this sequence
            existing = self.active_enrollments[contact_id]
            if existing.sequence_id == sequence_id and existing.status == SequenceStatus.ACTIVE:
                return existing
        
        sequence = self.sequence_library.get(sequence_id)
        if not sequence:
            raise ValueError(f"Sequence {sequence_id} not found")
        
        # Calculate first action timing
        first_action_delay = sequence.actions[0].delay_hours if sequence.actions else 0
        next_action_due = datetime.now() + timedelta(hours=first_action_delay)
        
        enrollment = ContactSequenceEnrollment(
            enrollment_id=str(uuid.uuid4()),
            contact_id=contact_id,
            sequence_id=sequence_id,
            enrolled_date=datetime.now(),
            current_action_index=0,
            next_action_due=next_action_due,
            status=SequenceStatus.ACTIVE,
            completion_data={}
        )
        
        self.active_enrollments[f"{contact_id}_{sequence_id}"] = enrollment
        
        # Log enrollment
        self._log_sequence_event(contact_id, sequence_id, "enrolled", {
            "enrollment_id": enrollment.enrollment_id,
            "sequence_name": sequence.name
        })
        
        return enrollment
    
    def process_due_actions(self) -> List[Dict[str, Any]]:
        """
        Process all due actions across active sequence enrollments
        """
        processed_actions = []
        current_time = datetime.now()
        
        for enrollment_key, enrollment in self.active_enrollments.items():
            if (enrollment.status == SequenceStatus.ACTIVE and 
                enrollment.next_action_due <= current_time):
                
                result = self._execute_sequence_action(enrollment)
                processed_actions.append(result)
        
        return processed_actions
    
    def _execute_sequence_action(
        self, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Execute the next action in a sequence for an enrolled contact
        """
        sequence = self.sequence_library[enrollment.sequence_id]
        
        if enrollment.current_action_index >= len(sequence.actions):
            # Sequence completed
            enrollment.status = SequenceStatus.COMPLETED
            enrollment.completion_data["completed_date"] = datetime.now().isoformat()
            return self._create_action_result("sequence_completed", enrollment, {})
        
        action = sequence.actions[enrollment.current_action_index]
        
        # Check if action conditions are met
        if not self._check_action_conditions(action, enrollment.contact_id):
            # Skip this action and move to next
            enrollment.current_action_index += 1
            self._schedule_next_action(enrollment, sequence)
            return self._create_action_result("action_skipped", enrollment, {
                "reason": "conditions_not_met",
                "action_id": action.action_id
            })
        
        # Execute the action
        execution_result = self._perform_action(action, enrollment)
        
        # Update enrollment state
        enrollment.current_action_index += 1
        self._schedule_next_action(enrollment, sequence)
        
        # Log action execution
        self._log_sequence_event(
            enrollment.contact_id, 
            enrollment.sequence_id, 
            "action_executed",
            {
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "result": execution_result
            }
        )
        
        return self._create_action_result("action_executed", enrollment, execution_result)
    
    def _perform_action(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Execute a specific action based on its type
        """
        action_handlers = {
            ActionType.SEND_EMAIL: self._handle_send_email,
            ActionType.DELIVER_CONTENT: self._handle_deliver_content,
            ActionType.CREATE_TASK: self._handle_create_task,
            ActionType.UPDATE_PROPERTIES: self._handle_update_properties,
            ActionType.NOTIFY_SALES: self._handle_notify_sales,
            ActionType.ADD_TO_LIST: self._handle_add_to_list,
            ActionType.SCHEDULE_CALL: self._handle_schedule_call
        }
        
        handler = action_handlers.get(action.action_type)
        if not handler:
            return {"error": f"Unknown action type: {action.action_type}"}
        
        try:
            return handler(action, enrollment)
        except Exception as e:
            return {"error": f"Action execution failed: {str(e)}"}
    
    def _handle_send_email(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Handle email sending action
        """
        email_template = action.parameters.get("template_id")
        personalization = action.parameters.get("personalization", {})
        
        # Get contact data for personalization
        contact_data = self.hubspot_client.get_contact(
            enrollment.contact_id, 
            ["email", "firstname", "lastname", "company"]
        )
        
        # Merge personalization data
        merged_personalization = {
            **contact_data.get("properties", {}),
            **personalization
        }
        
        # Send email via HubSpot
        email_result = self._send_personalized_email(
            enrollment.contact_id,
            email_template,
            merged_personalization
        )
        
        return {
            "action": "email_sent",
            "template_id": email_template,
            "email_id": email_result.get("email_id"),
            "success": email_result.get("success", False)
        }
    
    def _handle_deliver_content(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Handle content delivery action
        """
        # Get contact profile for content recommendation
        contact_profile = self._build_contact_profile(enrollment.contact_id)
        
        # Get content recommendations
        content_recommendations = self.content_engine.recommend_content(
            contact_profile, 
            num_recommendations=1
        )
        
        if not content_recommendations:
            return {"error": "No suitable content found"}
        
        recommended_content = content_recommendations[0]
        
        # Deliver content based on preferred channel
        delivery_result = self._deliver_content_to_contact(
            enrollment.contact_id,
            recommended_content
        )
        
        return {
            "action": "content_delivered",
            "content_id": recommended_content.content_id,
            "content_title": recommended_content.title,
            "delivery_channel": recommended_content.delivery_channel,
            "success": delivery_result.get("success", False)
        }
    
    def _handle_create_task(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Handle sales task creation action
        """
        task_config = {
            "subject": action.parameters.get("subject", "ABM Sequence Task"),
            "notes": action.parameters.get("notes", "Generated by nurture sequence"),
            "priority": action.parameters.get("priority", "medium"),
            "task_type": action.parameters.get("task_type", "follow_up"),
            "due_date": action.parameters.get("due_date", "+24_hours")
        }
        
        task_result = self.hubspot_client.create_sales_task(
            enrollment.contact_id,
            task_config
        )
        
        return {
            "action": "task_created",
            "task_id": task_result.get("id"),
            "subject": task_config["subject"],
            "success": bool(task_result.get("id"))
        }
    
    def _handle_update_properties(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Handle contact property updates
        """
        properties_to_update = action.parameters.get("properties", {})
        
        # Add sequence tracking properties
        properties_to_update.update({
            "last_sequence_action": action.action_id,
            "last_sequence_action_date": datetime.now().isoformat()
        })
        
        update_result = self.hubspot_client._make_request(
            "PATCH",
            f"/crm/v3/objects/contacts/{enrollment.contact_id}",
            {"properties": properties_to_update}
        )
        
        return {
            "action": "properties_updated",
            "updated_properties": list(properties_to_update.keys()),
            "success": bool(update_result.get("id"))
        }
    
    def _handle_notify_sales(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Handle sales team notification
        """
        notification_config = {
            "subject": action.parameters.get("subject", "ABM Sequence Notification"),
            "message": action.parameters.get("message", "Contact requires sales attention"),
            "urgency": action.parameters.get("urgency", "medium")
        }
        
        # Create a high-priority task for the sales rep
        task_result = self.hubspot_client.create_sales_task(
            enrollment.contact_id,
            {
                "subject": f"[ABM] {notification_config['subject']}",
                "notes": notification_config["message"],
                "priority": "high",
                "task_type": "sales_outreach",
                "due_date": "+4_hours"
            }
        )
        
        return {
            "action": "sales_notified",
            "notification_type": "task_created",
            "task_id": task_result.get("id"),
            "success": bool(task_result.get("id"))
        }
    
    def _handle_add_to_list(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Handle adding contact to HubSpot list
        """
        list_id = action.parameters.get("list_id")
        if not list_id:
            return {"error": "No list_id specified"}
        
        # Add contact to list via HubSpot API
        add_result = self._add_contact_to_list(enrollment.contact_id, list_id)
        
        return {
            "action": "added_to_list",
            "list_id": list_id,
            "success": add_result.get("success", False)
        }
    
    def _handle_schedule_call(
        self, 
        action: SequenceAction, 
        enrollment: ContactSequenceEnrollment
    ) -> Dict[str, Any]:
        """
        Handle call scheduling action
        """
        # This would integrate with calendaring system
        # For MVP, create a task for manual scheduling
        
        call_config = {
            "subject": "Schedule call with " + enrollment.contact_id,
            "notes": action.parameters.get("call_purpose", "ABM follow-up call"),
            "priority": "high",
            "task_type": "schedule_call",
            "due_date": "+24_hours"
        }
        
        task_result = self.hubspot_client.create_sales_task(
            enrollment.contact_id,
            call_config
        )
        
        return {
            "action": "call_scheduling_requested",
            "task_id": task_result.get("id"),
            "call_purpose": action.parameters.get("call_purpose"),
            "success": bool(task_result.get("id"))
        }
    
    def _should_trigger_sequence(
        self, 
        sequence: NurtureSequence, 
        contact_id: str, 
        trigger_data: Dict[str, Any]
    ) -> bool:
        """
        Determine if a sequence should be triggered for a contact
        """
        # Check if contact is already enrolled
        enrollment_key = f"{contact_id}_{sequence.sequence_id}"
        if enrollment_key in self.active_enrollments:
            return False
        
        # Check all trigger conditions
        for trigger in sequence.triggers:
            if not self._evaluate_trigger_condition(trigger, contact_id, trigger_data):
                return False
        
        return True
    
    def _evaluate_trigger_condition(
        self, 
        condition: TriggerCondition, 
        contact_id: str, 
        trigger_data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a single trigger condition
        """
        actual_value = trigger_data.get(condition.property_name)
        expected_value = condition.value
        
        if condition.operator == "equals":
            return actual_value == expected_value
        elif condition.operator == "greater_than":
            return actual_value > expected_value
        elif condition.operator == "less_than":
            return actual_value < expected_value
        elif condition.operator == "contains":
            return expected_value in str(actual_value)
        elif condition.operator == "changed":
            # Check if property changed from previous value
            return trigger_data.get(f"{condition.property_name}_changed", False)
        
        return False
    
    def _check_action_conditions(
        self, 
        action: SequenceAction, 
        contact_id: str
    ) -> bool:
        """
        Check if conditions are met for executing an action
        """
        if not action.conditions:
            return True
        
        # Get current contact data
        contact_data = self.hubspot_client.get_contact(contact_id)
        properties = contact_data.get("properties", {})
        
        for condition in action.conditions:
            if not self._evaluate_trigger_condition(condition, contact_id, properties):
                return False
        
        return True
    
    def _schedule_next_action(
        self, 
        enrollment: ContactSequenceEnrollment, 
        sequence: NurtureSequence
    ) -> None:
        """
        Schedule the next action in the sequence
        """
        if enrollment.current_action_index >= len(sequence.actions):
            # No more actions - sequence completed
            enrollment.status = SequenceStatus.COMPLETED
            return
        
        next_action = sequence.actions[enrollment.current_action_index]
        enrollment.next_action_due = datetime.now() + timedelta(hours=next_action.delay_hours)
    
    def _initialize_sequence_library(self) -> Dict[str, NurtureSequence]:
        """
        Initialize the library of available nurture sequences
        """
        sequences = {}
        
        # Awareness Stage Sequence for Technical Directors
        awareness_tech_sequence = NurtureSequence(
            sequence_id="awareness_tech_001",
            name="Technical Director Awareness Nurture",
            description="Educational content sequence for technical decision makers in awareness stage",
            target_industry="all",
            target_persona="technical_director",
            target_journey_stage="problem_awareness",
            triggers=[
                TriggerCondition(
                    trigger_type=TriggerType.JOURNEY_STAGE_CHANGE,
                    property_name="abm_journey_stage",
                    operator="equals",
                    value="problem_awareness",
                    metadata={}
                ),
                TriggerCondition(
                    trigger_type=TriggerType.ENGAGEMENT_THRESHOLD,
                    property_name="abm_content_engagement_score",
                    operator="greater_than",
                    value=20,
                    metadata={}
                )
            ],
            actions=[
                SequenceAction(
                    action_id="awareness_tech_001_action_001",
                    action_type=ActionType.DELIVER_CONTENT,
                    delay_hours=2,
                    conditions=[],
                    parameters={"content_type": "whitepaper", "topic": "technical_overview"},
                    success_criteria={"engagement_rate": 0.3}
                ),
                SequenceAction(
                    action_id="awareness_tech_001_action_002",
                    action_type=ActionType.SEND_EMAIL,
                    delay_hours=72,
                    conditions=[],
                    parameters={
                        "template_id": "tech_follow_up_email",
                        "personalization": {"content_focus": "implementation"}
                    },
                    success_criteria={"open_rate": 0.25}
                ),
                SequenceAction(
                    action_id="awareness_tech_001_action_003",
                    action_type=ActionType.DELIVER_CONTENT,
                    delay_hours=120,
                    conditions=[],
                    parameters={"content_type": "implementation_guide", "topic": "getting_started"},
                    success_criteria={"download_rate": 0.15}
                )
            ],
            sequence_duration_days=14,
            success_metrics={"progression_rate": 0.4, "engagement_increase": 0.3},
            status=SequenceStatus.ACTIVE
        )
        
        sequences[awareness_tech_sequence.sequence_id] = awareness_tech_sequence
        
        # High Engagement Follow-up Sequence
        high_engagement_sequence = NurtureSequence(
            sequence_id="high_engagement_001",
            name="High Engagement Acceleration",
            description="Fast-track sequence for highly engaged contacts",
            target_industry="all",
            target_persona="all",
            target_journey_stage="all",
            triggers=[
                TriggerCondition(
                    trigger_type=TriggerType.ENGAGEMENT_THRESHOLD,
                    property_name="abm_content_engagement_score",
                    operator="greater_than",
                    value=75,
                    metadata={}
                )
            ],
            actions=[
                SequenceAction(
                    action_id="high_engagement_001_action_001",
                    action_type=ActionType.NOTIFY_SALES,
                    delay_hours=1,
                    conditions=[],
                    parameters={
                        "subject": "High engagement contact ready for outreach",
                        "message": "Contact showing strong engagement signals - immediate follow-up recommended",
                        "urgency": "high"
                    },
                    success_criteria={"task_completion": 0.8}
                ),
                SequenceAction(
                    action_id="high_engagement_001_action_002",
                    action_type=ActionType.DELIVER_CONTENT,
                    delay_hours=24,
                    conditions=[],
                    parameters={"content_type": "demo_video", "priority": "high_intent"},
                    success_criteria={"engagement_rate": 0.6}
                )
            ],
            sequence_duration_days=7,
            success_metrics={"demo_request_rate": 0.3, "sales_contact_rate": 0.8},
            status=SequenceStatus.ACTIVE
        )
        
        sequences[high_engagement_sequence.sequence_id] = high_engagement_sequence
        
        return sequences
    
    def get_sequence_performance_report(self, sequence_id: str) -> Dict[str, Any]:
        """
        Generate performance report for a specific sequence
        """
        sequence = self.sequence_library.get(sequence_id)
        if not sequence:
            return {"error": "Sequence not found"}
        
        # Get all enrollments for this sequence
        enrollments = [
            e for e in self.active_enrollments.values() 
            if e.sequence_id == sequence_id
        ]
        
        if not enrollments:
            return {
                "sequence_id": sequence_id,
                "sequence_name": sequence.name,
                "total_enrollments": 0,
                "performance": "No enrollment data available"
            }
        
        # Calculate performance metrics
        total_enrollments = len(enrollments)
        completed_enrollments = len([e for e in enrollments if e.status == SequenceStatus.COMPLETED])
        active_enrollments = len([e for e in enrollments if e.status == SequenceStatus.ACTIVE])
        
        completion_rate = completed_enrollments / total_enrollments if total_enrollments > 0 else 0
        
        return {
            "sequence_id": sequence_id,
            "sequence_name": sequence.name,
            "total_enrollments": total_enrollments,
            "active_enrollments": active_enrollments,
            "completed_enrollments": completed_enrollments,
            "completion_rate": completion_rate,
            "average_duration_days": sequence.sequence_duration_days,
            "target_success_metrics": sequence.success_metrics,
            "last_updated": datetime.now().isoformat()
        }
    
    def _build_contact_profile(self, contact_id: str):
        """
        Build contact profile for content recommendation
        """
        # This would integrate with the contact profile system
        # For now, return a basic profile structure
        from content_recommender import ContactProfile, Industry
        
        contact_data = self.hubspot_client.get_contact(contact_id)
        properties = contact_data.get("properties", {})
        
        return ContactProfile(
            contact_id=contact_id,
            company_id=properties.get("company"),
            industry=Industry.STAFFING_RECRUITMENT,  # Would be determined from data
            persona_type=properties.get("abm_persona_classification", "technical_director"),
            journey_stage=properties.get("abm_journey_stage", "problem_awareness"),
            company_size="enterprise",
            engagement_history=[],
            content_preferences={},
            last_interaction=datetime.now()
        )
    
    def _create_action_result(
        self, 
        result_type: str, 
        enrollment: ContactSequenceEnrollment, 
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create standardized action result
        """
        return {
            "result_type": result_type,
            "enrollment_id": enrollment.enrollment_id,
            "contact_id": enrollment.contact_id,
            "sequence_id": enrollment.sequence_id,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
    
    def _log_sequence_event(
        self, 
        contact_id: str, 
        sequence_id: str, 
        event_type: str, 
        details: Dict[str, Any]
    ) -> None:
        """
        Log sequence events for audit and analysis
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "contact_id": contact_id,
            "sequence_id": sequence_id,
            "event_type": event_type,
            "details": details
        }
        
        # In production, this would write to proper logging system
        print(f"Sequence Event: {json.dumps(log_entry, indent=2)}")
    
    def _send_personalized_email(self, contact_id: str, template_id: str, personalization: Dict) -> Dict:
        """Placeholder for email sending functionality"""
        return {"success": True, "email_id": f"email_{contact_id}_{template_id}"}
    
    def _deliver_content_to_contact(self, contact_id: str, content_recommendation) -> Dict:
        """Placeholder for content delivery functionality"""
        return {"success": True, "delivery_id": f"delivery_{contact_id}_{content_recommendation.content_id}"}
    
    def _add_contact_to_list(self, contact_id: str, list_id: str) -> Dict:
        """Placeholder for list management functionality"""
        return {"success": True, "list_id": list_id}

# Usage Example
if __name__ == "__main__":
    # This would be initialized with actual client instances
    nurture_engine = AutomatedNurtureEngine(None, None, None)
    
    # Example trigger evaluation
    trigger_data = {
        "abm_journey_stage": "problem_awareness",
        "abm_content_engagement_score": 30,
        "abm_persona_classification": "technical_director"
    }
    
    triggered_sequences = nurture_engine.evaluate_sequence_triggers("contact_123", trigger_data)
    print(f"Triggered sequences: {triggered_sequences}")
    
    # Example enrollment
    if triggered_sequences:
        enrollment = nurture_engine.enroll_contact_in_sequence("contact_123", triggered_sequences[0])
        print(f"Enrolled in sequence: {enrollment.sequence_id}")
