import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go

dash.register_page(__name__, name='Doctors', order=3)

# load data
df = pd.read_csv("assets/hospital_dataset.csv")

# data prep
date_cols = ['Admission_Date', 'Discharge_Date', 'Date']
for col in date_cols:
    df[col] = pd.to_datetime(df[col])
df['Zip_Code'] = df['Zip_Code'].astype(str)

# kpis
total_doctors = df['Consultant_Doctor'].nunique()
avg_patients_per_doc = df.shape[0] / total_doctors
peak_workload = df['Consultant_Doctor'].value_counts().max()

def create_doctor_dropdown(df):
    doctors = sorted(df['Consultant_Doctor'].unique())
    dropdown_buttons = [
        dict(
            label="All Doctors",
            method="restyle",
            args=[{"visible": [True] * len(doctors)}]
        )
    ]

    for doctor in doctors:
        dropdown_buttons.append(dict(
            label=doctor,
            method="restyle",
            args=[{"visible": [d == doctor for d in doctors]}]
        )
    )
    return dropdown_buttons

doc_buttons = create_doctor_dropdown(df)

# SCATTER PLOT
df['Year'] = pd.to_datetime(df['Admission_Date']).dt.year

fig_scatter = px.scatter(
    df, 
    x="Billing_Amount", 
    y="Patient_Satisfaction_Score", 
    animation_frame="Year", 
    animation_group="Consultant_Doctor",
    size="Length_of_Stay", 
    color="Department", 
    hover_name="Consultant_Doctor",
    log_x=True, 
    size_max=55, 
    range_x=[df['Billing_Amount'].min(), df['Billing_Amount'].max()], 
    range_y=[0, 10],
    # title="Doctor Analysis: Satisfaction vs. Billing",
    template="plotly_white",
    color_discrete_sequence=['#076821', '#228B22', '#3CB371', '#66BB6A', '#81C784', '#A5D6A7', '#C8E6C9']
)

fig_scatter.update_layout(
    margin=dict(l=50, r=50, t=80, b=50),
    updatemenus=[
        dict(
            buttons=doc_buttons,
            direction="down",
            showactive=True,
            x=0, xanchor="left",
            y=1.2, yanchor="top",
        ),
    ]
)


# SUNBURST
fig_sunburst = px.sunburst(
    df, 
    path=['Department', 'Consultant_Doctor'], 
    values='Billing_Amount', 
    color='Department',
    color_discrete_sequence=['#076821', '#1B5E20', '#2E7D32', '#388E3C', '#4CAF50', '#81C784'],
    #title="Consultant Doctor Hierarchy by Department",
    template="plotly_white"
)

fig_sunburst.update_layout(
    updatemenus=[
        dict(
            buttons=doc_buttons,
            direction="down",
            showactive=True,
            x=0.05, xanchor="left",
            y=1.15, yanchor="top",
        ),
    ],
    margin=dict(t=80, l=20, r=20, b=20)
)

fig_sunburst.update_traces(
    hovertemplate='<b>%{label}</b><br>Total Billing: $%{value:,.2f}'
)

# POLAR
doctor_counts = df.groupby(['Consultant_Doctor']).size().reset_index(name='Patient_Count')

fig_polar = px.bar_polar(
    doctor_counts, 
    r="Patient_Count", 
    theta="Consultant_Doctor",
    color="Consultant_Doctor",
    template="plotly_white",
    color_discrete_sequence=['#076821', '#228B22', '#3CB371', '#66BB6A', '#81C784', '#A5D6A7', '#C8E6C9'],
    # title="Consultant Doctor Workload Distribution"
)

fig_polar.update_layout(
    updatemenus=[
        dict(
            buttons=doc_buttons,
            direction="down",
            showactive=True,
            x=0.05, xanchor="left",
            y=1.15, yanchor="top",
        ),
    ],
    margin=dict(t=80, l=20, r=20, b=20)
)


# TABLE
doc_table_df = df.groupby('Consultant_Doctor').agg({
    'Patient_ID': 'count',
    'Patient_Satisfaction_Score': 'mean',
    'Billing_Amount': 'sum',
    'Department': 'first'
}).reset_index().rename(columns={'Patient_ID': 'Total_Patients'})

doc_table_df = doc_table_df.sort_values('Consultant_Doctor')
doctors = doc_table_df['Consultant_Doctor'].tolist()

fig_table = go.Figure()

fig_table.add_trace(
    go.Table(
        header=dict(
            values=["<b>Consultant Doctor</b>", "<b>Department</b>", "<b>Patients</b>", "<b>Avg Satisfaction</b>", "<b>Total Revenue</b>"],
            fill_color='#076821',
            align='left',
            font=dict(color='white', size=13, family="Arial"),
            height=35
        ),
        cells=dict(
            values=[
                doc_table_df['Consultant_Doctor'],
                doc_table_df['Department'],
                doc_table_df['Total_Patients'],
                doc_table_df['Patient_Satisfaction_Score'].round(2),
                doc_table_df['Billing_Amount'].apply(lambda x: f"${x:,.2f}")
            ],
            fill_color='#F1F8E9',
            align='left',
            font=dict(color='#076821', size=12),
            height=30
        )
    )
)

fig_table.update_layout(
    # title="Consultant Doctor Clinical Performance Directory",
    margin=dict(t=100, l=20, r=20, b=20)
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
fig_scatter, fig_sunburst, fig_polar, fig_table = apply_transparent_bg(
    fig_scatter, fig_sunburst, fig_polar, fig_table
)

layout = dbc.Container([
    
    # HEADING SECTION
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3('Consultant Doctor Performance and Workload Analytics Dashboard', className="fw-bold mb-0", style={"color": "#076821"}),
            ], className="my-5 ps-3 border-start border-4")
        ])
    ]),

    # KPI ROW 
    dbc.Row([
        dbc.Col(make_kpi_card("Total Doctors", f"{total_doctors:,}"), xs=12, sm=4, lg=4),
        dbc.Col(make_kpi_card("Avg. Patient Load", f"{avg_patients_per_doc:.1f}"), xs=12, sm=4, lg=4),
        dbc.Col(make_kpi_card("Peak Workload", f"{peak_workload:,}"), xs=12, sm=4, lg=4),
    ], className="mb-2 g-3"),

    # SCATTER PLOT
    dbc.Row([
        dbc.Col(make_graph_card("Doctor Analysis: Satisfaction vs. Billing", fig_scatter), width=12),
    ], className="mb-2"),

    # SUNBURST / POLAR ROW
    dbc.Row([
        dbc.Col(make_graph_card("Consultant Doctor Hierarchy by Department", fig_sunburst), md=6, xs=12),
        dbc.Col(make_graph_card("Consultant Doctor Workload Distribution", fig_polar), md=6, xs=12),
    ], className="mb-2"),

    # TABLE
    dbc.Row([
        dbc.Col(make_graph_card("Consultant Doctor Clinical Performance Directory", fig_table), width=12),
    ], className="mb-2"),


], fluid=True)