# Data Governance - Momentum Product Analytics Platform

## Overview

This document outlines Momentum's approach to data governance, privacy compliance, and responsible data handling practices. As a B2B SaaS analytics platform operating in Southeast Asia, we prioritize compliance with regional data protection regulations while maintaining data utility for product analytics.

**Scope:** Applies to all user data collected, processed, and stored by Momentum, including data flowing through Segment, PostHog, and Customer.io.

**Last Updated:** November 8, 2025

---

## Table of Contents

1. [Regulatory Framework](#regulatory-framework)
2. [Data Classification](#data-classification)
3. [Data Collection Principles](#data-collection-principles)
4. [Privacy by Design](#privacy-by-design)
5. [Data Subject Rights](#data-subject-rights)
6. [Data Retention & Deletion](#data-retention--deletion)
7. [Security Measures](#security-measures)
8. [Third-Party Data Processors](#third-party-data-processors)
9. [Consent Management](#consent-management)
10. [Incident Response](#incident-response)
11. [Multi-Market Compliance](#multi-market-compliance)

---

## Regulatory Framework

### Primary Regulations

Momentum operates under the following data protection frameworks:

#### 1. PDPA - Personal Data Protection Act (Singapore)

**Applicability:** All users in Singapore, data stored/processed in Singapore

**Key Requirements:**
- Obtain consent before collecting personal data
- Use data only for disclosed purposes
- Implement reasonable security measures
- Provide access to and correction of personal data
- Retain data only as long as necessary

**Regulatory Authority:** Personal Data Protection Commission (PDPC) Singapore

**Reference:** https://www.pdpc.gov.sg/

---

#### 2. PDP - Peraturan Perlindungan Data Pribadi (Indonesia)

**Applicability:** All users in Indonesia, data of Indonesian citizens

**Key Requirements:**
- Lawful basis for processing (consent, contract, legal obligation)
- Data minimization principle
- Purpose limitation
- Data localization requirements (certain data must be stored in Indonesia)
- Right to erasure and data portability

**Regulatory Authority:** Ministry of Communication and Informatics (Kominfo)

**Reference:** UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi

---

#### 3. GDPR - General Data Protection Regulation (EU)

**Applicability:** PostHog EU cloud instance, potential EU customers

**Key Requirements:**
- Legal basis for processing
- Data protection impact assessments
- Data Protection Officer (for certain thresholds)
- Strict consent requirements
- Right to be forgotten

**Note:** While not our primary market, GDPR compliance ensures gold-standard privacy practices.

---

### Compliance Matrix

| Requirement | PDPA (SG) | PDP (ID) | GDPR (EU) | Momentum Approach |
|-------------|-----------|----------|-----------|-------------------|
| **Consent Required** | Yes | Yes | Yes | ✅ Obtained at signup |
| **Purpose Limitation** | Yes | Yes | Yes | ✅ Disclosed in ToS |
| **Data Minimization** | Implied | Yes | Yes | ✅ Only essential data |
| **Access Rights** | Yes | Yes | Yes | ✅ Self-service portal |
| **Deletion Rights** | Yes | Yes | Yes | ✅ Automated process |
| **Data Localization** | No | Yes* | No | ⚠️ ID users: local storage |
| **Breach Notification** | 72h (if harm) | Immediate | 72h | ✅ 24h target |

*Indonesia requires certain sensitive data to be stored locally

---

## Data Classification

### PII - Personally Identifiable Information

**Definition:** Data that can identify a specific individual

**Examples in Momentum:**
- ❌ **Direct PII (High Risk):**
  - Email addresses (primary identifier)
  - Full names
  - IP addresses (raw)
  - Phone numbers (if collected)

- ⚠️ **Indirect PII (Medium Risk):**
  - User ID (hashed, pseudo-anonymous)
  - Company names (can identify individuals in small companies)
  - Session IDs (temporary, tied to user)

**Handling Requirements:**
- Direct PII: Encrypted at rest, hashed in analytics tools
- Indirect PII: Minimized where possible, pseudonymized
- Never log PII in application logs or error messages

---

### Non-PII Data

**Definition:** Aggregated or anonymized data that cannot identify individuals

**Examples:**
- Event counts (e.g., "1,000 reports created today")
- Feature adoption rates
- Aggregate metrics by country/industry
- Anonymized behavioral patterns

**Handling:** Can be retained indefinitely, used for product analytics and machine learning

---

### Sensitive Personal Data

**Definition:** Data revealing sensitive attributes (GDPR Article 9, PDP Pasal 4)

**Types:**
- Racial or ethnic origin
- Political opinions
- Religious beliefs
- Health data
- Biometric data

**Momentum Position:** **We do NOT collect sensitive personal data**

If inadvertently collected (e.g., user enters sensitive info in custom fields):
- Immediate deletion upon detection
- Security incident logged
- User notified if required

---

## Data Collection Principles

### 1. Consent-Based Collection

**When We Collect Consent:**
- ✅ During signup (checkbox: "I agree to Terms of Service and Privacy Policy")
- ✅ Before enabling session recording (separate opt-in)
- ✅ Before sending marketing emails (separate checkbox)

**Consent Requirements:**
- Must be freely given, specific, informed, and unambiguous
- Granular (separate consent for analytics vs marketing)
- Easily withdrawable (one-click unsubscribe)

**Implementation:**

```javascript
// Signup form - explicit consent
<form onSubmit={handleSignup}>
  <input type="checkbox" name="terms_consent" required>
    I agree to <a href="/terms">Terms of Service</a> and 
    <a href="/privacy">Privacy Policy</a>
  </input>
  
  <input type="checkbox" name="marketing_consent">
    I want to receive product updates and tips (optional)
  </input>
</form>

// Track consent
analytics.identify(userId, {
  consent_analytics: true,
  consent_marketing: marketingCheckbox.checked,
  consent_date: new Date().toISOString()
});
```

---

### 2. Purpose Limitation

**Principle:** Data collected for one purpose cannot be used for unrelated purposes without additional consent.

**Our Purposes:**

| Purpose | Data Used | Legal Basis | Consent Required |
|---------|-----------|-------------|------------------|
| **Service Delivery** | All user & event data | Contract | Implicit (ToS) |
| **Product Analytics** | Anonymized events | Legitimate Interest | No |
| **Marketing** | Email, preferences | Consent | Yes (opt-in) |
| **Customer Support** | User profile, usage | Contract | Implicit |
| **Security** | IP, session logs | Legal Obligation | No |

**Example Violation We Avoid:**
❌ Using email addresses collected for account creation to send unsolicited marketing
✅ Separate opt-in for marketing communications

---

### 3. Data Minimization

**Principle:** Collect only data necessary for stated purposes.

**What We Collect:**

✅ **Necessary:**
- Email (account identifier, password reset)
- Company name (B2B context)
- Events (core product functionality)

❌ **Unnecessary (NOT collected):**
- Date of birth
- Home address
- Credit card details (handled by Stripe, not stored by us)
- Social security numbers
- Photos/documents (unless user uploads)

**Event Properties Review:**
- Every property in taxonomy must justify business need
- Remove "nice to have" data that doesn't drive decisions

---

## Privacy by Design

### Principles Applied

**1. Proactive Not Reactive**
- Privacy considerations in feature design phase
- Privacy impact assessments for new features
- Security reviews before deployment

**2. Privacy as Default Setting**
- Session recording: Opt-in, not opt-out
- Marketing emails: Opt-in only
- Data sharing: Disabled by default

**3. Privacy Embedded into Design**
- User IDs: Hashed/UUIDs, not sequential integers
- Emails: Hashed before sending to analytics tools
- IP addresses: Last octet removed (anonymization)

**4. Full Functionality with Privacy**
- Analytics work without revealing individual identities
- Segments based on behavior, not personal attributes
- Insights available without exposing PII

---

### Technical Implementation

**Email Hashing:**

```javascript
// Before sending to PostHog/analytics
const crypto = require('crypto');

function hashEmail(email) {
  return crypto
    .createHash('sha256')
    .update(email.toLowerCase().trim())
    .digest('hex')
    .substring(0, 16);  // First 16 chars for brevity
}

// Usage
analytics.identify(userId, {
  email_hash: hashEmail(user.email),  // Hashed
  // email: user.email  ❌ Never send raw email to analytics
});
```

**IP Anonymization:**

```javascript
// Remove last octet before storing
function anonymizeIP(ip) {
  const parts = ip.split('.');
  if (parts.length === 4) {
    parts[3] = '0';  // 192.168.1.123 → 192.168.1.0
    return parts.join('.');
  }
  return ip;
}

// Segment automatically does this, but verify:
analytics.track('event_name', properties, {
  context: {
    ip: anonymizeIP(req.ip)
  }
});
```

**Session Recording Masking:**

```javascript
// PostHog session recording config
posthog.init('YOUR_API_KEY', {
  session_recording: {
    maskAllInputs: true,  // Mask all form inputs
    maskAllText: false,   // Allow text for UX analysis
    maskTextSelector: '.sensitive',  // Mask specific elements
    blockClass: 'ph-no-capture',  // Don't record these elements
    ignoreClass: 'ph-ignore',
  }
});
```

---

## Data Subject Rights

Users have the following rights under PDPA, PDP, and GDPR:

### 1. Right to Access

**User Request:** "What data do you have about me?"

**Response Time:** 30 days (PDPA/GDPR), 14 days (target)

**Implementation:**
- Self-service portal: Settings → Privacy → Download My Data
- Exports all user data in JSON format
- Includes: profile, events, segments, reports

**Automation:**

```javascript
// Data export API endpoint
app.get('/api/users/:userId/export', authenticate, async (req, res) => {
  const userId = req.params.userId;
  
  // Verify user is requesting their own data
  if (req.user.id !== userId) {
    return res.status(403).json({ error: 'Unauthorized' });
  }
  
  const userData = {
    profile: await db.users.findOne({ user_id: userId }),
    events: await db.events.find({ userId: userId }).toArray(),
    segments: await getSegmentsForUser(userId),
    reports: await getReportsForUser(userId),
    export_date: new Date().toISOString()
  };
  
  res.json(userData);
});
```

---

### 2. Right to Rectification

**User Request:** "My company name is wrong, please update it."

**Response Time:** Immediate (self-service)

**Implementation:**
- Users can edit profile in Settings
- Changes propagate to Segment → PostHog → Customer.io
- Audit log of changes maintained

---

### 3. Right to Erasure ("Right to be Forgotten")

**User Request:** "Delete all my data."

**Response Time:** 30 days (complete deletion from all systems)

**Implementation:**

**Step 1: User-Initiated Deletion**
```javascript
// Account deletion endpoint
app.post('/api/users/:userId/delete', authenticate, async (req, res) => {
  const userId = req.params.userId;
  
  // 1. Mark account for deletion (grace period)
  await db.users.update(
    { user_id: userId },
    { 
      deletion_requested_at: new Date(),
      account_status: 'pending_deletion'
    }
  );
  
  // 2. Queue deletion job (executes after 30-day grace period)
  await queue.schedule('user_deletion', { userId }, { delay: '30 days' });
  
  res.json({ 
    message: 'Deletion scheduled. You have 30 days to cancel.',
    cancellation_url: `/account/cancel-deletion`
  });
});
```

**Step 2: Deletion Job (Background)**
```javascript
// Background job - executes after 30 days
async function deleteUserData(userId) {
  // 1. Delete from application database
  await db.users.delete({ user_id: userId });
  await db.events.deleteMany({ userId: userId });
  
  // 2. Delete from Segment
  await segmentAPI.delete(`/users/${userId}`);
  
  // 3. Delete from PostHog
  await posthogAPI.post('/api/person/delete', { distinct_id: userId });
  
  // 4. Delete from Customer.io
  await customerioAPI.delete(`/customers/${userId}`);
  
  // 5. Log deletion (retain for audit)
  await auditLog.create({
    action: 'user_deleted',
    user_id: userId,
    timestamp: new Date(),
    reason: 'user_request'
  });
}
```

**What Gets Deleted:**
- ✅ User profile (name, email, company)
- ✅ All events associated with user
- ✅ Segment memberships
- ✅ Reports created by user
- ✅ Customer.io marketing profile

**What We Retain:**
- ✅ Aggregated analytics (anonymized, no user linkage)
- ✅ Audit logs (legal requirement, 7 years)
- ✅ Billing records (tax law, 7 years)

---

### 4. Right to Data Portability

**User Request:** "Give me my data in a format I can use elsewhere."

**Response Time:** 7 days

**Implementation:**
- Export as JSON (machine-readable)
- Option to export as CSV (Excel-compatible)
- Includes all events, reports, segments

---

### 5. Right to Restrict Processing

**User Request:** "Stop using my data for analytics, but keep my account active."

**Response Time:** Immediate

**Implementation:**

```javascript
// User opts out of analytics
analytics.identify(userId, {
  analytics_consent: false,
  consent_withdrawn_at: new Date()
});

// Stop tracking events for this user
if (!user.analytics_consent) {
  // Still track critical events (login, billing) but not behavioral
  return;
}
```

---

### 6. Right to Object

**User Request:** "Stop sending me marketing emails."

**Response Time:** Immediate

**Implementation:**
- One-click unsubscribe in all emails
- Preference center in Settings
- Synced with Customer.io suppression list

---

## Data Retention & Deletion

### Retention Policies

| Data Type | Retention Period | Rationale | Post-Retention Action |
|-----------|------------------|-----------|----------------------|
| **User Profile** | While account active + 30 days | Service delivery | Delete |
| **Events** | While account active + 90 days | Analytics, support | Anonymize or delete |
| **Session Recordings** | 30 days | Debugging, UX research | Auto-delete |
| **Audit Logs** | 7 years | Legal compliance | Archive offline |
| **Billing Records** | 7 years | Tax law (SG/ID) | Archive offline |
| **Support Tickets** | 3 years | Quality assurance | Anonymize PII |
| **Marketing Consent** | Until withdrawn | Legal proof | Retain record |

### Automated Deletion

**Cron Job - Daily Cleanup:**

```javascript
// Runs daily at 2 AM UTC
async function dailyDataCleanup() {
  const now = new Date();
  
  // 1. Delete expired session recordings (>30 days)
  await posthog.deleteRecordings({
    older_than: addDays(now, -30)
  });
  
  // 2. Delete soft-deleted users (grace period ended)
  const usersToDelete = await db.users.find({
    deletion_requested_at: { $lte: addDays(now, -30) },
    account_status: 'pending_deletion'
  });
  
  for (const user of usersToDelete) {
    await deleteUserData(user.user_id);
  }
  
  // 3. Anonymize old events for inactive users (>90 days)
  await db.events.updateMany(
    { 
      userId: { $in: inactiveUserIds },
      timestamp: { $lte: addDays(now, -90) }
    },
    {
      $set: { userId: 'anonymous' },
      $unset: { email: '', name: '' }
    }
  );
  
  console.log(`Cleanup complete: ${usersToDelete.length} users deleted`);
}
```

---

## Security Measures

### Data Protection Controls

**1. Encryption**

**In Transit:**
- TLS 1.3 for all API connections
- HTTPS enforced (HSTS headers)
- Certificate pinning for mobile apps

**At Rest:**
- AES-256 encryption for database
- Encrypted backups
- Segment, PostHog, Customer.io: All encrypt at rest

**Implementation:**

```javascript
// Database connection - encryption enforced
const dbConfig = {
  ssl: true,
  sslmode: 'require',
  sslcert: fs.readFileSync('client-cert.pem'),
  sslkey: fs.readFileSync('client-key.pem'),
  sslrootcert: fs.readFileSync('server-ca.pem')
};
```

---

**2. Access Controls**

**Principle of Least Privilege:**
- Developers: Read-only production access
- Support team: Access only to assigned tickets
- Admins: Full access, audit logged

**Implementation:**

```javascript
// Role-based access control
const roles = {
  admin: ['read', 'write', 'delete', 'export'],
  support: ['read', 'limited_write'],
  analyst: ['read', 'export_anonymized'],
  developer: ['read']
};

function checkPermission(user, action) {
  return roles[user.role].includes(action);
}
```

---

**3. Audit Logging**

**All sensitive operations logged:**
- User data access (who viewed what, when)
- Data exports
- Deletion requests
- Permission changes

**Log Format:**

```json
{
  "timestamp": "2025-11-08T10:30:00Z",
  "action": "user_data_accessed",
  "actor_id": "admin_123",
  "subject_id": "usr_456",
  "resource": "user_profile",
  "ip_address": "192.168.1.0",
  "outcome": "success"
}
```

**Retention:** 7 years (compliance requirement)

---

**4. Regular Security Audits**

**Schedule:**
- Quarterly: Internal security review
- Annually: Third-party penetration testing
- Continuous: Automated vulnerability scanning

**Scope:**
- Application vulnerabilities (OWASP Top 10)
- Infrastructure configuration
- Third-party dependencies
- Access control effectiveness

---

## Third-Party Data Processors

### Subprocessor Register

| Service | Purpose | Data Shared | Location | Compliance |
|---------|---------|-------------|----------|------------|
| **Segment** | Customer Data Platform | All events, user profiles | US | SOC 2, Privacy Shield |
| **PostHog** | Product Analytics | Events (email hashed) | EU/US | GDPR, SOC 2 |
| **Customer.io** | Marketing Automation | Email, user properties | US | GDPR, SOC 2 |
| **Stripe** | Payment Processing | Billing info (we don't store) | US | PCI-DSS |
| **AWS** | Infrastructure | All data | SG/ID/US | ISO 27001, SOC 2 |

### Data Processing Agreements (DPAs)

**Required:** Signed DPAs with all subprocessors

**Key Clauses:**
- Subprocessor only processes data per our instructions
- Maintains appropriate security measures
- Assists with data subject requests
- Notifies us of breaches within 24 hours
- Deletes data upon contract termination

**Review:** Annually, or when adding new subprocessors

---

## Consent Management

### Consent Tracking

**What We Track:**

```javascript
// User consent record
{
  user_id: "usr_123",
  consents: {
    terms_of_service: {
      given: true,
      timestamp: "2025-10-15T08:30:00Z",
      version: "v2.1",
      ip_address: "192.168.1.0"
    },
    analytics_tracking: {
      given: true,
      timestamp: "2025-10-15T08:30:00Z"
    },
    marketing_emails: {
      given: false,
      timestamp: "2025-10-15T08:30:00Z"
    },
    session_recording: {
      given: true,
      timestamp: "2025-10-20T14:00:00Z"
    }
  }
}
```

### Consent Withdrawal

**Process:**
1. User clicks "Manage Privacy" in Settings
2. Toggles consent switches
3. Changes take effect immediately
4. Audit log records withdrawal

**PostHog Session Recording - Withdraw:**

```javascript
// User withdraws session recording consent
posthog.opt_out_capturing();  // Stops all tracking
posthog.delete_session_recording();  // Deletes existing recordings
```

---

## Incident Response

### Data Breach Protocol

**Definition:** Unauthorized access, loss, or disclosure of personal data

**Response Steps:**

**1. Detection & Containment (0-1 hour)**
- Identify scope of breach
- Isolate affected systems
- Preserve evidence

**2. Assessment (1-4 hours)**
- Determine data types affected
- Count affected users
- Assess harm potential

**3. Notification (4-72 hours)**

**Thresholds:**

| Severity | Criteria | Notification Required |
|----------|----------|----------------------|
| **High** | Sensitive data, >100 users | Regulator (24h), Users (24h), Public |
| **Medium** | Non-sensitive, >1000 users | Regulator (72h), Users (72h) |
| **Low** | Minimal data, <100 users | Internal log only |

**Notification Template:**

```
Subject: Important Security Notice - Action Required

Dear [User Name],

We are writing to inform you of a security incident that may have affected 
your account.

What Happened:
[Brief description]

What Data Was Affected:
[Specific data types]

What We're Doing:
[Mitigation steps]

What You Should Do:
[User actions: reset password, monitor account, etc.]

Questions: security@momentum.com
```

**4. Remediation (1-7 days)**
- Fix vulnerability
- Restore systems
- Enhanced monitoring

**5. Post-Incident Review (7-14 days)**
- Root cause analysis
- Update security controls
- Training for team

---

## Multi-Market Compliance

### Indonesia-Specific Requirements

**Data Localization (PDP Article 20)**

**Requirement:** Certain data must be stored and processed within Indonesia

**Categories Requiring Local Storage:**
- ❌ **Public Sector Data** - N/A (we're B2B SaaS)
- ⚠️ **Financial Data** - Billing records for Indonesian customers
- ⚠️ **Personal Data** (if "strategically important") - User profiles

**Momentum Approach:**

**Option 1: Hybrid Storage (Recommended)**
```
Indonesian Users:
  - User profiles → AWS Jakarta region
  - Events → PostHog EU (pseudonymized, no direct PII)
  - Billing → AWS Jakarta

Non-Indonesian Users:
  - Standard infrastructure
```

**Option 2: PostHog Self-Hosted (Future)**
- Deploy PostHog instance in AWS Jakarta
- Full data sovereignty
- Higher operational cost

**Current Status:** Evaluating based on customer volume in Indonesia

---

### Singapore-Specific Requirements

**Do Not Call (DNC) Registry**

**Requirement:** Cannot send marketing SMS to numbers on DNC registry

**Momentum Approach:**
- We don't collect phone numbers currently
- If added: Check DNC registry before SMS campaigns
- Email marketing: Not covered by DNC (but PDPA consent rules apply)

---

### Cross-Border Data Transfers

**PDPA Section 26:** Can transfer data outside Singapore if:
1. Recipient country has comparable data protection, OR
2. User consents to transfer, OR
3. Necessary for contract performance

**Our Transfers:**

| From | To | Legal Basis | Safeguard |
|------|----|-----------|-----------| 
| SG → US (Segment) | Contract | Standard Contractual Clauses |
| SG → EU (PostHog) | Adequacy Decision | GDPR compliance |
| ID → US (Customer.io) | Consent | Explicit consent at signup |

---

## Compliance Checklist

### Ongoing Compliance Tasks

**Monthly:**
- ✅ Review new user consent rates
- ✅ Check data retention compliance
- ✅ Audit access logs for anomalies

**Quarterly:**
- ✅ Update privacy policy (if needed)
- ✅ Review subprocessor agreements
- ✅ Security vulnerability scan
- ✅ Data breach simulation exercise

**Annually:**
- ✅ Full privacy audit
- ✅ Third-party penetration test
- ✅ Staff privacy training
- ✅ Data map update (what data flows where)

---

## Documentation & Transparency

### Public Documents

**Required:**
- ✅ Privacy Policy (detailed, user-friendly)
- ✅ Terms of Service
- ✅ Cookie Policy (if applicable)
- ✅ Subprocessor List
- ✅ Data Processing Addendum (DPA) for enterprise customers

**Location:** momentum.com/legal

**Updates:** Notify users 30 days before major changes

---

## Training & Awareness

**All Employees:**
- Privacy basics training (annually)
- Phishing awareness (quarterly)
- Incident response procedures

**Engineering Team:**
- Secure coding practices
- Privacy by design principles
- Data minimization techniques

**Customer Success:**
- Handling data subject requests
- Recognizing data breaches
- Escalation procedures

---

## Version History

- v1.0 (2025-11-08): Initial data governance framework for case study submission

---

## References

- [PDPC Singapore](https://www.pdpc.gov.sg/)
- [Indonesia PDP Law (UU 27/2022)](https://peraturan.bpk.go.id/Home/Details/229798)
- [GDPR Official Text](https://gdpr-info.eu/)
- [ISO 27001 - Information Security Management](https://www.iso.org/isoiec-27001-information-security.html)