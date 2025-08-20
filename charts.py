import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

class TBChartGenerator:
    def __init__(self, df):
        self.df = df.copy()
        self.rwanda_population = 14260000
        self.colors = {
            'cured': '#2E8B57',
            'others': '#D3D3D3', 
            'high_risk': '#DC143C',
            'new_cases': '#4169E1',
            'relapse': '#FF8C00',
            'diagnosed': '#1E90FF'
        }
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess the TB data for analysis"""
        # Convert enrollment date to datetime
        date_col = 'Enrollment date(Diagnostic Date)'
        self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
        self.df = self.df.dropna(subset=[date_col]).copy()
        
        # Extract Year-Month period
        self.df['YearMonth'] = self.df[date_col].dt.to_period('M')
        self.df['Quarter'] = self.df[date_col].dt.to_period('Q')
        
        # Process treatment outcomes
        self.df['Is_Cured'] = self.df['Treatment outcome'].apply(
            lambda x: 1 if str(x).strip().lower() == 'cured' else 0
        )
        
        self.df['Is_CuredCompleted'] = self.df['Treatment outcome'].apply(
            lambda x: 1 if str(x).strip().lower() in ['cured', 'completed'] else 0
        )
        
        # Process high-risk groups
        self._process_high_risk_groups()
        
        # Process TB notifications
        self.df['New_Case'] = self.df['Previous treatment history'].str.strip().str.lower() == 'new'
        self.df['Relapse_Case'] = self.df['Previous treatment history'].str.strip().str.lower() == 'relapse'
        
        # Process age groups
        self.df['TB_Current age'] = pd.to_numeric(self.df['TB_Current age'], errors='coerce')
        self.df['Under14'] = self.df['TB_Current age'] < 14
    
    def _process_high_risk_groups(self):
        """Process high-risk group flags"""
        # Age-based flags
        self.df['TB_Current age'] = pd.to_numeric(self.df['TB_Current age'], errors='coerce')
        self.df['Under15'] = self.df['TB_Current age'] < 15
        self.df['Above65'] = self.df['TB_Current age'] > 65
        
        # Yes/No columns
        yes_no_cols = ['Prisoners', 'Contact of TPB+', 'Contact of MDR - TB',
                       'Diabetic (new)', 'Mining worker (new)', 'Refugee ']
        
        for col in yes_no_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip().str.lower().map(
                    {'yes': True, 'no': False}
                ).fillna(False)
        
        # HIV positive flag
        if 'HIV status' in self.df.columns:
            self.df['HIV_Positive'] = self.df['HIV status'].astype(str).str.strip().str.lower() == 'positive'
        else:
            self.df['HIV_Positive'] = False
        
        # Combine all high-risk flags
        available_flags = [col for col in yes_no_cols if col in self.df.columns]
        high_risk_flags = available_flags + ['HIV_Positive', 'Under15', 'Above65']
        
        self.df['High_Risk'] = self.df[high_risk_flags].any(axis=1)
    
    def get_big_numbers(self, period_filter=None):
        """Calculate key metrics for big number displays"""
        filtered_df = self._apply_period_filter(period_filter) if period_filter else self.df
        
        # Total cured cases
        total_cured = filtered_df['Is_Cured'].sum()
        
        # LTBI coverage calculation
        ltbi_coverage = self._calculate_ltbi_coverage(filtered_df)
        
        # Yearly normalized incidence
        yearly_incidence = self._calculate_yearly_incidence(filtered_df)
        
        return {
            'total_cured': int(total_cured),
            'ltbi_coverage': round(ltbi_coverage, 1),
            'yearly_incidence': round(yearly_incidence, 1)
        }
    
    def _apply_period_filter(self, period_filter):
        """Apply date range filter to dataframe"""
        if period_filter is None:
            return self.df
        
        start_date, end_date = period_filter
        date_col = 'Enrollment date(Diagnostic Date)'
        return self.df[
            (self.df[date_col] >= start_date) & 
            (self.df[date_col] <= end_date)
        ].copy()
    
    def _calculate_ltbi_coverage(self, df_subset):
        """Calculate LTBI coverage percentage"""
        try:
            under5_cols = [
                'Number of contacts <5 years living with index case',
                'Number of positive TB cases among contacts <5 years',
                'Number of < 5 years contacts with TPT completed'
            ]
            
            # Check if columns exist
            missing_cols = [col for col in under5_cols if col not in df_subset.columns]
            if missing_cols:
                return 0.0
            
            # Convert to numeric
            for col in under5_cols:
                df_subset[col] = pd.to_numeric(df_subset[col], errors='coerce').fillna(0)
            
            # Calculate eligible children
            eligible = (df_subset['Number of contacts <5 years living with index case'] - 
                       df_subset['Number of positive TB cases among contacts <5 years'])
            eligible = eligible.clip(lower=0)  # Ensure non-negative
            
            # Calculate coverage
            completed = df_subset['Number of < 5 years contacts with TPT completed']
            coverage = (completed.sum() / eligible.sum() * 100) if eligible.sum() > 0 else 0
            
            return min(coverage, 100)  # Cap at 100%
            
        except Exception:
            return 0.0
    
    def _calculate_yearly_incidence(self, df_subset):
        """Calculate yearly normalized TB incidence per 100,000"""
        try:
            # Count new and relapse cases
            new_relapse_cases = df_subset[
                df_subset['Previous treatment history'].str.strip().str.lower().isin(['new', 'relapse'])
            ]
            
            total_cases = len(new_relapse_cases)
            
            # Get time span in months
            if len(df_subset) == 0:
                return 0.0
                
            date_col = 'Enrollment date(Diagnostic Date)'
            min_date = df_subset[date_col].min()
            max_date = df_subset[date_col].max()
            
            months_span = max(1, (max_date - min_date).days / 30.44)  # Average days per month
            
            # Normalize to yearly incidence
            yearly_cases = (total_cases / months_span) * 12
            incidence_per_100k = (yearly_cases / self.rwanda_population) * 100000
            
            return incidence_per_100k
            
        except Exception:
            return 0.0
    
    def create_treatment_outcome_pie(self, period_filter=None, use_completed=False):
        """Create pie chart for treatment outcomes"""
        filtered_df = self._apply_period_filter(period_filter) if period_filter else self.df
        
        # Get latest month data
        latest_month = filtered_df['YearMonth'].max()
        latest_data = filtered_df[filtered_df['YearMonth'] == latest_month]
        
        if use_completed:
            latest_data['Outcome'] = latest_data['Treatment outcome'].apply(
                lambda x: 'Cured+Completed' if str(x).strip().lower() in ['cured', 'completed'] else 'Others'
            )
            title = f"Cured+Completed vs Others - {latest_month}"
        else:
            latest_data['Outcome'] = latest_data['Treatment outcome'].apply(
                lambda x: 'Cured' if str(x).strip().lower() == 'cured' else 'Others'
            )
            title = f"Cured vs Others - {latest_month}"
        
        pie_counts = latest_data['Outcome'].value_counts()
        
        fig = px.pie(
            values=pie_counts.values,
            names=pie_counts.index,
            title=title,
            color_discrete_map={'Cured': self.colors['cured'], 
                              'Cured+Completed': self.colors['cured'],
                              'Others': self.colors['others']}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, title_x=0.5)
        
        return fig
    
    def create_treatment_time_series(self, period_filter=None, period_type='monthly', use_completed=False):
        """Create time series for treatment outcomes"""
        filtered_df = self._apply_period_filter(period_filter) if period_filter else self.df
        
        # Group by period
        group_col = 'YearMonth' if period_type == 'monthly' else 'Quarter'
        
        if use_completed:
            monthly_counts = filtered_df.groupby(group_col).agg(
                Diagnosed=('Method of TB confirmation', 'count'),
                CuredCompleted=('Is_CuredCompleted', 'sum')
            ).reset_index()
            cured_col = 'CuredCompleted'
            cured_label = 'Cured+Completed'
        else:
            monthly_counts = filtered_df.groupby(group_col).agg(
                Diagnosed=('Method of TB confirmation', 'count'),
                Cured=('Is_Cured', 'sum')
            ).reset_index()
            cured_col = 'Cured'
            cured_label = 'Cured'
        
        # Convert to datetime
        monthly_counts['Date'] = monthly_counts[group_col].dt.to_timestamp()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_counts['Date'],
            y=monthly_counts['Diagnosed'],
            mode='lines+markers',
            name='Diagnosed',
            line=dict(color=self.colors['diagnosed'], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_counts['Date'],
            y=monthly_counts[cured_col],
            mode='lines+markers',
            name=cured_label,
            line=dict(color=self.colors['cured'], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f"Diagnosed vs {cured_label} Patients Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Patients",
            height=400,
            hovermode='x unified',
            title_x=0.5
        )
        
        return fig
    
    def create_high_risk_pie(self, period_filter=None):
        """Create pie chart for high-risk distribution"""
        filtered_df = self._apply_period_filter(period_filter) if period_filter else self.df
        
        latest_month = filtered_df['YearMonth'].max()
        latest_data = filtered_df[filtered_df['YearMonth'] == latest_month]
        
        latest_data['High_Risk_Label'] = latest_data['High_Risk'].apply(
            lambda x: 'High Risk' if x else 'Others'
        )
        
        pie_counts = latest_data['High_Risk_Label'].value_counts()
        
        fig = px.pie(
            values=pie_counts.values,
            names=pie_counts.index,
            title=f"High-Risk vs Other TB Cases - {latest_month}",
            color_discrete_map={'High Risk': self.colors['high_risk'], 
                              'Others': self.colors['others']}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, title_x=0.5)
        
        return fig
    
    def create_high_risk_time_series(self, period_filter=None, period_type='monthly'):
        """Create time series for high-risk cases"""
        filtered_df = self._apply_period_filter(period_filter) if period_filter else self.df
        
        group_col = 'YearMonth' if period_type == 'monthly' else 'Quarter'
        
        monthly_counts = filtered_df.groupby(group_col).agg(
            Diagnosed=('Method of TB confirmation', 'count'),
            High_Risk=('High_Risk', 'sum')
        ).reset_index()
        
        monthly_counts['Date'] = monthly_counts[group_col].dt.to_timestamp()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_counts['Date'],
            y=monthly_counts['Diagnosed'],
            mode='lines+markers',
            name='Diagnosed',
            line=dict(color=self.colors['diagnosed'], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_counts['Date'],
            y=monthly_counts['High_Risk'],
            mode='lines+markers',
            name='High Risk',
            line=dict(color=self.colors['high_risk'], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Monthly Diagnosed vs High-Risk TB Cases",
            xaxis_title="Date",
            yaxis_title="Number of Patients",
            height=400,
            hovermode='x unified',
            title_x=0.5
        )
        
        return fig
    
    def create_notification_time_series(self, period_filter=None, period_type='monthly'):
        """Create time series for TB notifications"""
        filtered_df = self._apply_period_filter(period_filter) if period_filter else self.df
        
        group_col = 'YearMonth' if period_type == 'monthly' else 'Quarter'
        
        monthly_notification = filtered_df.groupby(group_col).agg(
            New=('New_Case', 'sum'),
            Relapse=('Relapse_Case', 'sum')
        ).reset_index()
        
        monthly_notification['Date'] = monthly_notification[group_col].dt.to_timestamp()
        
        # Calculate incidence per 100,000
        monthly_notification['New_rate'] = monthly_notification['New'] / self.rwanda_population * 100000
        monthly_notification['Relapse_rate'] = monthly_notification['Relapse'] / self.rwanda_population * 100000
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_notification['Date'],
            y=monthly_notification['New_rate'],
            mode='lines+markers',
            name='New Case Rate',
            line=dict(color=self.colors['new_cases'], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_notification['Date'],
            y=monthly_notification['Relapse_rate'],
            mode='lines+markers',
            name='Relapse Case Rate',
            line=dict(color=self.colors['relapse'], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="TB Notification: Incidence per 100,000 Population",
            xaxis_title="Date",
            yaxis_title="Rate (/100,000)",
            height=400,
            hovermode='x unified',
            title_x=0.5
        )
        
        return fig
    
    def create_under14_pie(self, period_filter=None):
        """Create pie chart for under-14 TB cases"""
        filtered_df = self._apply_period_filter(period_filter) if period_filter else self.df
        
        # Filter under 14
        under_14_df = filtered_df[filtered_df['Under14'] == True]
        
        # Flag New OR Relapse cases
        under_14_df = under_14_df.copy()
        under_14_df['New_or_Relapse'] = under_14_df['Previous treatment history'].str.strip().str.lower().isin(['new', 'relapse'])
        
        # Count groups
        case_counts = {
            'New/Relapse': under_14_df['New_or_Relapse'].sum(),
            'Other': len(under_14_df) - under_14_df['New_or_Relapse'].sum()
        }
        
        fig = px.pie(
            values=list(case_counts.values()),
            names=list(case_counts.keys()),
            title='TB Cases in Under 14 Years: New+Relapse vs Other',
            color_discrete_map={'New/Relapse': self.colors['new_cases'], 
                              'Other': self.colors['others']}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, title_x=0.5)
        
        return fig