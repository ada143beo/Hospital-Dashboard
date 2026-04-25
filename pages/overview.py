import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go

dash.register_page(__name__, path='/', name='Overview', order=1)

# load data
df = pd.read_csv("assets/hospital_dataset.csv")

# data prep
date_cols = ['Admission_Date', 'Discharge_Date', 'Date']
for col in date_cols:
    df[col] = pd.to_datetime(df[col])
df['Zip_Code'] = df['Zip_Code'].astype(str)

# kpis
total_transactions = df['Transaction_ID'].nunique()
total_revenue = df['Total_Sales_Amount'].sum()
avg_billing = df['Billing_Amount'].mean()
avg_stay = df['Length_of_Stay'].mean()
avg_satisfaction = df['Patient_Satisfaction_Score'].mean()
emergency_pct = (df['Emergency_Case'] == 'Yes').mean() * 100


# AREA CHART 
revenue_trend = df.groupby('Date')['Total_Sales_Amount'].sum().reset_index()

area_fig = px.area(
    revenue_trend, 
    x='Date', 
    y='Total_Sales_Amount',
    #title='Hospital Daily Revenue Trend (Total Sales)',
    template='plotly_white'
)

area_fig.update_traces(line_color='#2ca02c', line_width=2)

area_fig.update_layout(
    hovermode='x unified',
    xaxis_title="Timeline",
    yaxis_title="Total Sales Amount ($)",
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
        rangeslider=dict(visible=True), type="date"
    ), 

)


# BAR/ PIE CHART
status_counts = df['Payment_Status'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']

bar_pie_fig = go.Figure()

bar_pie_fig.add_trace(go.Bar(
    x=status_counts['Status'],
    y=status_counts['Count'],
    marker_color=['#2E7D32', '#4CAF50', '#81C784'],
    visible=True
))


bar_pie_fig.add_trace(go.Pie(
    labels=status_counts['Status'],
    values=status_counts['Count'],
    marker=dict(colors=['#2E7D32', '#4CAF50', '#81C784']),
    visible=False
))

bar_pie_fig.update_layout(
    #title='Patient Distribution by Payment Status',
    template='plotly_white', margin=dict(t=50, b=0),
    updatemenus=[
        dict(
            type="dropdown", direction="down", x=0.1, y=1.15, showactive=True,
            buttons=list([
                dict(label="Bar Chart",
                    method="update",
                    args=[{"visible": [True, False]}, 
                          {"yaxis": {"title": "Number of Patients"}, 
                           "xaxis": {"title": "Status"}}]
                ),
                dict(label="Pie Chart",
                    method="update",
                    args=[{"visible": [False, True]}, 
                          {"yaxis": {"visible": False}, 
                           "xaxis": {"visible": False}}]
                )
            ]),
        )
    ]
)


# BAR/ PIE 2
method_counts = df['Payment_Method'].value_counts().reset_index()
method_counts.columns = ['Method', 'Count']

bar_pie_2_fig = go.Figure()

bar_pie_2_fig.add_trace(go.Bar(
    x=method_counts['Method'],
    y=method_counts['Count'],
    marker_color=["#1E5E21", "#288D2B",'#4CAF50',  '#81C784'],
    visible=True
))

bar_pie_2_fig.add_trace(go.Pie(
    labels=method_counts['Method'],
    values=method_counts['Count'],
    marker=dict(colors=["#1E5E21", "#288D2B",'#4CAF50',  '#81C784']),
    visible=False
))

bar_pie_2_fig.update_layout(
    #title='Patient Distribution by Payment Method',
    template='plotly_white', margin=dict(t=50, b=0),
    updatemenus=[
        dict(
            type="dropdown",
            direction="down",
            x=0.1,
            y=1.15,
            showactive=True,
            buttons=list([
                dict(
                    label="Bar Chart",
                    method="update",
                    args=[{"visible": [True, False]}, 
                          {"yaxis": {"title": "Number of Patients"}, 
                           "xaxis": {"title": "Status"}}]
                ),
                dict(
                    label="Pie Chart",
                    method="update",
                    args=[{"visible": [False, True]}, 
                          {"yaxis": {"visible": False}, 
                           "xaxis": {"visible": False}}]
                )
            ]),
        )
    ]
)


# SANKEY DIAGRAM
df['Month'] = df['Date'].dt.strftime('%B %Y')
months = sorted(df['Date'].unique())
month_labels = [d.strftime('%B %Y') for d in pd.to_datetime(months).unique()]

def get_sankey_data(filtered_df):
    # Flow 1: Admission_Type -> Department
    flow1 = filtered_df.groupby(['Admission_Type', 'Department']).size().reset_index(name='value')
    flow1.columns = ['source', 'target', 'value']
    
    # Flow 2: Department -> Payment_Status
    flow2 = filtered_df.groupby(['Department', 'Payment_Status']).size().reset_index(name='value')
    flow2.columns = ['source', 'target', 'value']
    
    full_flow = pd.concat([flow1, flow2])
    
    # Unique labels for nodes
    labels = list(pd.unique(full_flow[['source', 'target']].values.ravel('K')))
    mapping = {label: i for i, label in enumerate(labels)}
    
    return labels, {
        'source': full_flow['source'].map(mapping).tolist(),
        'target': full_flow['target'].map(mapping).tolist(),
        'value': full_flow['value'].tolist()
    }

# 2. Create Initial Figure
initial_month = month_labels[0]
labels, data = get_sankey_data(df[df['Month'] == initial_month])

sankey_fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15, thickness=20, line=dict(color="black", width=0.5),
        label=labels,
        color="#2E7D32" 
    ),
    link=dict(
        source=data['source'],
        target=data['target'],
        value=data['value'],
        color="rgba(76, 175, 80, 0.4)" 
    )
)])

# 3. Add Slider Logic (Frames)
frames = []
for m in month_labels:
    l, d = get_sankey_data(df[df['Month'] == m])
    frames.append(go.Frame(
        data=[go.Sankey(
            node=dict(label=l, color="#2E7D32"),
            link=dict(source=d['source'], target=d['target'], value=d['value'])
        )],
        name=m
    ))

sankey_fig.frames = frames

# 4. Configure Slider Layout
sliders = [dict(
    steps=[dict(
        method="animate",
        args=[[m], dict(mode="immediate", frame=dict(duration=300, redraw=True), transition=dict(duration=0))],
        label=m
    ) for m in month_labels],
    active=0,
    currentvalue={"prefix": "Selected Month: "},
    pad={"t": 50}
)]

sankey_fig.update_layout(
    # title_text="Patient Flow: Admission → Department → Payment Status",
    font_size=12,
    template="plotly_white",
    sliders=sliders,
    height=500
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
area_fig, bar_pie_fig, bar_pie_2_fig, sankey_fig = apply_transparent_bg(
    area_fig, bar_pie_fig, bar_pie_2_fig, sankey_fig
)


layout = dbc.Container([
    
    # HEADING SECTION
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3('Operational & Financial Executive Overview', className="fw-bold mb-0", style={"color": "#076821"}),
            ], className="my-5 ps-3 border-start border-4")
        ])
    ]),

    # KPI ROW 
    dbc.Row([
        dbc.Col(make_kpi_card("Total Transactions", f"{total_transactions:,}"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Total Revenue", f"${total_revenue:,.0f}"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Avg. Billing", f"${avg_billing:,.0f}"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Avg. Stay", f"{avg_stay:.1f} Days"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Satisfaction", f"{avg_satisfaction:.1f}/10"), xs=12, sm=6, lg=2),
        dbc.Col(make_kpi_card("Emergency Rate", f"{emergency_pct:.1f}%"), xs=12, sm=6, lg=2),
    ], className="mb-2"),

    # AREA CHART ROW
    dbc.Row([
        dbc.Col(make_graph_card("Revenue Trends", area_fig), width=12),
    ], className="mb-2"),

    # BAR / PIE CHARTS ROW
    dbc.Row([
        dbc.Col(make_graph_card("Payment Status", bar_pie_fig), md=6, xs=12),
        dbc.Col(make_graph_card("Payment Methods", bar_pie_2_fig), md=6, xs=12),
    ], className="mb-2"),

    # SANKEY DIAGRAM ROW
    dbc.Row([
        dbc.Col(make_graph_card("Patient Flow: Admission → Dept → Payment", sankey_fig), width=12),
    ], className="mb-2"),


], fluid=True)