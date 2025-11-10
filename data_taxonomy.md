# Data Taxonomy - Momentum Product Analytics Platform

## Overview
This document defines all events, user properties, and data types tracked in the Momentum analytics platform. This taxonomy follows Segment's tracking specification and is compatible with PostHog and Customer.io.

---

## 1. Event Schema

Events represent user actions within the product. Each event follows this structure:

```json
{
  "event": "string",           // Event name (required)
  "userId": "string",          // Unique user identifier (required)
  "timestamp": "ISO8601",      // When event occurred (required)
  "properties": {object},      // Event-specific data (optional)
  "context": {object}          // System context (optional)
}
```

---

## 2. Core Events Taxonomy

### 2.1 User Lifecycle Events

#### `user_signed_up`
**Description:** Fired when a new user completes registration
**Trigger:** User submits signup form successfully
**Properties:**
- `signup_method` (string) - How user signed up: 'email', 'google', 'github'
- `company_size` (string) - Company size bracket: '1-10', '11-50', '51-200', '201-500', '501+'
- `industry` (string) - Business industry/category
- `country` (string) - ISO country code (e.g., 'SG', 'ID', 'MY')
- `referral_source` (string) - How they found us: 'organic', 'paid_ads', 'referral', 'direct'

**Example:**
```json
{
  "event": "user_signed_up",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T03:45:22.000Z",
  "properties": {
    "signup_method": "google",
    "company_size": "11-50",
    "industry": "e-commerce",
    "country": "SG",
    "referral_source": "organic"
  }
}
```

---

#### `user_logged_in`
**Description:** User successfully authenticates
**Trigger:** Valid credentials accepted
**Properties:**
- `login_method` (string) - 'email', 'google', 'github', 'sso'
- `session_id` (string) - Unique session identifier
- `device_type` (string) - 'desktop', 'mobile', 'tablet'

---

#### `user_onboarding_started`
**Description:** User begins the onboarding flow
**Trigger:** Onboarding wizard initiated
**Properties:**
- `onboarding_version` (string) - Version of onboarding flow (e.g., 'v2.1')

---

#### `user_onboarding_completed`
**Description:** User completes all onboarding steps
**Trigger:** Final onboarding step submitted
**Properties:**
- `time_to_complete_seconds` (integer) - Duration of onboarding
- `steps_completed` (integer) - Number of steps finished
- `skipped_steps` (array[string]) - Names of skipped steps

---

### 2.2 Feature Usage Events

#### `dashboard_viewed`
**Description:** User views their main analytics dashboard
**Trigger:** Dashboard page loads
**Properties:**
- `page_load_time_ms` (integer) - Time to render dashboard
- `widgets_visible` (integer) - Number of widgets displayed

---

#### `report_created`
**Description:** User creates a new analytics report
**Trigger:** Report creation confirmed
**Properties:**
- `report_type` (string) - 'funnel', 'retention', 'engagement', 'custom'
- `metrics_selected` (array[string]) - Metrics included in report
- `date_range_days` (integer) - Time period analyzed

---

#### `segment_created`
**Description:** User defines a new user segment
**Trigger:** Segment saved successfully
**Properties:**
- `segment_name` (string) - User-defined segment name
- `condition_count` (integer) - Number of conditions in segment
- `condition_types` (array[string]) - Types: 'behavioral', 'demographic', 'temporal'
- `estimated_size` (integer) - Predicted number of users in segment

---

#### `segment_updated`
**Description:** User modifies an existing segment
**Trigger:** Changes to segment saved
**Properties:**
- `segment_id` (string) - Unique segment identifier
- `changes_made` (array[string]) - What was modified

---

#### `query_executed`
**Description:** User runs an analytics query
**Trigger:** Query submitted to analytics engine
**Properties:**
- `query_type` (string) - 'event_count', 'user_count', 'funnel', 'retention'
- `date_range_days` (integer) - Time period queried
- `execution_time_ms` (integer) - Query processing time
- `result_count` (integer) - Number of results returned

---

#### `chart_viewed`
**Description:** User views a data visualization
**Trigger:** Chart renders on screen
**Properties:**
- `chart_type` (string) - 'line', 'bar', 'pie', 'funnel', 'table'
- `metric_displayed` (string) - Primary metric shown

---

#### `export_initiated`
**Description:** User exports data
**Trigger:** Export button clicked
**Properties:**
- `export_format` (string) - 'csv', 'json', 'pdf'
- `data_type` (string) - 'report', 'segment', 'raw_events'
- `record_count` (integer) - Number of records exported

---

### 2.3 Integration Events

#### `integration_connected`
**Description:** User connects a third-party integration
**Trigger:** OAuth or API key successfully configured
**Properties:**
- `integration_type` (string) - 'segment', 'posthog', 'customerio', 'slack', 'webhook'
- `configuration_method` (string) - 'oauth', 'api_key', 'manual'

---

#### `data_source_configured`
**Description:** User sets up a new data source
**Trigger:** Data source configuration saved
**Properties:**
- `source_type` (string) - 'web', 'mobile_ios', 'mobile_android', 'server'
- `sdk_version` (string) - Version of tracking SDK

---

### 2.4 Collaboration Events

#### `team_member_invited`
**Description:** User invites someone to their workspace
**Trigger:** Invitation email sent
**Properties:**
- `invitee_email` (string, hashed) - Invited person's email
- `role_assigned` (string) - 'admin', 'editor', 'viewer'

---

#### `dashboard_shared`
**Description:** User shares a dashboard with team
**Trigger:** Share action completed
**Properties:**
- `share_method` (string) - 'link', 'email', 'internal'
- `permission_level` (string) - 'view', 'edit'

---

### 2.5 Subscription Events

#### `trial_started`
**Description:** User begins a free trial
**Trigger:** Trial period activated
**Properties:**
- `trial_duration_days` (integer) - Length of trial
- `plan_tier` (string) - 'starter', 'professional', 'enterprise'

---

#### `subscription_upgraded`
**Description:** User upgrades to paid plan
**Trigger:** Payment processed successfully
**Properties:**
- `previous_plan` (string) - Previous tier
- `new_plan` (string) - New tier
- `billing_cycle` (string) - 'monthly', 'annual'
- `mrr` (float) - Monthly recurring revenue amount

---

#### `payment_failed`
**Description:** Payment attempt unsuccessful
**Trigger:** Payment processor returns error
**Properties:**
- `failure_reason` (string) - Error code or message
- `payment_method` (string) - 'credit_card', 'paypal', 'invoice'

---

## 3. User Properties Schema

User properties are attributes that describe the user. These persist across sessions.

### 3.1 Identity Properties
- `user_id` (string) - Unique identifier, immutable
- `email` (string, hashed in exports) - User's email address
- `name` (string) - Full name
- `created_at` (ISO8601) - Account creation timestamp

### 3.2 Company/Demographic Properties
- `company_name` (string) - Organization name
- `company_size` (string) - Employee count bracket
- `industry` (string) - Business category
- `country` (string) - ISO country code
- `timezone` (string) - IANA timezone (e.g., 'Asia/Singapore')

### 3.3 Subscription Properties
- `plan_tier` (string) - Current subscription level
- `trial_end_date` (ISO8601) - When trial expires
- `subscription_status` (string) - 'trial', 'active', 'past_due', 'cancelled'
- `mrr` (float) - Monthly recurring revenue contribution

### 3.4 Behavioral Properties (Computed)
- `total_logins` (integer) - Lifetime login count
- `days_since_last_login` (integer) - Recency metric
- `total_reports_created` (integer) - Cumulative reports
- `total_segments_created` (integer) - Cumulative segments
- `total_queries_executed` (integer) - Cumulative queries
- `onboarding_completed` (boolean) - Onboarding status
- `feature_adoption_score` (float) - Composite score 0-100

### 3.5 Engagement Properties (Computed)
- `days_active_last_7` (integer) - Active days in last week
- `days_active_last_30` (integer) - Active days in last month
- `average_session_duration_minutes` (float) - Mean session length
- `last_active_at` (ISO8601) - Most recent activity timestamp

---

## 4. Context Properties

System-level information captured with every event:

- `app_version` (string) - Application version number
- `device_type` (string) - 'desktop', 'mobile', 'tablet'
- `os` (string) - Operating system
- `browser` (string) - Browser name and version
- `ip_address` (string, anonymized) - User's IP (last octet removed)
- `user_agent` (string) - Full user agent string
- `screen_resolution` (string) - Display dimensions
- `locale` (string) - User's language preference

---

## 5. Data Types Reference

| Type | Description | Example |
|------|-------------|---------|
| string | Text value | "user_signed_up" |
| integer | Whole number | 42 |
| float | Decimal number | 99.99 |
| boolean | True/false | true |
| ISO8601 | Timestamp | "2025-11-08T03:45:22.000Z" |
| array | List of values | ["funnel", "retention"] |
| object | Nested structure | {"key": "value"} |

---

## 6. Naming Conventions

- **Events:** Use snake_case (e.g., `user_signed_up`)
- **Properties:** Use snake_case (e.g., `company_size`)
- **Avoid abbreviations** unless industry standard (e.g., 'mrr' for monthly recurring revenue)
- **Be specific:** "button_clicked" → "export_button_clicked"
- **Use past tense** for events: "user_signed_up" not "user_signup"

---

## 7. Multi-Market Considerations

### Southeast Asia Focus
Given Momentum's target markets (Singapore, Indonesia, Malaysia):

- **Timezone handling:** All timestamps in UTC, timezone stored separately
- **Currency:** Store amounts in user's local currency + USD equivalent
- **Language:** Support `locale` property for i18n tracking
- **Compliance:** See data-governance.md for PDPA/PDP requirements

---

## 8. Session Definition

**Session boundary:** 30 minutes of inactivity
- If user returns after 30+ minutes idle, new session starts
- `session_id` generated on first event of session
- Expires after 24 hours regardless of activity

---

## Version History

- v1.0 (2025-11-08): Initial taxonomy for case study submission