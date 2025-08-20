import streamlit as st
import pandas as pd
from charts import TBChartGenerator
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="TB Surveillance Dashboard - Rwanda",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Replace your existing CSS section in main.py with this:

st.markdown("""
<style>
    /* Dark mode optimization */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Metric cards - dark theme */
    .metric-card {
        background: linear-gradient(145deg, #1e2329, #262d37);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid #333741;
        margin: 15px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }
    
    .big-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #1f77b4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 10px 0;
    }
    
    /* Target indicators - enhanced for dark mode */
    .target-indicator {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-left: 10px;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .target-good {
        background: linear-gradient(135deg, #00c851, #007e33);
        color: #ffffff;
        border: 1px solid #00c851;
    }
    
    .target-warning {
        background: linear-gradient(135deg, #ffbb33, #ff8800);
        color: #ffffff;
        border: 1px solid #ffbb33;
    }
    
    .target-danger {
        background: linear-gradient(135deg, #ff4444, #cc0000);
        color: #ffffff;
        border: 1px solid #ff4444;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e2329;
        border-right: 2px solid #333741;
    }
    
    .sidebar .sidebar-content {
        background-color: #1e2329;
        color: #fafafa;
    }
    
    /* Headers and text */
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
        font-weight: 600;
    }
    
    h1 {
        background: linear-gradient(135deg, #00d4ff, #1f77b4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Tabs styling for dark mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #1e2329;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #262d37, #1e2329);
        border-radius: 10px;
        padding: 12px 24px;
        color: #fafafa;
        border: 1px solid #333741;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #333741, #262d37);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff, #1f77b4) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
        border: 1px solid #00d4ff;
    }
    
    /* Info boxes and expandable sections */
    .streamlit-expanderHeader {
        background-color: #262d37 !important;
        border: 1px solid #333741;
        border-radius: 8px;
        color: #fafafa !important;
    }
    
    .streamlit-expanderContent {
        background-color: #1e2329 !important;
        border: 1px solid #333741;
        color: #fafafa !important;
    }
    
    /* Metrics styling */
    .css-1xarl3l {
        background-color: #262d37;
        border: 1px solid #333741;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* Input widgets */
    .stSelectbox > div > div {
        background-color: #262d37;
        border: 1px solid #333741;
        color: #fafafa;
    }
    
    .stDateInput > div > div {
        background-color: #262d37;
        border: 1px solid #333741;
        color: #fafafa;
    }
    
    .stRadio > div {
        background-color: #262d37;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #333741;
    }
    
    /* Charts container */
    .js-plotly-plot {
        background-color: #1e2329 !important;
        border-radius: 10px;
        border: 1px solid #333741;
    }
    
    /* Success/info/warning boxes */
    .stSuccess {
        background-color: #0d4a2d;
        border: 1px solid #00c851;
        color: #fafafa;
    }
    
    .stInfo {
        background-color: #1a237e;
        border: 1px solid #1f77b4;
        color: #fafafa;
    }
    
    .stWarning {
        background-color: #4a2c0a;
        border: 1px solid #ffbb33;
        color: #fafafa;
    }
    
    .stError {
        background-color: #4a0d0d;
        border: 1px solid #ff4444;
        color: #fafafa;
    }
    
    /* Footer */
    .footer {
        background-color: #1e2329;
        color: #8b949e;
        text-align: center;
        padding: 20px;
        border-top: 1px solid #333741;
        margin-top: 40px;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e2329;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333741;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4a5568;
    }
    
    /* Plotly chart dark mode optimization */
    .modebar {
        background-color: #262d37 !important;
    }
    
    /* Animation for metric cards */
    @keyframes glow {
        0% { box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        50% { box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1); }
        100% { box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
    }
    
    .metric-card:hover {
        animation: glow 2s infinite;
    }
</style>
""", unsafe_allow_html=True)




@st.cache_data(ttl=300)  # Cache for 5 minutes for auto-refresh
def load_data():
    """Load TB surveillance data"""
    try:
        df = pd.read_csv("data/Tuberculosis 2023-2024.csv", encoding="latin1")
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/Tuberculosis 2023-2024.csv' exists.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def get_target_indicator(value, target, target_type="higher_better"):
    """Get target achievement indicator"""
    if target_type == "higher_better":
        if value >= target:
            return "target-good", "✅ Target Met"
        elif value >= target * 0.8:
            return "target-warning", "⚠️ Close to Target"
        else:
            return "target-danger", "❌ Below Target"
    else:  # lower_better
        if value <= target:
            return "target-good", "✅ Target Met"
        elif value <= target * 1.2:
            return "target-warning", "⚠️ Close to Target"
        else:
            return "target-danger", "❌ Above Target"

def main():
    # Header
    st.title("🏥 TB Surveillance Dashboard - Rwanda")
    st.markdown("**Monitoring Tuberculosis Cases and Treatment Outcomes**")
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Initialize chart generator
    chart_gen = TBChartGenerator(df)
    
    # Sidebar for filters
    with st.sidebar:
        st.header("📊 Dashboard Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (5 min)", value=True)
        
        if auto_refresh:
            # Auto-refresh placeholder
            refresh_placeholder = st.empty()
            refresh_placeholder.text("🔄 Auto-refresh enabled")
        
        st.markdown("---")
        
        # Date range filter
        st.subheader("📅 Date Filter")
        
        # Get date range from data
        date_col = 'Enrollment date(Diagnostic Date)'
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        
        # Date range selector
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Period type
        period_type = st.radio(
            "📈 Analysis Period",
            ["monthly", "quarterly"],
            index=0
        )
        
        # Treatment outcome type
        outcome_type = st.selectbox(
            "🎯 Treatment Success Definition",
            ["Cured Only", "Cured + Completed"],
            index=1
        )
        
        st.markdown("---")
        
        # Targets information
        st.subheader("🎯 Targets")
        st.info("""
        **LTBI Coverage:** >90%
        **TB Incidence Target:** 46/100,000 population
        """)
        
        # Last updated
        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Prepare period filter
    period_filter = None
    if len(date_range) == 2:
        period_filter = (
            pd.Timestamp(date_range[0]),
            pd.Timestamp(date_range[1])
        )
    
    # Get big numbers
    big_numbers = chart_gen.get_big_numbers(period_filter)
    use_completed = outcome_type == "Cured + Completed"
    
    # Key Metrics Row
    st.header("📈 Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Total Cured Cases</h3>
            <div class="big-number">{big_numbers['total_cured']:,}</div>
            <p>{"Cured + Completed" if use_completed else "Cured Only"} cases in selected period</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ltbi_value = big_numbers['ltbi_coverage']
        ltbi_class, ltbi_text = get_target_indicator(ltbi_value, 90, "higher_better")
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>💉 LTBI Coverage</h3>
            <div class="big-number">{ltbi_value}%</div>
            <span class="target-indicator {ltbi_class}">{ltbi_text}</span>
            <p>Target: >90%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        incidence_value = big_numbers['yearly_incidence']
        incidence_class, incidence_text = get_target_indicator(incidence_value, 46, "lower_better")
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Yearly TB Incidence</h3>
            <div class="big-number">{incidence_value}</div>
            <span class="target-indicator {incidence_class}">{incidence_text}</span>
            <p>per 100,000 population (Target: ≤46)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Treatment Outcomes", 
        "⚠️ High-Risk Groups", 
        "📋 TB Notifications", 
        "👶 Pediatric Analysis"
    ])
    
    with tab1:
        st.header("🎯 Treatment Outcome Success")
        st.markdown("Analysis of cured cases and treatment success rates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Latest Month Distribution")
            pie_fig = chart_gen.create_treatment_outcome_pie(period_filter, use_completed)
            st.plotly_chart(pie_fig, use_container_width=True)
        
        with col2:
            st.subheader("Trends Over Time")
            time_fig = chart_gen.create_treatment_time_series(period_filter, period_type, use_completed)
            st.plotly_chart(time_fig, use_container_width=True)
        
        # Additional insights
        with st.expander("📝 Treatment Outcome Insights"):
            st.markdown(f"""
            - **Analysis Period:** {period_type.title()} from {date_range[0]} to {date_range[1]}
            - **Success Definition:** {outcome_type}
            - **Total Cases:** {big_numbers['total_cured']:,} successful treatments
            - **Data Source:** Treatment completion dates and diagnostic dates
            """)
    
    with tab2:
        st.header("⚠️ High-Risk Groups Analysis")
        st.markdown("TB trends in high-risk populations including prisoners, HIV+, contacts, elderly, children, diabetics, mining workers, and refugees")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Latest Month Distribution")
            hr_pie_fig = chart_gen.create_high_risk_pie(period_filter)
            st.plotly_chart(hr_pie_fig, use_container_width=True)
        
        with col2:
            st.subheader("Monthly Trends")
            hr_time_fig = chart_gen.create_high_risk_time_series(period_filter, period_type)
            st.plotly_chart(hr_time_fig, use_container_width=True)
        
        with st.expander("📝 High-Risk Group Definitions"):
            st.markdown("""
            **High-risk categories include:**
            - 👥 **Contacts:** Contact of TPB+, Contact of MDR-TB
            - 🏥 **Medical:** HIV positive, Diabetic
            - 👶👴 **Age groups:** Under 15 years, Above 65 years  
            - 🏭 **Occupational:** Mining workers
            - 🏛️ **Institutional:** Prisoners
            - 🌍 **Social:** Refugees
            """)
    
    with tab3:
        st.header("📋 TB Notifications: New and Relapse Cases")
        st.markdown("Analysis of new TB cases and relapse incidents with incidence rates per 100,000 population")
        
        notification_fig = chart_gen.create_notification_time_series(period_filter, period_type)
        st.plotly_chart(notification_fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "🆕 New Cases (Latest Month)", 
                value=f"{chart_gen.df[chart_gen.df['New_Case']==True].groupby('YearMonth').size().iloc[-1] if len(chart_gen.df[chart_gen.df['New_Case']==True]) > 0 else 0}",
                delta=None
            )
        
        with col2:
            st.metric(
                "🔄 Relapse Cases (Latest Month)", 
                value=f"{chart_gen.df[chart_gen.df['Relapse_Case']==True].groupby('YearMonth').size().iloc[-1] if len(chart_gen.df[chart_gen.df['Relapse_Case']==True]) > 0 else 0}",
                delta=None
            )
        
        with st.expander("📝 Notification Analysis Details"):
            st.markdown(f"""
            - **Rwanda Population:** {chart_gen.rwanda_population:,}
            - **Incidence Calculation:** (Cases / Population) × 100,000
            - **Target Incidence:** ≤46 per 100,000 population
            - **Current Yearly Incidence:** {big_numbers['yearly_incidence']:.1f} per 100,000
            - **Data includes:** New cases and relapse cases based on enrollment dates
            """)
    
    with tab4:
        st.header("👶 Pediatric TB Analysis")
        st.markdown("LTBI treatment coverage for contacts under 5 years and TB cases in children under 14")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💉 LTBI Coverage (Under 5)")
            
            # LTBI Coverage metrics
            ltbi_coverage = big_numbers['ltbi_coverage']
            target_class, target_text = get_target_indicator(ltbi_coverage, 90, "higher_better")
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="big-number" style="color: {'#2E8B57' if ltbi_coverage >= 90 else '#DC143C'}">{ltbi_coverage}%</div>
                <span class="target-indicator {target_class}">{target_text}</span>
                <p><strong>Formula:</strong> (TPT Completed) / (Contacts <5 - Positive TB cases) × 100</p>
            </div>
            """, unsafe_allow_html=True)
            
            # LTBI calculation details
            with st.expander("📊 LTBI Calculation Details"):
                try:
                    # Get the actual numbers for display
                    filtered_df = chart_gen._apply_period_filter(period_filter) if period_filter else chart_gen.df
                    
                    contacts_living = filtered_df['Number of contacts <5 years living with index case'].sum()
                    positive_tb = filtered_df['Number of positive TB cases among contacts <5 years'].sum()
                    tpt_completed = filtered_df['Number of < 5 years contacts with TPT completed'].sum()
                    eligible = contacts_living - positive_tb
                    
                    st.markdown(f"""
                    **Numerator:** Children <5 who received TPT = {tpt_completed:,.0f}
                    
                    **Denominator Calculation:**
                    - Contacts <5 living with index case: {contacts_living:,.0f}
                    - Minus positive TB cases among contacts <5: {positive_tb:,.0f}
                    - **Eligible children:** {eligible:,.0f}
                    
                    **Coverage:** {tpt_completed:,.0f} / {eligible:,.0f} = {ltbi_coverage:.1f}%
                    """)
                except:
                    st.warning("Detailed calculation data not available")
        
        with col2:
            st.subheader("🧒 Under 14 TB Cases")
            under14_fig = chart_gen.create_under14_pie(period_filter)
            st.plotly_chart(under14_fig, use_container_width=True)
        
        # Additional pediatric metrics
        st.subheader("📈 Pediatric TB Statistics")
        
        try:
            filtered_df = chart_gen._apply_period_filter(period_filter) if period_filter else chart_gen.df
            under14_df = filtered_df[filtered_df['Under14'] == True]
            total_under14 = len(under14_df)
            new_relapse_under14 = under14_df[
                under14_df['Previous treatment history'].str.strip().str.lower().isin(['new', 'relapse'])
            ]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Under 14 Cases", total_under14)
            
            with col2:
                st.metric("New/Relapse Under 14", len(new_relapse_under14))
            
            with col3:
                percentage = (len(new_relapse_under14) / total_under14 * 100) if total_under14 > 0 else 0
                st.metric("% New/Relapse", f"{percentage:.1f}%")
            
        except Exception as e:
            st.warning("Could not calculate pediatric statistics")
        
        with st.expander("📝 Pediatric Analysis Notes"):
            st.markdown("""
            **LTBI Treatment Coverage:**
            - **Target:** >90% of eligible children under 5 receive preventive treatment
            - **Eligible:** Children <5 living with TB index cases, excluding those with active TB
            - **Importance:** Prevents TB development in high-risk young children
            
            **Under 14 TB Cases:**
            - **Focus:** New and relapse cases in children
            - **Significance:** Pediatric TB often indicates recent transmission
            - **Clinical note:** Children are more likely to develop severe forms of TB
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>TB Surveillance Dashboard</strong> | Rwanda Ministry of Health</p>
        <p>Data Source: Tuberculosis 2023-2024 Surveillance System</p>
        <p style='font-size: 0.8em;'>Dashboard automatically refreshes every 5 minutes when enabled</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(300)  # Wait 5 minutes
        st.rerun()

if __name__ == "__main__":
    main()