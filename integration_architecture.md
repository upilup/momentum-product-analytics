# Integration Architecture - Momentum Product Analytics Platform

## Overview

This document describes the data flow architecture for Momentum's analytics platform, detailing how user events and properties move between systems to enable product analytics, user segmentation, and marketing automation.

**Key Systems:**
- **Segment** - Customer Data Platform (CDP) that collects and routes data
- **PostHog** - Product analytics and session replay platform
- **Customer.io** - Marketing automation and messaging platform
- **Momentum Application** - Our core SaaS product

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   Web App    │  │  Mobile App  │  │   Backend    │               │
│  │ (JavaScript) │  │  (iOS/Andr.) │  │  (Node.js)   │               │
│  └──────┬───────┘  └───────┬──────┘  └────────┬─────┘               │
│         │                  │                  │                     │
│         │ Segment SDK      │ Segment SDK      │ Segment API         │
│         └──────────────────┴──────────────────┘                     │
│                            │                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             ↓
                             
┌─────────────────────────────────────────────────────────────────────┐
│                    SEGMENT (Customer Data Platform)                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Functions:                                                         │
│  • Collect events from all sources                                  │
│  • Validate and normalize data                                      │
│  • Enrich with context (IP, device, browser)                        │
│  • Route to downstream destinations                                 │
│  • Replay events if destination is down                             │
│                                                                     │
│  Data Stored:                                                       │
│  • Raw event stream (30 days retention)                             │
│  • User profiles (traits/properties)                                │
│  • Debugger logs for troubleshooting                                │
│                                                                     │
└───────────────┬────────────────────────────────┬────────────────────┘
                │                                │
        ┌───────┴────────┐                ┌──────┴───────┐
        ↓                ↓                ↓              ↓
        
┌─────────────────────┐          ┌─────────────────────┐
│      POSTHOG        │          │     CUSTOMER.IO     │
│  Product Analytics  │          │  Marketing Platform │
├─────────────────────┤          ├─────────────────────┤
│                     │          │                     │
│ Functions:          │          │ Functions:          │
│ • Event analytics   │          │ • User segmentation │
│ • User cohorts      │          │ • Email campaigns   │
│ • Funnel analysis   │          │ • Push notifications│
│ • Retention reports │          │ • In-app messages   │
│ • Session replays   │          │ • Journey workflows │
│ • Feature flags     │          │ • A/B testing       │
│                     │          │                     │
│ Data Stored:        │          │ Data Stored:        │
│ • All events        │          │ • User profiles     │
│ • User properties   │          │ • Behavioral data   │
│ • Session recordings│          │ • Campaign history  │
│ • Computed metrics  │          │ • Message delivery  │
│                     │          │                     │
└──────────┬──────────┘          └───────────┬─────────┘
           │                                 │
           │                                 │
           ↓                                 ↓
           
┌─────────────────────────────────────────────────────────────────────┐
│                     MOMENTUM APPLICATION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Consumes data via:                                                 │
│  • PostHog API - Fetch analytics data for display                   │
│  • Customer.io API - Trigger campaigns, check delivery status       │
│  • Segment API - Historical event queries (if needed)               │
│                                                                     │
│  Displays to users:                                                 │
│  • Analytics dashboards                                             │
│  • User segments and cohorts                                        │
│  • Campaign performance                                             │
│  • Product usage insights                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Breakdown

### 1. Event Collection Phase

**Step 1: User Action Occurs**
```
User clicks "Create Report" button in Momentum web app
```

**Step 2: Frontend Tracks Event**
```javascript
// Web app sends event to Segment
analytics.track('report_created', {
  report_type: 'funnel',
  metrics_selected: ['conversion_rate'],
  date_range_days: 30
});
```

**Step 3: Segment Receives & Validates**
- Checks event name format
- Validates property types
- Adds context (timestamp, IP, device info)
- Assigns to correct user profile

**Step 4: Segment Routes to Destinations**
- Sends copy to PostHog for analytics
- Sends copy to Customer.io for messaging
- Stores in Segment's own database

---

### 2. PostHog Processing

**What PostHog Does With Events:**

```
┌─────────────────────────────────────────────┐
│ Event: report_created                       │
│ User: usr_8k3n9mwp                          │
│ Timestamp: 2025-11-08T14:15:30Z             │
│ Properties: {report_type: "funnel", ...}    │
└─────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │ PostHog Processing    │
        └───────────────────────┘
                    ↓
    ┌───────────────┴───────────────┐
    ↓                               ↓
┌─────────────┐            ┌──────────────┐
│  Analytics  │            │   Cohorts    │
│   Engine    │            │   Builder    │
└─────────────┘            └──────────────┘
    ↓                               ↓
• Count events               • Update "Power Users"
• Build funnels              • Update "At-Risk Users"
• Track retention            • Recalculate segment sizes
• Generate insights          • Trigger automations
```

**PostHog Features Used:**

1. **Event Analytics**
   - Count of `report_created` events over time
   - Breakdown by `report_type`
   - Trends and patterns

2. **User Cohorts (Segments)**
   - Define rules: "Users who created >5 reports in last 30 days"
   - Auto-update cohort membership
   - Calculate cohort sizes

3. **Funnel Analysis**
   - Track user journey: Signup → Onboarding → First Report → Active User
   - Identify drop-off points

4. **Session Replay**
   - Watch actual user sessions
   - Debug issues users encounter

---

### 3. Customer.io Processing

**What Customer.io Does With Events:**

```
┌─────────────────────────────────────────────┐
│ Event: report_created                       │
│ User: usr_8k3n9mwp                          │
└─────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │ Customer.io Processing│
        └───────────────────────┘
                    ↓
    ┌───────────────┴───────────────┐
    ↓                               ↓
┌─────────────┐            ┌──────────────┐
│   Profile   │            │  Workflows   │
│   Update    │            │   Trigger    │
└─────────────┘            └──────────────┘
    ↓                               ↓
• Update user attributes     • Check if triggers match
• Increment counters         • Send onboarding email
• Set last activity          • Schedule follow-up
• Calculate segments         • Log to campaign
```

**Customer.io Features Used:**

1. **User Profiles**
   - Update `total_reports_created` counter
   - Set `last_report_created_at` timestamp
   - Add to "Active Users" segment

2. **Behavioral Triggers**
   - IF user creates first report → Send "Congrats!" email
   - IF user creates 10 reports → Upgrade nudge
   - IF no reports in 7 days → Re-engagement email

3. **Segmentation**
   - Segment: "Created report in last 7 days"
   - Use for targeted campaigns
   - Export for analysis

4. **Campaigns**
   - Drip email sequences
   - In-app notifications
   - Push notifications (mobile)

---

## Integration Configuration

### Segment Setup

**1. Install Segment in Web App:**

```javascript
// index.html
<script>
  !function(){var analytics=window.analytics=window.analytics||[];
  // ... Segment snippet ...
  analytics.load("YOUR_WRITE_KEY");
  analytics.page();
}();
</script>
```

**2. Configure Destinations:**

In Segment dashboard:
- Navigate to Connections > Destinations
- Add PostHog destination
  - PostHog API Key: `phc_xxxxxxxxxxxxx`
  - PostHog Host: `https://app.posthog.com`
- Add Customer.io destination
  - Site ID: `xxxxxxxxxxxxx`
  - API Key: `xxxxxxxxxxxxx`

**3. Enable Event Filtering (Optional):**

```
PostHog receives:
✓ All user events
✓ All user properties
✗ Page views (PostHog has its own)

Customer.io receives:
✓ Lifecycle events (signup, login, subscription)
✓ Feature usage events
✓ User properties
✗ Dashboard views (too noisy for marketing)
```

---

### PostHog Setup

**1. Project Configuration:**

```yaml
Project Name: Momentum Production
Data Retention: 7 years
Session Recording: Enabled
  - Sample Rate: 10%
  - Mask sensitive fields: true
Feature Flags: Enabled
Cohorts: Enabled
```

**2. Create Key Cohorts:**

```
Cohort: "Power Users"
Conditions:
  - report_created count >= 10 in last 30 days
  - query_executed count >= 50 in last 30 days
  - last_active within 7 days

Cohort: "At-Risk Users"
Conditions:
  - subscription_status = "active"
  - last_active_at > 14 days ago
  - onboarding_completed = true

Cohort: "Trial Users"
Conditions:
  - subscription_status = "trial"
  - created_at within last 14 days
```

**3. Set Up Dashboards:**

- Product Overview Dashboard
- Feature Adoption Dashboard
- Retention Dashboard
- Conversion Funnel Dashboard

---

### Customer.io Setup

**1. Workspace Configuration:**

```yaml
Workspace: Momentum
Region: US (or EU for GDPR)
Timezone: UTC
Unsubscribe Settings:
  - One-click unsubscribe: Enabled
  - Preference center: Enabled
```

**2. Define Segments:**

```
Segment: "Onboarding Incomplete"
Conditions:
  - created_at within last 7 days
  - onboarding_completed = false
Action: Send onboarding reminders

Segment: "High Value Users"
Conditions:
  - mrr >= 99
  - total_reports_created >= 20
Action: VIP support, feature previews

Segment: "Churned Users"
Conditions:
  - subscription_status = "cancelled"
  - last_active > 30 days ago
Action: Win-back campaign
```

**3. Create Campaigns:**

**Campaign 1: Onboarding Sequence**
```
Trigger: user_signed_up
Wait: 1 hour
Send: Welcome email
Wait: 1 day
If: onboarding_completed = false
  Send: "Need help getting started?"
Wait: 3 days
If: onboarding_completed = false
  Send: "Let's schedule a call"
```

**Campaign 2: Feature Adoption**
```
Trigger: onboarding_completed = true
Wait: 2 days
If: report_created count = 0
  Send: "Create your first report" guide
```

---

## Data Sync & Latency

### Real-time vs Batch Processing

**Real-time (< 5 seconds):**
- Segment → PostHog (streaming)
- Segment → Customer.io (streaming)
- Critical for: Feature flags, live cohorts, behavioral triggers

**Near-real-time (< 1 minute):**
- PostHog cohort recalculations
- Customer.io segment updates

**Batch (hourly/daily):**
- Customer.io complex segments
- PostHog computed properties
- Analytics report generation

---

### Expected Latency

```
User Action
    ↓ < 100ms
Segment Receives Event
    ↓ < 2 seconds
PostHog Processes Event
    ↓ < 5 seconds
Event Appears in PostHog UI
    ↓ < 30 seconds
Cohort Membership Updated
    ↓ < 1 minute
Customer.io Receives Event
    ↓ < 5 seconds
Workflow Evaluates Trigger
    ↓ < 30 seconds
Email/Notification Sent
```

---

## API Integrations

### Momentum App → PostHog

**Use Case:** Fetch analytics data to display in Momentum UI

```javascript
// Fetch event counts for dashboard
const response = await fetch('https://app.posthog.com/api/projects/12345/insights/trend/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${POSTHOG_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    events: [{ id: 'report_created' }],
    date_from: '-30d',
    interval: 'day'
  })
});

const data = await response.json();
// Display chart in Momentum dashboard
```

---

### Momentum App → Customer.io

**Use Case:** Manually trigger campaigns or check message status

```javascript
// Trigger campaign when user hits milestone
const response = await fetch('https://track.customer.io/api/v1/campaigns/123/triggers', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${CUSTOMERIO_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    recipients: {
      id: userId
    },
    data: {
      milestone: '100_reports_created',
      reward_code: 'POWER_USER_100'
    }
  })
});
```

---

## Error Handling & Monitoring

### Segment Error Handling

**Automatic Retries:**
- If PostHog is down, Segment queues events
- Retry up to 3 times with exponential backoff
- Events not lost if destination temporarily unavailable

**Monitoring:**
```javascript
// Segment debugger
analytics.on('track', (event, properties) => {
  console.log('Event tracked:', event);
});

// Check delivery status in Segment UI
// Connections > Destinations > PostHog > Event Delivery
```

---

### Circuit Breakers

**Prevent cascade failures:**

```javascript
// If PostHog API is down, don't block user actions
const trackEvent = async (event, properties) => {
  try {
    await analytics.track(event, properties);
  } catch (error) {
    // Log error but don't throw
    console.error('Tracking failed:', error);
    // User's action still succeeds
  }
};
```

---

## Security & Compliance

### Data in Transit

- All connections use HTTPS/TLS 1.3
- Segment validates SSL certificates
- No plaintext transmission

### Data at Rest

- Segment: Encrypted with AES-256
- PostHog: Encrypted database storage
- Customer.io: SOC 2 Type II compliant

### PII Handling

**Segment:**
- Email addresses hashed before sending to analytics tools
- IP addresses anonymized (last octet removed)
- Raw PII only in Customer.io for messaging

**PostHog:**
- Session recordings mask input fields
- Exclude URLs with sensitive data
- GDPR data deletion API available

**Customer.io:**
- Stores full PII for messaging
- Users can unsubscribe/delete data
- Respect do-not-contact lists

---

## Multi-Region Considerations

### Data Residency

**Singapore (SG) Users:**
- Segment: Asia-Pacific region
- PostHog: EU Cloud (GDPR compliant)
- Customer.io: US region (standard tier)

**Indonesia (ID) Users:**
- Must comply with local data regulations
- Consider PostHog self-hosted for data sovereignty
- Customer.io EU region for better compliance

### Timezone Handling

All timestamps stored in UTC:
```javascript
// Convert to user's local timezone for display only
const userTimezone = 'Asia/Singapore';
const localTime = moment(utcTimestamp).tz(userTimezone).format();
```

---

## Scalability

### Current Architecture Capacity

- **Segment:** 1M events/month (Startup plan)
- **PostHog:** 1M events/month (Free tier)
- **Customer.io:** 5K profiles (Essentials plan)

### Scaling Triggers

**Upgrade Segment when:**
- Exceeding 800K events/month (80% capacity)
- Need higher API rate limits
- Require longer data retention

**Upgrade PostHog when:**
- Exceeding 800K events/month
- Need more than 10% session recording
- Require team collaboration features

**Upgrade Customer.io when:**
- Exceeding 4K profiles
- Need advanced segmentation
- Require A/B testing

---

## Troubleshooting

### Common Issues

**Issue:** Events not appearing in PostHog
```
Solution:
1. Check Segment debugger for delivery errors
2. Verify PostHog destination is enabled
3. Check PostHog project API key
4. Wait up to 5 minutes for batch processing
```

**Issue:** Customer.io campaigns not triggering
```
Solution:
1. Verify user exists in Customer.io
2. Check segment membership
3. Review workflow conditions
4. Check campaign throttling settings
```

**Issue:** Duplicate events
```
Solution:
1. Check for multiple SDK initializations
2. Verify event only tracked once per user action
3. Use Segment's de-duplication feature
```

---

## Testing Strategy

### Development Environment

```
Development Stack:
- Segment: Test write key
- PostHog: Development project
- Customer.io: Test workspace

Test Data:
- Use test user IDs (prefix: "test_")
- Mock events with clear labels
- Clean up test data weekly
```

### Staging Environment

```
Staging Stack:
- Segment: Staging write key  
- PostHog: Staging project
- Customer.io: Test workspace (same as dev)

Validation:
- End-to-end event flow tests
- Campaign trigger tests
- API integration tests
```

### Production Monitoring

```
Metrics to Monitor:
- Event delivery success rate (target: >99%)
- Average event latency (target: <5s)
- Segment destination errors (target: <0.1%)
- PostHog query response time (target: <2s)
- Customer.io campaign send rate
```

---

## Disaster Recovery

### Backup Strategy

**Segment:**
- Raw events retained 30 days
- Replay events if destination was down
- Archive critical events to S3 (optional)

**PostHog:**
- Daily automated backups
- 7-year retention in cloud version
- Export data via API if needed

**Customer.io:**
- User profiles backed up automatically
- Campaign history retained indefinitely
- Export segments regularly

### Failover Plan

**If Segment Goes Down:**
```
1. Events queued in browser/app (max 100 events)
2. Implement direct PostHog tracking as fallback
3. Manual replay after Segment recovers
```

**If PostHog Goes Down:**
```
1. Analytics dashboard shows stale data
2. Core app functionality unaffected
3. Events queued in Segment
4. Auto-replayed when PostHog recovers
```

**If Customer.io Goes Down:**
```
1. Emails not sent (acceptable temporary degradation)
2. Core app functionality unaffected
3. Events queued in Segment
4. Campaigns catch up when service recovers
```

---

## Cost Optimization

### Current Monthly Costs (Estimated)

```
Segment: $120/month (Team plan)
PostHog: $0 (Free tier, <1M events)
Customer.io: $150/month (5K profiles)
Total: $270/month
```

### Cost Reduction Strategies

1. **Event Sampling for Session Recording**
   - Record only 10% of sessions
   - Save PostHog costs

2. **Filter Noisy Events**
   - Don't send `dashboard_viewed` to Customer.io
   - Reduce unnecessary data transfer

3. **Segment Archive to S3**
   - Store old events in cheap storage
   - Query rarely, cost-effective

---

## Version History

- v1.0 (2025-11-08): Initial architecture for case study submission

---

## References

- [Segment Documentation](https://segment.com/docs/)
- [PostHog Documentation](https://posthog.com/docs)
- [Customer.io Documentation](https://customer.io/docs/)