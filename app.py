"""
IT Service Desk Analytics Dashboard
A Streamlit-based POC demonstrating incident analytics, SLA compliance,
device lifecycle tracking, and Active Directory user provisioning metrics
for a financial services environment.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_generator import load_all_data
from analytics import (
    calculate_sla_compliance,
    ticket_volume_trend,
    resolution_time_stats,
    top_incident_subcategories,
    trade_floor_vs_corporate,
    contact_method_breakdown,
    priority_distribution,
    monthly_sla_trend,
    vip_ticket_analysis,
    device_refresh_summary,
    device_status_counts,
    warranty_exposure,
    refresh_cost_forecast,
    device_age_distribution,
    ad_action_summary,
    ad_automation_rate,
    ad_monthly_trend,
    ad_department_activity,
    ad_failure_analysis,
    compute_kpis,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="IT Service Desk Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Brand colour palette (inspired by Macquarie Group)
COLORS = {
    "primary": "#003366",
    "secondary": "#0066CC",
    "accent": "#00A3E0",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "light": "#F8F9FA",
    "dark": "#212529",
}

CHART_PALETTE = [
    "#003366", "#0066CC", "#00A3E0", "#28A745",
    "#FFC107", "#DC3545", "#6F42C1", "#FD7E14",
]


# ---------------------------------------------------------------------------
# Data Loading (cached)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Generating analytics data...")
def get_data():
    return load_all_data(
        ticket_count=5000,
        device_count=1200,
        ad_event_count=3000,
        months=12,
    )


data = get_data()
tickets = data["tickets"]
devices = data["devices"]
ad_events = data["ad_events"]

kpis = compute_kpis(tickets, devices, ad_events)


# ---------------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------------

st.sidebar.title("Filters")
st.sidebar.markdown("---")

# Date range filter
min_date = tickets["created_at"].min().date()
max_date = tickets["created_at"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Location filter
all_locations = sorted(tickets["location"].unique())
selected_locations = st.sidebar.multiselect(
    "Locations",
    options=all_locations,
    default=all_locations,
)

# Support type filter
support_types = st.sidebar.multiselect(
    "Support Type",
    options=["Trade Floor", "Corporate"],
    default=["Trade Floor", "Corporate"],
)

# Priority filter
selected_priorities = st.sidebar.multiselect(
    "Priority",
    options=["Critical", "High", "Medium", "Low"],
    default=["Critical", "High", "Medium", "Low"],
)

# Apply filters
if len(date_range) == 2:
    mask = (
        (tickets["created_at"].dt.date >= date_range[0])
        & (tickets["created_at"].dt.date <= date_range[1])
        & (tickets["location"].isin(selected_locations))
        & (tickets["support_type"].isin(support_types))
        & (tickets["priority"].isin(selected_priorities))
    )
    filtered_tickets = tickets[mask].copy()
else:
    filtered_tickets = tickets.copy()

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Showing **{len(filtered_tickets):,}** of **{len(tickets):,}** tickets"
)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("IT Service Desk Analytics Dashboard")
st.caption(
    "Financial Services IT Operations | Incident Management, SLA Compliance, "
    "Device Lifecycle & Active Directory Analytics"
)

# KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(
    "Total Tickets (12 mo)",
    f"{kpis['total_tickets']:,}",
    f"{kpis['mom_ticket_change_pct']:+.1f}% MoM",
)
col2.metric("Open Tickets", f"{kpis['open_tickets']:,}")
col3.metric("SLA Compliance", f"{kpis['overall_sla_pct']}%")
col4.metric("Avg Resolution", f"{kpis['avg_resolution_hours']} hrs")
col5.metric("Devices Due Refresh", f"{kpis['devices_due_refresh']:,}")

st.markdown("---")


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_incidents, tab_sla, tab_devices, tab_ad = st.tabs(
    [
        "Incident Analytics",
        "SLA Compliance",
        "Device Lifecycle",
        "AD User Analytics",
    ]
)


# ===== TAB 1: Incident Analytics ===========================================
with tab_incidents:
    st.header("Incident Volume & Resolution Analysis")

    # -- Row 1: Volume trend + Priority breakdown ---
    r1c1, r1c2 = st.columns([2, 1])

    with r1c1:
        st.subheader("Weekly Ticket Volume")
        vol = ticket_volume_trend(filtered_tickets, freq="W")
        fig_vol = px.area(
            vol,
            x="period",
            y="ticket_count",
            labels={"period": "Week", "ticket_count": "Tickets"},
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig_vol.update_layout(
            hovermode="x unified",
            margin=dict(l=0, r=0, t=10, b=0),
            height=350,
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with r1c2:
        st.subheader("Priority Distribution")
        pri = priority_distribution(filtered_tickets)
        fig_pri = px.pie(
            pri,
            values="count",
            names="priority",
            color="priority",
            color_discrete_map={
                "Critical": COLORS["danger"],
                "High": COLORS["warning"],
                "Medium": COLORS["secondary"],
                "Low": COLORS["success"],
            },
            hole=0.45,
        )
        fig_pri.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig_pri, use_container_width=True)

    # -- Row 2: Trade Floor vs Corporate + Top subcategories ---
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.subheader("Trade Floor vs Corporate Support")
        tfc = trade_floor_vs_corporate(filtered_tickets)
        fig_tfc = make_subplots(
            rows=1,
            cols=3,
            subplot_titles=["Total Tickets", "Avg Resolution (hrs)", "SLA Compliance (%)"],
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
        )
        for idx, (col_name, title) in enumerate(
            [
                ("total_tickets", "Total Tickets"),
                ("avg_resolution_hours", "Avg Res. (hrs)"),
                ("sla_compliance_pct", "SLA (%)"),
            ],
            start=1,
        ):
            fig_tfc.add_trace(
                go.Bar(
                    x=tfc["support_type"],
                    y=tfc[col_name],
                    marker_color=[COLORS["primary"], COLORS["accent"]],
                    text=tfc[col_name],
                    textposition="auto",
                    showlegend=False,
                ),
                row=1,
                col=idx,
            )
        fig_tfc.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_tfc, use_container_width=True)

    with r2c2:
        st.subheader("Top 10 Incident Subcategories")
        top_sub = top_incident_subcategories(filtered_tickets, top_n=10)
        fig_top = px.bar(
            top_sub,
            x="count",
            y="subcategory",
            orientation="h",
            color="category",
            color_discrete_sequence=CHART_PALETTE,
            labels={"count": "Tickets", "subcategory": ""},
        )
        fig_top.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35),
        )
        st.plotly_chart(fig_top, use_container_width=True)

    # -- Row 3: Resolution Time + Contact Method ---
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.subheader("Resolution Time by Category")
        res_stats = resolution_time_stats(filtered_tickets, group_by="category")
        fig_res = px.bar(
            res_stats,
            x="category",
            y=["mean_hours", "median_hours", "p90_hours"],
            barmode="group",
            labels={"value": "Hours", "category": ""},
            color_discrete_sequence=[COLORS["primary"], COLORS["accent"], COLORS["warning"]],
        )
        fig_res.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                title="",
                orientation="h",
                yanchor="bottom",
                y=-0.35,
            ),
        )
        st.plotly_chart(fig_res, use_container_width=True)

    with r3c2:
        st.subheader("Contact Method Breakdown")
        cm = contact_method_breakdown(filtered_tickets)
        fig_cm = px.bar(
            cm,
            x="contact_method",
            y="count",
            color="contact_method",
            color_discrete_sequence=CHART_PALETTE,
            labels={"count": "Tickets", "contact_method": ""},
        )
        fig_cm.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    # -- Row 4: VIP analysis ---
    st.subheader("VIP vs Standard Requester Handling")
    vip = vip_ticket_analysis(filtered_tickets)
    vc1, vc2, vc3 = st.columns(3)
    for _, row in vip.iterrows():
        col = vc1 if row["requester_type"] == "VIP" else vc2
        col.metric(
            f"{row['requester_type']} Tickets",
            f"{row['ticket_count']:,}",
        )
        col.metric(
            f"{row['requester_type']} Avg Resolution",
            f"{row['avg_resolution_hours']:.1f} hrs",
        )
        col.metric(
            f"{row['requester_type']} SLA Compliance",
            f"{row['sla_compliance_pct']}%",
        )


# ===== TAB 2: SLA Compliance ===============================================
with tab_sla:
    st.header("SLA Compliance Analysis")

    # Monthly trend
    st.subheader("Monthly SLA Compliance Trend")
    sla_trend = monthly_sla_trend(filtered_tickets)
    fig_sla_trend = go.Figure()
    fig_sla_trend.add_trace(
        go.Scatter(
            x=sla_trend["month"],
            y=sla_trend["compliance_pct"],
            mode="lines+markers",
            name="SLA Compliance %",
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=8),
        )
    )
    fig_sla_trend.add_hline(
        y=95,
        line_dash="dash",
        line_color=COLORS["danger"],
        annotation_text="95% Target",
        annotation_position="top left",
    )
    fig_sla_trend.update_layout(
        yaxis=dict(title="Compliance %", range=[60, 100]),
        xaxis=dict(title="Month"),
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_sla_trend, use_container_width=True)

    # SLA by priority + by category
    sc1, sc2 = st.columns(2)

    with sc1:
        st.subheader("SLA Compliance by Priority")
        sla_pri = calculate_sla_compliance(filtered_tickets, group_by="priority")
        fig_sla_pri = px.bar(
            sla_pri,
            x="priority",
            y="compliance_pct",
            color="priority",
            text="compliance_pct",
            color_discrete_map={
                "Critical": COLORS["danger"],
                "High": COLORS["warning"],
                "Medium": COLORS["secondary"],
                "Low": COLORS["success"],
            },
            labels={"compliance_pct": "Compliance %", "priority": ""},
        )
        fig_sla_pri.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_sla_pri.add_hline(y=95, line_dash="dash", line_color=COLORS["danger"])
        fig_sla_pri.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            yaxis=dict(range=[0, 105]),
        )
        st.plotly_chart(fig_sla_pri, use_container_width=True)

    with sc2:
        st.subheader("SLA Compliance by Category")
        sla_cat = calculate_sla_compliance(filtered_tickets, group_by="category")
        fig_sla_cat = px.bar(
            sla_cat,
            x="compliance_pct",
            y="category",
            orientation="h",
            text="compliance_pct",
            color_discrete_sequence=[COLORS["primary"]],
            labels={"compliance_pct": "Compliance %", "category": ""},
        )
        fig_sla_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_sla_cat.add_vline(x=95, line_dash="dash", line_color=COLORS["danger"])
        fig_sla_cat.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(range=[0, 105]),
        )
        st.plotly_chart(fig_sla_cat, use_container_width=True)

    # SLA by location
    st.subheader("SLA Compliance by Location")
    sla_loc = calculate_sla_compliance(filtered_tickets, group_by="location")
    fig_sla_loc = px.bar(
        sla_loc,
        x="location",
        y="compliance_pct",
        text="compliance_pct",
        color="compliance_pct",
        color_continuous_scale=["#DC3545", "#FFC107", "#28A745"],
        labels={"compliance_pct": "Compliance %", "location": ""},
    )
    fig_sla_loc.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_sla_loc.add_hline(y=95, line_dash="dash", line_color=COLORS["danger"])
    fig_sla_loc.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(range=[0, 105]),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_sla_loc, use_container_width=True)

    # SLA detail table
    with st.expander("Detailed SLA Compliance Table"):
        sla_detail = calculate_sla_compliance(filtered_tickets, group_by="category")
        st.dataframe(
            sla_detail.style.format(
                {"compliance_pct": "{:.1f}%", "sla_met_count": "{:,.0f}", "total_tickets": "{:,.0f}"}
            ),
            use_container_width=True,
        )


# ===== TAB 3: Device Lifecycle ==============================================
with tab_devices:
    st.header("Device Lifecycle & Refresh Tracking")

    # KPI row
    dc1, dc2, dc3, dc4 = st.columns(4)
    dc1.metric("Total Devices", f"{len(devices):,}")
    dc2.metric("Refresh Due", f"{int(devices['refresh_due'].sum()):,}")
    dc3.metric("In Warranty", f"{int(devices['warranty_active'].sum()):,}")
    dc4.metric(
        "Active Devices",
        f"{len(devices[devices['status'] == 'Active']):,}",
    )

    # Refresh summary + Status pie
    d1, d2 = st.columns([2, 1])

    with d1:
        st.subheader("Device Refresh Status by Type")
        refresh = device_refresh_summary(devices)
        fig_refresh = px.bar(
            refresh,
            x="device_type",
            y=["total_devices", "refresh_due_count"],
            barmode="group",
            labels={"value": "Count", "device_type": ""},
            color_discrete_sequence=[COLORS["primary"], COLORS["danger"]],
        )
        fig_refresh.update_layout(
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(title="", orientation="h", yanchor="bottom", y=-0.3),
            xaxis_tickangle=-25,
        )
        st.plotly_chart(fig_refresh, use_container_width=True)

    with d2:
        st.subheader("Device Status")
        ds = device_status_counts(devices)
        fig_ds = px.pie(
            ds,
            values="count",
            names="status",
            color_discrete_sequence=CHART_PALETTE,
            hole=0.45,
        )
        fig_ds.update_layout(
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig_ds, use_container_width=True)

    # Age distribution + Warranty
    d3, d4 = st.columns(2)

    with d3:
        st.subheader("Device Age Distribution")
        age_dist = device_age_distribution(devices)
        fig_age = px.bar(
            age_dist,
            x="age_bracket",
            y="count",
            color_discrete_sequence=[COLORS["secondary"]],
            labels={"count": "Devices", "age_bracket": "Age"},
        )
        fig_age.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with d4:
        st.subheader("Warranty Coverage by Device Type")
        warr = warranty_exposure(devices)
        warr["out_of_warranty"] = warr["total"] - warr["in_warranty"]
        fig_warr = px.bar(
            warr,
            x="device_type",
            y=["in_warranty", "out_of_warranty"],
            barmode="stack",
            color_discrete_sequence=[COLORS["success"], COLORS["danger"]],
            labels={"value": "Devices", "device_type": ""},
        )
        fig_warr.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(title="", orientation="h", yanchor="bottom", y=-0.35),
            xaxis_tickangle=-25,
        )
        st.plotly_chart(fig_warr, use_container_width=True)

    # Cost forecast
    st.subheader("Refresh Cost Forecast")
    cost_fc = refresh_cost_forecast(devices)
    if not cost_fc.empty:
        total_cost = cost_fc["total_cost"].sum()
        st.info(f"Estimated total refresh cost: **${total_cost:,.0f}**")
        fig_cost = px.bar(
            cost_fc,
            x="device_type",
            y="total_cost",
            text="units_due",
            color_discrete_sequence=[COLORS["warning"]],
            labels={"total_cost": "Estimated Cost ($)", "device_type": ""},
        )
        fig_cost.update_traces(
            texttemplate="%{text} units", textposition="outside"
        )
        fig_cost.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_cost, use_container_width=True)
    else:
        st.success("No devices currently due for refresh.")

    # Inventory table
    with st.expander("Device Inventory Detail"):
        display_cols = [
            "asset_id",
            "device_type",
            "manufacturer",
            "status",
            "age_months",
            "refresh_due",
            "warranty_active",
            "location",
            "assigned_user",
        ]
        st.dataframe(
            devices[display_cols].sort_values("age_months", ascending=False),
            use_container_width=True,
            height=400,
        )


# ===== TAB 4: AD User Analytics ============================================
with tab_ad:
    st.header("Active Directory & User Provisioning Analytics")

    # KPI row
    ac1, ac2, ac3, ac4 = st.columns(4)
    ac1.metric("Total AD Events", f"{len(ad_events):,}")
    ac2.metric("Success Rate", f"{kpis['ad_success_rate']}%")
    auto_rate = ad_automation_rate(ad_events)
    auto_pct = auto_rate.loc[auto_rate["type"] == "Automated", "pct"].values
    ac3.metric("Automation Rate", f"{auto_pct[0] if len(auto_pct) > 0 else 0}%")
    ac4.metric(
        "Failed Events",
        f"{len(ad_events[~ad_events['success']]):,}",
    )

    # Monthly trend + Automation pie
    a1, a2 = st.columns([2, 1])

    with a1:
        st.subheader("Monthly AD Provisioning Volume")
        ad_trend = ad_monthly_trend(ad_events)
        fig_ad_trend = px.area(
            ad_trend,
            x="month",
            y="event_count",
            labels={"month": "Month", "event_count": "Events"},
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig_ad_trend.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            hovermode="x unified",
        )
        st.plotly_chart(fig_ad_trend, use_container_width=True)

    with a2:
        st.subheader("Automated vs Manual")
        fig_auto = px.pie(
            auto_rate,
            values="count",
            names="type",
            color="type",
            color_discrete_map={
                "Automated": COLORS["success"],
                "Manual": COLORS["secondary"],
            },
            hole=0.45,
        )
        fig_auto.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig_auto, use_container_width=True)

    # Action summary + Department
    a3, a4 = st.columns(2)

    with a3:
        st.subheader("AD Actions Summary")
        ad_summary = ad_action_summary(ad_events)
        fig_ad_sum = px.bar(
            ad_summary,
            x="total_events",
            y="action",
            orientation="h",
            color="success_rate",
            color_continuous_scale=["#DC3545", "#FFC107", "#28A745"],
            labels={
                "total_events": "Events",
                "action": "",
                "success_rate": "Success %",
            },
        )
        fig_ad_sum.update_layout(
            height=420,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_ad_sum, use_container_width=True)

    with a4:
        st.subheader("AD Activity by Department")
        dept = ad_department_activity(ad_events).head(10)
        fig_dept = px.bar(
            dept,
            x="event_count",
            y="department",
            orientation="h",
            color_discrete_sequence=[COLORS["accent"]],
            labels={"event_count": "Events", "department": ""},
        )
        fig_dept.update_layout(
            height=420,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    # Failure analysis
    st.subheader("Failed AD Actions Analysis")
    failures = ad_failure_analysis(ad_events)
    if not failures.empty:
        fc1, fc2 = st.columns([1, 2])
        with fc1:
            st.dataframe(failures, use_container_width=True, height=300)
        with fc2:
            fig_fail = px.bar(
                failures,
                x="action",
                y="failure_count",
                color_discrete_sequence=[COLORS["danger"]],
                labels={"failure_count": "Failures", "action": ""},
            )
            fig_fail.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis_tickangle=-30,
            )
            st.plotly_chart(fig_fail, use_container_width=True)
    else:
        st.success("No failed AD actions in the selected period.")

    # Completion time distribution
    st.subheader("Task Completion Time: Automated vs Manual")
    fig_box = px.box(
        ad_events,
        x="is_automated",
        y="completion_minutes",
        color="is_automated",
        labels={
            "is_automated": "Execution Type",
            "completion_minutes": "Completion Time (min)",
        },
        color_discrete_map={True: COLORS["success"], False: COLORS["secondary"]},
        category_orders={"is_automated": [True, False]},
    )
    fig_box.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        xaxis=dict(
            tickvals=[True, False],
            ticktext=["Automated", "Manual"],
        ),
    )
    st.plotly_chart(fig_box, use_container_width=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.caption(
    "IT Service Desk Analytics Dashboard | POC built with Streamlit, Pandas & Plotly | "
    "Data is synthetically generated for demonstration purposes."
)
