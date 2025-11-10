# Segmentation Logic - Momentum Product Analytics Platform

## Overview

This document defines the segmentation logic for grouping users based on their behavioral patterns and demographic characteristics. These segments enable targeted analytics, personalized marketing campaigns, and product insights.

**Purpose:** Provide clear, reproducible rules for identifying user cohorts that drive business decisions.

---

## Segment Types

### Behavioral Segments (3)
Based on user actions, engagement patterns, and product usage:
1. Power Users
2. At-Risk Users  
3. Inactive Trial Users

### Demographic Segments (2)
Based on user attributes and company characteristics:
4. Southeast Asia Enterprise Customers
5. Small Business Starters

---

## Behavioral Segment #1: Power Users

### Business Definition
Users who actively engage with the platform, create multiple reports and segments, and demonstrate high feature adoption. These are our most valuable customers who extract maximum value from the product.

### Plain Language Rule
**"Active users who created at least 10 reports in the last 30 days, executed at least 50 queries in the last 30 days, and logged in within the last 7 days."**

### Segmentation Criteria

| Criterion | Operator | Value | Rationale |
|-----------|----------|-------|-----------|
| `total_reports_created` | >= | 10 (last 30 days) | Indicates regular use of core analytics feature |
| `total_queries_executed` | >= | 50 (last 30 days) | Shows deep engagement with data exploration |
| `days_since_last_login` | <= | 7 | Confirms recent, ongoing activity |
| `onboarding_completed` | = | true | Must have completed onboarding |

### SQL Query

```sql
-- Power Users Segment
SELECT 
    user_id,
    email,
    company_name,
    plan_tier,
    total_reports_created,
    total_queries_executed,
    days_since_last_login,
    feature_adoption_score
FROM users
WHERE 
    onboarding_completed = true
    AND days_since_last_login <= 7
    AND user_id IN (
        -- Users with 10+ reports in last 30 days
        SELECT user_id
        FROM events
        WHERE event = 'report_created'
          AND timestamp >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY user_id
        HAVING COUNT(*) >= 10
    )
    AND user_id IN (
        -- Users with 50+ queries in last 30 days
        SELECT user_id
        FROM events
        WHERE event = 'query_executed'
          AND timestamp >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY user_id
        HAVING COUNT(*) >= 50
    )
ORDER BY feature_adoption_score DESC;
```

### Alternative: Using Computed Properties

If user properties are pre-computed (recommended for performance):

```sql
-- Power Users Segment (Using Computed Properties)
SELECT 
    user_id,
    email,
    company_name,
    plan_tier,
    total_reports_created,
    total_queries_executed,
    feature_adoption_score
FROM users
WHERE 
    onboarding_completed = true
    AND days_since_last_login <= 7
    AND total_reports_created >= 10  -- Assumes this is rolling 30-day count
    AND total_queries_executed >= 50  -- Assumes this is rolling 30-day count
ORDER BY feature_adoption_score DESC;
```

### PostHog Cohort Definition

**In PostHog UI:**

1. Navigate to: People → Cohorts → New Cohort
2. Name: "Power Users"
3. Conditions:
   ```
   Performed event: report_created
     - At least 10 times
     - In the last 30 days
   
   AND
   
   Performed event: query_executed
     - At least 50 times
     - In the last 30 days
   
   AND
   
   Performed event: user_logged_in
     - At least 1 time
     - In the last 7 days
   
   AND
   
   User property: onboarding_completed
     - equals true
   ```

**PostHog API (Programmatic):**

```javascript
// Create Power Users cohort via PostHog API
const response = await fetch('https://app.posthog.com/api/projects/12345/cohorts/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${POSTHOG_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Power Users',
    groups: [
      {
        properties: [
          {
            key: 'report_created',
            type: 'event',
            event_type: 'report_created',
            operator: 'gte',
            value: 10,
            time_value: 30,
            time_interval: 'day'
          },
          {
            key: 'query_executed',
            type: 'event',
            event_type: 'query_executed',
            operator: 'gte',
            value: 50,
            time_value: 30,
            time_interval: 'day'
          },
          {
            key: 'user_logged_in',
            type: 'event',
            event_type: 'user_logged_in',
            operator: 'gte',
            value: 1,
            time_value: 7,
            time_interval: 'day'
          },
          {
            key: 'onboarding_completed',
            type: 'person',
            operator: 'exact',
            value: ['true']
          }
        ]
      }
    ]
  })
});
```

### Threshold Rationale

- **10 reports/30 days:** Averages to ~2-3 reports per week, indicating regular usage
- **50 queries/30 days:** Shows frequent data exploration (1-2 queries per day)
- **7 days since login:** Ensures current engagement, filters out recently inactive users
- **Onboarding completed:** Excludes users still learning the platform

### Expected Segment Size
**~15-20% of active users** (based on typical SaaS engagement patterns)

In our sample data: Approximately 30-40 users out of 250

### Business Use Cases

**Product:**
- Feature beta testing candidates
- User research interview recruitment
- Product feedback requests

**Marketing:**
- Case study candidates
- Referral program invitations
- Upsell to higher tiers (if on Starter)

**Customer Success:**
- Success story documentation
- Community ambassador program
- Reduced risk of churn (proactive retention)

---

## Behavioral Segment #2: At-Risk Users

### Business Definition
Paying customers (not on trial) who have completed onboarding but show declining engagement. These users are at risk of churning and need intervention to re-engage.

### Plain Language Rule
**"Active paying customers who completed onboarding, but haven't logged in for 14+ days, and created fewer than 3 reports in the last 30 days."**

### Segmentation Criteria

| Criterion | Operator | Value | Rationale |
|-----------|----------|-------|-----------|
| `subscription_status` | = | 'active' | Must be paying customers |
| `plan_tier` | IN | ('starter', 'professional', 'enterprise') | Exclude trial users |
| `onboarding_completed` | = | true | Previously engaged users |
| `days_since_last_login` | >= | 14 | Shows inactivity |
| `total_reports_created` | < | 3 (last 30 days) | Low feature usage |

### SQL Query

```sql
-- At-Risk Users Segment
SELECT 
    user_id,
    email,
    company_name,
    plan_tier,
    subscription_status,
    mrr,
    days_since_last_login,
    last_active_at,
    total_reports_created,
    feature_adoption_score
FROM users
WHERE 
    subscription_status = 'active'
    AND plan_tier IN ('starter', 'professional', 'enterprise')
    AND onboarding_completed = true
    AND days_since_last_login >= 14
    AND user_id IN (
        -- Users with fewer than 3 reports in last 30 days
        SELECT user_id
        FROM events
        WHERE event = 'report_created'
          AND timestamp >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY user_id
        HAVING COUNT(*) < 3
        
        UNION
        
        -- Users with NO reports in last 30 days
        SELECT DISTINCT user_id
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1
            FROM events e
            WHERE e.user_id = u.user_id
              AND e.event = 'report_created'
              AND e.timestamp >= CURRENT_DATE - INTERVAL '30 days'
        )
    )
ORDER BY mrr DESC, days_since_last_login DESC;
```

### Alternative: Using Computed Properties

```sql
-- At-Risk Users Segment (Simplified)
SELECT 
    user_id,
    email,
    company_name,
    plan_tier,
    mrr,
    days_since_last_login,
    last_active_at
FROM users
WHERE 
    subscription_status = 'active'
    AND plan_tier IN ('starter', 'professional', 'enterprise')
    AND onboarding_completed = true
    AND days_since_last_login >= 14
    AND total_reports_created < 3  -- Assumes rolling 30-day count
ORDER BY mrr DESC, days_since_last_login DESC;
```

### PostHog Cohort Definition

**In PostHog UI:**

1. Navigate to: People → Cohorts → New Cohort
2. Name: "At-Risk Users"
3. Conditions:
   ```
   User property: subscription_status
     - equals 'active'
   
   AND
   
   User property: plan_tier
     - is one of ['starter', 'professional', 'enterprise']
   
   AND
   
   User property: onboarding_completed
     - equals true
   
   AND
   
   Performed event: user_logged_in
     - Did NOT perform
     - In the last 14 days
   
   AND
   
   Performed event: report_created
     - Less than 3 times
     - In the last 30 days
   ```

### Threshold Rationale

- **14 days inactive:** Long enough to indicate disengagement, but not too late for intervention
- **< 3 reports in 30 days:** Below minimum viable usage threshold
- **Active subscription:** Focus on revenue at risk
- **Completed onboarding:** Previously engaged, so inactivity is a change in behavior

### Expected Segment Size
**~10-15% of paying users** (industry standard churn risk rate)

In our sample data: Approximately 15-25 users out of ~150 paying customers

### Business Use Cases

**Customer Success:**
- Proactive outreach campaigns
- "We miss you" emails with feature highlights
- Schedule check-in calls
- Offer training refreshers

**Product:**
- Identify UX friction points
- Feature usage gap analysis
- Exit survey deployment

**Marketing:**
- Win-back campaigns
- Re-engagement email sequences
- Special offer/discount to reactive

---

## Behavioral Segment #3: Inactive Trial Users

### Business Definition
Users currently on trial who show low engagement and are unlikely to convert to paying customers without intervention. These users need onboarding support or activation campaigns.

### Plain Language Rule
**"Trial users who signed up within the last 14 days, completed onboarding, but haven't created any reports and logged in fewer than 3 times."**

### Segmentation Criteria

| Criterion | Operator | Value | Rationale |
|-----------|----------|-------|-----------|
| `plan_tier` | = | 'trial' | Trial period users only |
| `subscription_status` | = | 'trial' | Currently in trial |
| `created_at` | >= | CURRENT_DATE - 14 days | Within trial period |
| `total_logins` | < | 3 | Low engagement signal |
| `total_reports_created` | = | 0 | Never used core feature |
| `onboarding_completed` | = | true | Completed setup but not adopting |

### SQL Query

```sql
-- Inactive Trial Users Segment
SELECT 
    user_id,
    email,
    company_name,
    company_size,
    country,
    created_at,
    trial_end_date,
    total_logins,
    total_reports_created,
    days_since_last_login,
    DATEDIFF(day, CURRENT_DATE, trial_end_date) AS days_until_trial_ends
FROM users
WHERE 
    plan_tier = 'trial'
    AND subscription_status = 'trial'
    AND created_at >= CURRENT_DATE - INTERVAL '14 days'
    AND onboarding_completed = true
    AND total_reports_created = 0
    AND user_id IN (
        -- Users with fewer than 3 logins total
        SELECT user_id
        FROM events
        WHERE event = 'user_logged_in'
        GROUP BY user_id
        HAVING COUNT(*) < 3
    )
ORDER BY trial_end_date ASC;  -- Prioritize users whose trial ends soonest
```

### Alternative: Using Computed Properties

```sql
-- Inactive Trial Users Segment (Simplified)
SELECT 
    user_id,
    email,
    company_name,
    created_at,
    trial_end_date,
    total_logins,
    days_since_last_login,
    DATEDIFF(day, CURRENT_DATE, trial_end_date) AS days_until_trial_ends
FROM users
WHERE 
    plan_tier = 'trial'
    AND subscription_status = 'trial'
    AND created_at >= CURRENT_DATE - INTERVAL '14 days'
    AND onboarding_completed = true
    AND total_reports_created = 0
    AND total_logins < 3
ORDER BY trial_end_date ASC;
```

### PostHog Cohort Definition

**In PostHog UI:**

1. Navigate to: People → Cohorts → New Cohort
2. Name: "Inactive Trial Users"
3. Conditions:
   ```
   User property: plan_tier
     - equals 'trial'
   
   AND
   
   User property: subscription_status
     - equals 'trial'
   
   AND
   
   User property: created_at
     - is in the last 14 days
   
   AND
   
   User property: onboarding_completed
     - equals true
   
   AND
   
   Performed event: user_logged_in
     - Less than 3 times
     - In the last 14 days
   
   AND
   
   Performed event: report_created
     - Exactly 0 times
     - In the last 14 days
   ```

### Threshold Rationale

- **< 3 logins:** Minimal engagement, haven't built a habit
- **0 reports created:** Never experienced core value proposition
- **Within 14-day trial:** Still time to intervene and convert
- **Onboarding completed:** Not a setup issue, it's an activation issue

### Expected Segment Size
**~20-30% of trial users** (typical for SaaS with 14-day trials)

In our sample data: Approximately 8-15 users

### Business Use Cases

**Customer Success:**
- Triggered onboarding assistance emails
- "Need help creating your first report?" campaigns
- Offer live demo/walkthrough sessions
- Send tutorial videos and guides

**Product:**
- Identify onboarding friction
- Test different activation flows
- Measure impact of feature prompts

**Marketing:**
- Drip email campaigns focused on use cases
- Success story examples
- Extended trial offers as last resort

---

## Demographic Segment #4: Southeast Asia Enterprise Customers

### Business Definition
Large companies (200+ employees) based in Southeast Asia, representing high-value accounts with expansion potential and specific regional needs.

### Plain Language Rule
**"Companies with 200+ employees located in Singapore, Indonesia, or Malaysia, with active paid subscriptions."**

### Segmentation Criteria

| Criterion | Operator | Value | Rationale |
|-----------|----------|-------|-----------|
| `company_size` | IN | ('201-500', '501+') | Enterprise-scale companies |
| `country` | IN | ('SG', 'ID', 'MY') | Southeast Asia focus markets |
| `subscription_status` | = | 'active' | Currently paying customers |
| `plan_tier` | IN | ('professional', 'enterprise') | Higher-tier plans |

### SQL Query

```sql
-- Southeast Asia Enterprise Customers Segment
SELECT 
    user_id,
    email,
    company_name,
    company_size,
    industry,
    country,
    plan_tier,
    mrr,
    subscription_status,
    feature_adoption_score,
    total_reports_created,
    created_at
FROM users
WHERE 
    company_size IN ('201-500', '501+')
    AND country IN ('SG', 'ID', 'MY')
    AND subscription_status = 'active'
    AND plan_tier IN ('professional', 'enterprise')
ORDER BY mrr DESC, company_size DESC;
```

### PostHog Cohort Definition

**In PostHog UI:**

1. Navigate to: People → Cohorts → New Cohort
2. Name: "SEA Enterprise Customers"
3. Conditions:
   ```
   User property: company_size
     - is one of ['201-500', '501+']
   
   AND
   
   User property: country
     - is one of ['SG', 'ID', 'MY']
   
   AND
   
   User property: subscription_status
     - equals 'active'
   
   AND
   
   User property: plan_tier
     - is one of ['professional', 'enterprise']
   ```

### Threshold Rationale

- **201+ employees:** Enterprise classification threshold
- **SG, ID, MY:** Primary markets with strongest traction
- **Active subscription:** Current customers, not churned
- **Professional/Enterprise plans:** Higher ACV, strategic accounts

### Expected Segment Size
**~5-8% of total users** (enterprise makes up smaller portion but higher value)

In our sample data: Approximately 10-15 users

### Business Use Cases

**Sales:**
- Account expansion opportunities
- Multi-seat license upsells
- Enterprise feature adoption

**Customer Success:**
- Dedicated account management
- Quarterly business reviews
- Custom training programs
- Prioritized support

**Product:**
- Enterprise feature validation
- Regional compliance requirements (PDPA, PDP)
- Integration priorities
- Case study candidates

**Marketing:**
- Regional event invitations
- Local language content
- Industry-specific campaigns

---

## Demographic Segment #5: Small Business Starters

### Business Definition
Small businesses (1-50 employees) on entry-level plans, representing the long-tail customer base with potential for organic growth and referrals.

### Plain Language Rule
**"Small companies with 1-50 employees on the Starter plan with active subscriptions."**

### Segmentation Criteria

| Criterion | Operator | Value | Rationale |
|-----------|----------|-------|-----------|
| `company_size` | IN | ('1-10', '11-50') | Small business classification |
| `plan_tier` | = | 'starter' | Entry-level plan |
| `subscription_status` | = | 'active' | Paying customers |

### SQL Query

```sql
-- Small Business Starters Segment
SELECT 
    user_id,
    email,
    company_name,
    company_size,
    industry,
    country,
    plan_tier,
    mrr,
    subscription_status,
    feature_adoption_score,
    total_reports_created,
    created_at,
    referral_source
FROM users
WHERE 
    company_size IN ('1-10', '11-50')
    AND plan_tier = 'starter'
    AND subscription_status = 'active'
ORDER BY feature_adoption_score DESC, created_at DESC;
```

### PostHog Cohort Definition

**In PostHog UI:**

1. Navigate to: People → Cohorts → New Cohort
2. Name: "Small Business Starters"
3. Conditions:
   ```
   User property: company_size
     - is one of ['1-10', '11-50']
   
   AND
   
   User property: plan_tier
     - equals 'starter'
   
   AND
   
   User property: subscription_status
     - equals 'active'
   ```

### Threshold Rationale

- **1-50 employees:** SMB sweet spot
- **Starter plan:** Entry-level commitment
- **Active subscription:** Currently paying, not trial

### Expected Segment Size
**~35-45% of paying users** (largest segment by count, smaller by revenue)

In our sample data: Approximately 60-80 users

### Business Use Cases

**Growth:**
- Upgrade campaigns to Professional plan
- Feature education (show what they're missing)
- Volume discount offers for team expansion

**Community:**
- User community building
- Peer learning programs
- Referral incentive programs

**Product:**
- Feature adoption tracking
- Freemium to paid conversion patterns
- Self-serve success metrics

**Support:**
- Self-service documentation
- Automated help center
- Community support forums

---

## Segment Overlap Analysis

### Venn Diagram Concepts

Users can belong to multiple segments:

```
Power Users ∩ SEA Enterprise = "High-value engaged customers"
  → VIP treatment, executive relationships

At-Risk Users ∩ Small Business = "Churn risk, lower recovery cost"
  → Automated win-back campaigns

Inactive Trial ∩ SEA Enterprise = "High-potential, needs activation"
  → White-glove onboarding, direct outreach
```

### Mutually Exclusive Segments

These segments should NOT overlap:
- Power Users ⊄ At-Risk Users (contradictory by definition)
- Inactive Trial ⊄ Any paid plan segment

---

## Segment Performance Metrics

### Key Metrics to Track Per Segment

**For All Segments:**
- Segment size over time (growth/shrinkage)
- Average MRR per user
- Feature adoption score distribution
- Retention rate

**Behavioral Segments:**
- Movement between segments (upgrade/downgrade paths)
- Time spent in each segment
- Conversion rates (e.g., Trial → Power User)

**Demographic Segments:**
- Market penetration by region
- Industry distribution
- Growth rate by segment

---

## SQL Maintenance Scripts

### Refresh Computed User Properties

These queries should run daily to keep user properties up-to-date:

```sql
-- Update total_reports_created (last 30 days)
UPDATE users u
SET total_reports_created = (
    SELECT COUNT(*)
    FROM events e
    WHERE e.user_id = u.user_id
      AND e.event = 'report_created'
      AND e.timestamp >= CURRENT_DATE - INTERVAL '30 days'
);

-- Update total_queries_executed (last 30 days)
UPDATE users u
SET total_queries_executed = (
    SELECT COUNT(*)
    FROM events e
    WHERE e.user_id = u.user_id
      AND e.event = 'query_executed'
      AND e.timestamp >= CURRENT_DATE - INTERVAL '30 days'
);

-- Update days_since_last_login
UPDATE users u
SET days_since_last_login = DATEDIFF(
    day,
    (SELECT MAX(timestamp) FROM events e WHERE e.user_id = u.user_id AND e.event = 'user_logged_in'),
    CURRENT_DATE
);

-- Update last_active_at
UPDATE users u
SET last_active_at = (
    SELECT MAX(timestamp)
    FROM events e
    WHERE e.user_id = u.user_id
);
```

---

## Testing & Validation

### Segment Size Validation

Expected ranges based on industry benchmarks:

| Segment | Expected % | Sample Data Count (250 users) |
|---------|-----------|-------------------------------|
| Power Users | 15-20% | 30-40 users |
| At-Risk Users | 10-15% | 15-25 users |
| Inactive Trial Users | 20-30% of trials | 8-15 users |
| SEA Enterprise | 5-8% | 10-15 users |
| Small Business Starters | 35-45% of paid | 60-80 users |

### Query Performance Benchmarks

- Power Users query: < 2 seconds (with indexes on user_id, timestamp, event)
- At-Risk Users query: < 1 second (mostly user property filters)
- All queries: < 3 seconds at 10K users, < 10 seconds at 100K users

### Recommended Indexes

```sql
-- Events table
CREATE INDEX idx_events_user_timestamp ON events(user_id, timestamp);
CREATE INDEX idx_events_event_timestamp ON events(event, timestamp);

-- Users table
CREATE INDEX idx_users_status_plan ON users(subscription_status, plan_tier);
CREATE INDEX idx_users_country_size ON users(country, company_size);
CREATE INDEX idx_users_days_since_login ON users(days_since_last_login);
```

---

## Version History

- v1.0 (2025-11-08): Initial segmentation logic for case study submission

---

## References

- [Data Taxonomy](./data-taxonomy.md) - Event and property definitions
- [Event Tracking Plan](./event-tracking-plan.md) - Implementation details
- [PostHog Cohorts Documentation](https://posthog.com/docs/user-guides/cohorts)