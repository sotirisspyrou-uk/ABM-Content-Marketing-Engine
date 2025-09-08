# Content Recommendation Engine
# Version: 08-09-2025 15:25:00
# File Path: /app/engines/content_recommender.py

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd

class ContentType(Enum):
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"
    ROI_CALCULATOR = "roi_calculator"
    DEMO_VIDEO = "demo_video"
    WEBINAR = "webinar"
    IMPLEMENTATION_GUIDE = "implementation_guide"
    COMPARISON_CHART = "comparison_chart"

class Industry(Enum):
    STAFFING_RECRUITMENT = "staffing_recruitment"
    B2B_BANKING = "b2b_banking"
    BIOTECH_CDMO = "biotech_cdmo"
    B2B_TRAVEL = "b2b_travel"
    DUE_DILIGENCE = "due_diligence"

@dataclass
class ContentItem:
    content_id: str
    title: str
    content_type: ContentType
    target_industries: List[Industry]
    target_personas: List[str]
    target_journey_stages: List[str]
    content_length_minutes: int
    complexity_level: str  # "basic", "intermediate", "advanced"
    publish_date: datetime
    performance_metrics: Dict[str, float]
    content_tags: List[str]
    file_path: str

@dataclass
class ContactProfile:
    contact_id: str
    company_id: str
    industry: Industry
    persona_type: str
    journey_stage: str
    company_size: str
    engagement_history: List[Dict]
    content_preferences: Dict[str, float]
    last_interaction: datetime

@dataclass
class ContentRecommendation:
    content_id: str
    title: str
    relevance_score: float
    personalization_notes: str
    optimal_timing: datetime
    delivery_channel: str
    expected_engagement_rate: float
    next_logical_content: Optional[str]

class ContentRecommendationEngine:
    """
    Intelligent content recommendation system for ABM campaigns
    """
    
    def __init__(self, content_library_path: str):
        self.content_library = self._load_content_library(content_library_path)
        self.persona_preferences = self._load_persona_preferences()
        self.industry_mappings = self._load_industry_mappings()
        self.engagement_weights = self._load_engagement_weights()
    
    def recommend_content(
        self, 
        contact_profile: ContactProfile, 
        num_recommendations: int = 3,
        exclude_recent_days: int = 7
    ) -> List[ContentRecommendation]:
        """
        Generate personalized content recommendations for a contact
        """
        
        # Filter out recently consumed content
        available_content = self._filter_recent_content(
            contact_profile, exclude_recent_days
        )
        
        # Calculate relevance scores for all available content
        scored_content = []
        for content in available_content:
            relevance_score = self._calculate_relevance_score(
                content, contact_profile
            )
            
            if relevance_score > 0.3:  # Minimum relevance threshold
                scored_content.append((content, relevance_score))
        
        # Sort by relevance score
        scored_content.sort(key=lambda x: x[1], reverse=True)
        
        # Generate recommendations
        recommendations = []
        for i, (content, score) in enumerate(scored_content[:num_recommendations]):
            recommendation = self._create_recommendation(
                content, contact_profile, score, rank=i+1
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_relevance_score(
        self, 
        content: ContentItem, 
        profile: ContactProfile
    ) -> float:
        """
        Multi-factor relevance scoring algorithm
        """
        
        # Industry alignment (25% weight)
        industry_score = self._calculate_industry_alignment(
            content.target_industries, profile.industry
        ) * 0.25
        
        # Persona fit (20% weight) 
        persona_score = self._calculate_persona_alignment(
            content.target_personas, profile.persona_type
        ) * 0.20
        
        # Journey stage alignment (20% weight)
        stage_score = self._calculate_stage_alignment(
            content.target_journey_stages, profile.journey_stage
        ) * 0.20
        
        # Engagement history match (15% weight)
        engagement_score = self._calculate_engagement_history_match(
            content, profile.engagement_history
        ) * 0.15
        
        # Content freshness (10% weight)
        freshness_score = self._calculate_content_freshness(
            content.publish_date
        ) * 0.10
        
        # Content performance (10% weight)
        performance_score = self._calculate_content_performance(
            content.performance_metrics
        ) * 0.10
        
        total_score = (
            industry_score + persona_score + stage_score + 
            engagement_score + freshness_score + performance_score
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_industry_alignment(
        self, 
        content_industries: List[Industry], 
        contact_industry: Industry
    ) -> float:
        """
        Calculate how well content aligns with contact's industry
        """
        if contact_industry in content_industries:
            return 1.0
        
        # Check for industry adjacency (e.g., banking and fintech)
        industry_similarity = self.industry_mappings.get(
            contact_industry.value, {}
        )
        
        max_similarity = 0.0
        for content_industry in content_industries:
            similarity = industry_similarity.get(content_industry.value, 0.0)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_persona_alignment(
        self, 
        content_personas: List[str], 
        contact_persona: str
    ) -> float:
        """
        Calculate how well content matches contact's persona
        """
        if contact_persona in content_personas:
            return 1.0
        
        # Check for persona adjacency (e.g., technical and operations roles)
        persona_similarity = self.persona_preferences.get(
            contact_persona, {}
        ).get("similar_personas", {})
        
        max_similarity = 0.0
        for content_persona in content_personas:
            similarity = persona_similarity.get(content_persona, 0.0)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_stage_alignment(
        self, 
        content_stages: List[str], 
        contact_stage: str
    ) -> float:
        """
        Calculate journey stage alignment with content
        """
        if contact_stage in content_stages:
            return 1.0
        
        # Adjacent stages get partial credit
        stage_adjacency = {
            "problem_awareness": {"solution_exploration": 0.6},
            "solution_exploration": {
                "problem_awareness": 0.4, 
                "vendor_evaluation": 0.6
            },
            "vendor_evaluation": {
                "solution_exploration": 0.4,
                "decision_finalization": 0.6
            },
            "decision_finalization": {"vendor_evaluation": 0.4},
            "post_purchase_expansion": {"decision_finalization": 0.3}
        }
        
        adjacent_scores = stage_adjacency.get(contact_stage, {})
        max_score = 0.0
        
        for content_stage in content_stages:
            score = adjacent_scores.get(content_stage, 0.0)
            max_score = max(max_score, score)
        
        return max_score
    
    def _calculate_engagement_history_match(
        self, 
        content: ContentItem, 
        engagement_history: List[Dict]
    ) -> float:
        """
        Score based on past engagement patterns
        """
        if not engagement_history:
            return 0.5  # Neutral score for new contacts
        
        # Analyze preferences from history
        content_type_preferences = {}
        topic_preferences = {}
        
        for engagement in engagement_history:
            content_type = engagement.get("content_type")
            topics = engagement.get("topics", [])
            engagement_quality = engagement.get("quality_score", 0.5)
            
            # Weight by engagement quality
            if content_type:
                content_type_preferences[content_type] = (
                    content_type_preferences.get(content_type, 0) + engagement_quality
                )
            
            for topic in topics:
                topic_preferences[topic] = (
                    topic_preferences.get(topic, 0) + engagement_quality
                )
        
        # Calculate match score
        type_match = content_type_preferences.get(content.content_type.value, 0.5)
        
        topic_match = 0.0
        if content.content_tags:
            topic_scores = [
                topic_preferences.get(tag, 0.3) for tag in content.content_tags
            ]
            topic_match = max(topic_scores) if topic_scores else 0.3
        
        return (type_match * 0.6 + topic_match * 0.4) / max(1.0, len(engagement_history) * 0.1)
    
    def _calculate_content_freshness(self, publish_date: datetime) -> float:
        """
        Score content based on recency (newer = better)
        """
        days_old = (datetime.now() - publish_date).days
        
        if days_old <= 30:
            return 1.0
        elif days_old <= 90:
            return 0.8
        elif days_old <= 180:
            return 0.6
        elif days_old <= 365:
            return 0.4
        else:
            return 0.2
    
    def _calculate_content_performance(self, metrics: Dict[str, float]) -> float:
        """
        Score content based on historical performance
        """
        engagement_rate = metrics.get("engagement_rate", 0.5)
        conversion_rate = metrics.get("conversion_rate", 0.1)
        completion_rate = metrics.get("completion_rate", 0.7)
        
        # Weighted average of performance metrics
        performance_score = (
            engagement_rate * 0.4 +
            conversion_rate * 0.4 +
            completion_rate * 0.2
        )
        
        return min(1.0, performance_score)
    
    def _create_recommendation(
        self, 
        content: ContentItem, 
        profile: ContactProfile, 
        relevance_score: float,
        rank: int
    ) -> ContentRecommendation:
        """
        Create detailed content recommendation
        """
        
        # Calculate optimal timing
        optimal_timing = self._calculate_optimal_timing(
            content, profile, rank
        )
        
        # Determine delivery channel
        delivery_channel = self._determine_delivery_channel(
            content, profile
        )
        
        # Predict engagement rate
        expected_engagement = self._predict_engagement_rate(
            content, profile, relevance_score
        )
        
        # Find next logical content
        next_content = self._find_next_logical_content(
            content, profile
        )
        
        # Generate personalization notes
        personalization_notes = self._generate_personalization_notes(
            content, profile, relevance_score
        )
        
        return ContentRecommendation(
            content_id=content.content_id,
            title=content.title,
            relevance_score=relevance_score,
            personalization_notes=personalization_notes,
            optimal_timing=optimal_timing,
            delivery_channel=delivery_channel,
            expected_engagement_rate=expected_engagement,
            next_logical_content=next_content
        )
    
    def _calculate_optimal_timing(
        self, 
        content: ContentItem, 
        profile: ContactProfile, 
        rank: int
    ) -> datetime:
        """
        Calculate optimal delivery timing based on engagement patterns
        """
        base_delay_hours = rank * 24  # Stagger recommendations
        
        # Adjust based on content urgency
        if content.content_type in [ContentType.ROI_CALCULATOR, ContentType.DEMO_VIDEO]:
            base_delay_hours = min(base_delay_hours, 4)  # High-intent content delivered quickly
        
        # Adjust based on journey stage urgency
        stage_urgency = {
            "vendor_evaluation": 0.5,  # Faster delivery in evaluation stage
            "decision_finalization": 0.3,  # Very fast in decision stage
            "problem_awareness": 2.0,  # Slower nurture in awareness
            "solution_exploration": 1.0,  # Normal timing
            "post_purchase_expansion": 1.5  # Moderate pace for expansion
        }
        
        urgency_multiplier = stage_urgency.get(profile.journey_stage, 1.0)
        adjusted_delay = base_delay_hours * urgency_multiplier
        
        return datetime.now() + timedelta(hours=adjusted_delay)
    
    def _determine_delivery_channel(
        self, 
        content: ContentItem, 
        profile: ContactProfile
    ) -> str:
        """
        Determine optimal delivery channel for content
        """
        # Channel preferences by persona
        persona_channels = {
            "c_suite_executive": "email",  # Executives prefer email
            "technical_director": "website",  # Technical users browse directly
            "operations_manager": "email",  # Operations prefer structured delivery
            "financial_decision_maker": "sales_enablement"  # Finance needs sales context
        }
        
        # Content type preferences
        content_channels = {
            ContentType.ROI_CALCULATOR: "website",
            ContentType.DEMO_VIDEO: "email",
            ContentType.WHITEPAPER: "email",
            ContentType.CASE_STUDY: "sales_enablement"
        }
        
        # Prioritize content type preference, fallback to persona preference
        preferred_channel = content_channels.get(
            content.content_type,
            persona_channels.get(profile.persona_type, "email")
        )
        
        return preferred_channel
    
    def _predict_engagement_rate(
        self, 
        content: ContentItem, 
        profile: ContactProfile, 
        relevance_score: float
    ) -> float:
        """
        Predict likely engagement rate for this content-contact combination
        """
        base_rate = content.performance_metrics.get("engagement_rate", 0.15)
        
        # Adjust based on relevance score
        relevance_boost = relevance_score * 0.3
        
        # Adjust based on contact engagement history
        historical_engagement = sum(
            eng.get("engagement_quality", 0.5) 
            for eng in profile.engagement_history[-5:]  # Last 5 interactions
        ) / max(1, len(profile.engagement_history[-5:]))
        
        predicted_rate = base_rate + relevance_boost + (historical_engagement * 0.2)
        
        return min(0.95, max(0.05, predicted_rate))
    
    def _find_next_logical_content(
        self, 
        current_content: ContentItem, 
        profile: ContactProfile
    ) -> Optional[str]:
        """
        Identify logical follow-up content
        """
        content_progression = {
            ContentType.WHITEPAPER: [ContentType.CASE_STUDY, ContentType.WEBINAR],
            ContentType.CASE_STUDY: [ContentType.DEMO_VIDEO, ContentType.ROI_CALCULATOR],
            ContentType.ROI_CALCULATOR: [ContentType.DEMO_VIDEO, ContentType.IMPLEMENTATION_GUIDE],
            ContentType.DEMO_VIDEO: [ContentType.IMPLEMENTATION_GUIDE, ContentType.COMPARISON_CHART],
            ContentType.WEBINAR: [ContentType.CASE_STUDY, ContentType.DEMO_VIDEO]
        }
        
        next_types = content_progression.get(current_content.content_type, [])
        
        # Find best matching next content
        for content in self.content_library:
            if (content.content_type in next_types and 
                profile.industry in content.target_industries and
                profile.journey_stage in content.target_journey_stages):
                return content.content_id
        
        return None
    
    def _generate_personalization_notes(
        self, 
        content: ContentItem, 
        profile: ContactProfile, 
        relevance_score: float
    ) -> str:
        """
        Generate notes explaining why this content was recommended
        """
        notes = []
        
        if profile.industry in content.target_industries:
            notes.append(f"Industry-specific content for {profile.industry.value}")
        
        if profile.persona_type in content.target_personas:
            notes.append(f"Tailored for {profile.persona_type} role")
        
        if profile.journey_stage in content.target_journey_stages:
            notes.append(f"Matches {profile.journey_stage} stage")
        
        if relevance_score > 0.8:
            notes.append("High relevance match")
        elif relevance_score > 0.6:
            notes.append("Good relevance match")
        
        return "; ".join(notes)
    
    def _filter_recent_content(
        self, 
        profile: ContactProfile, 
        exclude_days: int
    ) -> List[ContentItem]:
        """
        Filter out content consumed recently
        """
        recent_content_ids = set()
        cutoff_date = datetime.now() - timedelta(days=exclude_days)
        
        for engagement in profile.engagement_history:
            if engagement.get("timestamp", datetime.min) > cutoff_date:
                recent_content_ids.add(engagement.get("content_id"))
        
        return [
            content for content in self.content_library
            if content.content_id not in recent_content_ids
        ]
    
    def _load_content_library(self, library_path: str) -> List[ContentItem]:
        """
        Load content library from JSON file
        """
        # In production, this would load from actual content management system
        # For MVP, return sample content library
        return [
            ContentItem(
                content_id="wp_001",
                title="The Future of Staffing: AI-Powered Recruitment",
                content_type=ContentType.WHITEPAPER,
                target_industries=[Industry.STAFFING_RECRUITMENT],
                target_personas=["c_suite_executive", "operations_manager"],
                target_journey_stages=["problem_awareness", "solution_exploration"],
                content_length_minutes=15,
                complexity_level="intermediate",
                publish_date=datetime.now() - timedelta(days=30),
                performance_metrics={"engagement_rate": 0.25, "conversion_rate": 0.08},
                content_tags=["automation", "efficiency", "AI"],
                file_path="/content/whitepapers/ai_staffing.pdf"
            ),
            # Add more sample content items...
        ]
    
    def _load_persona_preferences(self) -> Dict:
        """
        Load persona preference mappings
        """
        return {
            "c_suite_executive": {
                "preferred_content_types": ["whitepaper", "case_study"],
                "content_length_preference": "short",
                "similar_personas": {"operations_manager": 0.6}
            },
            "technical_director": {
                "preferred_content_types": ["implementation_guide", "demo_video"],
                "content_length_preference": "detailed",
                "similar_personas": {"operations_manager": 0.7}
            }
        }
    
    def _load_industry_mappings(self) -> Dict:
        """
        Load industry similarity mappings
        """
        return {
            "b2b_banking": {
                "due_diligence": 0.6,  # Related financial services
                "staffing_recruitment": 0.3
            },
            "staffing_recruitment": {
                "b2b_travel": 0.4,  # Service industries
                "due_diligence": 0.3
            }
        }
    
    def _load_engagement_weights(self) -> Dict:
        """
        Load engagement scoring weights
        """
        return {
            "content_completion": 0.4,
            "time_spent": 0.3,
            "return_visits": 0.2,
            "social_sharing": 0.1
        }

# Usage Example
if __name__ == "__main__":
    # Initialize recommendation engine
    engine = ContentRecommendationEngine("/path/to/content/library.json")
    
    # Example contact profile
    profile = ContactProfile(
        contact_id="12345",
        company_id="67890",
        industry=Industry.STAFFING_RECRUITMENT,
        persona_type="technical_director",
        journey_stage="solution_exploration",
        company_size="enterprise",
        engagement_history=[],
        content_preferences={},
        last_interaction=datetime.now() - timedelta(days=2)
    )
    
    # Get recommendations
    recommendations = engine.recommend_content(profile, num_recommendations=3)
    
    for rec in recommendations:
        print(f"Recommended: {rec.title}")
        print(f"Relevance: {rec.relevance_score:.2f}")
        print(f"Notes: {rec.personalization_notes}")
        print("---")
