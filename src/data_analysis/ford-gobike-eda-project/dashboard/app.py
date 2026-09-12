import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
warnings.filterwarnings('ignore')


# ─── DATA (REAL DATA INTEGRATION) ───

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'notebooks', 'preprocessing', 'cleaned_fordgobike_data.csv')
    if not os.path.exists(file_path):
        file_path = "../notebooks/preprocessing/cleaned_fordgobike_data.csv"

    df = pd.read_csv(file_path)

    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
    df = df.dropna(subset=['start_time'])

    df.rename(columns={
        'start_station_name': 'start_station',
        'end_station_name': 'end_station',
        'member_gender': 'gender',
        'member_birth_year': 'birth_year',
        'member_age': 'age'
    }, inplace=True)

    if 'trip_id' not in df.columns:
        df['trip_id'] = range(1, len(df) + 1)

    df['date'] = df['start_time'].dt.date
    df['hour'] = df['start_time'].dt.hour
    df['day_of_week'] = df['start_time'].dt.day_name()
    df['month'] = df['start_time'].dt.month_name()

    if 'duration_min' not in df.columns:
        df['duration_min'] = (df['duration_sec'] / 60).round(2)

    if 'is_weekend' not in df.columns:
        df['is_weekend'] = df['start_time'].dt.dayofweek >= 5

    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df['age_group'] = pd.cut(
        df['age'], bins=[0, 25, 40, 60, 100],
        labels=['Young', 'Adult', 'Senior', 'Elder']
    )

    df['gender'] = df['gender'].fillna('Other')
    df.loc[~df['gender'].isin(['Male', 'Female']), 'gender'] = 'Other'

    df = df[(df['duration_min'] >= 1) & (df['duration_min'] <= 120)]
    df = df[(df['age'] >= 16) & (df['age'] <= 75)]
    df = df.dropna(subset=['start_station', 'end_station'])

    return df


RAW_DATA = load_data()
MIN_DATE = RAW_DATA['date'].min()
MAX_DATE = RAW_DATA['date'].max()


# ─── APP ───

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    ],
    suppress_callback_exceptions=True,
    title='GoBike Analytics Hub'
)
server = app.server


# ─── COLORS ───

C = {
    'bg':            '#0a0a0f',
    'surface':       'rgba(255,255,255,0.03)',
    'glass':         'rgba(255,255,255,0.06)',
    'glass_border':  'rgba(255,255,255,0.08)',
    'accent':        '#00d4aa',
    'accent2':       '#7b61ff',
    'accent3':       '#ff6b6b',
    'accent4':       '#ffd93d',
    'accent5':       '#4fc3f7',
    'text_primary':  '#ffffff',
    'text_secondary':'rgba(255,255,255,0.75)',
    'text_dim':      'rgba(255,255,255,0.4)',
    'grid':          'rgba(255,255,255,0.04)',
    'subscriber':    '#00d4aa',
    'customer':      '#7b61ff',
}


def base_layout(fig, title='', height=300):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Chakra Petch, sans-serif', color=C['text_secondary'], size=11),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(
            bgcolor='rgba(0,0,0,0)', borderwidth=0,
            font=dict(color=C['text_secondary'], size=10, family='Chakra Petch')
        ),
        xaxis=dict(
            gridcolor=C['grid'], zerolinecolor=C['grid'],
            tickfont=dict(color=C['text_dim'], size=9, family='Chakra Petch'),
            title_font=dict(color=C['text_secondary'], family='Chakra Petch')
        ),
        yaxis=dict(
            gridcolor=C['grid'], zerolinecolor=C['grid'],
            tickfont=dict(color=C['text_dim'], size=9, family='Chakra Petch'),
            title_font=dict(color=C['text_secondary'], family='Chakra Petch')
        ),
        title=dict(
            text=title,
            font=dict(color=C['text_primary'], size=14, family='Orbitron', weight=600),
            x=0.02, y=0.97
        ),
        height=height,
        hoverlabel=dict(
            bgcolor='rgba(10,10,15,0.95)',
            bordercolor='rgba(255,255,255,0.1)',
            font=dict(color='#fff', size=11, family='Chakra Petch')
        )
    )
    return fig


# ─── CHART FUNCTIONS ───

def chart_hourly_flow(df):
    hourly = df.groupby(['hour', 'user_type']).size().reset_index(name='count')
    fig = go.Figure()
    for utype, color, fill in [
        ('Subscriber', C['subscriber'], 'rgba(0,212,170,0.06)'),
        ('Customer',   C['customer'],   'rgba(123,97,255,0.06)'),
    ]:
        sub = hourly[hourly['user_type'] == utype].sort_values('hour')
        fig.add_trace(go.Scatter(
            x=sub['hour'], y=sub['count'], name=utype,
            mode='lines', line=dict(color=color, width=2, shape='spline', smoothing=1.3),
            fill='tozeroy', fillcolor=fill,
            hovertemplate='%{y:,} trips at %{x}:00<extra>' + utype + '</extra>',
        ))
    base_layout(fig, 'Hourly Trip Flow', 300)
    fig.update_xaxes(
        tickmode='array', tickvals=list(range(0, 24, 3)),
        ticktext=[f'{h:02d}:00' for h in range(0, 24, 3)]
    )
    return fig


def chart_weekday(df):
    order  = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    counts = df.groupby('day_of_week').size().reindex(order, fill_value=0).reset_index()
    counts.columns = ['day', 'count']
    short  = ['MON','TUE','WED','THU','FRI','SAT','SUN']
    counts['short'] = short
    colors = [C['accent'] if i < 5 else C['accent2'] for i in range(7)]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts['short'], y=counts['count'],
        marker=dict(color=colors, opacity=0.7, line=dict(width=0)),
        hovertemplate='%{x}: %{y:,} trips<extra></extra>',
    ))
    base_layout(fig, 'Weekly Distribution', 280)
    fig.update_layout(showlegend=False, bargap=0.4)
    return fig


def chart_heatmap(df):
    order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    heat  = df.groupby(['day_of_week','hour']).size().reset_index(name='trips')
    pivot = heat.pivot(index='day_of_week', columns='hour', values='trips').reindex(order).fillna(0)
    short = ['MON','TUE','WED','THU','FRI','SAT','SUN']
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f'{h:02d}' for h in range(24)],
        y=short,
        colorscale=[
            [0.0, 'rgba(10,10,15,0.9)'],
            [0.3, 'rgba(0,212,170,0.15)'],
            [0.6, 'rgba(0,212,170,0.4)'],
            [0.8, 'rgba(123,97,255,0.6)'],
            [1.0, 'rgba(123,97,255,0.9)'],
        ],
        showscale=True,
        colorbar=dict(thickness=6, len=0.8,
                      tickfont=dict(color=C['text_dim'], size=8), outlinewidth=0),
        hovertemplate='%{y} at %{x}:00<br>%{z} trips<extra></extra>',
        xgap=2, ygap=2,
    ))
    base_layout(fig, 'Activity Density Map', 260)
    return fig


def chart_user_donut(df):
    counts = df['user_type'].value_counts()
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.72,
        marker=dict(
            colors=[C['subscriber'], C['customer']],
            line=dict(color='rgba(10,10,15,0.9)', width=4)
        ),
        textfont=dict(color='rgba(0,0,0,0)', size=1),
        hovertemplate='%{label}<br>%{value:,} trips<br>%{percent}<extra></extra>',
    ))
    pct = counts.get('Subscriber', 0) / counts.sum() * 100 if counts.sum() > 0 else 0
    fig.add_annotation(
        text=f'{pct:.0f}%',
        font=dict(size=30, color='#fff', family='Orbitron', weight=700),
        showarrow=False, x=0.5, y=0.55
    )
    fig.add_annotation(
        text='SUBSCRIBERS',
        font=dict(size=8, color=C['text_dim'], family='Chakra Petch', weight=500),
        showarrow=False, x=0.5, y=0.38
    )
    base_layout(fig, 'User Composition', 280)
    return fig


def chart_gender_bars(df):
    counts = df.groupby(['gender', 'user_type']).size().reset_index(name='count')
    fig = go.Figure()
    for utype, color in [('Subscriber', C['subscriber']), ('Customer', C['customer'])]:
        sub = counts[counts['user_type'] == utype]
        fig.add_trace(go.Bar(
            name=utype, x=sub['gender'], y=sub['count'],
            marker=dict(color=color, opacity=0.75, line=dict(width=0)),
            hovertemplate='%{x} ' + utype + '<br>%{y:,} trips<extra></extra>',
        ))
    base_layout(fig, 'Gender Breakdown', 280)
    fig.update_layout(barmode='group', bargap=0.3, bargroupgap=0.1)
    return fig


def chart_age_distribution(df):
    fig = go.Figure()
    for utype, color in [('Subscriber', C['subscriber']), ('Customer', C['customer'])]:
        sub = df[df['user_type'] == utype]['age']
        fig.add_trace(go.Violin(
            y=sub, name=utype,
            fillcolor=color + '1A',
            line_color=color, meanline_visible=True,
            box_visible=True, points=False,
        ))
    base_layout(fig, 'Age Distribution', 280)
    fig.update_layout(violingap=0.4)
    return fig


def chart_duration_dist(df):
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df['duration_min'], nbinsx=50,
        marker=dict(
            color='rgba(0,212,170,0.3)',
            line=dict(color='rgba(0,212,170,0.5)', width=0.5)
        ),
        hovertemplate='%{x:.0f} min: %{y} trips<extra></extra>', name='',
    ))
    if len(df) > 0:
        med = df['duration_min'].median()
        fig.add_vline(x=med, line_dash='dash', line_color=C['accent3'], line_width=1.5,
                      annotation_text=f'MEDIAN {med:.1f}m',
                      annotation_font=dict(color=C['accent3'], size=9, family='Chakra Petch'))
    base_layout(fig, 'Duration Spread', 280)
    fig.update_xaxes(title_text='Minutes')
    fig.update_layout(showlegend=False)
    return fig


def chart_top_stations(df, col='start_station', title='Top Origin Stations'):
    top = df[col].value_counts().head(10).reset_index()
    top.columns = ['station', 'count']
    top = top.sort_values('count')
    fig = go.Figure(go.Bar(
        x=top['count'], y=top['station'], orientation='h',
        marker=dict(
            color=top['count'],
            colorscale=[[0, 'rgba(0,212,170,0.3)'], [1, 'rgba(123,97,255,0.8)']],
            opacity=0.8, line=dict(width=0),
        ),
        hovertemplate='%{y}<br>%{x:,} trips<extra></extra>',
    ))
    base_layout(fig, title, 340)
    fig.update_layout(showlegend=False)
    return fig


def chart_weekend_vs_weekday(df):
    df2 = df.copy()
    df2['period'] = df2['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
    stats = df2.groupby('period').agg(
        trips=('trip_id', 'count'),
        avg_dur=('duration_min', 'mean')
    ).reset_index()
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=['Trip Count', 'Avg Duration'],
                        horizontal_spacing=0.2)
    colors = [C['accent'], C['accent4']]
    for i, (col_name, lbl) in enumerate([('trips', 'Trips'), ('avg_dur', 'Minutes')], 1):
        fig.add_trace(go.Bar(
            x=stats['period'], y=stats[col_name],
            marker=dict(color=colors, opacity=0.75, line=dict(width=0)),
            hovertemplate='%{x}<br>%{y:,.1f} ' + lbl + '<extra></extra>',
            showlegend=False,
        ), row=1, col=i)
    base_layout(fig, 'Weekday vs Weekend', 280)
    for ann in fig.layout.annotations:
        ann.font = dict(color=C['text_secondary'], size=10, family='Chakra Petch')
    return fig


def chart_age_group_bar(df):
    order  = ['Young', 'Adult', 'Senior', 'Elder']
    colors = [C['accent'], C['accent5'], C['accent2'], C['accent3']]
    counts = df.groupby('age_group', observed=True).size().reindex(order, fill_value=0)
    fig = go.Figure(go.Bar(
        x=list(counts.index), y=list(counts.values),
        marker=dict(color=colors, opacity=0.75, line=dict(width=0)),
        hovertemplate='%{x}<br>%{y:,} trips<extra></extra>',
    ))
    base_layout(fig, 'Age Segments', 280)
    fig.update_layout(showlegend=False, bargap=0.4)
    return fig


def chart_duration_by_user(df):
    fig = go.Figure()
    for utype, color in [('Subscriber', C['subscriber']), ('Customer', C['customer'])]:
        sub = df[df['user_type'] == utype]['duration_min']
        fig.add_trace(go.Box(
            y=sub, name=utype, marker_color=color, line_color=color,
            fillcolor=color + '15', boxmean=True,
        ))
    base_layout(fig, 'Duration by User Type', 280)
    return fig


def chart_daily_trend(df):
    daily = df.groupby('date').size().reset_index(name='trips')
    daily['date'] = pd.to_datetime(daily['date'])
    daily = daily.sort_values('date')
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily['date'], y=daily['trips'],
        mode='lines+markers',
        line=dict(color=C['accent'], width=2, shape='spline', smoothing=1.2),
        marker=dict(size=4, color=C['accent'], line=dict(width=1, color=C['bg'])),
        fill='tozeroy', fillcolor='rgba(0,212,170,0.05)',
        hovertemplate='%{x|%b %d}<br>%{y:,} trips<extra></extra>',
    ))
    if len(daily) > 0:
        avg = daily['trips'].mean()
        fig.add_hline(y=avg, line_dash='dot', line_color=C['accent3'], line_width=1,
                      annotation_text=f'AVG {avg:.0f}',
                      annotation_font=dict(color=C['accent3'], size=9, family='Chakra Petch'))
    base_layout(fig, 'Daily Trip Trend', 260)
    fig.update_layout(showlegend=False)
    return fig


# ─── CSS ───

INLINE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&display=swap');

*{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:#030305;
  --accent:#00d4aa;
  --accent2:#7b61ff;
  --text:#ffffff;
  --text-sec:rgba(255,255,255,0.7);
  --text-dim:rgba(255,255,255,0.4);
}

html, body {
  cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="5" fill="%2300d4aa" stroke="white" stroke-width="1.5"/></svg>') 10 10, auto !important;
}
a, button, .nav-link, .rc-slider-handle, .filter-trigger-btn, input[type="checkbox"] {
  cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="10" r="7" fill="%237b61ff" stroke="white" stroke-width="1.5"/></svg>') 10 10, pointer !important;
}

body{
  background: linear-gradient(rgba(10,10,15,0.88), rgba(10,10,15,0.88)),
              url('https://i.postimg.cc/pVnKND7k/Symphonologie-at-The-Louvre-Jonathan-Kim.jpg') no-repeat center center fixed;
  background-size: cover;
  min-height: 100vh;
  font-family:'Chakra Petch',sans-serif;
  color:var(--text);
  overflow-x:hidden;
}

::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(0,212,170,0.3);border-radius:4px}

.nav-glass{
  position:fixed;top:0;left:0;right:0;z-index:9999;
  background: linear-gradient(rgba(5,5,8,0.75), rgba(5,5,8,0.75)),
              url('https://i.postimg.cc/W3yzWHT4/download.jpg') no-repeat center center;
  background-size: cover;
  backdrop-filter: blur(50px) saturate(200%);
  -webkit-backdrop-filter: blur(50px) saturate(200%);
  border-bottom: 1px solid rgba(0,212,170,0.2);
  height:70px;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 2.5rem;
  box-shadow: 0 4px 40px rgba(0,0,0,0.6);
}
.nav-brand{display:flex;align-items:center;gap:12px}
.nav-logo{
  width:38px;height:38px;border-radius:10px;
  background:linear-gradient(135deg,#00d4aa,#7b61ff);
  display:flex;align-items:center;justify-content:center;
  position:relative;overflow:hidden;
}
.nav-logo::after{
  content:'';position:absolute;top:-50%;left:-50%;
  width:200%;height:200%;
  background:conic-gradient(from 0deg,transparent,rgba(255,255,255,0.3),transparent);
  animation:logoSpin 4s linear infinite;
}
@keyframes logoSpin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.nav-logo i{position:relative;z-index:2;font-size:15px;color:#fff}
.nav-title{font-family:'Orbitron',sans-serif;font-size:1.15rem;font-weight:700;color:#fff;letter-spacing:0.5px}
.nav-subtitle{font-family:'Chakra Petch',sans-serif;font-size:0.65rem;color:var(--text-dim);letter-spacing:1px;text-transform:uppercase}

.nav-links{
  display:flex;align-items:center;gap:4px;
  background:rgba(0,0,0,0.4);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;padding:4px;
}
.nav-link{
  padding:8px 18px;border-radius:10px;
  font-family:'Chakra Petch',sans-serif;
  font-size:0.8rem;font-weight:600;
  color:var(--text-sec);
  transition:all 0.3s ease;
  border:none;background:transparent;
  position:relative;letter-spacing:0.3px;
}
.nav-link:hover{color:var(--text);background:rgba(255,255,255,0.06)}
.nav-link.active{
  color:#fff;
  background:rgba(0,212,170,0.15);
  box-shadow:0 0 15px rgba(0,212,170,0.15);
}
.nav-link.active::before{
  content:'';position:absolute;bottom:-1px;left:50%;
  transform:translateX(-50%);
  width:24px;height:2px;border-radius:1px;
  background:#00d4aa;
}

.filter-trigger-btn{
  background:transparent !important;
  border:1px solid #00d4aa !important;
  border-radius:12px !important;
  color:#00d4aa !important;
  font-family:'Orbitron',sans-serif !important;
  font-size:0.8rem !important;
  font-weight:700 !important;
  letter-spacing:1px;
  padding:8px 25px !important;
  box-shadow:inset 0 0 10px rgba(0,212,170,0.1), 0 0 15px rgba(0,212,170,0.2);
  transition:all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
}
.filter-trigger-btn:hover{
  background:rgba(0,212,170,0.15) !important;
  transform:translateY(-2px);
  box-shadow:inset 0 0 15px rgba(0,212,170,0.3), 0 0 25px rgba(0,212,170,0.4) !important;
  text-shadow:0 0 5px #00d4aa;
}

.custom-filter-sidebar{
  background: linear-gradient(rgba(5,5,8,0.85), rgba(5,5,8,0.95)),
              url('https://i.postimg.cc/W3yzWHT4/download.jpg') no-repeat center center !important;
  background-size: cover !important;
  backdrop-filter: blur(50px) saturate(200%) !important;
  -webkit-backdrop-filter: blur(50px) saturate(200%) !important;
  border-left: 2px solid #00d4aa !important;
  width: 450px !important;
  color: #fff !important;
  box-shadow: -15px 0 50px rgba(0,212,170,0.15) !important;
}
.offcanvas-header{
  border-bottom:1px solid rgba(0,212,170,0.2) !important;
  padding:1.5rem !important;
  background:rgba(0,0,0,0.3);
}
.offcanvas-title{
  font-family:'Orbitron',sans-serif !important;
  font-weight:700 !important;
  letter-spacing:2px;
  color:#00d4aa !important;
  font-size:1.3rem !important;
  text-shadow:0 0 10px rgba(0,212,170,0.5);
}
.btn-close{filter:invert(1) sepia(1) saturate(5) hue-rotate(130deg) !important;opacity:1 !important}
.offcanvas-body{padding:2rem 1.5rem !important}

.filter-vertical-stack{display:flex;flex-direction:column;gap:20px}
.filter-group{
  background:rgba(255,255,255,0.02);
  border:1px solid rgba(255,255,255,0.05);
  border-radius:15px;padding:20px;
  position:relative;transition:all 0.3s ease;overflow:hidden;
}
.filter-group::before{
  content:'';position:absolute;top:0;left:0;width:3px;height:100%;
  background:#7b61ff;transition:all 0.3s ease;
}
.filter-group:hover{background:rgba(255,255,255,0.04);border-color:rgba(123,97,255,0.4)}
.filter-group:hover::before{background:#00d4aa;box-shadow:0 0 15px #00d4aa}
.filter-group label.group-label{
  font-family:'Orbitron',monospace;font-size:0.75rem;color:#fff;
  text-transform:uppercase;letter-spacing:1.5px;font-weight:700;
  display:block;margin-bottom:15px;
}

/* ════════════════════════════════════════
   DATE RANGE PICKER — Dark Theme Fix
   ════════════════════════════════════════ */
.DateRangePicker,
.DateRangePicker > div {
  width: 100% !important;
  display: block !important;
}

.DateRangePickerInput,
.DateRangePickerInput__withBorder,
.DateRangePickerInput__showClearDates {
  background-color: rgba(0, 0, 0, 0.65) !important;
  background: rgba(0, 0, 0, 0.65) !important;
  border: 1px solid rgba(0, 212, 170, 0.45) !important;
  border-radius: 10px !important;
  padding: 6px 12px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  width: 100% !important;
  box-shadow: none !important;
}

.DateInput {
  background: transparent !important;
  background-color: transparent !important;
  width: 42% !important;
}

.DateInput_input,
.DateInput_input__1,
.DateInput_input__focused,
.DateInput_input__focused_2 {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  border-bottom: none !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  caret-color: #00d4aa !important;
  font-family: 'Orbitron', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  text-align: center !important;
  padding: 8px 4px !important;
  letter-spacing: 0.5px !important;
  outline: none !important;
  box-shadow: none !important;
}

.DateInput_input::placeholder {
  color: rgba(255, 255, 255, 0.4) !important;
  -webkit-text-fill-color: rgba(255, 255, 255, 0.4) !important;
}

.DateRangePickerInput_arrow,
.DateRangePickerInput_arrow_svg {
  color: #00d4aa !important;
  fill: #00d4aa !important;
}

.DateRangePickerInput_arrow_svg path {
  fill: #00d4aa !important;
}

.DateRangePicker_picker,
.DateRangePicker_picker__directionLeft,
.DateRangePicker_picker__directionRight {
  background-color: #0d0d14 !important;
  background: #0d0d14 !important;
  border: 1px solid rgba(0, 212, 170, 0.3) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7) !important;
  z-index: 99999 !important;
}

.CalendarMonth,
.CalendarMonthGrid,
.DayPicker,
.DayPicker__horizontal,
.DayPicker__withBorder {
  background: #0d0d14 !important;
  background-color: #0d0d14 !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 12px !important;
}

.CalendarMonth_caption,
.CalendarMonth_caption strong {
  color: #ffffff !important;
  font-family: 'Orbitron', sans-serif !important;
  font-size: 0.9rem !important;
}

.DayPickerNavigation_button,
.DayPickerNavigation_button__horizontalDefault {
  background: rgba(0, 212, 170, 0.12) !important;
  border: 1px solid rgba(0, 212, 170, 0.35) !important;
  border-radius: 8px !important;
}

.DayPickerNavigation_svg__horizontal {
  fill: #00d4aa !important;
}

.CalendarDay__default {
  background: transparent !important;
  background-color: transparent !important;
  color: rgba(255, 255, 255, 0.85) !important;
  border: 1px solid rgba(255, 255, 255, 0.04) !important;
  font-family: 'Chakra Petch', sans-serif !important;
}

.CalendarDay__default:hover {
  background: rgba(0, 212, 170, 0.18) !important;
  color: #00d4aa !important;
  border-color: rgba(0, 212, 170, 0.35) !important;
}

.CalendarDay__selected,
.CalendarDay__selected:active,
.CalendarDay__selected:hover {
  background: #00d4aa !important;
  background-color: #00d4aa !important;
  color: #0a0a0f !important;
  border-color: #00d4aa !important;
  font-weight: 700 !important;
}

.CalendarDay__selected_span {
  background: rgba(0, 212, 170, 0.22) !important;
  color: #00d4aa !important;
  border-color: rgba(0, 212, 170, 0.12) !important;
}

.CalendarDay__hovered_span,
.CalendarDay__hovered_span:hover {
  background: rgba(0, 212, 170, 0.14) !important;
  color: #00d4aa !important;
}

.CalendarDay__blocked_out_of_range {
  color: rgba(255, 255, 255, 0.15) !important;
}

.DayPickerKeyboardShortcuts_show {
  display: none !important;
}

.DayPicker_weekHeader_li small {
  color: rgba(0, 212, 170, 0.75) !important;
  font-family: 'Orbitron', sans-serif !important;
  font-size: 0.65rem !important;
  font-weight: 600 !important;
}

/* ════════════════════════════════════════
   RANGE SLIDER — Remove white boxes
   ════════════════════════════════════════ */
.rc-slider {
  margin-top: 18px !important;
  margin-bottom: 10px !important;
  padding: 0 !important;
  background: transparent !important;
}

.rc-slider-rail {
  background: rgba(255, 255, 255, 0.12) !important;
  height: 6px !important;
  border-radius: 4px !important;
}

.rc-slider-track {
  background: linear-gradient(90deg, #00d4aa, #7b61ff) !important;
  height: 6px !important;
  border-radius: 4px !important;
}

.rc-slider-handle {
  background-color: #0a0a0f !important;
  border: 3px solid #00d4aa !important;
  box-shadow: 0 0 12px rgba(0, 212, 170, 0.7) !important;
  width: 18px !important;
  height: 18px !important;
  margin-top: -6px !important;
  opacity: 1 !important;
  z-index: 2 !important;
}

.rc-slider-handle:hover,
.rc-slider-handle:active,
.rc-slider-handle-dragging {
  border-color: #00d4aa !important;
  box-shadow: 0 0 18px #00d4aa !important;
  background-color: #0a0a0f !important;
}

.rc-slider-dot {
  background: transparent !important;
  border: none !important;
  width: 0 !important;
  height: 0 !important;
  display: none !important;
}

.rc-slider-dot-active {
  display: none !important;
}

.rc-slider-mark {
  top: 18px !important;
  background: transparent !important;
  font-size: 0 !important;
}

.rc-slider-mark-text,
.rc-slider-mark-text-active {
  color: rgba(255, 255, 255, 0.75) !important;
  -webkit-text-fill-color: rgba(255, 255, 255, 0.75) !important;
  font-family: 'Orbitron', sans-serif !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  text-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  line-height: 1 !important;
  white-space: nowrap !important;
}

.rc-slider-mark-text-active {
  color: #00d4aa !important;
  -webkit-text-fill-color: #00d4aa !important;
  font-weight: 700 !important;
}

.rc-slider-tooltip {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.rc-slider-tooltip-inner {
  background: rgba(10, 10, 15, 0.95) !important;
  border: 1px solid rgba(0, 212, 170, 0.35) !important;
  color: #00d4aa !important;
  -webkit-text-fill-color: #00d4aa !important;
  font-family: 'Orbitron', sans-serif !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 4px 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}

.rc-slider-tooltip-arrow {
  border-top-color: rgba(0, 212, 170, 0.35) !important;
  border-bottom-color: rgba(0, 212, 170, 0.35) !important;
}

.rc-slider-tooltip-placement-top .rc-slider-tooltip-arrow {
  border-top-color: rgba(10, 10, 15, 0.95) !important;
}

/* Checkboxes */
.dash-checklist{display:flex;flex-wrap:wrap;gap:12px}
.dash-checklist label{
  color:#fff !important;
  font-size:0.85rem !important;
  font-family:'Chakra Petch' !important;
  display:flex !important;
  align-items:center;
  background:rgba(0,0,0,0.3);
  padding:6px 12px;
  border-radius:8px;
  border:1px solid rgba(255,255,255,0.1);
  transition:all 0.2s ease;
}
.dash-checklist label:hover{background:rgba(0,212,170,0.1);border-color:rgba(0,212,170,0.3)}
.dash-checklist input[type="checkbox"]{
  appearance:none;-webkit-appearance:none;
  width:18px;height:18px;
  background:rgba(0,0,0,0.5);
  border:1px solid #7b61ff;
  border-radius:4px;
  margin-right:10px !important;
  position:relative;transition:all 0.3s;
  flex-shrink:0;
}
.dash-checklist input[type="checkbox"]:checked{
  background:rgba(0,212,170,0.2);
  border-color:#00d4aa;
  box-shadow:0 0 10px rgba(0,212,170,0.5);
}
.dash-checklist input[type="checkbox"]:checked::after{
  content:'';position:absolute;
  left:5px;top:1px;width:6px;height:10px;
  border:solid #00d4aa;border-width:0 2px 2px 0;
  transform:rotate(45deg);
}

#duration-display{
  font-size:0.9rem;
  color:#00d4aa;
  text-align:center;
  margin-top:28px;
  font-family:'Orbitron',sans-serif;
  font-weight:bold;
  text-shadow:0 0 5px rgba(0,212,170,0.5);
  background:rgba(0,212,170,0.06);
  border:1px solid rgba(0,212,170,0.15);
  border-radius:8px;
  padding:6px 12px;
  letter-spacing:0.5px;
}

.page-container{max-width:1550px;margin:0 auto;padding:100px 2rem 4rem;position:relative;z-index:1}

@keyframes slideInUp{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:translateY(0)}}
.section-wrap{animation:slideInUp 0.8s cubic-bezier(0.15,0.85,0.35,1) both}

.sec-header{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid rgba(255,255,255,0.08)}
.sec-header-left{display:flex;align-items:center;gap:16px}
.sec-number{font-family:'Orbitron',monospace;font-size:0.75rem;font-weight:700;color:var(--accent);padding:4px 10px;border-radius:6px;background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.15);letter-spacing:1px}
.sec-title{font-family:'Orbitron',sans-serif;font-size:1.35rem;font-weight:700;color:#fff;letter-spacing:-0.5px}
.sec-desc{font-family:'Chakra Petch',sans-serif;font-size:0.8rem;color:var(--text-dim);letter-spacing:0.3px}

.g-panel{background:rgba(10,10,15,0.45);backdrop-filter:blur(25px) saturate(1.5);-webkit-backdrop-filter:blur(25px) saturate(1.5);border:1px solid rgba(255,255,255,0.06);border-radius:20px;padding:1.5rem;position:relative;overflow:hidden;transition:all 0.4s cubic-bezier(0.4,0,0.2,1)}
.g-panel::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.15),transparent)}
.g-panel:hover{border-color:rgba(255,255,255,0.15);background:rgba(10,10,15,0.6);transform:translateY(-3px);box-shadow:0 20px 50px rgba(0,0,0,0.5)}

.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:2.5rem}
.kpi-item{background:rgba(10,10,15,0.5);backdrop-filter:blur(25px);-webkit-backdrop-filter:blur(25px);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:1.3rem 1.4rem;position:relative;overflow:hidden;transition:all 0.4s cubic-bezier(0.4,0,0.2,1)}
.kpi-item::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--kpi-color,rgba(255,255,255,0.15)),transparent)}
.kpi-item::after{content:'';position:absolute;top:-40px;right:-20px;width:100px;height:100px;border-radius:50%;background:var(--kpi-color,rgba(0,212,170,0.06));filter:blur(40px);opacity:0.5}
.kpi-item:hover{transform:translateY(-4px) scale(1.02);border-color:var(--kpi-color,rgba(0,212,170,0.3));box-shadow:0 16px 48px rgba(0,0,0,0.5)}
.kpi-icon{width:42px;height:42px;border-radius:12px;background:var(--kpi-color-bg,rgba(0,212,170,0.08));border:1px solid var(--kpi-color-border,rgba(0,212,170,0.15));display:flex;align-items:center;justify-content:center;margin-bottom:1rem;font-size:16px;color:var(--kpi-color-text,#00d4aa)}
.kpi-value{font-family:'Orbitron',sans-serif;font-size:1.7rem;font-weight:800;color:#fff;letter-spacing:-0.5px;line-height:1;margin-bottom:8px}
.kpi-label{font-family:'Chakra Petch',sans-serif;font-size:0.65rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;font-weight:500;margin-bottom:8px}
.kpi-tag{display:inline-flex;align-items:center;gap:4px;font-family:'Chakra Petch',sans-serif;font-size:0.6rem;font-weight:600;padding:3px 8px;border-radius:6px}
.kpi-tag.green{background:rgba(0,212,170,0.1);color:#00d4aa;border:1px solid rgba(0,212,170,0.15)}
.kpi-tag.blue{background:rgba(79,195,247,0.1);color:#4fc3f7;border:1px solid rgba(79,195,247,0.15)}
.kpi-tag.purple{background:rgba(123,97,255,0.1);color:#7b61ff;border:1px solid rgba(123,97,255,0.15)}

.chart-row{display:grid;gap:18px;margin-bottom:18px}
.chart-2{grid-template-columns:1fr 1fr}
.chart-3{grid-template-columns:1fr 1fr 1fr}
.chart-1-2{grid-template-columns:1.5fr 1fr}
.chart-2-1{grid-template-columns:1fr 1.5fr}
.chart-3-1{grid-template-columns:2fr 1fr}
@media(max-width:768px){.chart-2,.chart-3,.chart-1-2,.chart-2-1,.chart-3-1{grid-template-columns:1fr}}

.insight-item{display:flex;gap:12px;padding:14px 16px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:14px;transition:all 0.3s ease;margin-bottom:10px}
.insight-item:hover{border-color:rgba(0,212,170,0.15);background:rgba(0,212,170,0.03);transform:translateX(4px)}
.insight-icon{width:36px;height:36px;border-radius:10px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:14px}
.insight-icon.green{background:rgba(0,212,170,0.1);color:#00d4aa;border:1px solid rgba(0,212,170,0.15)}
.insight-icon.purple{background:rgba(123,97,255,0.1);color:#7b61ff;border:1px solid rgba(123,97,255,0.15)}
.insight-icon.red{background:rgba(255,107,107,0.1);color:#ff6b6b;border:1px solid rgba(255,107,107,0.15)}
.insight-icon.yellow{background:rgba(255,217,61,0.1);color:#ffd93d;border:1px solid rgba(255,217,61,0.15)}
.insight-icon.blue{background:rgba(79,195,247,0.1);color:#4fc3f7;border:1px solid rgba(79,195,247,0.15)}
.insight-text{font-family:'Chakra Petch',sans-serif;font-size:0.82rem;color:var(--text-sec);line-height:1.6}
.insight-text strong{color:#fff;font-weight:600}

.rank-item{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:10px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);margin-bottom:6px;transition:all 0.3s ease}
.rank-item:hover{background:rgba(0,212,170,0.04);border-color:rgba(0,212,170,0.1)}
.rank-num{width:24px;height:24px;border-radius:7px;flex-shrink:0;background:linear-gradient(135deg,#00d4aa,#7b61ff);display:flex;align-items:center;justify-content:center;font-family:'Orbitron',monospace;font-size:0.65rem;font-weight:700;color:#fff}
.rank-name{flex:1;font-family:'Chakra Petch',sans-serif;font-size:0.8rem;color:var(--text-sec);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rank-bar{flex:0 0 80px;height:3px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden}
.rank-bar-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,#00d4aa,#7b61ff)}
.rank-val{font-family:'Orbitron',monospace;font-size:0.75rem;font-weight:600;color:#00d4aa;min-width:40px;text-align:right}

.footer-area{text-align:center;margin-top:3rem;padding:2rem 0;border-top:1px solid rgba(255,255,255,0.06)}
.footer-brand{font-family:'Orbitron',sans-serif;font-size:0.9rem;font-weight:600;color:var(--text-dim);letter-spacing:1px;margin-bottom:4px}
.footer-sub{font-family:'Chakra Petch',sans-serif;font-size:0.65rem;color:rgba(255,255,255,0.25);letter-spacing:0.5px}

.stg-1{animation:slideInUp 0.6s 0.05s ease-out both}
.stg-2{animation:slideInUp 0.6s 0.1s ease-out both}
.stg-3{animation:slideInUp 0.6s 0.15s ease-out both}
.stg-4{animation:slideInUp 0.6s 0.2s ease-out both}
.stg-5{animation:slideInUp 0.6s 0.25s ease-out both}
.stg-6{animation:slideInUp 0.6s 0.3s ease-out both}
.stg-7{animation:slideInUp 0.6s 0.35s ease-out both}
.stg-8{animation:slideInUp 0.6s 0.4s ease-out both}
.micro-line{width:40px;height:2px;border-radius:1px;background:linear-gradient(90deg,#00d4aa,#7b61ff);margin-bottom:12px}

/* CUSTOM DATE INPUTS */
.custom-date-row{
  display:flex;
  align-items:center;
  gap:10px;
  width:100%;
}

.date-arrow{
  color:#00d4aa;
  font-family:'Orbitron',sans-serif;
  font-size:1rem;
  font-weight:700;
  flex-shrink:0;
}

.custom-date-input{
  flex:1;
  width:100%;
  background:rgba(0,0,0,0.65) !important;
  border:1px solid rgba(0,212,170,0.45) !important;
  border-radius:10px !important;
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  font-family:'Orbitron',sans-serif !important;
  font-size:0.82rem !important;
  font-weight:600 !important;
  padding:10px 12px !important;
  outline:none !important;
  box-shadow:none !important;
  color-scheme:dark;
}

.custom-date-input:focus{
  border-color:#00d4aa !important;
  box-shadow:0 0 12px rgba(0,212,170,0.35) !important;
}

.custom-date-input::-webkit-calendar-picker-indicator{
  filter:invert(1) sepia(1) saturate(5) hue-rotate(130deg);
  cursor:pointer;
  opacity:0.85;
}

/* DURATION SLIDER */
.custom-duration-slider .rc-slider-mark,
.custom-duration-slider .rc-slider-mark-text,
.custom-duration-slider .rc-slider-dot{
  display:none !important;
  width:0 !important;
  height:0 !important;
  background:transparent !important;
  border:none !important;
}

.custom-duration-slider .rc-slider-step{
  display:none !important;
}

.custom-duration-slider .dash-range-slider-input{
  display:none !important;
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
}

.custom-duration-slider .rc-slider-rail{
  background:rgba(255,255,255,0.12) !important;
  height:6px !important;
}

.custom-duration-slider .rc-slider-track{
  background:linear-gradient(90deg,#00d4aa,#7b61ff) !important;
  height:6px !important;
}

.custom-duration-slider .rc-slider-handle{
  background:#0a0a0f !important;
  border:3px solid #00d4aa !important;
  box-shadow:0 0 12px rgba(0,212,170,0.7) !important;
  width:18px !important;
  height:18px !important;
  margin-top:-6px !important;
  opacity:1 !important;
}

.custom-duration-slider .rc-slider-tooltip-inner{
  background:rgba(10,10,15,0.95) !important;
  border:1px solid rgba(0,212,170,0.35) !important;
  color:#00d4aa !important;
  font-family:'Orbitron',sans-serif !important;
  font-size:11px !important;
  border-radius:6px !important;
}
"""

app.index_string = f"""<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>{INLINE_CSS}</style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>"""


# ─── LAYOUT HELPERS ───

def build_nav():
    return html.Nav(className='nav-glass', children=[
        html.Div(className='nav-brand', children=[
            html.Div(className='nav-logo', children=[html.I(className='fas fa-bicycle')]),
            html.Div([
                html.Div('GoBike Analytics', className='nav-title'),
                html.Div('SAN FRANCISCO // 2019', className='nav-subtitle'),
            ])
        ]),
        html.Div(className='nav-links', id='nav-links', children=[
            html.Button('Overview',     className='nav-link active', id='nav-overview',     n_clicks=0),
            html.Button('Temporal',     className='nav-link',        id='nav-temporal',     n_clicks=0),
            html.Button('Demographics', className='nav-link',        id='nav-demographics', n_clicks=0),
            html.Button('Stations',     className='nav-link',        id='nav-stations',     n_clicks=0),
            html.Button('Insights',     className='nav-link',        id='nav-insights',     n_clicks=0),
        ]),
        dbc.Button([
            html.I(className="fas fa-sliders-h", style={"marginRight": "10px"}),
            "DATA FILTERS"
        ], id="btn-open-filters", className="filter-trigger-btn", n_clicks=0)
    ])


def build_filters():
    min_date_str = str(MIN_DATE)
    max_date_str = str(MAX_DATE)

    return html.Div(className='filter-vertical-stack', children=[

        # DATE RANGE (custom dark inputs)
        html.Div(className='filter-group', children=[
            html.Label('DATE RANGE', className='group-label'),
            html.Div(className='custom-date-row', children=[
                dcc.Input(
                    id='filter-start-date',
                    type='text',
                    value=min_date_str,
                    placeholder='YYYY-MM-DD',
                    className='custom-date-input',
                ),
                html.Span('→', className='date-arrow'),
                dcc.Input(
                    id='filter-end-date',
                    type='text',
                    value=max_date_str,
                    placeholder='YYYY-MM-DD',
                    className='custom-date-input',
                ),
            ]),
        ]),

        # USER TYPE
        html.Div(className='filter-group', children=[
            html.Label('USER TYPE', className='group-label'),
            dcc.Checklist(
                id='filter-user-type',
                options=[
                    {'label': 'Subscriber', 'value': 'Subscriber'},
                    {'label': 'Customer',   'value': 'Customer'},
                ],
                value=['Subscriber', 'Customer'],
            ),
        ]),

        # GENDER
        html.Div(className='filter-group', children=[
            html.Label('GENDER', className='group-label'),
            dcc.Checklist(
                id='filter-gender',
                options=[
                    {'label': 'Male',   'value': 'Male'},
                    {'label': 'Female', 'value': 'Female'},
                    {'label': 'Other',  'value': 'Other'},
                ],
                value=['Male', 'Female', 'Other'],
            ),
        ]),

        # AGE GROUP
        html.Div(className='filter-group', children=[
            html.Label('AGE GROUP', className='group-label'),
            dcc.Checklist(
                id='filter-age-group',
                options=[
                    {'label': 'Young',  'value': 'Young'},
                    {'label': 'Adult',  'value': 'Adult'},
                    {'label': 'Senior', 'value': 'Senior'},
                    {'label': 'Elder',  'value': 'Elder'},
                ],
                value=['Young', 'Adult', 'Senior', 'Elder'],
            ),
        ]),

        # DURATION (without marks)
        html.Div(className='filter-group', children=[
            html.Label('DURATION (MIN)', className='group-label'),
            dcc.RangeSlider(
                id='filter-duration',
                min=1,
                max=120,
                step=1,
                value=[1, 60],
                marks={},
                tooltip={
                    'placement': 'bottom',
                    'always_visible': True,
                    'style': {
                        'color': '#00d4aa',
                        'fontFamily': 'Orbitron',
                        'fontSize': '11px',
                        'backgroundColor': 'rgba(10,10,15,0.95)',
                        'border': '1px solid rgba(0,212,170,0.35)',
                    },
                },
                allowCross=False,
                className='custom-duration-slider',
            ),
            html.Div(id='duration-display'),
        ]),
    ])


def build_kpi(value, label, icon, tag_text, tag_cls, color, delay):
    return html.Div(
        className=f'kpi-item {delay}',
        style={
            '--kpi-color':        color,
            '--kpi-color-bg':     f'{color}14',
            '--kpi-color-border': f'{color}26',
            '--kpi-color-text':   color,
        },
        children=[
            html.Div(className='kpi-icon', children=[html.I(className=icon)]),
            html.Div(value,    className='kpi-value'),
            html.Div(label,    className='kpi-label'),
            html.Div(tag_text, className=f'kpi-tag {tag_cls}'),
        ]
    )


def build_station_ranks(df, col='start_station', n=8):
    top   = df[col].value_counts().head(n)
    mx    = top.max() if len(top) > 0 else 1
    items = []
    for i, (station, count) in enumerate(top.items(), 1):
        pct = count / mx * 100
        items.append(
            html.Div(className='rank-item', children=[
                html.Div(str(i), className='rank-num'),
                html.Div(station, className='rank-name'),
                html.Div(className='rank-bar', children=[
                    html.Div(className='rank-bar-fill', style={'width': f'{pct}%'})
                ]),
                html.Div(f'{count:,}', className='rank-val'),
            ])
        )
    return items


def build_insights_list(df):
    if len(df) == 0:
        return [html.Div("No data matches the selected filters.", className='insight-text',
                         style={'padding': '1rem', 'color': 'rgba(255,255,255,0.4)'})]

    sub_pct   = df['user_type'].value_counts(normalize=True).get('Subscriber', 0) * 100
    peak_hour = df.groupby('hour').size().idxmax()
    top_start = df['start_station'].value_counts().index[0]
    avg_dur   = df['duration_min'].mean()
    top_gender= df['gender'].value_counts().index[0]
    wknd      = df[df['is_weekend']]['duration_min'].mean() if len(df[df['is_weekend']]) > 0 else 0
    wkday     = df[~df['is_weekend']]['duration_min'].mean() if len(df[~df['is_weekend']]) > 0 else 0

    items = [
        ('fas fa-chart-line', 'green',  [html.Strong(f'{sub_pct:.0f}%'), ' of all trips are by Subscribers, indicating strong platform loyalty.']),
        ('fas fa-clock',      'purple', [f'Peak activity occurs at ', html.Strong(f'{peak_hour:02d}:00'), ', aligning with typical commute windows.']),
        ('fas fa-map-marker-alt','red', [html.Strong(top_start), ' is the highest-traffic origin station.']),
        ('fas fa-stopwatch',  'yellow', [f'Average trip duration is ', html.Strong(f'{avg_dur:.1f} minutes'), '.']),
        ('fas fa-users',      'blue',   [html.Strong(top_gender), ' riders dominate usage across the network.']),
        ('fas fa-calendar-alt','green', [f'Weekend trips average ', html.Strong(f'{wknd:.1f} min'),
                                         f' vs ', html.Strong(f'{wkday:.1f} min'), ' on weekdays.']),
    ]
    return [
        html.Div(className='insight-item', children=[
            html.Div(className=f'insight-icon {cls}', children=[html.I(className=icon)]),
            html.Div(children, className='insight-text'),
        ]) for icon, cls, children in items
    ]


# ─── SECTIONS ───

def section_overview():
    return html.Div(id='section-overview', className='section-wrap', children=[
        html.Div(className='sec-header', children=[
            html.Div(className='sec-header-left', children=[
                html.Span('01', className='sec-number'),
                html.Div([
                    html.Div('System Overview', className='sec-title'),
                    html.Div('Core network performance and high-level metrics', className='sec-desc'),
                ]),
            ]),
        ]),
        html.Div(id='kpi-grid', className='kpi-grid'),
        html.Div(className='chart-row chart-3-1', children=[
            html.Div(className='g-panel stg-5', children=[dcc.Graph(id='chart-daily',      config={'displayModeBar': False})]),
            html.Div(className='g-panel stg-6', children=[dcc.Graph(id='chart-user-donut', config={'displayModeBar': False})]),
        ]),
    ])


def section_temporal():
    return html.Div(id='section-temporal', className='section-wrap', children=[
        html.Div(className='sec-header', children=[
            html.Div(className='sec-header-left', children=[
                html.Span('02', className='sec-number'),
                html.Div([
                    html.Div('Temporal Analysis', className='sec-title'),
                    html.Div('Time-based patterns and activity rhythms', className='sec-desc'),
                ]),
            ]),
        ]),
        html.Div(className='chart-row chart-2', children=[
            html.Div(className='g-panel stg-3', children=[dcc.Graph(id='chart-hourly',  config={'displayModeBar': False})]),
            html.Div(className='g-panel stg-4', children=[dcc.Graph(id='chart-weekday', config={'displayModeBar': False})]),
        ]),
        html.Div(className='chart-row chart-1-2', children=[
            html.Div(className='g-panel stg-5', children=[dcc.Graph(id='chart-heatmap', config={'displayModeBar': False})]),
            html.Div(className='g-panel stg-6', children=[dcc.Graph(id='chart-weekend', config={'displayModeBar': False})]),
        ]),
    ])


def section_demographics():
    return html.Div(id='section-demographics', className='section-wrap', children=[
        html.Div(className='sec-header', children=[
            html.Div(className='sec-header-left', children=[
                html.Span('03', className='sec-number'),
                html.Div([
                    html.Div('Demographics', className='sec-title'),
                    html.Div('User segmentation and behavioral profiling', className='sec-desc'),
                ]),
            ]),
        ]),
        html.Div(className='chart-row chart-3', children=[
            html.Div(className='g-panel stg-3', children=[dcc.Graph(id='chart-gender',     config={'displayModeBar': False})]),
            html.Div(className='g-panel stg-4', children=[dcc.Graph(id='chart-age-group',  config={'displayModeBar': False})]),
            html.Div(className='g-panel stg-5', children=[dcc.Graph(id='chart-age-violin', config={'displayModeBar': False})]),
        ]),
        html.Div(className='chart-row chart-2', children=[
            html.Div(className='g-panel stg-6', children=[dcc.Graph(id='chart-dur-dist', config={'displayModeBar': False})]),
            html.Div(className='g-panel stg-7', children=[dcc.Graph(id='chart-dur-user', config={'displayModeBar': False})]),
        ]),
    ])


def section_stations():
    return html.Div(id='section-stations', className='section-wrap', children=[
        html.Div(className='sec-header', children=[
            html.Div(className='sec-header-left', children=[
                html.Span('04', className='sec-number'),
                html.Div([
                    html.Div('Station Network', className='sec-title'),
                    html.Div('Geographic distribution and popular routes', className='sec-desc'),
                ]),
            ]),
        ]),
        html.Div(className='chart-row chart-2', children=[
            html.Div(className='g-panel stg-3', children=[dcc.Graph(id='chart-top-start', config={'displayModeBar': False})]),
            html.Div(className='g-panel stg-4', children=[dcc.Graph(id='chart-top-end',   config={'displayModeBar': False})]),
        ]),
        html.Div(className='chart-row chart-2', children=[
            html.Div(className='g-panel stg-5', style={'padding': '1.5rem'}, children=[
                html.Div(className='micro-line'),
                html.Div('Top Origin Stations',
                         style={'fontFamily': 'Orbitron', 'fontSize': '0.9rem',
                                'fontWeight': '600', 'color': '#fff', 'marginBottom': '1rem'}),
                html.Div(id='rank-start'),
            ]),
            html.Div(className='g-panel stg-6', style={'padding': '1.5rem'}, children=[
                html.Div(className='micro-line'),
                html.Div('Top Destination Stations',
                         style={'fontFamily': 'Orbitron', 'fontSize': '0.9rem',
                                'fontWeight': '600', 'color': '#fff', 'marginBottom': '1rem'}),
                html.Div(id='rank-end'),
            ]),
        ]),
    ])


def section_insights():
    return html.Div(id='section-insights', className='section-wrap', children=[
        html.Div(className='sec-header', children=[
            html.Div(className='sec-header-left', children=[
                html.Span('05', className='sec-number'),
                html.Div([
                    html.Div('Intelligence Report', className='sec-title'),
                    html.Div('Auto-generated analytical findings', className='sec-desc'),
                ]),
            ]),
        ]),
        html.Div(className='g-panel stg-3', style={'padding': '1.5rem'}, children=[
            html.Div(id='insights-list'),
        ]),
    ])


# ─── FULL LAYOUT ───

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    build_nav(),

    dbc.Offcanvas(
        build_filters(),
        id="filter-offcanvas",
        title="DATA FILTERS",
        is_open=False,
        placement="end",
        className="custom-filter-sidebar"
    ),

    html.Div(className='page-container', children=[
        section_overview(),
        section_temporal(),
        section_demographics(),
        section_stations(),
        section_insights(),
        html.Div(className='footer-area', children=[
            html.Div('GoBike Analytics Hub', className='footer-brand'),
            html.Div('ORBITRON // CHAKRA PETCH // PLOTLY DASH // 2024', className='footer-sub'),
        ]),
    ]),
])


# ─── CALLBACKS ───

@app.callback(
    [
        Output('nav-overview',     'className'),
        Output('nav-temporal',     'className'),
        Output('nav-demographics', 'className'),
        Output('nav-stations',     'className'),
        Output('nav-insights',     'className'),
        Output('section-overview',     'style'),
        Output('section-temporal',     'style'),
        Output('section-demographics', 'style'),
        Output('section-stations',     'style'),
        Output('section-insights',     'style'),
    ],
    [
        Input('nav-overview',     'n_clicks'),
        Input('nav-temporal',     'n_clicks'),
        Input('nav-demographics', 'n_clicks'),
        Input('nav-stations',     'n_clicks'),
        Input('nav-insights',     'n_clicks'),
    ],
    prevent_initial_call=False,
)
def handle_nav(n1, n2, n3, n4, n5):
    ctx  = callback_context
    show = {'display': 'block', 'marginBottom': '2.5rem'}
    hide = {'display': 'none'}

    if not ctx.triggered or ctx.triggered[0]['prop_id'] == '.':
        return ('nav-link active', 'nav-link', 'nav-link', 'nav-link', 'nav-link',
                show, show, show, show, show)

    btn     = ctx.triggered[0]['prop_id'].split('.')[0]
    classes = ['nav-link'] * 5
    styles  = [hide] * 5
    mapping = {
        'nav-overview': 0, 'nav-temporal': 1, 'nav-demographics': 2,
        'nav-stations': 3, 'nav-insights': 4
    }
    if btn in mapping:
        idx          = mapping[btn]
        classes[idx] = 'nav-link active'
        styles[idx]  = show

    return (*classes, *styles)


@app.callback(
    Output("filter-offcanvas", "is_open"),
    Input("btn-open-filters", "n_clicks"),
    State("filter-offcanvas", "is_open"),
)
def toggle_filter_sidebar(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [
        Output('kpi-grid',        'children'),
        Output('chart-daily',     'figure'),
        Output('chart-user-donut','figure'),
        Output('chart-hourly',    'figure'),
        Output('chart-weekday',   'figure'),
        Output('chart-heatmap',   'figure'),
        Output('chart-weekend',   'figure'),
        Output('chart-gender',    'figure'),
        Output('chart-age-group', 'figure'),
        Output('chart-age-violin','figure'),
        Output('chart-dur-dist',  'figure'),
        Output('chart-dur-user',  'figure'),
        Output('chart-top-start', 'figure'),
        Output('chart-top-end',   'figure'),
        Output('rank-start',      'children'),
        Output('rank-end',        'children'),
        Output('insights-list',   'children'),
        Output('duration-display','children'),
    ],
    [
        Input('filter-start-date', 'value'),
        Input('filter-end-date',   'value'),
        Input('filter-user-type', 'value'),
        Input('filter-gender',    'value'),
        Input('filter-age-group', 'value'),
        Input('filter-duration',  'value'),
    ]
)
def update_all(start_date, end_date, user_types, genders, age_groups, dur_range):
    mask = pd.Series(True, index=RAW_DATA.index)

    if start_date and end_date:
        s = pd.to_datetime(start_date).date()
        e = pd.to_datetime(end_date).date()
        mask &= (RAW_DATA['date'] >= s) & (RAW_DATA['date'] <= e)
    if user_types:
        mask &= RAW_DATA['user_type'].isin(user_types)
    if genders:
        mask &= RAW_DATA['gender'].isin(genders)
    if age_groups:
        mask &= RAW_DATA['age_group'].isin(age_groups)
    if dur_range:
        mask &= (RAW_DATA['duration_min'] >= dur_range[0]) & (RAW_DATA['duration_min'] <= dur_range[1])

    df = RAW_DATA[mask]

    total   = len(df)
    avg_dur = df['duration_min'].mean() if total else 0
    bikes   = df['bike_id'].nunique()   if total else 0
    sub_pct = (df['user_type'] == 'Subscriber').mean() * 100 if total else 0
    peak_hr = df.groupby('hour').size().idxmax() if total else 0

    kpis = [
        build_kpi(f'{total:,}',       'TOTAL TRIPS',      'fas fa-route',      'Filtered',        'green',  '#00d4aa', 'stg-1'),
        build_kpi(f'{avg_dur:.1f}m',  'AVG DURATION',     'fas fa-clock',      'Per trip',        'blue',   '#4fc3f7', 'stg-2'),
        build_kpi(f'{bikes:,}',       'ACTIVE BIKES',     'fas fa-bicycle',    'Unique IDs',      'purple', '#7b61ff', 'stg-3'),
        build_kpi(f'{sub_pct:.0f}%',  'SUBSCRIBER RATE',  'fas fa-user-check', 'Loyalty metric',  'green',  '#00d4aa', 'stg-4'),
        build_kpi(f'{peak_hr:02d}:00','PEAK HOUR',        'fas fa-bolt',       'Highest activity','purple', '#7b61ff', 'stg-5'),
    ]

    dur_text = f'{dur_range[0]} MIN — {dur_range[1]} MIN' if dur_range else '1 MIN — 120 MIN'

    return (
        kpis,
        chart_daily_trend(df),
        chart_user_donut(df),
        chart_hourly_flow(df),
        chart_weekday(df),
        chart_heatmap(df),
        chart_weekend_vs_weekday(df),
        chart_gender_bars(df),
        chart_age_group_bar(df),
        chart_age_distribution(df),
        chart_duration_dist(df),
        chart_duration_by_user(df),
        chart_top_stations(df, 'start_station', 'Top Origin Stations'),
        chart_top_stations(df, 'end_station',   'Top Destination Stations'),
        build_station_ranks(df, 'start_station'),
        build_station_ranks(df, 'end_station'),
        build_insights_list(df),
        dur_text,
    )


if __name__ == '__main__':
    app.run(debug=True, port=8050)