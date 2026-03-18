"""
IT Service Desk Data Generator
Generates realistic sample data simulating a financial services IT environment.
Covers incident tickets, device inventory, and Active Directory user records.
"""

import random
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# Domain Constants
# ---------------------------------------------------------------------------

LOCATIONS = {
    "trade_floor": [
        "Sydney Trading Floor",
        "London Trading Floor",
        "Hong Kong Trading Floor",
        "New York Trading Floor",
    ],
    "corporate": [
        "Sydney Corporate",
        "London Corporate",
        "Melbourne Corporate",
        "Mumbai Shared Services",
    ],
}

ALL_LOCATIONS = LOCATIONS["trade_floor"] + LOCATIONS["corporate"]

DEPARTMENTS = {
    "trade_floor": [
        "Equities Trading",
        "Fixed Income Trading",
        "Commodities Trading",
        "FX Trading",
        "Derivatives Trading",
    ],
    "corporate": [
        "Risk Management",
        "Compliance",
        "Finance",
        "Human Resources",
        "Legal",
        "Operations",
        "IT Infrastructure",
        "Executive Leadership",
    ],
}

VIP_TITLES = [
    "Managing Director",
    "Executive Director",
    "Senior Vice President",
    "Head of Trading",
    "Chief Risk Officer",
    "Chief Financial Officer",
    "Division Director",
]

STANDARD_TITLES = [
    "Analyst",
    "Associate",
    "Senior Associate",
    "Vice President",
    "Trader",
    "Senior Trader",
    "Portfolio Manager",
    "Risk Analyst",
    "Compliance Officer",
    "Operations Analyst",
]

# Incident categories modelled on a financial services IT service desk
INCIDENT_CATEGORIES = {
    "Trading Systems": {
        "subcategories": [
            "Bloomberg Terminal - Connectivity",
            "Bloomberg Terminal - Application Error",
            "Reuters Eikon - Login Failure",
            "Reuters Eikon - Data Feed Issue",
            "Trading Platform - Order Entry",
            "Trading Platform - Market Data",
            "FIX Engine - Connection Drop",
            "Risk System - Calculation Error",
        ],
        "weight": 0.25,
        "avg_resolution_hours": 1.5,
    },
    "Desktop & Hardware": {
        "subcategories": [
            "Workstation - Blue Screen",
            "Workstation - Performance Degradation",
            "Multi-Monitor Setup - Display Issue",
            "Docking Station - Connectivity",
            "Peripheral - Keyboard/Mouse",
            "Peripheral - Headset/Audio",
            "Laptop - Battery/Power",
            "Printer - Paper Jam/Offline",
        ],
        "weight": 0.20,
        "avg_resolution_hours": 2.0,
    },
    "Network & Connectivity": {
        "subcategories": [
            "VPN - Connection Failure",
            "VPN - Slow Performance",
            "Wi-Fi - Unable to Connect",
            "Wired Network - No Connectivity",
            "Network Drive - Access Denied",
            "DNS Resolution - Failure",
            "Proxy - Website Blocked",
            "Latency - High Network Latency",
        ],
        "weight": 0.15,
        "avg_resolution_hours": 3.0,
    },
    "Office 365": {
        "subcategories": [
            "Outlook - Sync Failure",
            "Outlook - Calendar Issue",
            "Teams - Audio/Video Problem",
            "Teams - Screen Share Failure",
            "SharePoint - Access Denied",
            "OneDrive - Sync Error",
            "Excel - Macro/Add-in Failure",
            "Office - Activation Issue",
        ],
        "weight": 0.18,
        "avg_resolution_hours": 2.5,
    },
    "Active Directory & Access": {
        "subcategories": [
            "AD - Account Locked Out",
            "AD - Password Reset",
            "AD - Group Membership Change",
            "MFA - Token Issue",
            "SSO - Login Failure",
            "Application Access - Permission Request",
            "Shared Mailbox - Access Request",
            "Security Certificate - Expired",
        ],
        "weight": 0.12,
        "avg_resolution_hours": 1.0,
    },
    "Software & Applications": {
        "subcategories": [
            "Software Installation Request",
            "Application - Crash on Launch",
            "Application - License Expired",
            "Browser - Plugin/Extension Issue",
            "Java - Version Conflict",
            "PDF Reader - Rendering Issue",
            "Antivirus - False Positive Block",
            "Patch - Post-Update Issue",
        ],
        "weight": 0.10,
        "avg_resolution_hours": 4.0,
    },
}

PRIORITIES = ["Critical", "High", "Medium", "Low"]
PRIORITY_WEIGHTS = [0.05, 0.20, 0.50, 0.25]

SLA_HOURS = {"Critical": 2, "High": 4, "Medium": 8, "Low": 24}

STATUSES = ["Open", "In Progress", "Pending Vendor", "Resolved", "Closed"]

DEVICE_TYPES = {
    "Trading Workstation": {"refresh_months": 36, "cost": 4500, "weight": 0.25},
    "Corporate Laptop": {"refresh_months": 48, "cost": 2200, "weight": 0.30},
    "Bloomberg Terminal": {"refresh_months": 60, "cost": 24000, "weight": 0.10},
    "Multi-Monitor Array": {"refresh_months": 48, "cost": 3500, "weight": 0.10},
    "Docking Station": {"refresh_months": 48, "cost": 350, "weight": 0.10},
    "IP Phone": {"refresh_months": 60, "cost": 600, "weight": 0.08},
    "Mobile Device": {"refresh_months": 24, "cost": 1200, "weight": 0.07},
}

DEVICE_STATUSES = ["Active", "In Refresh Queue", "Decommissioned", "In Repair", "Spare"]

AD_ACTIONS = [
    "Account Created",
    "Account Disabled",
    "Password Reset",
    "Group Added",
    "Group Removed",
    "OU Transfer",
    "MFA Enrolled",
    "MFA Reset",
    "License Assigned",
    "License Removed",
    "Account Unlocked",
    "Permissions Modified",
]


# ---------------------------------------------------------------------------
# Generator Functions
# ---------------------------------------------------------------------------


def generate_tickets(
    count: int = 5000,
    months: int = 12,
    end_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """Generate realistic IT service desk incident tickets.

    Args:
        count: Number of tickets to generate.
        months: How many months of history to create.
        end_date: The latest date for tickets (defaults to today).

    Returns:
        DataFrame with one row per ticket.
    """
    if end_date is None:
        end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    categories = list(INCIDENT_CATEGORIES.keys())
    cat_weights = [INCIDENT_CATEGORIES[c]["weight"] for c in categories]

    records = []
    for i in range(count):
        ticket_id = f"INC{100000 + i}"

        # Choose category, subcategory, and priority
        category = random.choices(categories, weights=cat_weights, k=1)[0]
        cat_info = INCIDENT_CATEGORIES[category]
        subcategory = random.choice(cat_info["subcategories"])
        priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS, k=1)[0]

        # Location and department (trade floor tickets are weighted higher)
        is_trade_floor = random.random() < 0.55
        if is_trade_floor:
            location = random.choice(LOCATIONS["trade_floor"])
            department = random.choice(DEPARTMENTS["trade_floor"])
        else:
            location = random.choice(LOCATIONS["corporate"])
            department = random.choice(DEPARTMENTS["corporate"])

        support_type = "Trade Floor" if is_trade_floor else "Corporate"

        # VIP flag — senior leaders / traders
        is_vip = random.random() < (0.25 if is_trade_floor else 0.08)

        # Created timestamp (business-hours bias)
        created = fake.date_time_between(start_date=start_date, end_date=end_date)
        if created.weekday() >= 5:
            created -= timedelta(days=created.weekday() - 4)
        hour = int(np.random.normal(11, 3))
        hour = max(6, min(20, hour))
        created = created.replace(hour=hour, minute=random.randint(0, 59))

        # Resolution time (log-normal centred on category average)
        base_hours = cat_info["avg_resolution_hours"]
        if priority == "Critical":
            base_hours *= 0.6
        elif priority == "High":
            base_hours *= 0.8
        elif priority == "Low":
            base_hours *= 1.8

        resolution_hours = max(0.1, np.random.lognormal(np.log(base_hours), 0.7))
        resolved_at = created + timedelta(hours=resolution_hours)

        # SLA compliance
        sla_target = SLA_HOURS[priority]
        sla_met = resolution_hours <= sla_target

        # Current status
        if resolved_at <= end_date:
            status = random.choices(
                ["Resolved", "Closed"], weights=[0.3, 0.7], k=1
            )[0]
        else:
            status = random.choices(
                ["Open", "In Progress", "Pending Vendor"], weights=[0.3, 0.5, 0.2], k=1
            )[0]
            resolved_at = None
            resolution_hours = None
            sla_met = None

        # Assignee
        assignee = fake.name()

        # Contact method
        contact_method = random.choices(
            ["Walk-up", "Phone", "Email", "Self-Service Portal", "Teams Chat"],
            weights=[0.30, 0.25, 0.15, 0.15, 0.15] if is_trade_floor else [0.10, 0.20, 0.25, 0.30, 0.15],
            k=1,
        )[0]

        records.append(
            {
                "ticket_id": ticket_id,
                "created_at": created,
                "resolved_at": resolved_at,
                "category": category,
                "subcategory": subcategory,
                "priority": priority,
                "status": status,
                "location": location,
                "department": department,
                "support_type": support_type,
                "is_vip": is_vip,
                "sla_target_hours": sla_target,
                "resolution_hours": round(resolution_hours, 2) if resolution_hours else None,
                "sla_met": sla_met,
                "assignee": assignee,
                "contact_method": contact_method,
                "requester": fake.name(),
            }
        )

    df = pd.DataFrame(records)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["resolved_at"] = pd.to_datetime(df["resolved_at"])
    return df.sort_values("created_at").reset_index(drop=True)


def generate_devices(
    count: int = 1200,
    end_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """Generate device inventory with lifecycle data.

    Args:
        count: Number of devices.
        end_date: Reference date for age calculations.

    Returns:
        DataFrame with one row per device.
    """
    if end_date is None:
        end_date = datetime.now()

    device_types = list(DEVICE_TYPES.keys())
    device_weights = [DEVICE_TYPES[d]["weight"] for d in device_types]

    records = []
    for i in range(count):
        asset_id = f"AST{200000 + i}"
        device_type = random.choices(device_types, weights=device_weights, k=1)[0]
        info = DEVICE_TYPES[device_type]

        # Purchase date — uniform over the refresh window
        max_age_days = int(info["refresh_months"] * 30 * 1.3)
        purchase_date = end_date - timedelta(days=random.randint(1, max_age_days))
        age_months = (end_date - purchase_date).days / 30.0

        # Warranty (typically 3 years)
        warranty_end = purchase_date + timedelta(days=3 * 365)
        warranty_active = warranty_end >= end_date

        # Refresh status
        refresh_due = age_months >= info["refresh_months"]
        months_until_refresh = max(0, info["refresh_months"] - age_months)

        # Device status
        if refresh_due:
            status = random.choices(
                ["Active", "In Refresh Queue", "Decommissioned"],
                weights=[0.3, 0.5, 0.2],
                k=1,
            )[0]
        else:
            status = random.choices(
                ["Active", "In Repair", "Spare"],
                weights=[0.85, 0.08, 0.07],
                k=1,
            )[0]

        location = random.choice(ALL_LOCATIONS)
        assigned_user = fake.name() if status == "Active" else None

        records.append(
            {
                "asset_id": asset_id,
                "device_type": device_type,
                "manufacturer": random.choice(["Dell", "Lenovo", "HP", "Apple"])
                if "Bloomberg" not in device_type
                else "Bloomberg LP",
                "model": fake.bothify(text="??-####"),
                "purchase_date": purchase_date.date(),
                "age_months": round(age_months, 1),
                "refresh_cycle_months": info["refresh_months"],
                "months_until_refresh": round(months_until_refresh, 1),
                "refresh_due": refresh_due,
                "warranty_end": warranty_end.date(),
                "warranty_active": warranty_active,
                "status": status,
                "location": location,
                "assigned_user": assigned_user,
                "unit_cost": info["cost"],
            }
        )

    return pd.DataFrame(records)


def generate_ad_events(
    count: int = 3000,
    months: int = 12,
    end_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """Generate Active Directory provisioning and management events.

    Args:
        count: Number of AD events.
        months: Months of history.
        end_date: Latest event date.

    Returns:
        DataFrame with one row per AD event.
    """
    if end_date is None:
        end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    records = []
    for i in range(count):
        event_id = f"AD{300000 + i}"
        action = random.choice(AD_ACTIONS)

        timestamp = fake.date_time_between(start_date=start_date, end_date=end_date)
        if timestamp.weekday() >= 5:
            timestamp -= timedelta(days=timestamp.weekday() - 4)
        hour = int(np.random.normal(10, 2.5))
        hour = max(7, min(18, hour))
        timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))

        location = random.choice(ALL_LOCATIONS)
        department = random.choice(
            DEPARTMENTS["trade_floor"] + DEPARTMENTS["corporate"]
        )

        # Automated vs manual
        is_automated = action in [
            "Account Locked Out",
            "License Assigned",
            "License Removed",
            "MFA Enrolled",
        ] or random.random() < 0.35

        # Completion time (minutes)
        if is_automated:
            completion_minutes = round(random.uniform(0.5, 5), 1)
        else:
            completion_minutes = round(max(1, np.random.lognormal(np.log(15), 0.8)), 1)

        records.append(
            {
                "event_id": event_id,
                "timestamp": timestamp,
                "action": action,
                "target_user": fake.user_name(),
                "display_name": fake.name(),
                "department": department,
                "location": location,
                "performed_by": "SYSTEM" if is_automated else fake.name(),
                "is_automated": is_automated,
                "completion_minutes": completion_minutes,
                "success": random.random() < 0.97,
            }
        )

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)


def load_all_data(
    ticket_count: int = 5000,
    device_count: int = 1200,
    ad_event_count: int = 3000,
    months: int = 12,
) -> dict[str, pd.DataFrame]:
    """Convenience loader that returns all three datasets.

    Returns:
        Dictionary with keys 'tickets', 'devices', 'ad_events'.
    """
    return {
        "tickets": generate_tickets(count=ticket_count, months=months),
        "devices": generate_devices(count=device_count),
        "ad_events": generate_ad_events(count=ad_event_count, months=months),
    }


if __name__ == "__main__":
    data = load_all_data()
    for name, df in data.items():
        print(f"{name}: {len(df)} rows, columns: {list(df.columns)}")
        print(df.head(3))
        print()
