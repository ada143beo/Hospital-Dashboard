import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go

dash.register_page(__name__, name='Patients', order=2)

# load data
df = pd.read_csv("assets/hospital_dataset.csv")

# data prep
date_cols = ['Admission_Date', 'Discharge_Date', 'Date']
for col in date_cols:
    df[col] = pd.to_datetime(df[col])
df['Zip_Code'] = df['Zip_Code'].astype(str)

# kpis
total_patients = df['Patient_ID'].nunique()
satisfaction_pct = df['Patient_Satisfaction_Score'].mean() * 10
emergency_cases = (df['Emergency_Case'] == 'Yes').sum()
follow_up_needed = (df['Follow_Up_Required'] == 'Yes').sum()
emergency_rate = (df['Emergency_Case'] == 'Yes').mean() * 100
follow_up_rate = (df['Follow_Up_Required'] == 'Yes').mean() * 100
total_followup_ratio = (follow_up_needed / total_patients) * 100


# TREE MAP/ HEATMAP
grouped = df.groupby(['Gender', 'Bed_Category'])['Patient_ID'].nunique().reset_index()
grouped.columns = ['Gender', 'Bed_Category', 'Count']

all_labels = ["Total Patients"] + grouped['Bed_Category'].unique().tolist() + grouped['Gender'].tolist()
all_parents = [""] + ["Total Patients"] * len(grouped['Bed_Category'].unique()) + grouped['Bed_Category'].tolist()
all_values = [grouped['Count'].sum()] + grouped.groupby('Bed_Category')['Count'].sum().tolist() + grouped['Count'].tolist()

heatmap_data = grouped.pivot(index='Gender', columns='Bed_Category', values='Count')

tree_heat_fig = go.Figure()

tree_heat_fig.add_trace(go.Treemap(
    labels=all_labels,
    parents=all_parents,
    values=all_values,
    branchvalues="total",
    marker=dict(colorscale='Greens'),
    visible=True,
    name="Treemap"
))

tree_heat_fig.add_trace(go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale='Greens',
    visible=False,
    name="Heatmap",
    text=heatmap_data.values,
    texttemplate="%{text}", 
))

tree_heat_fig.update_layout(
    #title='Patient Distribution: Gender vs. Bed Category',
    template='plotly_white',
    updatemenus=[
        dict(
            type="dropdown",
            direction="down",
            x=0.01,
            y=1.15,
            showactive=True,
            buttons=list([
                dict(
                    label="Treemap View",
                    method="update",
                    args=[{"visible": [True, False]}, 
                          {"title": "Hierarchy: Bed Category & Gender"}]
                ),
                dict(
                    label="HeatMap View",
                    method="update",
                    args=[{"visible": [False, True]}, 
                          {"title": "Intensity: Gender vs. Bed Category"}]
                ),
            ]),
        )
    ]
)


# HISTOGRAM
hist_fig = px.histogram(
    df, 
    x="Age", 
    nbins=30,
    title="Age Distribution of Patients",
    template='plotly_white',
    color_discrete_sequence=['#076821'] 
)

hist_fig.update_layout(
    xaxis_title="Patient Age",
    yaxis_title="Frequency",
    hovermode='x unified',
    bargap=0.05,
    xaxis=dict(
        rangeslider=dict(visible=True),
        type="linear"
    )
)

hist_fig.update_traces(
    marker_line_color='white',
    marker_line_width=1,
    opacity=0.85
)

# STACKED BAR CHART
patient_trend = df.groupby(['Date', 'Admission_Type'])['Patient_ID'].nunique().reset_index()
patient_trend.columns = ['Date', 'Admission_Type', 'Patient_Count']


stacked_bar_fig = px.bar(
    patient_trend, 
    x='Date', 
    y='Patient_Count',
    color='Admission_Type',
    title='Hospital Patient Volume Trend Per Admission Type',
    template='plotly_white',
    color_discrete_sequence=["#1E5E21", "#288D2B",'#4CAF50',  '#81C784'] 
)

stacked_bar_fig.update_layout(
    hovermode='x unified',
    xaxis_title="Timeline",
    yaxis_title="Total Patients",
    bargap=0.1, 
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    ),
)

# 3D SURFACE / 2D HEATMAP
z_data = pd.crosstab(df['Department'], df['Treatment_Plan'])

surface_heatmap_fig = go.Figure()

surface_heatmap_fig.add_trace(go.Surface(
    z=z_data.values, 
    x=z_data.columns, 
    y=z_data.index, 
    colorscale="Greens",
    colorbar=dict(title="Volume", thickness=15),
))

surface_heatmap_fig.update_layout(
    #title='Department vs. Treatment Plan Analysis',
    margin=dict(t=30, b=0, l=0, r=0),
    template="plotly_white",
    scene=dict(
        xaxis_title='Treatment Plan',
        yaxis_title='Department',
        zaxis_title='Volume',
        aspectratio=dict(x=1, y=1, z=0.7),
        aspectmode="manual"
    ),
    updatemenus=[
        dict(
            buttons=list([
                dict(
                    args=[{"type": "surface"}],
                    label="3D Surface",
                    method="restyle"
                ),
                dict(
                    args=[{"type": "heatmap"}],
                    label="2D Heatmap",
                    method="restyle"
                )
            ]),
            direction="down",
            showactive=True,
            x=0,
            xanchor="left",
            y=1.2,
            yanchor="top"
        ),
    ]

)

surface_heatmap_fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True))


# SCATTER PLOT
df_3d = df.groupby(['Department', pd.Grouper(key='Date', freq='W')]).size().reset_index(name='Patient_Count')

scatter_fig = go.Figure(data=[go.Scatter3d(
    x=df_3d['Date'],
    y=df_3d['Department'],
    z=df_3d['Patient_Count'],
    mode='markers',
    marker=dict(
        size=7,
        color=df_3d['Patient_Count'],   
        colorscale='Greens',           
        colorbar=dict(title='Patients', thickness=15),
        line_color='rgb(140, 140, 170)'
    )
)])

scatter_fig.update_layout(
    # title='Patient Volume per Department Trend',
    template="plotly_white", 
    scene=dict(
        xaxis_title='Timeline',
        yaxis_title='Department',
        zaxis_title='Number of Patients'
    ),
    margin=dict(t=30, b=0, l=0, r=0)
)

def card_style():
    style_c = {
        "border": "1px solid #e3e6f0",
        "borderTop": "5px solid #076821",
        "borderRadius": "16px",
        "boxShadow": "0 2px 6px #076821",
    }
    return style_c

def make_kpi_card(title, value):  
    return dbc.Card(
        dbc.CardBody([
            html.Span(title, className="text-uppercase text-muted fw-semibold mb-2", style={"letterSpacing": "0.7px", "fontSize": "12px"}),
            html.H4(value, className="fw-bold", style={"color": "#076821"})
        ]),
        style={**card_style()},
        className="mb-4 text-center"
    )

def make_graph_card(title, figure):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="fw-bold text-dark mt-2 border-bottom pb-2"),
            dcc.Graph(figure=figure)
        ]),
        style={**card_style()},
        className="mb-4 text-center"
    )

# REMOVE BACKGROUD
def apply_transparent_bg(*figs):
    for fig in figs:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)'
        )
    return figs

# apply to all figures
tree_heat_fig, hist_fig, stacked_bar_fig, surface_heatmap_fig, scatter_fig  = apply_transparent_bg(
    tree_heat_fig, hist_fig, stacked_bar_fig, surface_heatmap_fig, scatter_fig 
)

layout = dbc.Container([
    
    # HEADING SECTION
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3('Patient Behavior and Clinical Activity Overview Dashboard', className="fw-bold mb-0", style={"color": "#076821"}),
            ], className="my-5 ps-3 border-start border-4")
        ])
    ]),

    # KPI ROW 
    dbc.Row([
        dbc.Col(make_kpi_card("Total Patients", f"{total_patients:,}"), xs=12, sm=4, lg=2),
        dbc.Col(make_kpi_card("Satisfaction Rate", f"{satisfaction_pct:.1f}%"), xs=12, sm=4, lg=2),
        dbc.Col(make_kpi_card("Emergency Cases", f"{emergency_cases:,}"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Emergency Rate", f"{emergency_rate:.1f}%"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Follow-ups Due", f"{follow_up_needed:,}"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Follow-up Rate", f"{follow_up_rate:.1f}%"), xs=12, sm=6, lg=2),
        
    ], className="mb-2"),

    # HISTOGRAM / TREEMAP
    dbc.Row([
        dbc.Col(make_graph_card("Patient Age Distribution", hist_fig), md=6, xs=12),
        dbc.Col(make_graph_card("Patient Distribution per Gender and Bed Category", tree_heat_fig), md=6, xs=12),
    ], className="mb-2"),

    # STACKED BAR
    dbc.Row([
        dbc.Col(make_graph_card("Hospital Patient Volume Trend Per Admission Type", stacked_bar_fig), width=12),
    ], className="mb-2"),

    # 3D SURFACE & SCATTER ROW
    dbc.Row([
        dbc.Col(make_graph_card("Department vs. Treatment Volume", surface_heatmap_fig), md=6, xs=12),
        dbc.Col(make_graph_card("Volume Trend by Department", scatter_fig), md=6, xs=12),
    ], className="pb-5"),

], fluid=True)