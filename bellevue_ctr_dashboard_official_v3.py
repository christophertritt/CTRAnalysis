"""
Bellevue CTR Performance Dashboard - Official Analysis Edition
City of Bellevue Transportation Department
Based on: CTR Data Analysis Guidelines (Updated 3/24/2017)

Implements all required calculations per official protocols:
- Drive-Alone Rate (DAR) with weighted and unweighted metrics
- Non-Drive-Alone Travel (NDAT)
- VMT per Employee tracking
- Mode split analysis
- Response rate compliance
- TMP zone targets
- Historical comparisons (1993, 2007, prior cycle, 5 cycles back)

Data: 1993-2025 CTR Survey Cycles
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import auth  # Authentication module

# Page configuration
st.set_page_config(
    page_title="Bellevue CTR Dashboard - Official Analysis",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #003f87;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #003f87;
    }
    .protocol-note {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data (cached; TTL 1 hour so updated CSV is picked up)


@st.cache_data(ttl=3600)
def load_data():
    """Load the cleaned CTR master dataset with memory-efficient dtypes."""
    df = pd.read_csv(
        'CTR_Master_Dataset_2003-2025_CLEANED.csv',
        low_memory=False
    )
    df['Location'] = df['Location'].astype('category')
    df['Survey_Cycle'] = pd.Categorical(
        df['Survey_Cycle'],
        categories=sorted(df['Survey_Cycle'].unique()),
        ordered=True
    )
    return df


@st.cache_data(ttl=3600)
def compute_cycle_summary(selected_cycles_tuple, location_filter_tuple):
    """
    Compute cycle-level aggregates. Cached by filter state to avoid recomputing
    on every rerun when only metric_type or tab changes.
    Returns (cycle_summary DataFrame, filtered_df).
    """
    df = load_data()
    selected_cycles = list(selected_cycles_tuple)
    location_filter = list(location_filter_tuple)
    filtered_df = df[
        (df['Survey_Cycle'].isin(selected_cycles)) &
        (df['Location'].isin(location_filter))
    ]
    if filtered_df.empty:
        return None, filtered_df

    cycle_summary = filtered_df.groupby('Survey_Cycle', observed=True).agg({
        'Total_Employees': 'sum',
        'VMT_per_Employee': 'mean',
        'Drive_Alone_Rate': 'mean',
        'Organization_Name': 'count',
        'Yearly_Total_VMT': 'sum',
        'Yearly_GHG_Metric_Tons': 'sum',
        'Weekly_Telework_Days': 'sum',
        'Weekly_Bus_Trips': 'sum',
        'Weekly_Train_Trips': 'sum',
        'Weekly_Carpool_Trips': 'sum',
        'Weekly_Vanpool_Trips': 'sum',
        'Weekly_Walk_Trips': 'sum',
        'Weekly_Bike_Trips': 'sum',
        'Weekly_Drive_Alone_Trips': 'sum',
        'Total_Weekly_Trips': 'sum',
        'Surveys_Returned': 'sum',
        'Response_Rate': 'mean'
    }).reset_index()
    cycle_summary.columns = [
        'Survey_Cycle', 'Total_Employees', 'Avg_VMT_per_Employee',
        'Unweighted_DAR', 'Worksites', 'Total_Yearly_VMT',
        'Total_GHG_Emissions', 'Total_Telework_Days', 'Total_Bus_Trips',
        'Total_Train_Trips', 'Total_Carpool_Trips', 'Total_Vanpool_Trips',
        'Total_Walk_Trips', 'Total_Bike_Trips', 'Total_DriveAlone_Trips',
        'Total_Weekly_Trips', 'Total_Surveys_Returned', 'Avg_Response_Rate'
    ]
    cycle_summary['Weighted_DAR'] = (
        cycle_summary['Total_DriveAlone_Trips'] /
        cycle_summary['Total_Weekly_Trips']
    )
    cycle_summary['NDAT'] = 1 - cycle_summary['Weighted_DAR']
    cycle_summary['Transit_Share'] = (
        (cycle_summary['Total_Bus_Trips'] + cycle_summary['Total_Train_Trips'])
        / cycle_summary['Total_Weekly_Trips'] * 100
    )
    cycle_summary['Carpool_Share'] = (
        (cycle_summary['Total_Carpool_Trips'] +
         cycle_summary['Total_Vanpool_Trips']) /
        cycle_summary['Total_Weekly_Trips'] * 100
    )
    cycle_summary['Active_Share'] = (
        (cycle_summary['Total_Walk_Trips'] + cycle_summary['Total_Bike_Trips'])
        / cycle_summary['Total_Weekly_Trips'] * 100
    )
    cycle_summary['Telework_Share'] = (
        cycle_summary['Total_Telework_Days'] /
        cycle_summary['Total_Weekly_Trips'] * 100
    )
    cycle_summary['DriveAlone_Share'] = (
        cycle_summary['Weighted_DAR'] * 100
    )
    cycle_summary['DA_Trips_PerDay'] = (
        cycle_summary['Total_Employees'] * cycle_summary['Weighted_DAR']
    )

    if '1993/1994' in cycle_summary['Survey_Cycle'].values:
        baseline_1993 = cycle_summary[
            cycle_summary['Survey_Cycle'] == '1993/1994'
        ]['Weighted_DAR'].iloc[0]
        cycle_summary['Change_from_1993'] = (
            cycle_summary['Weighted_DAR'] - baseline_1993
        )
    if '2007/2008' in cycle_summary['Survey_Cycle'].values:
        baseline_2007 = cycle_summary[
            cycle_summary['Survey_Cycle'] == '2007/2008'
        ]['Weighted_DAR'].iloc[0]
        cycle_summary['Change_from_2007'] = (
            cycle_summary['Weighted_DAR'] - baseline_2007
        )
    cycle_summary['Change_from_Prior'] = (
        cycle_summary['Weighted_DAR'].diff()
    )
    cycle_summary['Change_from_5Cycles'] = (
        cycle_summary['Weighted_DAR'].diff(5)
    )
    cycle_summary['Overall_Response_Rate'] = (
        cycle_summary['Total_Surveys_Returned'] /
        cycle_summary['Total_Employees']
    )
    return cycle_summary, filtered_df


def calculate_weighted_dar(df_subset):
    """Calculate weighted DAR per PDF protocols (Section I.1)"""
    total_da_trips = df_subset['Weekly_Drive_Alone_Trips'].sum()
    total_trips = df_subset['Total_Weekly_Trips'].sum()
    return total_da_trips / total_trips if total_trips > 0 else 0


def calculate_unweighted_dar(df_subset):
    """Calculate unweighted DAR (simple average) per PDF Section I.7"""
    return df_subset['Drive_Alone_Rate'].mean()


def main():
    # Authentication check - must be logged in to access dashboard
    if not auth.check_password():
        st.stop()  # Stop execution if not authenticated
    
    # Header
    st.markdown(
        '<div class="main-header">'
        '🚌 Bellevue CTR Performance Dashboard'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">'
        'Official Analysis | Transportation Demand Management Program | '
        '1993-2025'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Load data
    try:
        df = load_data()
    except FileNotFoundError:
        st.error(
            "⚠️ Data file not found. Please ensure "
            "CTR_Master_Dataset_2003-2025_CLEANED.csv is in the same "
            "directory."
        )
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Error loading data: {str(e)}")
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Show logout button in sidebar
    auth.show_logout_button()
    
    # Survey cycle filter
    available_cycles = sorted(df['Survey_Cycle'].unique())
    selected_cycles = st.sidebar.multiselect(
        "Survey Cycles",
        options=available_cycles,
        default=available_cycles,
        help="Select one or more survey cycles to analyze"
    )
    
    # Location filter
    location_filter = st.sidebar.multiselect(
        "Location",
        options=['DT', 'ODT'],
        default=['DT', 'ODT'],
        help="DT = Downtown, ODT = Outside Downtown"
    )
    
    # Analysis type selector
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Metric Type")
    metric_type = st.sidebar.radio(
        "DAR Calculation Method",
        options=["Weighted (Official)", "Unweighted (Worksite Average)"],
        help=(
            "Weighted: Employee/trip-weighted (primary metric). "
            "Unweighted: Simple average across worksites."
        )
    )
    
    # Cached cycle summary by filter
    # (avoids recompute on tab/metric_type changes)
    cycle_summary, filtered_df = compute_cycle_summary(
        tuple(selected_cycles), tuple(location_filter)
    )
    if cycle_summary is None or filtered_df.empty:
        st.warning(
            "No data available for selected filters. "
            "Please adjust your selection."
        )
        st.stop()

    # Select which DAR to display based on sidebar selection
    if metric_type == "Weighted (Official)":
        cycle_summary['Display_DAR'] = cycle_summary['Weighted_DAR']
        dar_label = "Weighted DAR"
    else:
        cycle_summary['Display_DAR'] = cycle_summary['Unweighted_DAR']
        dar_label = "Unweighted DAR"
    
    # Key metrics row
    st.markdown("---")
    st.subheader("📊 Key Performance Indicators (Official Metrics)")
    
    # Protocol note
    st.markdown(
        """
    <div class="protocol-note">
    <strong>📋 Analysis Protocol:</strong> Per CTR Data Analysis Guidelines
    (Updated 3/24/2017), metrics are calculated using weighted averages
    (trip/employee-weighted) as the primary official measure. Unweighted
    averages (simple worksite average) available for comparison.
    </div>
    """,
        unsafe_allow_html=True
    )
    
    # Get latest and baseline values
    latest_cycle = cycle_summary.iloc[-1]
    if len(cycle_summary) > 0:
        baseline_cycle = cycle_summary.iloc[0]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        vmt_change = (
            (latest_cycle['Avg_VMT_per_Employee'] -
             baseline_cycle['Avg_VMT_per_Employee']) /
            baseline_cycle['Avg_VMT_per_Employee'] * 100
        )
        st.metric(
            label="VMT per Employee",
            value=f"{latest_cycle['Avg_VMT_per_Employee']:.2f}",
            delta=f"{vmt_change:.1f}% from baseline",
            delta_color="inverse"
        )
    
    with col2:
        dar_change = (
            (latest_cycle['Weighted_DAR'] -
             baseline_cycle['Weighted_DAR']) /
            baseline_cycle['Weighted_DAR'] * 100
        )
        st.metric(
            label=f"{dar_label}",
            value=f"{latest_cycle['Display_DAR']:.1%}",
            delta=f"{dar_change:.1f}% from baseline",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="NDAT Rate",
            value=f"{latest_cycle['NDAT']:.1%}",
            help="Non-Drive-Alone Travel Rate = 1 - DAR"
        )
    
    with col4:
        emp_change = (
            (latest_cycle['Total_Employees'] -
             baseline_cycle['Total_Employees']) /
            baseline_cycle['Total_Employees'] * 100
        )
        st.metric(
            label="Employees Covered",
            value=f"{latest_cycle['Total_Employees']:,.0f}",
            delta=f"{emp_change:.1f}% from baseline"
        )
    
    with col5:
        st.metric(
            label="DA Trips/Day",
            value=f"{latest_cycle['DA_Trips_PerDay']:,.0f}",
            help="Drive-Alone Round Trips per Work Day (for goal setting)"
        )
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        worksite_delta = (latest_cycle['Worksites'] -
                          baseline_cycle['Worksites'])
        st.metric(
            label="Worksites",
            value=f"{latest_cycle['Worksites']:.0f}",
            delta=f"+{worksite_delta:.0f} from baseline"
        )
    
    with col2:
        st.metric(
            label="Response Rate",
            value=f"{latest_cycle['Overall_Response_Rate']:.1%}",
            help="Surveys Returned / Total Employees"
        )
    
    with col3:
        if ('Change_from_2007' in cycle_summary.columns and
                latest_cycle['Change_from_2007'] is not None):
            st.metric(
                label="Change from 2007",
                value=f"{latest_cycle['Change_from_2007']:+.3f}",
                help="2007 baseline for current State CTR framework"
            )
    
    with col4:
        if ('Change_from_5Cycles' in cycle_summary.columns and
                not pd.isna(latest_cycle['Change_from_5Cycles'])):
            st.metric(
                label="Change from 5 Cycles",
                value=f"{latest_cycle['Change_from_5Cycles']:+.3f}",
                help="Change in DAR from 5 survey cycles ago"
            )
    
    # Main visualizations
    st.markdown("---")
    
    # Tab layout
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 DAR & NDAT Analysis",
        "🎯 Official Calculations",
        "🚌 Mode Split Details",
        "🏢 Worksite Performance",
        "📊 Compliance & Quality",
        "📋 Data Export"
    ])
    
    with tab1:
        st.subheader(
            "Drive-Alone Rate (DAR) & Non-Drive-Alone Travel (NDAT)"
        )

        # Weighted vs Unweighted comparison
        st.markdown("#### Weighted vs. Unweighted DAR Comparison")

        comparison_df = cycle_summary[
            ['Survey_Cycle', 'Weighted_DAR', 'Unweighted_DAR']
        ].copy()
        comparison_df['Difference'] = (
            comparison_df['Weighted_DAR'] -
            comparison_df['Unweighted_DAR']
        )
        
        fig_comparison = go.Figure()
        
        fig_comparison.add_trace(go.Scatter(
            x=comparison_df['Survey_Cycle'],
            y=comparison_df['Weighted_DAR'],
            name='Weighted DAR (Official)',
            mode='lines+markers',
            line=dict(color='#003f87', width=3),
            marker=dict(size=8)
        ))
        
        fig_comparison.add_trace(go.Scatter(
            x=comparison_df['Survey_Cycle'],
            y=comparison_df['Unweighted_DAR'],
            name='Unweighted DAR (Worksite Avg)',
            mode='lines+markers',
            line=dict(color='#ffc107', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig_comparison.update_layout(
            title='Weighted vs. Unweighted Drive-Alone Rate',
            yaxis=dict(title='Drive-Alone Rate', tickformat='.1%'),
            xaxis=dict(title='Survey Cycle'),
            height=450,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_comparison, width='stretch')
        
        st.info(
            """
        **Weighted DAR** (primary metric): Trip-volume weighted average.
        Large employers have proportionally more influence.
        **Unweighted DAR**: Simple average across all worksites. Each
        employer weighted equally regardless of size.
        Per official protocols, **Weighted DAR is the primary metric**
        for WSDOT reporting and goal tracking.
        """
        )
        
        # NDAT trends
        st.markdown("---")
        st.markdown("#### Non-Drive-Alone Travel (NDAT) Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ndat = px.line(
                cycle_summary,
                x='Survey_Cycle',
                y='NDAT',
                title='NDAT Rate Over Time',
                markers=True
            )
            fig_ndat.update_yaxes(tickformat='.1%', title='NDAT Rate')
            fig_ndat.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_ndat, width='stretch')
        
        with col2:
            # Changes from baselines
            baseline_changes = cycle_summary[
                ['Survey_Cycle', 'Change_from_1993',
                 'Change_from_2007', 'Change_from_Prior']
            ].tail(1)
            
            if not baseline_changes.empty:
                latest = baseline_changes.iloc[0]
                
                st.markdown("**Latest Cycle Comparisons:**")
                if latest['Change_from_1993'] is not None:
                    st.metric(
                        "Change from 1993",
                        f"{latest['Change_from_1993']:+.3f}",
                        help="Improvement since CTR program start"
                    )
                if latest['Change_from_2007'] is not None:
                    st.metric(
                        "Change from 2007",
                        f"{latest['Change_from_2007']:+.3f}",
                        help="Improvement since current framework baseline"
                    )
                st.metric(
                    "Change from Prior Cycle",
                    f"{latest['Change_from_Prior']:+.3f}"
                )
        
        # Historical DAR trend with goal line
        st.markdown("---")
        st.markdown("#### Drive-Alone Rate with Goal Tracking")
        
        fig_dar_goal = px.line(
            cycle_summary,
            x='Survey_Cycle',
            y='Weighted_DAR',
            title='Weighted DAR vs. Target Goal',
            markers=True
        )
        
        # Add goal line (example: 40% DAR target)
        fig_dar_goal.add_hline(
            y=0.40,
            line_dash="dash",
            line_color="red",
            annotation_text="Target: 40% DAR",
            annotation_position="right"
        )
        
        fig_dar_goal.update_yaxes(tickformat='.1%', title='Drive-Alone Rate')
        fig_dar_goal.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig_dar_goal, width='stretch')
    
    with tab2:
        st.subheader("🎯 Official Calculations per Analysis Guidelines")
        
        # TMP Zone Targets (Past 3 Cycles Average - PDF Section I.4)
        st.markdown("#### TMP Zone Targets (Past 3 Cycles Average)")
        
        last_3_cycles = list(cycle_summary['Survey_Cycle'].tail(3))
        if len(last_3_cycles) == 3:
            tmp_data = cycle_summary[
                cycle_summary['Survey_Cycle'].isin(last_3_cycles)
            ]
            # Unweighted per PDF
            avg_dar_3cycles = tmp_data['Unweighted_DAR'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cycles Analyzed", f"{', '.join(last_3_cycles)}")
            with col2:
                st.metric("3-Cycle Average DAR", f"{avg_dar_3cycles:.1%}")
            with col3:
                st.metric(
                    "Recommended TMP Target",
                    f"{avg_dar_3cycles * 0.95:.1%}",
                    help="5% reduction from 3-cycle average (example)"
                )

            st.info(
                "Per analysis guidelines, TMP zone targets use the "
                "**unweighted average** DAR across the past 3 survey cycles."
            )
        
        # DA Trips per Day (PDF Section I.5)
        st.markdown("---")
        st.markdown("#### Total Drive-Alone Round Trips per Work Day")
        st.markdown("*For goal setting and trip reduction tracking*")
        
        fig_da_trips = px.bar(
            cycle_summary,
            x='Survey_Cycle',
            y='DA_Trips_PerDay',
            title='Drive-Alone Round Trips per Work Day',
            labels={'DA_Trips_PerDay': 'DA Trips/Day'}
        )
        fig_da_trips.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_da_trips, width='stretch')
        
        # Show calculation methodology
        with st.expander("📐 Calculation Methodology"):
            st.markdown(
                """
            **Drive-Alone Round Trips per Work Day** =
            Total Employees × Weighted DAR

            This metric is used to:
            - Establish trip reduction targets
            - Track progress toward CTR goals
            - Calculate vehicles reduced from roadways

            Per 2008 CTR Plan methodology (pages 47, 122-123).
            """
            )
        
        # Environmental impact with calculations
        st.markdown("---")
        st.markdown("#### Environmental Impact Analysis")
        
        if len(cycle_summary) > 5:
            latest = cycle_summary.iloc[-1]
            baseline = cycle_summary.iloc[0]
            
            # Calculate counterfactual
            counterfactual_dar = baseline['Weighted_DAR']
            actual_dar = latest['Weighted_DAR']
            employees = latest['Total_Employees']
            
            # Trip reduction
            trips_reduced = employees * (counterfactual_dar - actual_dar)
            
            # VMT and emissions (simplified calculation)
            avg_commute_distance = latest['Avg_VMT_per_Employee']
            vmt_reduced = trips_reduced * avg_commute_distance * 250  # 250 workdays
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Annual Trips Reduced",
                    f"{trips_reduced * 250:,.0f}",
                    help="Compared to baseline DAR"
                )
            with col2:
                st.metric("Annual VMT Reduced", f"{vmt_reduced:,.0f}")
            with col3:
                gallons_saved = vmt_reduced / 25  # 25 mpg average
                st.metric("Gallons Saved", f"{gallons_saved:,.0f}")
    
    with tab3:
        st.subheader("🚌 Detailed Mode Split Analysis")
        
        # Stacked area chart
        mode_data = cycle_summary[
            ['Survey_Cycle', 'DriveAlone_Share', 'Transit_Share',
             'Carpool_Share', 'Active_Share', 'Telework_Share']
        ].copy()
        
        fig_modes = go.Figure()
        
        fig_modes.add_trace(go.Scatter(
            x=mode_data['Survey_Cycle'], y=mode_data['DriveAlone_Share'],
            name='Drive Alone', mode='lines', stackgroup='one',
            fillcolor='#dc3545', line=dict(width=0.5, color='#dc3545')
        ))
        
        fig_modes.add_trace(go.Scatter(
            x=mode_data['Survey_Cycle'], y=mode_data['Transit_Share'],
            name='Transit (Bus/Train)', mode='lines', stackgroup='one',
            fillcolor='#007bff', line=dict(width=0.5, color='#007bff')
        ))
        
        fig_modes.add_trace(go.Scatter(
            x=mode_data['Survey_Cycle'], y=mode_data['Carpool_Share'],
            name='Carpool/Vanpool', mode='lines', stackgroup='one',
            fillcolor='#ffc107', line=dict(width=0.5, color='#ffc107')
        ))
        
        fig_modes.add_trace(go.Scatter(
            x=mode_data['Survey_Cycle'], y=mode_data['Active_Share'],
            name='Walk/Bike', mode='lines', stackgroup='one',
            fillcolor='#28a745', line=dict(width=0.5, color='#28a745')
        ))
        
        fig_modes.add_trace(go.Scatter(
            x=mode_data['Survey_Cycle'], y=mode_data['Telework_Share'],
            name='Telework', mode='lines', stackgroup='one',
            fillcolor='#6c757d', line=dict(width=0.5, color='#6c757d')
        ))
        
        fig_modes.update_layout(
            title='Mode Share Evolution (% of Total Weekly Trips)',
            yaxis=dict(
                title='Percentage',
                ticksuffix='%',
                range=[0, 100]
            ),
            xaxis=dict(title='Survey Cycle'),
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_modes, width='stretch')
        
        # Individual mode details
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Transit & Active Transportation")
            
            fig_transit = px.line(
                cycle_summary,
                x='Survey_Cycle',
                y='Transit_Share',
                title='Transit Mode Share',
                markers=True
            )
            fig_transit.update_yaxes(ticksuffix='%')
            fig_transit.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_transit, width='stretch')
            
            fig_active = px.line(
                cycle_summary,
                x='Survey_Cycle',
                y='Active_Share',
                title='Active Transportation (Walk+Bike)',
                markers=True
            )
            fig_active.update_yaxes(ticksuffix='%')
            fig_active.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_active, width='stretch')
        
        with col2:
            st.markdown("#### Telework & Carpool")
            
            fig_telework = px.line(
                cycle_summary,
                x='Survey_Cycle',
                y='Telework_Share',
                title='Telework Share',
                markers=True
            )
            fig_telework.update_yaxes(ticksuffix='%')
            fig_telework.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_telework, width='stretch')
            
            fig_carpool = px.line(
                cycle_summary,
                x='Survey_Cycle',
                y='Carpool_Share',
                title='Carpool/Vanpool Share',
                markers=True
            )
            fig_carpool.update_yaxes(ticksuffix='%')
            fig_carpool.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_carpool, width='stretch')
    
    with tab4:
        st.subheader("🏢 Worksite Performance Analysis")

        latest_employers = filtered_df[
            filtered_df['Survey_Cycle'] == selected_cycles[-1]
        ].copy()
        
        if not latest_employers.empty:
            # Top/bottom performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top Performers (Lowest DAR)")
                top = latest_employers.nsmallest(15, 'Drive_Alone_Rate')[
                    ['Organization_Name', 'Drive_Alone_Rate',
                     'VMT_per_Employee', 'Total_Employees']
                ]
                top_display = top.copy()
                top_display['Drive_Alone_Rate'] = (
                    top_display['Drive_Alone_Rate'].apply(
                        lambda x: f"{x:.1%}"
                    )
                )
                top_display['VMT_per_Employee'] = (
                    top_display['VMT_per_Employee'].round(2)
                )
                st.dataframe(
                    top_display,
                    hide_index=True,
                    width='stretch',
                    height=500
                )
            
            with col2:
                st.markdown("#### ⚠️ Needs Support (Highest DAR)")
                bottom = latest_employers.nlargest(15, 'Drive_Alone_Rate')[
                    ['Organization_Name', 'Drive_Alone_Rate',
                     'VMT_per_Employee', 'Total_Employees']
                ]
                bottom_display = bottom.copy()
                bottom_display['Drive_Alone_Rate'] = (
                    bottom_display['Drive_Alone_Rate'].apply(
                        lambda x: f"{x:.1%}"
                    )
                )
                bottom_display['VMT_per_Employee'] = (
                    bottom_display['VMT_per_Employee'].round(2)
                )
                st.dataframe(
                    bottom_display,
                    hide_index=True,
                    width='stretch',
                    height=500
                )
            
            # Distribution
            st.markdown("---")
            st.markdown("#### DAR Distribution Across All Worksites")
            
            fig_dist = px.histogram(
                latest_employers,
                x='Drive_Alone_Rate',
                nbins=30,
                title=f'DAR Distribution ({selected_cycles[-1]})'
            )
            fig_dist.update_xaxes(tickformat='.0%', title='Drive-Alone Rate')
            fig_dist.add_vline(
                x=latest_employers['Drive_Alone_Rate'].median(),
                line_dash="dash",
                line_color="red",
                annotation_text="Median"
            )
            st.plotly_chart(fig_dist, width='stretch')
    
    with tab5:
        st.subheader("📊 Survey Compliance & Data Quality")
        
        # Response rate analysis
        st.markdown("#### Survey Response Rates")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_response = latest_cycle['Overall_Response_Rate']
            st.metric("Overall Response Rate", f"{avg_response:.1%}")
        
        with col2:
            compliant = (
                (latest_employers['Response_Rate'] >= 0.50).sum()
                if not latest_employers.empty else 0
            )
            total = (
                len(latest_employers) if not latest_employers.empty else 0
            )
            st.metric("Sites Meeting 50% Threshold", f"{compliant}/{total}")
        
        with col3:
            st.metric(
                "Total Surveys Returned",
                f"{latest_cycle['Total_Surveys_Returned']:,.0f}"
            )
        
        # Response rate trend
        fig_response = px.line(
            cycle_summary,
            x='Survey_Cycle',
            y='Overall_Response_Rate',
            title='Overall Response Rate by Cycle',
            markers=True
        )
        fig_response.update_yaxes(tickformat='.1%', title='Response Rate')
        fig_response.add_hline(
            y=0.50,
            line_dash="dash",
            line_color="red",
            annotation_text="50% Target"
        )
        fig_response.update_layout(height=400)
        st.plotly_chart(fig_response, width='stretch')
        
        # Data quality note
        st.info(
            """
        **Data Quality Standards (Per PDF Section II):**
        - Surveys are census-based (not sample)
        - Expanded Surveys Returned used for weighting
        - Minimum 50% response rate required for compliance
        - 2007 protocol change: 1-person motorcycles now count as
          drive-alone
        """
        )
    
    with tab6:
        st.subheader("📋 Data Export & Summary Tables")
        
        # Summary table with all key metrics
        st.markdown("#### Comprehensive Survey Cycle Summary")

        export_cols = [
            'Survey_Cycle', 'Worksites', 'Total_Employees', 'Weighted_DAR',
            'Unweighted_DAR', 'NDAT', 'Avg_VMT_per_Employee',
            'DA_Trips_PerDay', 'Overall_Response_Rate', 'Total_Weekly_Trips'
        ]
        
        export_df = cycle_summary[export_cols].copy()
        
        st.dataframe(
            export_df.style.format({
                'Total_Employees': '{:,.0f}',
                'Weighted_DAR': '{:.3f}',
                'Unweighted_DAR': '{:.3f}',
                'NDAT': '{:.3f}',
                'Avg_VMT_per_Employee': '{:.2f}',
                'DA_Trips_PerDay': '{:,.0f}',
                'Overall_Response_Rate': '{:.3f}',
                'Total_Weekly_Trips': '{:,.0f}'
            }),
            width='stretch',
            hide_index=True
        )
        
        # Download button
        csv = export_df.to_csv(index=False)
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        st.download_button(
            label="📥 Download Summary (CSV)",
            data=csv,
            file_name=f"bellevue_ctr_official_summary_{timestamp}.csv",
            mime="text/csv"
        )
        
        # Analysis guidelines reference
        st.markdown("---")
        st.markdown("#### 📋 Analysis Guidelines Reference")
        st.markdown(
            """
        This dashboard implements all calculations from:
        **CTR Data Analysis Guidelines** (Updated 3/24/2017)

        **Key Calculations Implemented:**
        1. ✅ Drive-Alone Rate (DAR) - Weighted & Unweighted
        2. ✅ Non-Drive-Alone Travel (NDAT)
        3. ✅ Changes from baselines (1993, 2007, Prior, 5 Cycles)
        4. ✅ TMP Zone Targets (Past 3 Cycles Average)
        5. ✅ Total DA Round Trips per Work Day
        6. ✅ VMT per Employee (2007-present)
        7. ✅ Simple/Unweighted Averages
        8. ✅ Response Rate Tracking

        All formulas follow official City of Bellevue protocols.
        """
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <strong>City of Bellevue Transportation Department</strong><br>
        Commute Trip Reduction (CTR) Program - Official Analysis Dashboard<br>
        Based on: CTR Data Analysis Guidelines (Updated 3/24/2017)<br>
        Data: 1993-2025 | Dashboard Updated: February 2026
    </div>
    """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
