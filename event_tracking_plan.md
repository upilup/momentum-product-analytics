# Event Tracking Plan - Momentum Product Analytics Platform

## Overview
This document provides implementation guidance for tracking user events in the Momentum platform. All events follow the Segment Tracking API specification and are designed for compatibility with PostHog analytics and Customer.io marketing automation.

**Purpose:** Ensure consistent, accurate event tracking across web, mobile, and server-side implementations.

**References:**
- [Segment Spec: Track](https://segment.com/docs/connections/spec/track/)
- [Data Taxonomy](./data-taxonomy.md)
- [Integration Architecture](./integration-architecture.md)

---

## Table of Contents
1. [Implementation Basics](#implementation-basics)
2. [User Lifecycle Events](#user-lifecycle-events)
3. [Feature Usage Events](#feature-usage-events)
4. [Integration Events](#integration-events)
5. [Collaboration Events](#collaboration-events)
6. [Subscription Events](#subscription-events)
7. [Quality Assurance](#quality-assurance)

---

## Implementation Basics

### Segment SDK Setup

**Web (JavaScript):**
```javascript
// Initialize Segment Analytics
analytics.load("YOUR_WRITE_KEY");

// Identify user (call once on login/signup)
analytics.identify("usr_8k3n9mwp", {
  email: "user@example.com",
  name: "Jane Doe",
  company_name: "Acme Corp",
  plan_tier: "professional"
});

// Track an event
analytics.track("Event Name", {
  property1: "value1",
  property2: "value2"
});
```

**Server-side (Node.js):**
```javascript
const Analytics = require('analytics-node');
const analytics = new Analytics('YOUR_WRITE_KEY');

analytics.track({
  userId: 'usr_8k3n9mwp',
  event: 'Event Name',
  properties: {
    property1: 'value1',
    property2: 'value2'
  },
  timestamp: new Date()
});
```

### Required Properties for ALL Events

Every event must include:
- `userId` - The unique user identifier
- `timestamp` - ISO 8601 formatted timestamp (auto-generated if not provided)
- `context` - Automatically captured by Segment SDK (device, browser, IP, etc.)

---

## User Lifecycle Events

### 1. User Signed Up

**Event Name:** `user_signed_up`

**When to Fire:** Immediately after successful account creation (after database record is created)

**Where to Implement:** 
- Backend: After user record saved to database
- Frontend: After receiving successful signup response

**Required Properties:**
- `signup_method` (string)
- `company_size` (string)
- `industry` (string)
- `country` (string)
- `referral_source` (string)

**Implementation Example:**

```javascript
// Frontend - After successful signup API call
const handleSignupSuccess = (userData) => {
  analytics.track('user_signed_up', {
    signup_method: userData.authProvider, // 'email', 'google', 'github'
    company_size: userData.companySize,   // '1-10', '11-50', '51-200', '201-500', '501+'
    industry: userData.industry,          // e.g., 'e-commerce', 'saas', 'fintech'
    country: userData.country,            // ISO code: 'SG', 'ID', 'MY'
    referral_source: getReferralSource()  // 'organic', 'paid_ads', 'referral', 'direct'
  });
  
  // Also identify the user
  analytics.identify(userData.userId, {
    email: userData.email,
    name: userData.name,
    created_at: new Date().toISOString()
  });
};
```

**Test Case:**
```javascript
// Expected call when user signs up via Google in Singapore
{
  "event": "user_signed_up",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T03:45:22.000Z",
  "properties": {
    "signup_method": "google",
    "company_size": "11-50",
    "industry": "e-commerce",
    "country": "SG",
    "referral_source": "paid_ads"
  }
}
```

---

### 2. User Logged In

**Event Name:** `user_logged_in`

**When to Fire:** After successful authentication (credentials verified)

**Where to Implement:** Backend authentication middleware

**Required Properties:**
- `login_method` (string)
- `session_id` (string)
- `device_type` (string)

**Implementation Example:**

```javascript
// Backend - After auth verification
const trackLogin = (userId, authMethod, req) => {
  const sessionId = req.session.id;
  const deviceType = detectDeviceType(req.headers['user-agent']);
  
  analytics.track({
    userId: userId,
    event: 'user_logged_in',
    properties: {
      login_method: authMethod,     // 'email', 'google', 'github', 'sso'
      session_id: sessionId,
      device_type: deviceType       // 'desktop', 'mobile', 'tablet'
    },
    context: {
      ip: req.ip,
      userAgent: req.headers['user-agent']
    }
  });
};
```

**Test Case:**
```json
{
  "event": "user_logged_in",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T10:30:15.000Z",
  "properties": {
    "login_method": "email",
    "session_id": "sess_x9k2p4n8",
    "device_type": "desktop"
  }
}
```

---

### 3. User Onboarding Started

**Event Name:** `user_onboarding_started`

**When to Fire:** When user enters the onboarding wizard

**Where to Implement:** Frontend - onboarding component mount

**Required Properties:**
- `onboarding_version` (string)

**Implementation Example:**

```javascript
// Frontend - Onboarding component
useEffect(() => {
  analytics.track('user_onboarding_started', {
    onboarding_version: 'v2.1'
  });
}, []);
```

**Test Case:**
```json
{
  "event": "user_onboarding_started",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T03:46:00.000Z",
  "properties": {
    "onboarding_version": "v2.1"
  }
}
```

---

### 4. User Onboarding Completed

**Event Name:** `user_onboarding_completed`

**When to Fire:** When user clicks "Finish" on final onboarding step

**Where to Implement:** Frontend - onboarding completion handler

**Required Properties:**
- `time_to_complete_seconds` (integer)
- `steps_completed` (integer)
- `skipped_steps` (array of strings)

**Implementation Example:**

```javascript
// Frontend - Track time and steps
const startTime = useRef(Date.now());

const handleOnboardingComplete = (completedSteps, skippedSteps) => {
  const duration = Math.floor((Date.now() - startTime.current) / 1000);
  
  analytics.track('user_onboarding_completed', {
    time_to_complete_seconds: duration,
    steps_completed: completedSteps.length,
    skipped_steps: skippedSteps  // e.g., ['connect_data_source', 'invite_team']
  });
  
  // Update user property
  analytics.identify(userId, {
    onboarding_completed: true
  });
};
```

**Test Case:**
```json
{
  "event": "user_onboarding_completed",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T04:05:30.000Z",
  "properties": {
    "time_to_complete_seconds": 1170,
    "steps_completed": 5,
    "skipped_steps": ["invite_team"]
  }
}
```

---

## Feature Usage Events

### 5. Dashboard Viewed

**Event Name:** `dashboard_viewed`

**When to Fire:** When dashboard page successfully loads and renders

**Where to Implement:** Frontend - dashboard component, after data loads

**Required Properties:**
- `page_load_time_ms` (integer)
- `widgets_visible` (integer)

**Implementation Example:**

```javascript
// Frontend - Dashboard component
useEffect(() => {
  const loadStart = performance.now();
  
  fetchDashboardData().then(() => {
    const loadTime = Math.round(performance.now() - loadStart);
    const widgetCount = document.querySelectorAll('.widget').length;
    
    analytics.track('dashboard_viewed', {
      page_load_time_ms: loadTime,
      widgets_visible: widgetCount
    });
  });
}, []);
```

**Test Case:**
```json
{
  "event": "dashboard_viewed",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T11:20:45.000Z",
  "properties": {
    "page_load_time_ms": 850,
    "widgets_visible": 6
  }
}
```

---

### 6. Report Created

**Event Name:** `report_created`

**When to Fire:** After report is successfully saved to database

**Where to Implement:** Backend - after report creation endpoint

**Required Properties:**
- `report_type` (string)
- `metrics_selected` (array of strings)
- `date_range_days` (integer)

**Implementation Example:**

```javascript
// Backend - Report creation handler
app.post('/api/reports', async (req, res) => {
  const report = await createReport(req.body);
  
  analytics.track({
    userId: req.user.id,
    event: 'report_created',
    properties: {
      report_type: report.type,           // 'funnel', 'retention', 'engagement', 'custom'
      metrics_selected: report.metrics,   // ['daily_active_users', 'conversion_rate']
      date_range_days: report.dateRange   // 7, 30, 90
    }
  });
  
  res.json(report);
});
```

**Test Case:**
```json
{
  "event": "report_created",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T14:15:30.000Z",
  "properties": {
    "report_type": "funnel",
    "metrics_selected": ["signup_rate", "activation_rate", "retention_rate"],
    "date_range_days": 30
  }
}
```

---

### 7. Segment Created

**Event Name:** `segment_created`

**When to Fire:** After user segment is saved to database

**Where to Implement:** Backend - segment creation endpoint

**Required Properties:**
- `segment_name` (string)
- `condition_count` (integer)
- `condition_types` (array of strings)
- `estimated_size` (integer)

**Implementation Example:**

```javascript
// Backend - Segment creation
app.post('/api/segments', async (req, res) => {
  const segment = await createSegment(req.body);
  const estimatedUsers = await estimateSegmentSize(segment.conditions);
  
  const conditionTypes = segment.conditions.map(c => c.type);
  
  analytics.track({
    userId: req.user.id,
    event: 'segment_created',
    properties: {
      segment_name: segment.name,
      condition_count: segment.conditions.length,
      condition_types: conditionTypes,  // ['behavioral', 'demographic']
      estimated_size: estimatedUsers
    }
  });
  
  res.json(segment);
});
```

**Test Case:**
```json
{
  "event": "segment_created",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T15:30:20.000Z",
  "properties": {
    "segment_name": "Power Users",
    "condition_count": 3,
    "condition_types": ["behavioral", "behavioral", "demographic"],
    "estimated_size": 1247
  }
}
```

---

### 8. Query Executed

**Event Name:** `query_executed`

**When to Fire:** After analytics query completes (success or failure)

**Where to Implement:** Backend - analytics query service

**Required Properties:**
- `query_type` (string)
- `date_range_days` (integer)
- `execution_time_ms` (integer)
- `result_count` (integer)

**Implementation Example:**

```javascript
// Backend - Query execution
const executeQuery = async (userId, queryParams) => {
  const startTime = Date.now();
  
  try {
    const results = await runAnalyticsQuery(queryParams);
    const executionTime = Date.now() - startTime;
    
    analytics.track({
      userId: userId,
      event: 'query_executed',
      properties: {
        query_type: queryParams.type,       // 'event_count', 'user_count', 'funnel', 'retention'
        date_range_days: queryParams.days,
        execution_time_ms: executionTime,
        result_count: results.length
      }
    });
    
    return results;
  } catch (error) {
    // Track failed queries too
    analytics.track({
      userId: userId,
      event: 'query_executed',
      properties: {
        query_type: queryParams.type,
        date_range_days: queryParams.days,
        execution_time_ms: Date.now() - startTime,
        result_count: 0,
        error: error.message
      }
    });
    throw error;
  }
};
```

**Test Case:**
```json
{
  "event": "query_executed",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T16:45:10.000Z",
  "properties": {
    "query_type": "funnel",
    "date_range_days": 30,
    "execution_time_ms": 1250,
    "result_count": 8420
  }
}
```

---

### 9. Export Initiated

**Event Name:** `export_initiated`

**When to Fire:** When user clicks export button and generation begins

**Where to Implement:** Backend - export generation service

**Required Properties:**
- `export_format` (string)
- `data_type` (string)
- `record_count` (integer)

**Implementation Example:**

```javascript
// Backend - Export handler
app.post('/api/export', async (req, res) => {
  const { format, dataType, filters } = req.body;
  
  const records = await fetchExportData(dataType, filters);
  
  analytics.track({
    userId: req.user.id,
    event: 'export_initiated',
    properties: {
      export_format: format,      // 'csv', 'json', 'pdf'
      data_type: dataType,        // 'report', 'segment', 'raw_events'
      record_count: records.length
    }
  });
  
  const fileUrl = await generateExport(records, format);
  res.json({ url: fileUrl });
});
```

**Test Case:**
```json
{
  "event": "export_initiated",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T17:20:35.000Z",
  "properties": {
    "export_format": "csv",
    "data_type": "segment",
    "record_count": 3450
  }
}
```

---

## Integration Events

### 10. Integration Connected

**Event Name:** `integration_connected`

**When to Fire:** After OAuth flow completes or API key is validated

**Where to Implement:** Backend - integration configuration endpoint

**Required Properties:**
- `integration_type` (string)
- `configuration_method` (string)

**Implementation Example:**

```javascript
// Backend - OAuth callback
app.get('/api/integrations/callback/:provider', async (req, res) => {
  const { code } = req.query;
  const provider = req.params.provider;
  
  await exchangeCodeForToken(provider, code);
  await saveIntegration(req.user.id, provider);
  
  analytics.track({
    userId: req.user.id,
    event: 'integration_connected',
    properties: {
      integration_type: provider,        // 'segment', 'posthog', 'customerio', 'slack'
      configuration_method: 'oauth'      // 'oauth', 'api_key', 'manual'
    }
  });
  
  res.redirect('/settings/integrations');
});
```

**Test Case:**
```json
{
  "event": "integration_connected",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T12:10:50.000Z",
  "properties": {
    "integration_type": "slack",
    "configuration_method": "oauth"
  }
}
```

---

## Subscription Events

### 11. Trial Started

**Event Name:** `trial_started`

**When to Fire:** When user activates their free trial

**Where to Implement:** Backend - after signup (if trial included)

**Required Properties:**
- `trial_duration_days` (integer)
- `plan_tier` (string)

**Implementation Example:**

```javascript
// Backend - User registration with trial
const activateTrial = async (userId) => {
  const trialEndDate = addDays(new Date(), 14);
  
  await updateUser(userId, {
    subscription_status: 'trial',
    trial_end_date: trialEndDate,
    plan_tier: 'professional'
  });
  
  analytics.track({
    userId: userId,
    event: 'trial_started',
    properties: {
      trial_duration_days: 14,
      plan_tier: 'professional'
    }
  });
};
```

**Test Case:**
```json
{
  "event": "trial_started",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T03:45:22.000Z",
  "properties": {
    "trial_duration_days": 14,
    "plan_tier": "professional"
  }
}
```

---

### 12. Subscription Upgraded

**Event Name:** `subscription_upgraded`

**When to Fire:** After successful payment processing

**Where to Implement:** Backend - payment webhook handler

**Required Properties:**
- `previous_plan` (string)
- `new_plan` (string)
- `billing_cycle` (string)
- `mrr` (float)

**Implementation Example:**

```javascript
// Backend - Stripe webhook handler
app.post('/webhooks/stripe', async (req, res) => {
  const event = req.body;
  
  if (event.type === 'customer.subscription.updated') {
    const subscription = event.data.object;
    const user = await findUserByStripeId(subscription.customer);
    
    analytics.track({
      userId: user.id,
      event: 'subscription_upgraded',
      properties: {
        previous_plan: user.plan_tier,
        new_plan: subscription.items.data[0].price.product.name,
        billing_cycle: subscription.items.data[0].price.recurring.interval, // 'monthly', 'annual'
        mrr: subscription.items.data[0].price.unit_amount / 100
      }
    });
    
    // Update user record
    await updateUser(user.id, {
      plan_tier: subscription.items.data[0].price.product.name,
      subscription_status: 'active'
    });
  }
  
  res.status(200).send();
});
```

**Test Case:**
```json
{
  "event": "subscription_upgraded",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T09:30:00.000Z",
  "properties": {
    "previous_plan": "starter",
    "new_plan": "professional",
    "billing_cycle": "monthly",
    "mrr": 99.00
  }
}
```

---

## Segmentation Builder Instrumentation

These events track how users interact with the segment builder UI itself:

### 13. Segment Builder Opened

**Event Name:** `segment_builder_opened`

**When to Fire:** When user navigates to segment creation page

**Where to Implement:** Frontend - segment builder component mount

**Implementation Example:**

```javascript
// Frontend
useEffect(() => {
  analytics.track('segment_builder_opened', {
    source: 'navigation_menu' // 'navigation_menu', 'dashboard_button', 'quick_action'
  });
}, []);
```

---

### 14. Segment Condition Added

**Event Name:** `segment_condition_added`

**When to Fire:** When user adds a new condition to segment

**Where to Implement:** Frontend - condition builder

**Required Properties:**
- `condition_type` (string)
- `operator` (string)
- `total_conditions` (integer)

**Implementation Example:**

```javascript
// Frontend - When user adds a condition
const handleAddCondition = (conditionType, operator) => {
  analytics.track('segment_condition_added', {
    condition_type: conditionType,  // 'behavioral', 'demographic', 'temporal'
    operator: operator,             // 'equals', 'greater_than', 'contains', 'in_last_days'
    total_conditions: conditions.length + 1
  });
  
  // Add condition to state
  addCondition({ type: conditionType, operator: operator });
};
```

**Test Case:**
```json
{
  "event": "segment_condition_added",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T15:28:15.000Z",
  "properties": {
    "condition_type": "behavioral",
    "operator": "greater_than",
    "total_conditions": 2
  }
}
```

---

### 15. Segment Preview Generated

**Event Name:** `segment_preview_generated`

**When to Fire:** When user clicks "Preview" to see matching users

**Where to Implement:** Frontend - after preview API call

**Required Properties:**
- `preview_size` (integer)
- `generation_time_ms` (integer)

**Implementation Example:**

```javascript
// Frontend - Preview handler
const handlePreview = async () => {
  const startTime = performance.now();
  
  const results = await api.previewSegment(conditions);
  const generationTime = Math.round(performance.now() - startTime);
  
  analytics.track('segment_preview_generated', {
    preview_size: results.count,
    generation_time_ms: generationTime
  });
  
  setPreviewData(results);
};
```

**Test Case:**
```json
{
  "event": "segment_preview_generated",
  "userId": "usr_8k3n9mwp",
  "timestamp": "2025-11-08T15:29:45.000Z",
  "properties": {
    "preview_size": 1247,
    "generation_time_ms": 680
  }
}
```

---

## Quality Assurance

### Testing Checklist

Before deploying tracking code, verify:

✅ **Event Naming:**
- [ ] Uses exact event names from taxonomy (snake_case)
- [ ] No typos or variations

✅ **Properties:**
- [ ] All required properties included
- [ ] Correct data types (string, integer, boolean, etc.)
- [ ] Values match allowed enums from taxonomy

✅ **User Identification:**
- [ ] `userId` is consistent across events
- [ ] `identify()` called on login/signup
- [ ] User properties updated when changed

✅ **Timestamps:**
- [ ] Uses ISO 8601 format
- [ ] Timezone is UTC
- [ ] Server-side events use server timestamp

✅ **Error Handling:**
- [ ] Tracking failures don't break app functionality
- [ ] Failed events logged for debugging

### Validation Tools

**Segment Debugger:**
- Monitor live events: https://app.segment.com/debugger
- Check property formats and values

**PostHog Session Recording:**
- Verify events fire at correct moments in user flow

**Browser Console:**
```javascript
// Enable Segment debug mode
analytics.debug(true);

// Check what's being tracked
analytics.track('test_event', { test: 'value' });
```

---

## Common Mistakes to Avoid

❌ **DON'T:**
- Track PII (personally identifiable information) without hashing
- Use inconsistent event names (`user_signup` vs `user_signed_up`)
- Omit required properties
- Track on wrong trigger (e.g., button click instead of API success)
- Block app functionality if tracking fails

✅ **DO:**
- Hash emails in events, keep raw emails only in `identify()`
- Use exact names from taxonomy
- Include all required properties
- Track after server confirms action
- Wrap tracking in try-catch blocks

---

## Multi-Market Considerations

### Timezone Handling
```javascript
// Always convert to UTC before tracking
const trackEvent = (eventName, properties) => {
  analytics.track(eventName, {
    ...properties,
    timestamp: new Date().toISOString(), // Automatically UTC
    user_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  });
};
```

### Currency Tracking
```javascript
// Store both local currency and USD equivalent
{
  amount_local: 150000,        // Indonesian Rupiah
  currency_local: 'IDR',
  amount_usd: 9.85,
  currency_usd: 'USD',
  exchange_rate: 15228.43
}
```

### Language/Locale
```javascript
// Track user's language preference
analytics.identify(userId, {
  locale: navigator.language,  // e.g., 'id-ID', 'en-SG'
  preferred_language: 'id'     // ISO 639-1 code
});
```

---

## Support & Questions

For tracking implementation questions:
- Refer to [Data Taxonomy](./data-taxonomy.md) for event definitions
- Check [Integration Architecture](./integration-architecture.md) for data flow
- Review Segment documentation: https://segment.com/docs

---

## Version History

- v1.0 (2025-11-08): Initial tracking plan for case study submission