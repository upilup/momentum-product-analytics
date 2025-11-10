"""
Sample Data Generator for Momentum Product Analytics Platform

This script generates realistic sample data for testing the analytics platform:
- 250 users with varied profiles
- 10,000+ events representing different user behaviors
- Realistic patterns: power users, churned users, trial users, etc.

Usage:
    python generate_sample_data.py

Outputs:
    - sample_users.json: User profiles with properties
    - sample_events.json: Event stream with timestamps and properties
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import hashlib

# Seed for reproducibility
random.seed(42)

# Configuration
NUM_USERS = 250
START_DATE = datetime(2025, 10, 1)  # Start generating events from Oct 1
END_DATE = datetime(2025, 11, 8)    # Up to today

# Reference data for realistic variety
COUNTRIES = ['SG', 'ID', 'MY', 'TH', 'PH']
COUNTRY_WEIGHTS = [0.35, 0.30, 0.20, 0.10, 0.05]  # Singapore and Indonesia focus

INDUSTRIES = [
    'e-commerce', 'saas', 'fintech', 'edtech', 'healthtech',
    'logistics', 'retail', 'media', 'gaming', 'consulting'
]

COMPANY_SIZES = ['1-10', '11-50', '51-200', '201-500', '501+']
COMPANY_SIZE_WEIGHTS = [0.40, 0.30, 0.20, 0.07, 0.03]  # Mostly small companies

SIGNUP_METHODS = ['email', 'google', 'github']
SIGNUP_METHOD_WEIGHTS = [0.40, 0.45, 0.15]

REFERRAL_SOURCES = ['organic', 'paid_ads', 'referral', 'direct']
REFERRAL_WEIGHTS = [0.35, 0.30, 0.25, 0.10]

PLAN_TIERS = ['trial', 'starter', 'professional', 'enterprise']

REPORT_TYPES = ['funnel', 'retention', 'engagement', 'custom']
EXPORT_FORMATS = ['csv', 'json', 'pdf']
INTEGRATION_TYPES = ['segment', 'posthog', 'customerio', 'slack', 'webhook']

# User behavior archetypes
USER_ARCHETYPES = {
    'power_user': {
        'weight': 0.15,
        'activity_level': (0.8, 1.0),  # Active 80-100% of days
        'feature_adoption': (0.7, 1.0),  # Uses most features
        'events_per_day': (15, 30),
        'likely_plan': ['professional', 'enterprise']
    },
    'active_user': {
        'weight': 0.25,
        'activity_level': (0.4, 0.7),
        'feature_adoption': (0.5, 0.8),
        'events_per_day': (8, 20),
        'likely_plan': ['starter', 'professional']
    },
    'casual_user': {
        'weight': 0.30,
        'activity_level': (0.2, 0.4),
        'feature_adoption': (0.3, 0.6),
        'events_per_day': (3, 10),
        'likely_plan': ['trial', 'starter']
    },
    'trial_user': {
        'weight': 0.15,
        'activity_level': (0.1, 0.3),
        'feature_adoption': (0.2, 0.5),
        'events_per_day': (2, 8),
        'likely_plan': ['trial']
    },
    'churned_user': {
        'weight': 0.15,
        'activity_level': (0.0, 0.1),  # Barely active
        'feature_adoption': (0.1, 0.3),
        'events_per_day': (0, 2),
        'likely_plan': ['trial', 'starter']
    }
}


def generate_user_id(index: int) -> str:
    """Generate unique user ID"""
    return f"usr_{hashlib.md5(str(index).encode()).hexdigest()[:8]}"


def generate_email(index: int, company: str) -> str:
    """Generate realistic email"""
    domains = ['gmail.com', 'company.com', 'startup.io', 'business.co']
    name = f"user{index}"
    domain = random.choice(domains) if random.random() > 0.3 else f"{company.lower().replace(' ', '')}.com"
    return f"{name}@{domain}"


def generate_session_id() -> str:
    """Generate session ID"""
    return f"sess_{hashlib.md5(str(random.random()).encode()).hexdigest()[:12]}"


def hash_email(email: str) -> str:
    """Hash email for privacy"""
    return hashlib.sha256(email.encode()).hexdigest()[:16]


def random_timestamp(start: datetime, end: datetime) -> str:
    """Generate random timestamp between start and end"""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    timestamp = start + timedelta(seconds=random_seconds)
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def generate_users(num_users: int) -> List[Dict]:
    """Generate user profiles"""
    users = []
    
    for i in range(num_users):
        user_id = generate_user_id(i)
        
        # Assign archetype
        archetype = random.choices(
            list(USER_ARCHETYPES.keys()),
            weights=[a['weight'] for a in USER_ARCHETYPES.values()]
        )[0]
        
        # Generate signup date (spread across October)
        signup_date = START_DATE + timedelta(days=random.randint(0, 30))
        
        # Basic properties
        country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS)[0]
        company_size = random.choices(COMPANY_SIZES, weights=COMPANY_SIZE_WEIGHTS)[0]
        industry = random.choice(INDUSTRIES)
        company_name = f"{random.choice(['Tech', 'Digital', 'Smart', 'Cloud', 'Fast'])} {random.choice(['Solutions', 'Systems', 'Dynamics', 'Innovations', 'Labs'])}"
        
        email = generate_email(i, company_name)
        
        # Plan based on archetype
        plan_tier = random.choice(USER_ARCHETYPES[archetype]['likely_plan'])
        
        # Subscription status
        if plan_tier == 'trial':
            subscription_status = 'trial'
            trial_end = (signup_date + timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            subscription_status = 'active' if archetype != 'churned_user' else random.choice(['past_due', 'cancelled'])
            trial_end = None
        
        # Behavioral metrics (will be computed from events, but we set initial values)
        activity_range = USER_ARCHETYPES[archetype]['activity_level']
        total_days = (END_DATE - signup_date).days
        days_active_30 = int(min(30, total_days) * random.uniform(*activity_range))
        days_active_7 = int(min(7, total_days) * random.uniform(*activity_range))
        
        adoption_range = USER_ARCHETYPES[archetype]['feature_adoption']
        feature_adoption_score = round(random.uniform(*adoption_range) * 100, 1)
        
        user = {
            'user_id': user_id,
            'email': hash_email(email),  # Hashed for privacy
            'name': f"User {i}",
            'created_at': signup_date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'company_name': company_name,
            'company_size': company_size,
            'industry': industry,
            'country': country,
            'timezone': {
                'SG': 'Asia/Singapore',
                'ID': 'Asia/Jakarta',
                'MY': 'Asia/Kuala_Lumpur',
                'TH': 'Asia/Bangkok',
                'PH': 'Asia/Manila'
            }[country],
            'plan_tier': plan_tier,
            'trial_end_date': trial_end,
            'subscription_status': subscription_status,
            'mrr': {
                'trial': 0,
                'starter': 29,
                'professional': 99,
                'enterprise': 299
            }[plan_tier] if subscription_status == 'active' else 0,
            'onboarding_completed': archetype != 'churned_user' and random.random() > 0.2,
            'total_logins': 0,  # Will be computed from events
            'total_reports_created': 0,
            'total_segments_created': 0,
            'total_queries_executed': 0,
            'days_active_last_7': days_active_7,
            'days_active_last_30': days_active_30,
            'days_since_last_login': 0,  # Will be computed
            'average_session_duration_minutes': round(random.uniform(5, 45), 1),
            'feature_adoption_score': feature_adoption_score,
            'last_active_at': None,  # Will be set from events
            'archetype': archetype  # For our reference (not normally stored)
        }
        
        users.append(user)
    
    return users


def generate_events_for_user(user: Dict, start_date: datetime, end_date: datetime) -> List[Dict]:
    """Generate realistic event stream for a single user"""
    events = []
    user_id = user['user_id']
    archetype = user['archetype']
    signup_date = datetime.fromisoformat(user['created_at'].replace('Z', ''))
    
    # Don't generate events before signup
    user_start = max(start_date, signup_date)
    if user_start >= end_date:
        return events
    
    total_days = (end_date - user_start).days
    if total_days <= 0:
        return events
    
    # Get activity parameters
    activity_level = random.uniform(*USER_ARCHETYPES[archetype]['activity_level'])
    events_per_day_range = USER_ARCHETYPES[archetype]['events_per_day']
    feature_adoption = random.uniform(*USER_ARCHETYPES[archetype]['feature_adoption'])
    
    # 1. SIGNUP EVENT (always first)
    signup_event = {
        'event': 'user_signed_up',
        'userId': user_id,
        'timestamp': user['created_at'],
        'properties': {
            'signup_method': random.choices(SIGNUP_METHODS, weights=SIGNUP_METHOD_WEIGHTS)[0],
            'company_size': user['company_size'],
            'industry': user['industry'],
            'country': user['country'],
            'referral_source': random.choices(REFERRAL_SOURCES, weights=REFERRAL_WEIGHTS)[0]
        }
    }
    events.append(signup_event)
    
    # 2. ONBOARDING EVENTS
    if user['onboarding_completed']:
        onboarding_start = signup_date + timedelta(minutes=5)
        onboarding_complete = onboarding_start + timedelta(minutes=random.randint(10, 60))
        
        events.append({
            'event': 'user_onboarding_started',
            'userId': user_id,
            'timestamp': onboarding_start.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'properties': {
                'onboarding_version': 'v2.1'
            }
        })
        
        events.append({
            'event': 'user_onboarding_completed',
            'userId': user_id,
            'timestamp': onboarding_complete.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'properties': {
                'time_to_complete_seconds': int((onboarding_complete - onboarding_start).total_seconds()),
                'steps_completed': random.randint(4, 6),
                'skipped_steps': random.sample(['invite_team', 'connect_data_source'], k=random.randint(0, 1))
            }
        })
    
    # 3. TRIAL STARTED (if applicable)
    if user['plan_tier'] == 'trial':
        events.append({
            'event': 'trial_started',
            'userId': user_id,
            'timestamp': user['created_at'],
            'properties': {
                'trial_duration_days': 14,
                'plan_tier': 'professional'
            }
        })
    
    # 4. REGULAR ACTIVITY EVENTS
    # Determine which days the user is active
    active_days = []
    for day_offset in range(total_days):
        if random.random() < activity_level:
            active_days.append(user_start + timedelta(days=day_offset))
    
    session_id = None
    last_activity_time = None
    
    for active_day in sorted(active_days):
        # How many events on this day?
        num_events_today = random.randint(*events_per_day_range)
        
        # Generate session ID for this day
        session_id = generate_session_id()
        
        # Login event (start of session)
        login_time = active_day.replace(
            hour=random.randint(8, 18),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        events.append({
            'event': 'user_logged_in',
            'userId': user_id,
            'timestamp': login_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'properties': {
                'login_method': random.choice(['email', 'google', 'github']),
                'session_id': session_id,
                'device_type': random.choice(['desktop', 'desktop', 'desktop', 'mobile', 'tablet'])  # Mostly desktop
            }
        })
        
        user['total_logins'] += 1
        last_activity_time = login_time
        
        # Dashboard view (common after login)
        if random.random() < 0.8:
            dashboard_time = login_time + timedelta(seconds=random.randint(5, 30))
            events.append({
                'event': 'dashboard_viewed',
                'userId': user_id,
                'timestamp': dashboard_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'properties': {
                    'page_load_time_ms': random.randint(300, 2000),
                    'widgets_visible': random.randint(4, 8)
                }
            })
            last_activity_time = dashboard_time
        
        # Generate other events throughout the session
        session_duration = random.randint(300, 3600)  # 5 min to 1 hour
        
        for _ in range(num_events_today - 2):  # -2 because we already did login and dashboard
            # Random time within session
            event_time = login_time + timedelta(seconds=random.randint(60, session_duration))
            
            # Choose event based on feature adoption
            if random.random() < feature_adoption * 0.6:  # Report creation (core feature)
                report_type = random.choice(REPORT_TYPES)
                events.append({
                    'event': 'report_created',
                    'userId': user_id,
                    'timestamp': event_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    'properties': {
                        'report_type': report_type,
                        'metrics_selected': random.sample(['daily_active_users', 'conversion_rate', 'retention_rate', 'churn_rate'], k=random.randint(1, 3)),
                        'date_range_days': random.choice([7, 30, 90])
                    }
                })
                user['total_reports_created'] += 1
            
            elif random.random() < feature_adoption * 0.5:  # Segment creation
                events.append({
                    'event': 'segment_created',
                    'userId': user_id,
                    'timestamp': event_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    'properties': {
                        'segment_name': random.choice(['Power Users', 'At-Risk Users', 'New Users', 'Trial Users', 'High Value']),
                        'condition_count': random.randint(1, 5),
                        'condition_types': random.sample(['behavioral', 'demographic', 'temporal'], k=random.randint(1, 3)),
                        'estimated_size': random.randint(50, 5000)
                    }
                })
                user['total_segments_created'] += 1
            
            elif random.random() < feature_adoption * 0.7:  # Query execution (very common)
                events.append({
                    'event': 'query_executed',
                    'userId': user_id,
                    'timestamp': event_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    'properties': {
                        'query_type': random.choice(['event_count', 'user_count', 'funnel', 'retention']),
                        'date_range_days': random.choice([7, 30, 90]),
                        'execution_time_ms': random.randint(200, 3000),
                        'result_count': random.randint(100, 10000)
                    }
                })
                user['total_queries_executed'] += 1
            
            elif random.random() < feature_adoption * 0.3:  # Chart viewed
                events.append({
                    'event': 'chart_viewed',
                    'userId': user_id,
                    'timestamp': event_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    'properties': {
                        'chart_type': random.choice(['line', 'bar', 'pie', 'funnel', 'table']),
                        'metric_displayed': random.choice(['daily_active_users', 'conversion_rate', 'retention_rate'])
                    }
                })
            
            elif random.random() < feature_adoption * 0.2:  # Export (less common)
                events.append({
                    'event': 'export_initiated',
                    'userId': user_id,
                    'timestamp': event_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    'properties': {
                        'export_format': random.choice(EXPORT_FORMATS),
                        'data_type': random.choice(['report', 'segment', 'raw_events']),
                        'record_count': random.randint(100, 50000)
                    }
                })
            
            last_activity_time = event_time
    
    # 5. INTEGRATION EVENTS (some users)
    if feature_adoption > 0.5 and random.random() < 0.3:
        integration_time = signup_date + timedelta(days=random.randint(1, 7))
        if integration_time < end_date:
            events.append({
                'event': 'integration_connected',
                'userId': user_id,
                'timestamp': integration_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'properties': {
                    'integration_type': random.choice(INTEGRATION_TYPES),
                    'configuration_method': random.choice(['oauth', 'api_key', 'manual'])
                }
            })
    
    # 6. SUBSCRIPTION UPGRADE (some users)
    if user['plan_tier'] in ['starter', 'professional'] and archetype in ['power_user', 'active_user']:
        if random.random() < 0.2:
            upgrade_time = signup_date + timedelta(days=random.randint(7, 25))
            if upgrade_time < end_date:
                new_plan = 'professional' if user['plan_tier'] == 'starter' else 'enterprise'
                events.append({
                    'event': 'subscription_upgraded',
                    'userId': user_id,
                    'timestamp': upgrade_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    'properties': {
                        'previous_plan': user['plan_tier'],
                        'new_plan': new_plan,
                        'billing_cycle': random.choice(['monthly', 'annual']),
                        'mrr': {'professional': 99.0, 'enterprise': 299.0}[new_plan]
                    }
                })
    
    # Update user's last active time
    if last_activity_time:
        user['last_active_at'] = last_activity_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        days_since = (END_DATE - last_activity_time).days
        user['days_since_last_login'] = max(0, days_since)
    
    return events


def main():
    """Generate sample data and save to JSON files"""
    print("🚀 Generating sample data for Momentum Product Analytics Platform...")
    print(f"📅 Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"👥 Generating {NUM_USERS} users...")
    
    # Generate users
    users = generate_users(NUM_USERS)
    print(f"✅ Generated {len(users)} user profiles")
    
    # Generate events for all users
    print("📊 Generating events...")
    all_events = []
    
    for i, user in enumerate(users):
        if (i + 1) % 50 == 0:
            print(f"   Processing user {i + 1}/{NUM_USERS}...")
        
        user_events = generate_events_for_user(user, START_DATE, END_DATE)
        all_events.extend(user_events)
    
    # Sort events by timestamp
    all_events.sort(key=lambda x: x['timestamp'])
    
    print(f"✅ Generated {len(all_events)} events")
    
    # Remove archetype field from users (internal use only)
    for user in users:
        del user['archetype']
    
    # Save to files
    print("💾 Saving to files...")
    
    with open('sample_users.json', 'w') as f:
        json.dump(users, f, indent=2)
    print("✅ Saved sample_users.json")
    
    with open('sample_events.json', 'w') as f:
        json.dump(all_events, f, indent=2)
    print("✅ Saved sample_events.json")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("📈 SUMMARY STATISTICS")
    print("="*60)
    
    print(f"\n👥 Users: {len(users)}")
    print(f"   Countries: {dict(zip(*np.unique([u['country'] for u in users], return_counts=True)))}")
    print(f"   Plan tiers: {dict(zip(*np.unique([u['plan_tier'] for u in users], return_counts=True)))}")
    
    print(f"\n📊 Events: {len(all_events)}")
    event_types = {}
    for event in all_events:
        event_type = event['event']
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print("   Top event types:")
    for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"     - {event_type}: {count}")
    
    # User behavior breakdown
    power_users = sum(1 for u in users if u['feature_adoption_score'] > 70)
    active_users = sum(1 for u in users if 40 <= u['feature_adoption_score'] <= 70)
    casual_users = sum(1 for u in users if u['feature_adoption_score'] < 40)
    
    print(f"\n🎯 User Segments:")
    print(f"   Power Users (score > 70): {power_users}")
    print(f"   Active Users (score 40-70): {active_users}")
    print(f"   Casual Users (score < 40): {casual_users}")
    
    print("\n✨ Sample data generation complete!")
    print("📁 Files created:")
    print("   - sample_users.json")
    print("   - sample_events.json")


if __name__ == '__main__':
    # Import numpy for statistics (optional, falls back to dict if not available)
    try:
        import numpy as np
    except ImportError:
        print("⚠️  NumPy not found, using basic statistics")
        # Simple fallback for unique counts
        class np:
            @staticmethod
            def unique(arr, return_counts=False):
                from collections import Counter
                c = Counter(arr)
                if return_counts:
                    return list(c.keys()), list(c.values())
                return list(c.keys())
    
    main()
