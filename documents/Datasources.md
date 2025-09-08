# Datasource Module - ABM Content Marketing System
**Version: 08-09-2025 14:34:00**  
**Authored by: Sotiris Spyrou, CEO, VerityAI**

## Status: INTERIM SOLUTION - Improvised Approach

### 1. PRIMARY DATA SOURCES

**HubSpot CRM API:**
- Endpoint: `/crm/v3/objects/contacts`
- Purpose: Contact data, engagement history, deal pipeline
- Authentication: Private app token
- Rate limits: 100 requests/10 seconds

**Content Management System:**
- Source: Internal content library/CMS
- Data: Content performance metrics, download tracking
- Integration: REST API or webhook-based

**Website Analytics:**
- Source: Google Analytics 4 / HubSpot Analytics
- Data: Page views, session duration, conversion events
- Purpose: Content consumption tracking

### 2. EXTERNAL DATA ENRICHMENT

**Company Intelligence:**
- **Clearbit API** (interim): Company size, industry, technology stack
- **LinkedIn Sales Navigator** (manual): Key personnel, recent updates
- **ZoomInfo API** (if available): Contact details, org charts

**Industry Data:**
- **Market research reports** (manual collection)
- **Industry publications** (RSS feeds, manual curation)
- **Regulatory updates** (government websites, manual monitoring)

### 3. SOCIAL LISTENING

**LinkedIn Monitoring:**
- Track company page activities
- Monitor executive thought leadership posts
- Identify engagement opportunities

**Twitter/X Tracking:**
- Industry hashtag monitoring
- Company mention tracking
- Competitor intelligence gathering

### 4. INTERIM API IMPLEMENTATION

```python
# Pseudo-code for interim data collection
class InterimDataSource:
    def __init__(self):
        self.hubspot_client = HubSpotClient(api_key=HUBSPOT_KEY)
        self.analytics_client = GAClient(credentials=GA_CREDS)
    
    def get_account_data(self, company_id):
        # Pull from HubSpot CRM
        contact_data = self.hubspot_client.get_contacts(company_id)
        engagement_data = self.hubspot_client.get_engagements(company_id)
        return {
            'contacts': contact_data,
            'engagement_history': engagement_data
        }
    
    def get_content_performance(self, content_id):
        # Pull from analytics
        return self.analytics_client.get_content_metrics(content_id)
    
    def enrich_company_data(self, domain):
        # Manual enrichment process for MVP
        return {
            'company_size': 'manual_lookup',
            'industry': 'manual_classification',
            'technology_stack': 'manual_research'
        }
```

### 5. DATA COLLECTION SCHEDULE

**Real-time Data:**
- HubSpot contact interactions
- Website behaviour tracking
- Email engagement metrics

**Daily Batch Processing:**
- Content performance aggregation
- Lead scoring updates
- Pipeline progression tracking

**Weekly Analysis:**
- Account engagement summaries
- Content effectiveness reports
- Persona behaviour patterns

**Monthly Deep Dive:**
- Industry trend analysis
- Competitive intelligence updates
- Content library audit

### 6. DATA QUALITY & GOVERNANCE

**Data Validation Rules:**
- Email format verification
- Company domain validation
- Duplicate contact detection
- Data freshness checks

**Privacy Compliance:**
- GDPR consent tracking
- Data retention policies
- Anonymisation procedures
- Audit trail maintenance

### 7. MVP DATA SOURCES (Simplified)

**Immediate Implementation:**
1. **HubSpot CRM** - Primary source for contacts, deals, interactions
2. **Google Analytics** - Website behaviour and content consumption
3. **Manual Research** - Company intelligence and industry insights
4. **Email Platform** - Engagement metrics and response tracking

**Phase 2 Integrations:**
1. Clearbit/ZoomInfo for data enrichment
2. Social media APIs for listening
3. Intent data providers
4. Advanced analytics platforms

### 8. API USAGE EXAMPLES

**HubSpot Contact Retrieval:**
```python
contacts = hubspot_client.crm.contacts.basic_api.get_page(
    properties=['firstname', 'lastname', 'email', 'company', 'jobtitle'],
    associations=['deals', 'companies']
)
```

**Content Tracking:**
```python
def track_content_engagement(contact_id, content_id, action):
    event_data = {
        'contact_id': contact_id,
        'content_id': content_id,
        'action': action,  # 'view', 'download', 'share'
        'timestamp': datetime.now(),
        'source': 'content_system'
    }
    return hubspot_client.events.send(event_data)
```

## Required Setup
- HubSpot API key with appropriate scopes
- Google Analytics 4 property setup
- Webhook endpoints for real-time data
- Data storage solution (PostgreSQL/MongoDB)
- ETL pipeline for data processing

## Limitations (MVP)
- Manual data enrichment initially
- Limited real-time processing
- Basic analytics dashboard
- No advanced intent data
- Simplified attribution modeling
