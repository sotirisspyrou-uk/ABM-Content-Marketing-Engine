# Engagement Analytics & Scoring Engine
# Version: 08-09-2025 15:35:00
# File Path: /app/engines/engagement_analytics.py

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

class EngagementType(Enum):
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    CONTENT_DOWNLOAD = "content_download"
    WEBSITE_VISIT = "website_visit"
    DEMO_REQUEST = "demo_request"
    PRICING_INQUIRY = "pricing_inquiry"
    SOCIAL_SHARE = "social_share"
    WEBINAR_ATTENDANCE = "webinar_attendance"

@dataclass
class EngagementEvent:
    event_id: str
    contact_id: str
    company_id: str
    event_type: EngagementType
    timestamp: datetime
    content_id: Optional[str]
    duration_seconds: Optional[int]
    metadata: Dict[str, Any]

@dataclass
class EngagementScore:
    contact_id: str
    current_score: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    engagement_velocity: float
    last_updated: datetime
    score_breakdown: Dict[str, float]

@dataclass
class AccountEngagementAnalysis:
    company_id: str
    overall_score: float
    stakeholder_count: int
    engagement_breadth: float  # Percentage of stakeholders engaged
    engagement_depth: float   # Average engagement quality
    journey_progression_rate: float
    key_insights: List[str]

class EngagementAnalyticsEngine:
    """
    Advanced engagement tracking and scoring system for ABM campaigns
    """
    
    def __init__(self):
        self.engagement_weights = self._load_engagement_weights()
        self.scoring_thresholds = self._load_scoring_thresholds()
        self.decay_factors = self._load_decay_factors()
    
    def calculate_contact_engagement_score(
        self, 
        contact_id: str, 
        events: List[EngagementEvent],
        time_window_days: int = 30
    ) -> EngagementScore:
        """
        Calculate comprehensive engagement score for a contact
        """
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        recent_events = [e for e in events if e.timestamp >= cutoff_date]
        
        if not recent_events:
            return EngagementScore(
                contact_id=contact_id,
                current_score=0.0,
                trend_direction="stable",
                engagement_velocity=0.0,
                last_updated=datetime.now(),
                score_breakdown={}
            )
        
        # Calculate component scores
        recency_score = self._calculate_recency_score(recent_events)
        frequency_score = self._calculate_frequency_score(recent_events, time_window_days)
        quality_score = self._calculate_quality_score(recent_events)
        diversity_score = self._calculate_diversity_score(recent_events)
        progression_score = self._calculate_progression_score(recent_events)
        
        # Weighted composite score
        composite_score = (
            recency_score * 0.20 +
            frequency_score * 0.25 + 
            quality_score * 0.25 +
            diversity_score * 0.15 +
            progression_score * 0.15
        )
        
        # Calculate trend and velocity
        trend_direction = self._calculate_engagement_trend(recent_events)
        engagement_velocity = self._calculate_engagement_velocity(recent_events)
        
        score_breakdown = {
            "recency": recency_score,
            "frequency": frequency_score,
            "quality": quality_score,
            "diversity": diversity_score,
            "progression": progression_score
        }
        
        return EngagementScore(
            contact_id=contact_id,
            current_score=min(100, composite_score),
            trend_direction=trend_direction,
            engagement_velocity=engagement_velocity,
            last_updated=datetime.now(),
            score_breakdown=score_breakdown
        )
    
    def _calculate_recency_score(self, events: List[EngagementEvent]) -> float:
        """
        Score based on how recently contact engaged
        """
        if not events:
            return 0.0
        
        most_recent = max(events, key=lambda e: e.timestamp)
        hours_since = (datetime.now() - most_recent.timestamp).total_seconds() / 3600
        
        # Decay function: score decreases over time
        if hours_since <= 24:
            return 100.0
        elif hours_since <= 48:
            return 80.0
        elif hours_since <= 72:
            return 60.0
        elif hours_since <= 168:  # 1 week
            return 40.0
        elif hours_since <= 336:  # 2 weeks
            return 20.0
        else:
            return 10.0
    
    def _calculate_frequency_score(
        self, 
        events: List[EngagementEvent], 
        time_window_days: int
    ) -> float:
        """
        Score based on frequency of engagement
        """
        event_count = len(events)
        events_per_day = event_count / max(1, time_window_days)
        
        # Logarithmic scaling to prevent overwhelming from excessive events
        frequency_score = min(100, (np.log(1 + events_per_day * 10) / np.log(11)) * 100)
        
        return frequency_score
    
    def _calculate_quality_score(self, events: List[EngagementEvent]) -> float:
        """
        Score based on quality and depth of engagement
        """
        if not events:
            return 0.0
        
        quality_scores = []
        
        for event in events:
            base_score = self.engagement_weights.get(event.event_type.value, 10)
            
            # Adjust for duration (if available)
            if event.duration_seconds:
                duration_multiplier = min(2.0, event.duration_seconds / 300)  # 5 minutes = 1.0x
                quality_score = base_score * duration_multiplier
            else:
                quality_score = base_score
            
            # Adjust for metadata signals
            if event.metadata:
                if event.metadata.get("completion_rate", 0) > 0.8:
                    quality_score *= 1.3
                if event.metadata.get("scroll_depth", 0) > 0.7:
                    quality_score *= 1.2
                if event.metadata.get("return_visit", False):
                    quality_score *= 1.1
            
            quality_scores.append(quality_score)
        
        return min(100, statistics.mean(quality_scores))
    
    def _calculate_diversity_score(self, events: List[EngagementEvent]) -> float:
        """
        Score based on diversity of engagement types
        """
        if not events:
            return 0.0
        
        unique_types = set(event.event_type for event in events)
        total_possible_types = len(EngagementType)
        
        diversity_ratio = len(unique_types) / total_possible_types
        diversity_score = diversity_ratio * 100
        
        # Bonus for high-value engagement types
        high_value_types = {
            EngagementType.DEMO_REQUEST,
            EngagementType.PRICING_INQUIRY,
            EngagementType.CONTENT_DOWNLOAD
        }
        
        high_value_present = unique_types.intersection(high_value_types)
        if high_value_present:
            diversity_score *= (1 + len(high_value_present) * 0.1)
        
        return min(100, diversity_score)
    
    def _calculate_progression_score(self, events: List[EngagementEvent]) -> float:
        """
        Score based on progression through engagement hierarchy
        """
        if not events:
            return 0.0
        
        # Define engagement hierarchy (higher numbers = more advanced)
        engagement_hierarchy = {
            EngagementType.EMAIL_OPEN: 1,
            EngagementType.EMAIL_CLICK: 2,
            EngagementType.WEBSITE_VISIT: 3,
            EngagementType.CONTENT_DOWNLOAD: 4,
            EngagementType.SOCIAL_SHARE: 4,
            EngagementType.WEBINAR_ATTENDANCE: 5,
            EngagementType.DEMO_REQUEST: 6,
            EngagementType.PRICING_INQUIRY: 7
        }
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        progression_indicators = []
        previous_level = 0
        
        for event in sorted_events:
            current_level = engagement_hierarchy.get(event.event_type, 0)
            if current_level > previous_level:
                progression_indicators.append(current_level - previous_level)
                previous_level = current_level
        
        if not progression_indicators:
            return 0.0
        
        # Calculate progression score
        total_progression = sum(progression_indicators)
        max_possible_progression = max(engagement_hierarchy.values())
        
        progression_score = (total_progression / max_possible_progression) * 100
        
        return min(100, progression_score)
    
    def _calculate_engagement_trend(self, events: List[EngagementEvent]) -> str:
        """
        Calculate whether engagement is trending up, down, or stable
        """
        if len(events) < 3:
            return "stable"
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        # Split into two halves and compare average engagement quality
        mid_point = len(sorted_events) // 2
        first_half = sorted_events[:mid_point]
        second_half = sorted_events[mid_point:]
        
        def avg_engagement_value(event_list):
            values = [self.engagement_weights.get(e.event_type.value, 10) for e in event_list]
            return statistics.mean(values) if values else 0
        
        first_half_avg = avg_engagement_value(first_half)
        second_half_avg = avg_engagement_value(second_half)
        
        change_threshold = 0.15  # 15% change threshold
        relative_change = (second_half_avg - first_half_avg) / max(1, first_half_avg)
        
        if relative_change > change_threshold:
            return "increasing"
        elif relative_change < -change_threshold:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_engagement_velocity(self, events: List[EngagementEvent]) -> float:
        """
        Calculate rate of engagement change (events per day trend)
        """
        if len(events) < 2:
            return 0.0
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        # Calculate daily event counts
        daily_counts = {}
        for event in sorted_events:
            date_key = event.timestamp.date()
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        if len(daily_counts) < 2:
            return 0.0
        
        # Calculate trend using linear regression
        dates = list(daily_counts.keys())
        counts = list(daily_counts.values())
        
        # Convert dates to ordinal for regression
        date_ordinals = [d.toordinal() for d in dates]
        
        # Simple linear regression
        n = len(date_ordinals)
        sum_x = sum(date_ordinals)
        sum_y = sum(counts)
        sum_xy = sum(x * y for x, y in zip(date_ordinals, counts))
        sum_x2 = sum(x * x for x in date_ordinals)
        
        # Calculate slope (velocity)
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        velocity = (n * sum_xy - sum_x * sum_y) / denominator
        
        return velocity
    
    def analyze_account_engagement(
        self, 
        company_id: str, 
        contact_scores: List[EngagementScore],
        events: List[EngagementEvent]
    ) -> AccountEngagementAnalysis:
        """
        Comprehensive account-level engagement analysis
        """
        if not contact_scores:
            return AccountEngagementAnalysis(
                company_id=company_id,
                overall_score=0.0,
                stakeholder_count=0,
                engagement_breadth=0.0,
                engagement_depth=0.0,
                journey_progression_rate=0.0,
                key_insights=["No engagement data available"]
            )
        
        # Calculate overall metrics
        overall_score = statistics.mean([score.current_score for score in contact_scores])
        stakeholder_count = len(contact_scores)
        
        # Engagement breadth: percentage of contacts with meaningful engagement
        engaged_contacts = [s for s in contact_scores if s.current_score > 20]
        engagement_breadth = len(engaged_contacts) / stakeholder_count * 100
        
        # Engagement depth: average score of engaged contacts
        engagement_depth = statistics.mean([s.current_score for s in engaged_contacts]) if engaged_contacts else 0
        
        # Journey progression rate
        progression_scores = [s.score_breakdown.get("progression", 0) for s in contact_scores]
        journey_progression_rate = statistics.mean(progression_scores)
        
        # Generate insights
        insights = self._generate_account_insights(
            contact_scores, events, overall_score, engagement_breadth, engagement_depth
        )
        
        return AccountEngagementAnalysis(
            company_id=company_id,
            overall_score=overall_score,
            stakeholder_count=stakeholder_count,
            engagement_breadth=engagement_breadth,
            engagement_depth=engagement_depth,
            journey_progression_rate=journey_progression_rate,
            key_insights=insights
        )
    
    def _generate_account_insights(
        self, 
        contact_scores: List[EngagementScore],
        events: List[EngagementEvent],
        overall_score: float,
        engagement_breadth: float,
        engagement_depth: float
    ) -> List[str]:
        """
        Generate actionable insights for account engagement
        """
        insights = []
        
        # Score-based insights
        if overall_score > 70:
            insights.append("High overall engagement - strong sales opportunity")
        elif overall_score > 40:
            insights.append("Moderate engagement - nurture with targeted content")
        else:
            insights.append("Low engagement - requires re-engagement strategy")
        
        # Breadth insights
        if engagement_breadth < 30:
            insights.append("Limited stakeholder engagement - expand reach within account")
        elif engagement_breadth > 70:
            insights.append("Broad stakeholder engagement - good account penetration")
        
        # Depth insights
        if engagement_depth > 60 and engagement_breadth < 50:
            insights.append("Deep but narrow engagement - identify and engage additional stakeholders")
        
        # Trend insights
        increasing_trends = [s for s in contact_scores if s.trend_direction == "increasing"]
        if len(increasing_trends) > len(contact_scores) * 0.6:
            insights.append("Positive engagement momentum across multiple contacts")
        
        decreasing_trends = [s for s in contact_scores if s.trend_direction == "decreasing"]
        if len(decreasing_trends) > len(contact_scores) * 0.4:
            insights.append("Declining engagement detected - immediate intervention needed")
        
        # Event pattern insights
        recent_events = [e for e in events if e.timestamp > datetime.now() - timedelta(days=7)]
        high_value_events = [e for e in recent_events if e.event_type in [
            EngagementType.DEMO_REQUEST, EngagementType.PRICING_INQUIRY
        ]]
        
        if high_value_events:
            insights.append(f"High-intent signals detected: {len(high_value_events)} high-value interactions")
        
        return insights
    
    def generate_engagement_report(
        self, 
        contact_scores: List[EngagementScore],
        account_analysis: AccountEngagementAnalysis,
        time_period: str = "30 days"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive engagement analytics report
        """
        # Score distribution
        score_ranges = {
            "high (70-100)": len([s for s in contact_scores if s.current_score >= 70]),
            "medium (40-69)": len([s for s in contact_scores if 40 <= s.current_score < 70]),
            "low (0-39)": len([s for s in contact_scores if s.current_score < 40])
        }
        
        # Trend analysis
        trend_distribution = {
            "increasing": len([s for s in contact_scores if s.trend_direction == "increasing"]),
            "stable": len([s for s in contact_scores if s.trend_direction == "stable"]),
            "decreasing": len([s for s in contact_scores if s.trend_direction == "decreasing"])
        }
        
        # Top performers
        top_performers = sorted(contact_scores, key=lambda s: s.current_score, reverse=True)[:5]
        
        # Recommendations
        recommendations = self._generate_recommendations(account_analysis, contact_scores)
        
        return {
            "report_generated": datetime.now().isoformat(),
            "time_period": time_period,
            "summary": {
                "total_contacts": len(contact_scores),
                "average_score": account_analysis.overall_score,
                "engagement_breadth_percent": account_analysis.engagement_breadth,
                "engagement_depth_score": account_analysis.engagement_depth
            },
            "score_distribution": score_ranges,
            "trend_analysis": trend_distribution,
            "top_performers": [
                {
                    "contact_id": score.contact_id,
                    "score": score.current_score,
                    "trend": score.trend_direction
                } for score in top_performers
            ],
            "key_insights": account_analysis.key_insights,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(
        self, 
        account_analysis: AccountEngagementAnalysis,
        contact_scores: List[EngagementScore]
    ) -> List[str]:
        """
        Generate actionable recommendations based on engagement analysis
        """
        recommendations = []
        
        if account_analysis.engagement_breadth < 40:
            recommendations.append("Expand stakeholder mapping and engage additional decision makers")
        
        if account_analysis.overall_score < 50:
            recommendations.append("Implement re-engagement campaign with high-value content")
        
        high_velocity_contacts = [s for s in contact_scores if s.engagement_velocity > 0.5]
        if high_velocity_contacts:
            recommendations.append(f"Prioritize {len(high_velocity_contacts)} contacts showing increased engagement")
        
        stalled_contacts = [s for s in contact_scores if s.engagement_velocity < -0.2]
        if stalled_contacts:
            recommendations.append(f"Address {len(stalled_contacts)} contacts with declining engagement")
        
        if account_analysis.journey_progression_rate > 60:
            recommendations.append("Strong progression signals - consider scheduling demos or sales calls")
        
        return recommendations
    
    def _load_engagement_weights(self) -> Dict[str, float]:
        """
        Load engagement scoring weights for different event types
        """
        return {
            "email_open": 5,
            "email_click": 10,
            "website_visit": 15,
            "content_download": 25,
            "social_share": 20,
            "webinar_attendance": 30,
            "demo_request": 50,
            "pricing_inquiry": 45
        }
    
    def _load_scoring_thresholds(self) -> Dict[str, float]:
        """
        Load scoring thresholds for various metrics
        """
        return {
            "high_engagement": 70,
            "medium_engagement": 40,
            "low_engagement": 20,
            "trend_change_threshold": 0.15
        }
    
    def _load_decay_factors(self) -> Dict[str, float]:
        """
        Load time-based decay factors for engagement scoring
        """
        return {
            "daily_decay": 0.95,
            "weekly_decay": 0.8,
            "monthly_decay": 0.6
        }

# Usage Example
if __name__ == "__main__":
    # Initialize analytics engine
    analytics = EngagementAnalyticsEngine()
    
    # Sample engagement events
    events = [
        EngagementEvent(
            event_id="evt_001",
            contact_id="contact_123",
            company_id="company_456",
            event_type=EngagementType.CONTENT_DOWNLOAD,
            timestamp=datetime.now() - timedelta(days=2),
            content_id="content_789",
            duration_seconds=300,
            metadata={"completion_rate": 0.9}
        )
    ]
    
    # Calculate engagement score
    score = analytics.calculate_contact_engagement_score("contact_123", events)
    print(f"Engagement score: {score.current_score:.2f}")
    print(f"Trend: {score.trend_direction}")
    print(f"Score breakdown: {score.score_breakdown}")
