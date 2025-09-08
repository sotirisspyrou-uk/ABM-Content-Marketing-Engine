#!/usr/bin/env python3
"""
Database Setup Script for ABM Content Marketing Engine
Creates all required tables and indexes in Supabase
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def create_database_schema():
    """Create all required database tables and indexes"""
    
    database_url = os.getenv("SUPABASE_DATABASE_URL")
    if not database_url:
        print("❌ SUPABASE_DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    engine = create_engine(database_url)
    
    # SQL statements for table creation
    sql_statements = [
        # Companies table
        """
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            hubspot_company_id VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            domain VARCHAR(255),
            industry VARCHAR(100),
            employee_count INTEGER,
            annual_revenue BIGINT,
            account_tier VARCHAR(20) DEFAULT 'tier_3_standard',
            engagement_velocity VARCHAR(20) DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Contacts table
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            hubspot_contact_id VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            job_title VARCHAR(200),
            company_id UUID REFERENCES companies(id),
            journey_stage VARCHAR(50) NOT NULL DEFAULT 'problem_awareness',
            persona_type VARCHAR(50) NOT NULL DEFAULT 'technical_director',
            engagement_score INTEGER DEFAULT 0 CHECK (engagement_score >= 0 AND engagement_score <= 100),
            last_interaction TIMESTAMP,
            preferred_content_format VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Content items table
        """
        CREATE TABLE IF NOT EXISTS content_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(255) NOT NULL,
            content_type VARCHAR(50) NOT NULL,
            target_industries TEXT[],
            target_personas TEXT[],
            target_journey_stages TEXT[],
            content_length_minutes INTEGER,
            complexity_level VARCHAR(20) DEFAULT 'intermediate',
            performance_metrics JSONB DEFAULT '{}',
            content_tags TEXT[],
            file_path VARCHAR(500),
            publish_date TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Engagement events table
        """
        CREATE TABLE IF NOT EXISTS engagement_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
            content_id UUID REFERENCES content_items(id),
            event_type VARCHAR(50) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            duration_seconds INTEGER,
            metadata JSONB DEFAULT '{}',
            quality_score FLOAT DEFAULT 0.5 CHECK (quality_score >= 0 AND quality_score <= 1),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Nurture sequences table
        """
        CREATE TABLE IF NOT EXISTS nurture_sequences (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            sequence_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            target_industry VARCHAR(100),
            target_persona VARCHAR(100),
            target_journey_stage VARCHAR(100),
            sequence_config JSONB NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            performance_metrics JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Nurture enrollments table
        """
        CREATE TABLE IF NOT EXISTS nurture_enrollments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
            sequence_id VARCHAR(100) REFERENCES nurture_sequences(sequence_id),
            current_action_index INTEGER DEFAULT 0,
            next_action_due TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active',
            enrolled_date TIMESTAMP DEFAULT NOW(),
            completion_data JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        
        # Performance indexes (CRITICAL for production performance)
        """
        CREATE INDEX IF NOT EXISTS idx_contacts_hubspot_id ON contacts(hubspot_contact_id);
        CREATE INDEX IF NOT EXISTS idx_contacts_company_id ON contacts(company_id);
        CREATE INDEX IF NOT EXISTS idx_contacts_journey_stage ON contacts(journey_stage);
        CREATE INDEX IF NOT EXISTS idx_contacts_engagement_score ON contacts(engagement_score);
        CREATE INDEX IF NOT EXISTS idx_engagement_events_contact_timestamp ON engagement_events(contact_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_engagement_events_type ON engagement_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_engagement_events_content ON engagement_events(content_id);
        CREATE INDEX IF NOT EXISTS idx_nurture_enrollments_due ON nurture_enrollments(next_action_due) WHERE status = 'active';
        CREATE INDEX IF NOT EXISTS idx_content_items_type_industry ON content_items USING GIN(target_industries);
        CREATE INDEX IF NOT EXISTS idx_content_items_persona ON content_items USING GIN(target_personas);
        """,
    ]
    
    try:
        with engine.connect() as conn:
            for i, sql in enumerate(sql_statements, 1):
                print(f"⏳ Executing statement {i}/{len(sql_statements)}...")
                conn.execute(text(sql))
                conn.commit()
        
        print("✅ Database schema created successfully!")
        print("\n📋 Created tables:")
        print("  - companies")
        print("  - contacts") 
        print("  - content_items")
        print("  - engagement_events")
        print("  - nurture_sequences")
        print("  - nurture_enrollments")
        print("\n🔍 Created indexes for optimal performance")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database_schema()
