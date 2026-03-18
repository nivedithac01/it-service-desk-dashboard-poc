"""
Core Analytics Engine
Provides SLA calculations, trend analysis, ticket categorisation,
device lifecycle insights, and Active Directory provisioning metrics.
"""

from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Incident / Ticket Analytics
# ---------------------------------------------------------------------------


def calculate_sla_compliance(
    tickets: pd.DataFrame,
    group_by: Optional[str] = None,
) -> pd.DataFrame:
    """Compute SLA compliance rates.

    Args:
        tickets: Tickets DataFrame (must contain 'sla_met' and optionally
                 the column named in *group_by*).
        group_by: Column name to segment results (e.g. 'priority', 'category').

    Returns:
        DataFrame with total tickets, met count, breached count, and compliance %.
    """
    resolved = tickets.dropna(subset=["sla_met"]).copy()

    if group_by and group_by in resolved.columns:
        grouped = resolved.groupby(group_by)
    else:
        resolved["_all"] = "Overall"
        grouped = resolved.groupby("_all")

    result = grouped.agg(
        total_tickets=("sla_met", "count"),
        sla_met_count=("sla_met", "sum"),
    )
    result["sla_breached_count"] = result["total_tickets"] - result["sla_met_count"]
    result["compliance_pct"] = (
        result["sla_met_count"] / result["total_tickets"] * 100
    ).round(2)

    return result.reset_index()


def ticket_volume_trend(
    tickets: pd.DataFrame,
    freq: str = "W",
) -> pd.DataFrame:
    """Aggregate ticket volumes over time.

    Args:
        tickets: Tickets DataFrame.
        freq: Pandas frequency string ('D', 'W', 'M').

    Returns:
        DataFrame indexed by period with ticket counts.
    """
    df = tickets.copy()
    df["period"] = df["created_at"].dt.to_period(freq).dt.to_timestamp()
    volume = df.groupby("period").size().reset_index(name="ticket_count")
    return volume


def resolution_time_stats(
    tickets: pd.DataFrame,
    group_by: str = "category",
) -> pd.DataFrame:
    """Descriptive statistics for resolution times, grouped by a column.

    Returns:
        DataFrame with mean, median, p90, and std of resolution_hours.
    """
    resolved = tickets.dropna(subset=["resolution_hours"])
    stats = (
        resolved.groupby(group_by)["resolution_hours"]
        .agg(
            mean_hours="mean",
            median_hours="median",
            p90_hours=lambda s: np.percentile(s, 90),
            std_hours="std",
            ticket_count="count",
        )
        .round(2)
        .reset_index()
    )
    return stats


def top_incident_subcategories(
    tickets: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:
    """Return the most frequent incident subcategories."""
    counts = (
        tickets.groupby(["category", "subcategory"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(top_n)
    )
    return counts


def trade_floor_vs_corporate(tickets: pd.DataFrame) -> pd.DataFrame:
    """Compare key metrics between trade-floor and corporate support.

    Returns:
        DataFrame with one row per support type summarising volume,
        avg resolution, SLA compliance, and VIP percentage.
    """
    resolved = tickets.dropna(subset=["resolution_hours"])
    summary = (
        resolved.groupby("support_type")
        .agg(
            total_tickets=("ticket_id", "count"),
            avg_resolution_hours=("resolution_hours", "mean"),
            median_resolution_hours=("resolution_hours", "median"),
            sla_compliance_pct=("sla_met", lambda s: round(s.mean() * 100, 2)),
            vip_pct=("is_vip", lambda s: round(s.mean() * 100, 2)),
        )
        .reset_index()
    )
    summary["avg_resolution_hours"] = summary["avg_resolution_hours"].round(2)
    summary["median_resolution_hours"] = summary["median_resolution_hours"].round(2)
    return summary


def contact_method_breakdown(tickets: pd.DataFrame) -> pd.DataFrame:
    """Count tickets by contact/channel method."""
    return (
        tickets.groupby("contact_method")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def priority_distribution(tickets: pd.DataFrame) -> pd.DataFrame:
    """Count tickets by priority level."""
    order = ["Critical", "High", "Medium", "Low"]
    dist = tickets.groupby("priority").size().reset_index(name="count")
    dist["priority"] = pd.Categorical(dist["priority"], categories=order, ordered=True)
    return dist.sort_values("priority")


def monthly_sla_trend(tickets: pd.DataFrame) -> pd.DataFrame:
    """Monthly SLA compliance trend.

    Returns:
        DataFrame with columns: month, compliance_pct, total, met, breached.
    """
    resolved = tickets.dropna(subset=["sla_met"]).copy()
    resolved["month"] = resolved["created_at"].dt.to_period("M").dt.to_timestamp()
    monthly = resolved.groupby("month").agg(
        total=("sla_met", "count"),
        met=("sla_met", "sum"),
    )
    monthly["breached"] = monthly["total"] - monthly["met"]
    monthly["compliance_pct"] = (monthly["met"] / monthly["total"] * 100).round(2)
    return monthly.reset_index()


def vip_ticket_analysis(tickets: pd.DataFrame) -> pd.DataFrame:
    """Compare VIP versus standard ticket handling."""
    resolved = tickets.dropna(subset=["resolution_hours"]).copy()
    return (
        resolved.groupby("is_vip")
        .agg(
            ticket_count=("ticket_id", "count"),
            avg_resolution_hours=("resolution_hours", "mean"),
            sla_compliance_pct=("sla_met", lambda s: round(s.mean() * 100, 2)),
        )
        .reset_index()
        .replace({True: "VIP", False: "Standard"})
        .rename(columns={"is_vip": "requester_type"})
    )


# ---------------------------------------------------------------------------
# Device Lifecycle Analytics
# ---------------------------------------------------------------------------


def device_refresh_summary(devices: pd.DataFrame) -> pd.DataFrame:
    """Summarise refresh status by device type."""
    return (
        devices.groupby("device_type")
        .agg(
            total_devices=("asset_id", "count"),
            refresh_due_count=("refresh_due", "sum"),
            avg_age_months=("age_months", "mean"),
            avg_months_to_refresh=("months_until_refresh", "mean"),
        )
        .round(1)
        .reset_index()
    )


def device_status_counts(devices: pd.DataFrame) -> pd.DataFrame:
    """Count devices by current status."""
    return (
        devices.groupby("status")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def warranty_exposure(devices: pd.DataFrame) -> pd.DataFrame:
    """Identify warranty status across device types."""
    return (
        devices.groupby("device_type")
        .agg(
            total=("asset_id", "count"),
            in_warranty=("warranty_active", "sum"),
        )
        .reset_index()
    )


def refresh_cost_forecast(devices: pd.DataFrame) -> pd.DataFrame:
    """Estimate replacement cost for devices due for refresh."""
    due = devices[devices["refresh_due"]].copy()
    forecast = (
        due.groupby("device_type")
        .agg(
            units_due=("asset_id", "count"),
            unit_cost=("unit_cost", "first"),
        )
        .reset_index()
    )
    forecast["total_cost"] = forecast["units_due"] * forecast["unit_cost"]
    return forecast


def device_age_distribution(devices: pd.DataFrame) -> pd.DataFrame:
    """Bin devices by age bracket for histogram display."""
    bins = [0, 6, 12, 24, 36, 48, 60, 120]
    labels = ["0-6m", "6-12m", "1-2y", "2-3y", "3-4y", "4-5y", "5y+"]
    df = devices.copy()
    df["age_bracket"] = pd.cut(df["age_months"], bins=bins, labels=labels, right=True)
    return df.groupby("age_bracket", observed=True).size().reset_index(name="count")


# ---------------------------------------------------------------------------
# Active Directory / User Provisioning Analytics
# ---------------------------------------------------------------------------


def ad_action_summary(ad_events: pd.DataFrame) -> pd.DataFrame:
    """Count and success rate per AD action type."""
    summary = (
        ad_events.groupby("action")
        .agg(
            total_events=("event_id", "count"),
            success_rate=("success", lambda s: round(s.mean() * 100, 2)),
            avg_completion_min=("completion_minutes", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("total_events", ascending=False)
    )
    return summary


def ad_automation_rate(ad_events: pd.DataFrame) -> pd.DataFrame:
    """Proportion of automated vs manual AD actions."""
    auto = ad_events.groupby("is_automated").size().reset_index(name="count")
    auto["is_automated"] = auto["is_automated"].map(
        {True: "Automated", False: "Manual"}
    )
    auto["pct"] = (auto["count"] / auto["count"].sum() * 100).round(2)
    return auto.rename(columns={"is_automated": "type"})


def ad_monthly_trend(ad_events: pd.DataFrame) -> pd.DataFrame:
    """Monthly volume of AD provisioning events."""
    df = ad_events.copy()
    df["month"] = df["timestamp"].dt.to_period("M").dt.to_timestamp()
    return df.groupby("month").size().reset_index(name="event_count")


def ad_department_activity(ad_events: pd.DataFrame) -> pd.DataFrame:
    """AD events per department."""
    return (
        ad_events.groupby("department")
        .agg(
            event_count=("event_id", "count"),
            avg_completion_min=("completion_minutes", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("event_count", ascending=False)
    )


def ad_failure_analysis(ad_events: pd.DataFrame) -> pd.DataFrame:
    """Breakdown of failed AD actions."""
    failed = ad_events[~ad_events["success"]]
    return (
        failed.groupby("action")
        .size()
        .reset_index(name="failure_count")
        .sort_values("failure_count", ascending=False)
    )


# ---------------------------------------------------------------------------
# KPI Helpers (used by the dashboard header row)
# ---------------------------------------------------------------------------


def compute_kpis(
    tickets: pd.DataFrame,
    devices: pd.DataFrame,
    ad_events: pd.DataFrame,
) -> dict:
    """Return a flat dictionary of top-level KPIs for the dashboard."""
    resolved = tickets.dropna(subset=["resolution_hours"])

    open_tickets = tickets[tickets["status"].isin(["Open", "In Progress"])].shape[0]
    overall_sla = (
        round(resolved["sla_met"].mean() * 100, 1) if len(resolved) > 0 else 0.0
    )
    avg_resolution = round(resolved["resolution_hours"].mean(), 1) if len(resolved) > 0 else 0.0
    devices_due_refresh = int(devices["refresh_due"].sum())
    total_ad_events = len(ad_events)
    ad_success_rate = round(ad_events["success"].mean() * 100, 1) if len(ad_events) > 0 else 0.0

    # Month-over-month ticket delta
    now = tickets["created_at"].max()
    current_month = tickets[
        tickets["created_at"] >= (now - timedelta(days=30))
    ].shape[0]
    prev_month = tickets[
        (tickets["created_at"] >= (now - timedelta(days=60)))
        & (tickets["created_at"] < (now - timedelta(days=30)))
    ].shape[0]
    mom_change = (
        round((current_month - prev_month) / prev_month * 100, 1)
        if prev_month > 0
        else 0.0
    )

    return {
        "total_tickets": len(tickets),
        "open_tickets": open_tickets,
        "overall_sla_pct": overall_sla,
        "avg_resolution_hours": avg_resolution,
        "devices_due_refresh": devices_due_refresh,
        "total_devices": len(devices),
        "total_ad_events": total_ad_events,
        "ad_success_rate": ad_success_rate,
        "mom_ticket_change_pct": mom_change,
        "current_month_tickets": current_month,
    }
