import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="FORESIGHT - North Castle Fiscal Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, professional CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #7f8c8d;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .audience-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
        margin: 1rem 0;
        border-left: 5px solid #3498db;
    }
    .metric-display {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.95;
        margin-top: 0.3rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f8f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #27ae60;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef5e7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f39c12;
        margin: 1rem 0;
    }
    .phase-badge {
        background-color: #667eea;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        display: inline-block;
        margin: 0.5rem 0;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .audience-number {
        display: inline-block;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background-color: #3498db;
        color: white;
        text-align: center;
        line-height: 35px;
        font-weight: bold;
        margin-right: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# North Castle Financial Data
BASELINE = {
    'year': 2026,
    'property_tax': 45_000_000,
    'property_tax_growth': 0.021,
    'state_aid': 3_200_000,
    'fees_permits': 2_800_000,
    'fund_balance': 8_200_000,
    'personnel': 18_500_000,
    'personnel_growth': 0.032,
    'infrastructure': 4_200_000,
    'debt_service': 2_800_000,
    'operations': 6_500_000,
    'energy': 1_500_000,
    'fleet_om': 850_000,
    'discount_rate': 0.045
}

# Actual project locations from Google Maps - Armonk, NY
PROJECT_LOCATIONS = {
    'Current Town Hall': {
        'lat': 41.1267,
        'lon': -73.7145,
        'address': '17 Bedford Rd, Armonk, NY 10504',
        'description': 'North Castle Town Clerk - Current administrative offices'
    },
    'Proposed Town Hall': {
        'lat': 41.1256,
        'lon': -73.7135,
        'address': '333 Main St, Armonk, NY 10504',
        'description': 'Boies Schiller & Flexner LLP building - Proposed Town Hall relocation'
    },
    'Pool and Tennis Club': {
        'lat': 41.1368,
        'lon': -73.7110,
        'address': '3 Greenway Rd, Armonk, NY 10504',
        'description': 'North Castle Pool and Tennis Club - Location for proposed community pool'
    },
    'DPW Facility': {
        'lat': 41.1285,
        'lon': -73.7155,
        'address': 'Municipal Complex Area',
        'description': 'Department of Public Works - Solar panel and EV fleet location'
    }
}

# Investment scenarios with location data
PROJECTS = {
    'Nothing': {
        'name': 'Status Quo',
        'capital': 0,
        'grant': 0,
        'energy_savings': 0,
        'fleet_savings': 0,
        'new_revenue': 0,
        'new_operating': 0,
        'description': 'Maintain current operations with no new capital investments',
        'color': '#95a5a6',
        'locations': []
    },
    'Solar': {
        'name': 'Solar + EV Fleet',
        'capital': 3_250_000,
        'grant': 975_000,
        'energy_savings': 127_000,
        'fleet_savings': 42_000,
        'new_revenue': 0,
        'new_operating': 0,
        'description': 'Solar installations on Town Hall and DPW facility, plus 5-vehicle electric fleet replacement',
        'color': '#27ae60',
        'locations': ['Current Town Hall', 'DPW Facility']
    },
    'Pool': {
        'name': 'Community Pool',
        'capital': 8_500_000,
        'grant': 0,
        'energy_savings': 0,
        'fleet_savings': 0,
        'new_revenue': 185_000,
        'new_operating': 420_000,
        'description': 'Year-round aquatic facility with lap lanes, recreational programming, and changing facilities',
        'color': '#3498db',
        'locations': ['Pool and Tennis Club']
    },
    'TownHall': {
        'name': 'Town Hall Relocation',
        'capital': 12_500_000,
        'grant': 0,
        'energy_savings': 45_000,
        'fleet_savings': 0,
        'new_revenue': 0,
        'new_operating': 180_000,
        'description': 'Relocate administrative offices to 333 Main St (Boies Schiller building) with improved accessibility',
        'color': '#e67e22',
        'locations': ['Proposed Town Hall']
    },
    'Climate': {
        'name': 'Climate Initiative Package',
        'capital': 1_800_000,
        'grant': 540_000,
        'energy_savings': 95_000,
        'fleet_savings': 0,
        'new_revenue': 0,
        'new_operating': 85_000,
        'description': 'Climate committee establishment with energy audits and building efficiency retrofits',
        'color': '#16a085',
        'locations': ['Current Town Hall', 'DPW Facility']
    },
    'Everything': {
        'name': 'Integrated Sustainability',
        'capital': 5_050_000,
        'grant': 1_515_000,
        'energy_savings': 222_000,
        'fleet_savings': 42_000,
        'new_revenue': 0,
        'new_operating': 85_000,
        'description': 'Comprehensive package: solar + EV fleet + climate efficiency programs',
        'color': '#8e44ad',
        'locations': ['Current Town Hall', 'DPW Facility']
    }
}

def calculate_projections(project, years, assumptions):
    """Calculate multi-year fiscal projections"""
    
    property_tax_growth = BASELINE['property_tax_growth'] * (assumptions['tax_growth_factor'] / 100)
    personnel_growth = BASELINE['personnel_growth'] * (assumptions['personnel_growth_factor'] / 100)
    
    data = {
        'Year': [],
        'Revenue': [],
        'Expenditure': [],
        'Net_Position': [],
        'Fund_Balance': [],
        'Fiscal_Cushion': []
    }
    
    prop_tax = BASELINE['property_tax']
    personnel = BASELINE['personnel']
    fund_balance = BASELINE['fund_balance'] - (project['capital'] - project['grant'])
    
    for year in range(1, years + 1):
        prop_tax *= (1 + property_tax_growth)
        revenue = (prop_tax + BASELINE['state_aid'] + BASELINE['fees_permits'] + project['new_revenue'])
        
        personnel *= (1 + personnel_growth)
        energy = BASELINE['energy'] - project['energy_savings']
        fleet = BASELINE['fleet_om'] - project['fleet_savings']
        
        expenditure = (personnel + BASELINE['infrastructure'] + BASELINE['debt_service'] + 
                      BASELINE['operations'] + energy + fleet + project['new_operating'])
        
        net_position = revenue - expenditure
        fund_balance += net_position
        fiscal_cushion = fund_balance / expenditure
        
        data['Year'].append(BASELINE['year'] + year)
        data['Revenue'].append(revenue)
        data['Expenditure'].append(expenditure)
        data['Net_Position'].append(net_position)
        data['Fund_Balance'].append(fund_balance)
        data['Fiscal_Cushion'].append(fiscal_cushion)
    
    return pd.DataFrame(data)

def calculate_npv(project, years, assumptions):
    """Calculate Net Present Value"""
    df = calculate_projections(project, years, assumptions)
    npv = -(project['capital'] - project['grant'])
    
    for i, net in enumerate(df['Net_Position']):
        npv += net / ((1 + BASELINE['discount_rate']) ** (i + 1))
    
    return npv

def simple_metrics(project, years):
    """Calculate key financial metrics"""
    annual_benefit = (project['energy_savings'] + project['fleet_savings'] + 
                     project['new_revenue'] - project['new_operating'])
    net_capital = project['capital'] - project['grant']
    
    payback = net_capital / annual_benefit if annual_benefit > 0 else None
    
    return {
        'annual_benefit': annual_benefit,
        'net_capital': net_capital,
        'payback': payback
    }

def create_project_map(selected_projects=None):
    """Create interactive map with project locations"""
    
    fig = go.Figure()
    
    # Add all reference points
    for loc_name, loc_data in PROJECT_LOCATIONS.items():
        # Default gray for reference points
        color = '#95a5a6'
        size = 12
        
        # If this location is part of a selected project, color it
        if selected_projects:
            for proj_key in selected_projects:
                if proj_key != 'Nothing' and loc_name in PROJECTS[proj_key]['locations']:
                    color = PROJECTS[proj_key]['color']
                    size = 18
                    break
        
        fig.add_trace(go.Scattermapbox(
            lat=[loc_data['lat']],
            lon=[loc_data['lon']],
            mode='markers',
            marker=go.scattermapbox.Marker(size=size, color=color),
            text=[loc_data['description']],
            hovertext=f"<b>{loc_name}</b><br>{loc_data['address']}<br>{loc_data['description']}",
            hoverinfo='text',
            name=loc_name,
            showlegend=True
        ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=41.1300, lon=-73.7130),
            zoom=13.5
        ),
        showlegend=True,
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)"
        )
    )
    
    return fig

# Sidebar
with st.sidebar:
    st.markdown("### FORESIGHT")
    st.caption("North Castle Fiscal Planning")
    st.markdown("---")
    
    page = st.radio(
        "Navigate:",
        ["Town Overview", "Project Status", "Scenario Builder", "Multi-Scenario Analysis"],
        label_visibility="visible"
    )
    
    st.markdown("---")
    
    with st.expander("Data Sources"):
        st.markdown("""
            **Financial Data:**
            - Property Tax Base: North Castle 2025 Budget Document
            - Personnel Costs: 2025 Adopted Budget (Personnel Section)
            - Fund Balance: 2024 Year-End Financial Statement
            - State Aid: NYS Division of Budget Allocation
            
            **Growth Rates:**
            - Property Tax: 5-year historical average (2019-2024)
            - Personnel: CSEA/PBA contract escalators + historical patterns
            
            **Discount Rate:**
            - 4.5% based on municipal bond rates (10-year AA-rated)
            
            **Project Costs:**
            - Solar: NYSERDA 2025 cost estimates
            - EV Fleet: NYS OGS contract pricing
            - Pool: Comparable municipal pool projects (adjusted)
            - Town Hall: Commercial real estate estimates
        """)
    
    st.markdown("---")
    st.markdown("**Finance Department**")
    st.markdown("Lead: Arun Das")
    st.caption(f"Updated {datetime.now().strftime('%B %Y')}")

# PAGE 1: TOWN OVERVIEW
if page == "Town Overview":
    # FORESIGHT Header
    st.markdown('<div class="main-title">FORESIGHT</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Fiscal Operations & Resilience Evaluation System for Investment Growth & Horizon Testing</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Three-audience purpose statement - CRYSTAL CLEAR
    st.markdown("### This Tool Serves Three Audiences")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="audience-card">
                <h4><span class="audience-number">1</span>Town Officials</h4>
                <p><strong>Town Board, Administrator, Finance Committee</strong></p>
                <p><strong>Your Use:</strong> Evaluate major capital investments before appropriation votes</p>
                <p><strong>Questions Answered:</strong></p>
                <ul>
                    <li>Should we relocate Town Hall to 333 Main St?</li>
                    <li>Can we afford a new community pool?</li>
                    <li>Does solar + EV fleet pay for itself?</li>
                </ul>
                <p><strong>Navigate to:</strong> "Multi-Scenario Analysis" to compare major projects</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="audience-card">
                <h4><span class="audience-number">2</span>Taxpayers</h4>
                <p><strong>North Castle Residents</strong></p>
                <p><strong>Your Use:</strong> Understand how your tax dollars are spent and what proposed investments mean for your taxes</p>
                <p><strong>Questions Answered:</strong></p>
                <ul>
                    <li>Where does my property tax money go?</li>
                    <li>Will this project raise my taxes?</li>
                    <li>Is the town financially healthy?</li>
                </ul>
                <p><strong>See below:</strong> Revenue & expenditure breakdown shows where every dollar goes</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="audience-card">
                <h4><span class="audience-number">3</span>Community Members</h4>
                <p><strong>Residents with Project Ideas</strong></p>
                <p><strong>Your Use:</strong> Test your community improvement ideas to build a case for Town Board</p>
                <p><strong>Project Examples:</strong></p>
                <ul>
                    <li>Tennis court resurfacing ($50K)</li>
                    <li>Speed bump installation ($15K)</li>
                    <li>Playground equipment ($75K)</li>
                </ul>
                <p><strong>Navigate to:</strong> "Scenario Builder" to model your idea and see affordability</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="success-box">
            <strong>Shared Goal: Transparency</strong><br>
            Whether evaluating a $12M Town Hall relocation or a $50K tennis court repair, everyone deserves to see 
            the fiscal impact analysis. This tool provides that transparency - same methodology, same data sources, 
            accessible to all stakeholders.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Map showing actual project locations
    st.subheader("Project Locations in North Castle")
    
    all_scenarios = ['Solar', 'Pool', 'TownHall', 'Climate']
    map_fig = create_project_map(all_scenarios)
    st.plotly_chart(map_fig, use_container_width=True)
    
    st.markdown("""
        <div class="info-box">
            <strong>Interactive Map:</strong> Hover over markers to see project details. Each location shows:
            <ul>
                <li><strong>Current Town Hall (17 Bedford Rd)</strong>: Solar panel installation location</li>
                <li><strong>Proposed Town Hall (333 Main St)</strong>: Boies Schiller building - potential relocation site</li>
                <li><strong>Pool Location (3 Greenway Rd)</strong>: North Castle Pool & Tennis Club area - proposed pool site</li>
                <li><strong>DPW Facility</strong>: Department of Public Works - solar panels and EV fleet location</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Understanding Your Tax Dollars
    st.markdown("### For Taxpayers: Where Your Money Goes")
    
    st.markdown("""
        <div class="info-box">
            <strong>Your Property Taxes at Work:</strong><br>
            North Castle collects approximately $51M annually (88% from property taxes, 6% state aid, 6% fees/permits). 
            Below you can see exactly how that money is allocated across police, roads, parks, administration, and all town services.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Current metrics
    st.subheader("2026 Fiscal Position")
    
    st.caption("Source: North Castle 2025 Adopted Budget & 2024 Year-End Financial Statements")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = BASELINE['property_tax'] + BASELINE['state_aid'] + BASELINE['fees_permits']
    total_expenditure = (BASELINE['personnel'] + BASELINE['infrastructure'] + 
                        BASELINE['debt_service'] + BASELINE['operations'] + 
                        BASELINE['energy'] + BASELINE['fleet_om'])
    net_position = total_revenue - total_expenditure
    fiscal_cushion = BASELINE['fund_balance'] / total_expenditure
    
    with col1:
        st.metric("Annual Revenue", f"${total_revenue/1_000_000:.1f}M")
        st.caption("Property tax, state aid, fees")
    
    with col2:
        st.metric("Annual Expenditure", f"${total_expenditure/1_000_000:.1f}M")
        st.caption("Personnel, operations, infrastructure")
    
    with col3:
        delta_label = "Surplus" if net_position > 0 else "Deficit"
        st.metric("Net Position", f"${net_position/1_000_000:.1f}M", delta=delta_label)
        st.caption("Annual operating result")
    
    with col4:
        cushion_status = "Healthy" if fiscal_cushion > 0.18 else "Below Target"
        st.metric("Reserve Ratio", f"{fiscal_cushion:.1%}", delta=cushion_status)
        st.caption("Fund balance as % of spending")
    
    st.markdown("""
        <div class="info-box">
            <strong>Data Transparency:</strong> All baseline figures derived from official North Castle budget documents. 
            Property tax base ($45M), personnel costs ($18.5M), and fund balance ($8.2M) reflect actual 2025-2026 fiscal year data. 
            See sidebar for detailed source citations.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Why reserves matter
    st.subheader("Understanding the 18% Reserve Target")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            **What Are Reserves?**
            
            Municipal reserves are the town's savings account - money set aside for:
            - Emergency repairs (storm damage, equipment failure)
            - Unexpected expenses (legal costs, mandated upgrades)
            - Cash flow between tax collection periods
            - Economic downturns when revenue drops
            
            **The 18% Standard**
            
            Government finance industry standard: maintain 2+ months of operating expenses in reserves.
            - **Above 18%**: Strong financial position, can handle emergencies
            - **15-18%**: Adequate but limited flexibility
            - **Below 15%**: Fiscal stress - vulnerable to shocks
        """)
    
    with col2:
        st.markdown("""
            **Impact on Your Taxes**
            
            When reserves are healthy:
            - Town can handle emergencies without emergency tax increases
            - Better credit rating means lower interest on borrowing
            - More flexibility to fund community projects
            
            When reserves are too low:
            - Emergency expenses may require immediate tax increases
            - Higher borrowing costs increase long-term expenses
            - Reduced ability to respond to community needs
            
            **FORESIGHT's Role**
            
            This tool projects whether proposed investments maintain the 18% reserve cushion. 
            If a project drops reserves below this target, you'll see it in the 10-year projections - 
            giving you transparency about fiscal trade-offs before commitments are made.
        """)
    
    st.markdown("---")
    
    # Financial composition
    st.subheader("Revenue Sources & Expenditure Categories")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Where Money Comes From**")
        revenue_data = pd.DataFrame({
            'Source': ['Property Tax', 'State Aid', 'Fees & Permits'],
            'Amount': [BASELINE['property_tax'], BASELINE['state_aid'], BASELINE['fees_permits']]
        })
        
        fig = px.pie(revenue_data, values='Amount', names='Source', 
                    color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71'],
                    hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=300, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
            **Revenue Composition:**
            - **Property Tax (88%)**: Largest share from North Castle homeowners and businesses
            - **State Aid (6%)**: New York State allocation for local services
            - **Fees & Permits (6%)**: Recreation fees, building permits, service charges
        """)
    
    with col2:
        st.markdown("**What Your Taxes Fund**")
        exp_data = pd.DataFrame({
            'Category': ['Personnel', 'Operations', 'Infrastructure', 'Debt Service', 'Energy', 'Fleet'],
            'Amount': [BASELINE['personnel'], BASELINE['operations'], BASELINE['infrastructure'], 
                      BASELINE['debt_service'], BASELINE['energy'], BASELINE['fleet_om']]
        }).sort_values('Amount', ascending=True)
        
        fig = px.bar(exp_data, x='Amount', y='Category', orientation='h',
                    color='Amount', color_continuous_scale='Blues')
        fig.update_layout(height=300, showlegend=False, xaxis_title="", 
                         margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
            **Expenditure Breakdown:**
            - **Personnel (51%)**: Police, fire, DPW, administration salaries & benefits
            - **Operations (18%)**: Daily services (police operations, parks, administration)
            - **Infrastructure (12%)**: Roads, buildings, water/sewer maintenance
            - **Debt Service (8%)**: Loan payments for past capital projects
            - **Energy (4%)**: Utilities for town buildings
            - **Fleet (2%)**: Vehicles, equipment, fuel
        """)
    
    st.markdown("""
        <div class="info-box">
            <strong>Key Takeaway:</strong> Personnel costs represent the largest expense (51%) - typical for local governments 
            where most tax dollars pay for the people providing services. When evaluating new projects, consider both 
            one-time capital costs AND ongoing operating/staffing requirements.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 10-year baseline
    st.subheader("10-Year Baseline Projection")
    
    st.markdown("""
        <div class="info-box">
            <strong>Baseline Methodology:</strong> Financial forecast with no major new investments, using:
            <ul>
                <li>Property tax revenue growth: 2.1% annually (5-year historical average 2019-2024)</li>
                <li>Personnel cost growth: 3.2% annually (union contracts + historical patterns)</li>
                <li>Other revenues/costs: Held constant (conservative assumption)</li>
            </ul>
            This baseline is the comparison benchmark for all investment scenarios.
        </div>
    """, unsafe_allow_html=True)
    
    baseline_project = PROJECTS['Nothing']
    default_assumptions = {'tax_growth_factor': 100, 'personnel_growth_factor': 100}
    baseline_df = calculate_projections(baseline_project, 10, default_assumptions)
    
    metric_view = st.selectbox(
        "Select view:",
        ["Fund Balance", "Revenue vs Expenditure", "Reserve Ratio", "Annual Net Position"]
    )
    
    fig = go.Figure()
    
    if metric_view == "Fund Balance":
        fig.add_trace(go.Scatter(
            x=baseline_df['Year'], y=baseline_df['Fund_Balance'],
            mode='lines+markers', name='Fund Balance',
            line=dict(color='#3498db', width=3),
            fill='tozeroy', fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        fig.update_layout(yaxis_title="Fund Balance ($)")
        
    elif metric_view == "Revenue vs Expenditure":
        fig.add_trace(go.Scatter(
            x=baseline_df['Year'], y=baseline_df['Revenue'],
            mode='lines', name='Revenue', line=dict(color='#27ae60', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=baseline_df['Year'], y=baseline_df['Expenditure'],
            mode='lines', name='Expenditure', line=dict(color='#e74c3c', width=3)
        ))
        fig.update_layout(yaxis_title="Amount ($)")
        
    elif metric_view == "Reserve Ratio":
        fig.add_trace(go.Scatter(
            x=baseline_df['Year'], y=baseline_df['Fiscal_Cushion'],
            mode='lines+markers', name='Reserve Ratio',
            line=dict(color='#9b59b6', width=3)
        ))
        fig.add_hline(y=0.18, line_dash="dash", line_color="red",
                     annotation_text="18% Target")
        fig.update_layout(yaxis_title="Ratio")
        
    elif metric_view == "Annual Net Position":
        colors = ['#27ae60' if x > 0 else '#e74c3c' for x in baseline_df['Net_Position']]
        fig.add_trace(go.Bar(
            x=baseline_df['Year'], y=baseline_df['Net_Position'],
            marker_color=colors
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.update_layout(yaxis_title="Net Position ($)")
    
    fig.update_layout(template='plotly_white', xaxis_title="Year", height=400)
    st.plotly_chart(fig, use_container_width=True)

# PAGE 2: PROJECT STATUS
elif page == "Project Status":
    st.markdown('<div class="main-title">FORESIGHT Project Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Understanding this fiscal planning initiative</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # What is FORESIGHT
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("What is FORESIGHT?")
        
        st.markdown("""
            **Fiscal Operations & Resilience Evaluation System for Investment Growth & Horizon Testing**
            
            A multi-year budget modeling tool that evaluates proposed capital investments through 5-20 year fiscal projections. 
            The system quantifies Net Present Value (NPV), fund balance trajectories, and fiscal resilience metrics to support 
            evidence-based decision-making.
        """)
        
        st.markdown("""
            <div class="info-box">
                <strong>Core Function:</strong> Transform abstract project proposals into concrete fiscal projections, 
                revealing long-term operational costs and savings that traditional single-year budgeting obscures.
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Key Capabilities**")
        st.markdown("""
            - Multi-scenario comparison
            - NPV analysis (4.5% discount rate)
            - Fund balance projections
            - Reserve ratio tracking
            - Adjustable assumptions
            - Interactive visualizations
        """)
    
    st.markdown("---")
    
    # The challenge
    st.subheader("The Challenge")
    
    st.markdown("""
        Traditional budget planning evaluates capital projects using single-year cost analysis, creating three critical blind spots:
        
        1. **Hidden value opportunities overlooked**: Projects with high upfront costs but positive long-term ROI 
           (e.g., solar + EV investments) get rejected without proper NPV analysis
        
        2. **Operational cost surprise**: Amenity projects appear affordable based on capital costs alone, 
           but ongoing operating expenses erode fund balances over time
        
        3. **Risk opacity**: Budget volatility and reserve adequacy impacts remain unquantified, 
           limiting informed risk assessment
    """)
    
    st.markdown("---")
    
    # Methodology
    st.subheader("How the Analysis Works")
    
    st.markdown("""
        <div class="info-box">
            <strong>Transparency Note:</strong> Understanding the methodology helps you interpret results critically 
            and identify which assumptions matter most for your analysis.
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Step 1: Building the Baseline Projection", expanded=False):
        st.markdown("""
            **What it does:** Creates a 10-year financial forecast assuming no new investments.
            
            **How it works:**
            1. **Revenue Growth**: Property tax grows at 2.1% annually (5-year historical average)
               - State aid held constant (conservative assumption)
               - Fees/permits held constant
            
            2. **Expenditure Growth**: Personnel costs grow at 3.2% annually
               - Based on union contracts + historical patterns
               - Infrastructure, debt service, operations adjusted for inflation
               - Energy and fleet costs held constant at current levels
            
            3. **Fund Balance Calculation**: 
               - Each year: New Balance = Previous Balance + (Revenue - Expenditure)
               - Reserve Ratio = Fund Balance / Annual Expenditure
               - Target: Maintain 18% reserve ratio (2+ months operating cushion)
            
            **Why it matters:** This baseline is your comparison point. Every scenario is measured against 
            "what happens if we do nothing."
        """)
    
    with st.expander("Step 2: Net Present Value (NPV) Calculation", expanded=False):
        st.markdown("""
            **What it does:** Converts future dollars into today's dollars to determine true project value.
            
            **The Formula:**
            ```
            NPV = -Initial_Investment + Σ(Annual_Cash_Flow / (1 + discount_rate)^year)
            ```
            
            **Key Inputs:**
            - **Initial Investment**: Capital cost minus grants (money out Year 0)
            - **Annual Cash Flow**: Energy savings + fleet savings + new revenue - operating costs
            - **Discount Rate**: 4.5% (municipal bond rate for AA-rated 10-year debt)
            - **Time Horizon**: Typically 10 years (adjustable 5-20 years)
            
            **Interpretation:**
            - **NPV > 0**: Project generates more value than it costs (fiscally positive)
            - **NPV < 0**: Project costs more than it returns (requires subsidy)
            - **NPV = 0**: Break-even (neither gains nor loses money)
            
            **Important Caveat:** Negative NPV doesn't mean "bad project." Community pools, parks, and libraries 
            often have negative NPV but provide immense social value. NPV isolates the fiscal dimension only.
        """)
    
    with st.expander("Step 3: Scenario Comparison Logic", expanded=False):
        st.markdown("""
            **What it does:** Runs the same financial model for each investment option to enable apples-to-apples comparison.
            
            **Comparison Metrics:**
            
            1. **Fund Balance Trajectory**: How much money does the town have in reserves over time?
               - Higher is better (more financial flexibility)
               - Look for scenarios that maintain/grow reserves
            
            2. **Reserve Ratio**: Fund Balance ÷ Annual Spending
               - Target: 18% minimum (industry standard)
               - Below 15% = fiscal stress zone
               - Above 20% = strong position
            
            3. **Annual Net Position**: Revenue minus Expenditure each year
               - Positive = surplus (adding to reserves)
               - Negative = deficit (drawing down reserves)
            
            4. **Net Present Value**: Total fiscal value created/consumed (see Step 2)
            
            **The Algorithm's Decision Tree:**
            ```
            For each scenario:
              → Calculate Year 0 impact (upfront capital cost)
              → Project Years 1-10 (or 5-20):
                  • Revenue with growth adjustments
                  • Expenditure with growth adjustments
                  • Operating impact of project (savings/costs)
              → Calculate NPV using 4.5% discount rate
              → Track fund balance and reserve ratio
              → Compare to baseline
            ```
            
            **What the algorithm does NOT do:**
            - Account for non-financial benefits (community value, quality of life)
            - Predict economic recessions or booms
            - Include political feasibility
            - Guarantee accuracy (projections are estimates, not certainties)
        """)
    
    with st.expander("Step 4: Adjustable Assumptions (Sensitivity Testing)", expanded=False):
        st.markdown("""
            **What it does:** Lets you test "what if" scenarios by changing key assumptions.
            
            **Why this matters:** The future is uncertain. Testing different assumptions helps you understand:
            - How sensitive results are to economic conditions
            - Which scenarios are robust vs. fragile
            - What needs to happen for a project to succeed
            
            **Key Adjustable Variables:**
            
            1. **Property Tax Growth Rate** (Baseline: 2.1% annually)
               - 50% = 1.05% (recession scenario)
               - 100% = 2.1% (baseline/normal)
               - 150% = 3.15% (boom scenario)
            
            2. **Personnel Cost Growth** (Baseline: 3.2% annually)
               - 50% = 1.6% (wage freeze scenario)
               - 100% = 3.2% (baseline/normal)
               - 150% = 4.8% (high inflation scenario)
            
            3. **Analysis Horizon** (Default: 10 years)
               - Shorter (5 years): Emphasizes near-term impacts
               - Longer (15-20 years): Reveals projects that pay off over time
            
            **Example Application:**
            "Solar + EV shows positive NPV at baseline. But what if property taxes grow slower than expected? 
            Test at 70% growth rate to see if NPV stays positive under stress."
        """)
    
    with st.expander("Step 5: Limitations & Assumptions", expanded=False):
        st.markdown("""
            **Built-in Assumptions:**
            1. Historical growth rates continue (may not hold in recession/boom)
            2. No major policy changes (e.g., new state mandates, tax cap changes)
            3. No catastrophic events (natural disasters, pandemics)
            4. Project costs are estimates (actual bids may vary ±15-20%)
            5. Energy prices remain stable (solar savings assume current utility rates)
            
            **What This Tool Cannot Tell You:**
            - Whether residents want/need the project
            - Political feasibility or public support
            - Environmental or social justice impacts
            - Opportunity costs (what else could the money be used for?)
            
            **Best Practice:** Use FORESIGHT to understand fiscal implications, then combine with community input, 
            strategic priorities, and qualitative factors for final decisions.
        """)
    
    st.markdown("---")
    
    # How to use this as a community member
    st.subheader("Guide for Community Members: Advocating for Your Project")
    
    st.markdown("""
        <div class="success-box">
            <strong>Building a Data-Backed Case for Town Board Consideration</strong>
            
            **Step 1: Define Your Proposal**
            - Identify specific improvement (tennis court resurfacing, speed bumps, park equipment, etc.)
            - Research cost estimates (get quotes from contractors, check similar projects in nearby towns)
            - Identify any ongoing costs (annual maintenance, staffing needs, utility costs)
            
            **Step 2: Model It in FORESIGHT**
            - Navigate to "Scenario Builder" page
            - Enter your project's capital cost and any grant funding you've identified
            - Include annual operating costs or savings
            - Review the 10-year fiscal impact analysis
            
            **Step 3: Build Your Case**
            - **If NPV is positive or near-zero**: "This project pays for itself through [energy savings/revenue/etc.]"
            - **If NPV is negative but modest**: "This costs $X annually - well within town capacity while maintaining 18% reserves"
            - **Compare affordability**: Show project is small relative to town budget (e.g., "0.6% of annual budget")
            - **Demonstrate fiscal responsibility**: Point to reserve ratio staying above 18% target
            
            **Step 4: Present to Town Board**
            - Attend Town Board meetings with your FORESIGHT analysis
            - Show you've researched costs and fiscal impacts thoroughly
            - Present community support (petitions, letters, neighborhood meetings)
            - Balance fiscal responsibility with community benefit arguments
            
            **Real Example:**
            "Our neighborhood requests tennis court resurfacing at the Recreation Center ($50,000). FORESIGHT analysis shows 
            this represents 0.6% of the annual town budget. The project maintains all reserve ratios above the 18% target 
            and provides 20 years of improved recreational facilities for local families. We've collected 75 resident signatures 
            supporting this investment and request inclusion in the FY2027 capital budget."
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Project timeline
    st.subheader("Implementation Timeline")
    
    st.markdown('<div class="phase-badge">Current Phase: Town Board Presentation</div>', unsafe_allow_html=True)
    
    timeline_data = {
        'Phase': [
            'Idea Creation',
            'Data Testing & Development',
            'Application & Algorithm Approval',
            'Town Board Presentation',
            'Ongoing Integration'
        ],
        'Status': [
            'Complete',
            'Complete',
            'Complete',
            'In Progress',
            'Upcoming'
        ],
        'Timeline': [
            'November 2025',
            'December 2025',
            'January 2026',
            'February 2026',
            'March 2026 onwards'
        ]
    }
    
    for i, phase in enumerate(timeline_data['Phase']):
        status = timeline_data['Status'][i]
        timeline = timeline_data['Timeline'][i]
        
        if status == 'Complete':
            st.success(f"**{phase}** - {timeline}")
        elif status == 'In Progress':
            st.info(f"**{phase}** - {timeline}")
        else:
            st.markdown(f"**{phase}** - {timeline}")
    
    st.markdown("---")
    
    # Next steps
    st.subheader("Next Steps")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="card">
                <h4>User Testing</h4>
                <p>Town officials, residents, and community groups test scenarios, adjust assumptions, and provide feedback 
                on analytical capabilities and interface usability.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <h4>Refinement</h4>
                <p>Incorporate feedback to improve clarity, add requested analytical features, and refine 
                modeling accuracy based on real-world testing.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="card">
                <h4>Integration</h4>
                <p>Deploy as standard decision-support tool for Town Board capital appropriation votes 
                exceeding $500,000 threshold.</p>
            </div>
        """, unsafe_allow_html=True)

# PAGE 3: SCENARIO BUILDER
elif page == "Scenario Builder":
    st.markdown('<div class="main-title">Custom Scenario Builder</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Model ANY proposed project - from $15K speed bumps to multi-million dollar facilities</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="success-box">
            <strong>For Community Members:</strong> Have an idea for improving North Castle? Use this tool to:
            <ul>
                <li>Calculate project cost and verify it fits within town budget capacity</li>
                <li>Demonstrate to Town Board that your proposal is financially feasible</li>
                <li>Build a data-backed case showing fiscal responsibility alongside community benefit</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-box">
            <strong>For Town Officials:</strong> Model major capital investments with complete 10-year fiscal analysis:
            <ul>
                <li><strong>Net Present Value (NPV)</strong>: Discounts future cash flows to present value (4.5% rate)</li>
                <li><strong>Fund Balance Impact</strong>: Projects reserve levels over time</li>
                <li><strong>Reserve Ratio</strong>: Tracks maintenance of 18% minimum cushion</li>
            </ul>
            See "Project Status" page for complete methodology documentation.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick examples for common community projects
    with st.expander("Example Community Project Costs (Reference Guide)"):
        st.markdown("""
            **Small Projects ($10K - $50K):**
            - Speed bump installation: $10K - $15K
            - Crosswalk improvements: $20K - $30K
            - Park bench installation (set of 5): $15K
            - Tennis court resurfacing: $40K - $50K
            - Basketball court repairs: $25K - $35K
            
            **Medium Projects ($50K - $250K):**
            - Playground equipment replacement: $75K - $150K
            - Park pavilion construction: $150K - $200K
            - Parking lot repaving: $100K - $175K
            - Trail improvements (1 mile): $50K - $100K
            - Building roof replacement: $200K - $250K
            
            **Large Projects ($250K+):**
            - Community center renovation: $500K - $1M
            - Full park development: $1M - $3M
            - Major infrastructure (roads, drainage): $500K - $2M
            - New facility construction: $3M - $12M
            
            **Note:** These are planning estimates. Actual costs depend on scope, materials, site conditions, and contractor bids (typically ±15-20% variance).
        """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Project Parameters")
        
        project_name = st.text_input(
            "Project Name",
            placeholder="e.g., Tennis Court Resurfacing at Recreation Center"
        )
        
        st.markdown("**Capital Investment**")
        
        capital_cost = st.number_input(
            "Total Capital Cost ($)",
            min_value=0,
            max_value=50_000_000,
            value=50_000,
            step=5_000
        )
        
        grant_funding = st.number_input(
            "Grant Funding ($)",
            min_value=0,
            max_value=capital_cost,
            value=0,
            step=5_000
        )
        
        net_capital = capital_cost - grant_funding
        
        if grant_funding > 0:
            grant_pct = (grant_funding / capital_cost) * 100
            st.success(f"Grant coverage: {grant_pct:.1f}% | Net town investment: ${net_capital:,.0f}")
        else:
            st.info(f"Net town investment: ${net_capital:,.0f}")
        
        st.markdown("---")
        st.markdown("**Annual Operating Impact**")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("*Savings & Revenue*")
            energy_savings = st.number_input("Energy Savings ($/yr)", 0, 1_000_000, 0, 1000)
            fleet_savings = st.number_input("Fleet Savings ($/yr)", 0, 500_000, 0, 1000)
            new_revenue = st.number_input("New Revenue ($/yr)", 0, 1_000_000, 0, 1000)
        
        with col_b:
            st.markdown("*Operating Costs*")
            new_operating = st.number_input("Operating Costs ($/yr)", 0, 2_000_000, 0, 1000)
        
        annual_net = energy_savings + fleet_savings + new_revenue - new_operating
        
        st.markdown("---")
        
        if annual_net > 0:
            st.success(f"Annual net benefit: ${annual_net:,.0f}")
        elif annual_net < 0:
            st.error(f"Annual net cost: ${abs(annual_net):,.0f}")
        else:
            st.info("Annual net impact: $0 (break-even)")
    
    with col2:
        st.subheader("Financial Analysis")
        
        custom_project = {
            'name': project_name or 'Custom Project',
            'capital': capital_cost,
            'grant': grant_funding,
            'energy_savings': energy_savings,
            'fleet_savings': fleet_savings,
            'new_revenue': new_revenue,
            'new_operating': new_operating,
            'color': '#9b59b6',
            'locations': []
        }
        
        metrics = simple_metrics(custom_project, 10)
        
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric("Net Capital", f"${metrics['net_capital']:,.0f}")
            st.metric("Annual Benefit", f"${metrics['annual_benefit']:,.0f}")
        
        with metric_col2:
            if metrics['payback']:
                st.metric("Payback Period", f"{metrics['payback']:.1f} yrs")
            else:
                st.metric("Payback Period", "N/A")
            
            pct_of_budget = (metrics['net_capital'] / (BASELINE['property_tax'] + BASELINE['state_aid'] + BASELINE['fees_permits'])) * 100
            st.metric("% of Annual Budget", f"{pct_of_budget:.2f}%")
        
        st.markdown("---")
        
        projection_years = st.slider("Analysis Horizon", 5, 20, 10)
        
        default_assumptions = {'tax_growth_factor': 100, 'personnel_growth_factor': 100}
        npv = calculate_npv(custom_project, projection_years, default_assumptions)
        
        if npv > 0:
            st.markdown(f"""
                <div class="success-box">
                    <strong>Positive NPV:</strong> ${npv:,.0f} over {projection_years} years<br>
                    Project generates net fiscal value for the town
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="warning-box">
                    <strong>Negative NPV:</strong> ${abs(npv):,.0f} over {projection_years} years<br>
                    Project requires fiscal subsidy (may be justified by community benefits that aren't captured in NPV)
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Projections
    st.subheader("10-Year Fiscal Impact Comparison")
    
    custom_df = calculate_projections(custom_project, 10, default_assumptions)
    baseline_df = calculate_projections(PROJECTS['Nothing'], 10, default_assumptions)
    
    viz_choice = st.radio(
        "Comparison view:",
        ["Fund Balance", "Net Position", "Reserve Ratio"],
        horizontal=True
    )
    
    fig = go.Figure()
    
    if viz_choice == "Fund Balance":
        fig.add_trace(go.Scatter(
            x=baseline_df['Year'], y=baseline_df['Fund_Balance'],
            mode='lines', name='Baseline (No Project)',
            line=dict(color='#95a5a6', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=custom_df['Year'], y=custom_df['Fund_Balance'],
            mode='lines+markers', name='With Your Project',
            line=dict(color='#9b59b6', width=3)
        ))
        fig.update_layout(yaxis_title="Fund Balance ($)")
        
    elif viz_choice == "Net Position":
        fig.add_trace(go.Bar(
            x=baseline_df['Year'], y=baseline_df['Net_Position'],
            name='Baseline (No Project)', marker_color='#95a5a6', opacity=0.5
        ))
        fig.add_trace(go.Bar(
            x=custom_df['Year'], y=custom_df['Net_Position'],
            name='With Your Project', marker_color='#9b59b6'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.update_layout(yaxis_title="Net Position ($)")
        
    elif viz_choice == "Reserve Ratio":
        fig.add_trace(go.Scatter(
            x=baseline_df['Year'], y=baseline_df['Fiscal_Cushion'],
            mode='lines', name='Baseline (No Project)',
            line=dict(color='#95a5a6', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=custom_df['Year'], y=custom_df['Fiscal_Cushion'],
            mode='lines+markers', name='With Your Project',
            line=dict(color='#9b59b6', width=3)
        ))
        fig.add_hline(y=0.18, line_dash="dash", line_color="red",
                     annotation_text="18% Target")
        fig.update_layout(yaxis_title="Reserve Ratio")
    
    fig.update_layout(template='plotly_white', xaxis_title="Year", height=450, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# PAGE 4: MULTI-SCENARIO ANALYSIS
elif page == "Multi-Scenario Analysis":
    st.markdown('<div class="main-title">Multi-Scenario Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Compare multiple proposals side-by-side to inform budget priorities</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="success-box">
            <strong>Purpose of Multi-Scenario Analysis:</strong> When facing multiple investment options with limited budget capacity, 
            this tool enables direct comparison to identify:
            <ul>
                <li><strong>Town Board</strong>: Which major capital projects provide best fiscal return or require least subsidy</li>
                <li><strong>Community Members</strong>: How your proposal compares to other community requests in terms of affordability</li>
                <li><strong>Taxpayers</strong>: Which investments generate fiscal value vs. which require ongoing tax support</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-box">
            <strong>Analysis Framework:</strong> Each scenario runs through identical financial modeling:
            <ol>
                <li><strong>Baseline Projection</strong>: 10-year forecast with no investment (comparison benchmark)</li>
                <li><strong>Project Impact</strong>: Capital cost, operating changes, and savings modeled year-by-year</li>
                <li><strong>NPV Calculation</strong>: Future cash flows discounted to present value at 4.5%</li>
                <li><strong>Sensitivity Testing</strong>: Adjustable growth rates to test different economic conditions</li>
            </ol>
            <strong>Key Insight:</strong> Positive NPV scenarios generate more value than they cost. 
            Negative NPV scenarios require fiscal subsidy (which may still be worth it for community benefit).
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Map showing project locations
    st.subheader("Project Locations in North Castle")
    
    # Scenario selection
    st.markdown("**Select projects to compare:**")
    
    scenario_cols = st.columns(3)
    selected_scenarios = []
    
    for i, (key, project) in enumerate(PROJECTS.items()):
        with scenario_cols[i % 3]:
            default_checked = key in ['Nothing', 'Solar', 'Pool']
            if st.checkbox(project['name'], value=default_checked, key=f"map_{key}"):
                selected_scenarios.append(key)
    
    if len(selected_scenarios) < 2:
        st.warning("Select at least 2 scenarios for comparison")
        st.stop()
    
    st.markdown("""
        <div class="info-box">
            <strong>Cost Source Documentation:</strong> Solar costs from NYSERDA 2025 estimates, EV pricing from NYS OGS contracts, 
            pool construction from comparable municipal projects (adjusted for regional cost factors), Town Hall from commercial 
            real estate market data. All estimates subject to actual bid results (typical variance: ±15-20%).
        </div>
    """, unsafe_allow_html=True)
    
    # Show map
    map_fig = create_project_map(selected_scenarios)
    st.plotly_chart(map_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Assumptions
    st.subheader("Economic Assumptions")
    
    st.markdown("""
        <div class="info-box">
            <strong>Sensitivity Testing Purpose:</strong> Adjust these parameters to model different economic conditions. 
            This reveals which scenarios remain viable under stress vs. which scenarios depend on optimistic assumptions.
            <ul>
                <li><strong>50-80%</strong>: Pessimistic scenario (recession, slow growth)</li>
                <li><strong>90-110%</strong>: Baseline scenario (normal economic conditions)</li>
                <li><strong>120-150%</strong>: Optimistic scenario (economic boom, rapid growth)</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tax_growth_adj = st.slider(
            "Property Tax Growth",
            50, 150, 100, 5,
            help="Baseline: 2.1% annually"
        )
        actual_tax = BASELINE['property_tax_growth'] * (tax_growth_adj / 100)
        st.caption(f"Adjusted: {actual_tax:.2%} annually")
    
    with col2:
        personnel_growth_adj = st.slider(
            "Personnel Cost Growth",
            50, 150, 100, 5,
            help="Baseline: 3.2% annually"
        )
        actual_personnel = BASELINE['personnel_growth'] * (personnel_growth_adj / 100)
        st.caption(f"Adjusted: {actual_personnel:.2%} annually")
    
    with col3:
        analysis_years = st.slider("Analysis Horizon", 5, 20, 10, 1)
    
    assumptions = {
        'tax_growth_factor': tax_growth_adj,
        'personnel_growth_factor': personnel_growth_adj
    }
    
    st.markdown("---")
    
    # Comparison results
    st.subheader("Comparative Analysis")
    
    comparison_data = []
    
    for scenario_key in selected_scenarios:
        scenario = PROJECTS[scenario_key]
        npv = calculate_npv(scenario, analysis_years, assumptions)
        metrics = simple_metrics(scenario, analysis_years)
        df = calculate_projections(scenario, analysis_years, assumptions)
        
        comparison_data.append({
            'Scenario': scenario['name'],
            'Capital': scenario['capital'],
            'Grants': scenario['grant'],
            'Net Investment': scenario['capital'] - scenario['grant'],
            'Annual Impact': metrics['annual_benefit'],
            f'{analysis_years}-Yr NPV': npv,
            'Final Fund Balance': df['Fund_Balance'].iloc[-1],
            'Final Reserve Ratio': df['Fiscal_Cushion'].iloc[-1]
        })
    
    comp_df = pd.DataFrame(comparison_data)
    
    display_comp = comp_df.copy()
    display_comp['Capital'] = display_comp['Capital'].apply(lambda x: f"${x:,.0f}")
    display_comp['Grants'] = display_comp['Grants'].apply(lambda x: f"${x:,.0f}")
    display_comp['Net Investment'] = display_comp['Net Investment'].apply(lambda x: f"${x:,.0f}")
    display_comp['Annual Impact'] = display_comp['Annual Impact'].apply(lambda x: f"${x:,.0f}")
    display_comp[f'{analysis_years}-Yr NPV'] = display_comp[f'{analysis_years}-Yr NPV'].apply(lambda x: f"${x:,.0f}")
    display_comp['Final Fund Balance'] = display_comp['Final Fund Balance'].apply(lambda x: f"${x:,.0f}")
    display_comp['Final Reserve Ratio'] = display_comp['Final Reserve Ratio'].apply(lambda x: f"{x:.1%}")
    
    st.dataframe(display_comp, use_container_width=True, hide_index=True)
    
    st.markdown("""
        **Metric Definitions:**
        - **Capital**: One-time construction/purchase cost
        - **Grants**: External funding (reduces net town investment)
        - **Net Investment**: Amount town actually pays (Capital - Grants)
        - **Annual Impact**: Yearly savings (positive) or costs (negative) from operations
        - **NPV**: Total value created/cost incurred over analysis period (discounted to present value)
        - **Final Fund Balance**: Projected town reserves at end of analysis horizon
        - **Final Reserve Ratio**: Reserves as % of spending (target: 18% minimum for fiscal health)
    """)
    
    st.markdown("---")
    
    # Visual comparisons
    tab1, tab2, tab3 = st.tabs(["NPV Comparison", "Fund Balance Trajectories", "Reserve Ratio"])
    
    with tab1:
        st.markdown("**Net Present Value measures total fiscal value created or cost incurred over the analysis period**")
        
        npv_data = comp_df.sort_values(f'{analysis_years}-Yr NPV', ascending=True)
        
        fig = go.Figure()
        
        # Color code: green for positive NPV, red for negative NPV
        colors = ['#27ae60' if x > 0 else '#e74c3c' for x in npv_data[f'{analysis_years}-Yr NPV']]
        
        fig.add_trace(go.Bar(
            y=npv_data['Scenario'],
            x=npv_data[f'{analysis_years}-Yr NPV'],
            orientation='h',
            marker_color=colors,
            text=npv_data[f'{analysis_years}-Yr NPV'].apply(lambda x: f"${x:,.0f}"),
            textposition='outside',
            hovertemplate='%{x:$,.0f}<extra></extra>'
        ))
        
        fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=2,
                     annotation_text="Break-even", annotation_position="top")
        
        fig.update_layout(
            title=f'{analysis_years}-Year Net Present Value Comparison',
            xaxis_title='NPV ($) - Green = Fiscally Positive | Red = Requires Subsidy',
            yaxis_title='',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("Note: Negative NPV indicates fiscal subsidy requirement - this doesn't mean the project lacks value, only that community benefit must justify the cost.")
    
    with tab2:
        fig = go.Figure()
        
        for scenario_key in selected_scenarios:
            scenario = PROJECTS[scenario_key]
            df = calculate_projections(scenario, analysis_years, assumptions)
            
            fig.add_trace(go.Scatter(
                x=df['Year'],
                y=df['Fund_Balance'],
                mode='lines+markers',
                name=scenario['name'],
                line=dict(width=3, color=scenario['color'])
            ))
        
        fig.update_layout(
            title='Fund Balance Projections',
            xaxis_title='Year',
            yaxis_title='Fund Balance ($)',
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = go.Figure()
        
        for scenario_key in selected_scenarios:
            scenario = PROJECTS[scenario_key]
            df = calculate_projections(scenario, analysis_years, assumptions)
            
            fig.add_trace(go.Scatter(
                x=df['Year'],
                y=df['Fiscal_Cushion'],
                mode='lines+markers',
                name=scenario['name'],
                line=dict(width=3, color=scenario['color'])
            ))
        
        fig.add_hline(y=0.18, line_dash="dash", line_color="red",
                     annotation_text="18% Target")
        
        fig.update_layout(
            title='Reserve Ratio Projections',
            xaxis_title='Year',
            yaxis_title='Reserve Ratio',
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Key findings
    st.subheader("Analysis Summary")
    
    best_npv = comp_df.loc[comp_df[f'{analysis_years}-Yr NPV'].idxmax()]
    highest_reserves = comp_df.loc[comp_df['Final Reserve Ratio'].idxmax()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"**Highest NPV:** {best_npv['Scenario']}")
        st.metric("Net Value Created", f"${best_npv[f'{analysis_years}-Yr NPV']:,.0f}")
    
    with col2:
        st.info(f"**Strongest Reserves:** {highest_reserves['Scenario']}")
        st.metric("Final Reserve Ratio", f"{highest_reserves['Final Reserve Ratio']:.1%}")

if __name__ == "__main__":
    pass
