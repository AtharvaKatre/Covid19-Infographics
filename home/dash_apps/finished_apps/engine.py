from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import requests
import json
import plotly.express as px


df = pd.read_csv('static/data.csv')
india = requests.get('https://api.covid19api.com/country/india')

# total india data
total_confirmed = india.json()[-1]['Confirmed']
total_deaths = india.json()[-1]['Deaths']
total_recovered = india.json()[-1]['Recovered']
total_active = india.json()[-1]['Active']

# total world data
world = requests.get('https://api.covid19api.com/summary')
total_world_cases = world.json()['Global']['TotalConfirmed']
total_world_recovered = world.json()['Global']['TotalRecovered']
total_world_deaths = world.json()['Global']['TotalDeaths']
total_world_active = (total_world_cases) - \
    (total_world_recovered + total_world_deaths)


def get_data(parameter):
    if parameter == 'total_world_confirmed':
        return total_world_cases
    if parameter == 'total_world_active':
        return total_world_active
    if parameter == 'total_world_recovered':
        return total_world_recovered
    if parameter == 'total_world_deaths':
        return total_world_deaths
    if parameter == 'total_confirmed':
        return total_confirmed
    if parameter == 'total_recovered':
        return total_recovered
    if parameter == 'total_active':
        return total_active
    if parameter == 'total_deaths':
        return total_deaths


# all data from day one
date_list = []
confirmed_list = []
death_list = []  # total deaths daily
daily_positive_list = []
daily_death_list = []  # new deaths daily

for i in range(0, len(india.json())):
    date_list.append(india.json()[i]['Date'][:10])
    confirmed_list.append(india.json()[i]['Confirmed'])
    death_list.append(india.json()[i]['Deaths'])

daily_positive_list = [confirmed_list[i] - confirmed_list[i-1]
                       for i in range(1, len(confirmed_list))]
daily_death_list = [death_list[i] - death_list[i-1]
                    for i in range(1, len(death_list))]
# adding zero to match the len of other lists
# adding zero doesn't matter at zero position as the cases were zero before day1
daily_positive_list.insert(0, 0)
daily_death_list.insert(0, 0)

# Statewise Testing Bar Graph
app = DjangoDash('SimpleExample')
fig1 = px.bar(x=df['State'], y=df['Positive'], title='State-wise Cases',
              color_discrete_sequence=px.colors.sequential.Plasma, )
fig1.update_layout(xaxis_title='', yaxis_title='', title_x=0.5)
app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='covid graph1',
            figure=fig1
        )
    ])

])


# total and positive stack chart
state_app1 = DjangoDash('state_app1')

state_app1.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='state graph1',
            figure={
                'data': [
                    {'x': df['Date'], 'y': df['TotalSamples'],
                        'type': 'bar', 'name': 'Tested', },
                    {'x': df['Date'], 'y': df['Positive'],
                        'type': 'bar', 'name': 'Positive', },

                ],
                'layout': {
                    'title': 'Positive results among total test samples ',
                    'barmode': 'stack',
                }

            }
        )
    ])

])

# daily positive line graph
home_app2 = DjangoDash('home_app2')
fig = px.line(x=date_list[:-1], y=daily_positive_list[:-1],
              color_discrete_sequence=['crimson'])
fig.update_layout(xaxis_title='', yaxis_title='No. of positive cases')
home_app2.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='home graph2',
            figure=fig
        )
    ])

])

# daily death line graph
state_app2 = DjangoDash('state_app2')
fig = px.line(x=date_list[:-1], y=daily_death_list[:-1],
              color_discrete_sequence=['crimson'])
fig.update_layout(xaxis_title='', yaxis_title='No. of deaths due to covid-19')
state_app2.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='state graph2',
            figure=fig
        )
    ])

])

# active death recoverd pie chart
home_app3 = DjangoDash('home_app3')

home_app3.layout = html.Div([
    html.Div([
        dcc.Graph(
            figure=go.Figure(
                data=[go.Pie(labels=['Active', 'Deaths', 'Recovered', ],
                             values=[total_world_active, total_world_deaths, total_world_recovered, ])],
                layout=go.Layout(title='')
            )
        )
    ])
])

# total confirmed vs active pie chart
home_app4 = DjangoDash('home_app4')

home_app4.layout = html.Div([
    html.Div([
        dcc.Graph(
            figure=go.Figure(
                data=[go.Pie(labels=['Total Confirmed', 'Active'],
                             values=[total_world_cases, total_world_active])],
                layout=go.Layout(title='')
            )
        )
    ])
])

# Choropleth map
home_app5 = DjangoDash('home_app5')

countries_data = requests.get('https://api.covid19api.com/summary')
countries_df = pd.DataFrame(countries_data.json()['Countries'])


def globe_data():
    fig = px.choropleth(countries_df, locations="Country",
                        color="TotalConfirmed",
                        hover_data=['NewConfirmed', 'TotalConfirmed',
                                    'NewDeaths', 'TotalDeaths', 'NewRecovered',
                                    'TotalRecovered', 'Date',
                                    ],
                        locationmode="country names",
                        projection="orthographic",
                        color_continuous_scale=px.colors.sequential.dense,
                        height=550,
                        width=590,

                        ).update_layout(clickmode='event+select', title_text='Global Data', title_x=0.5,)
    return fig


home_app5.layout = html.Div(children=[
    dcc.Graph(
        id='choropleth_map',
        figure=globe_data(),
        config={
            'displayModeBar': False,
        }
    ),
])

# symptoms bar
home_app6 = DjangoDash('home_app6')

symptoms = {'symptom': ['Fever',
                        'Dry cough',
                        'Fatigue',
                        'Sputum production',
                        'Shortness of breath',
                        'Muscle pain',
                        'Sore throat',
                        'Headache',
                        'Chills',
                        'Nausea or vomiting',
                        'Nasal congestion',
                        'Diarrhoea',
                        'Haemoptysis',
                        'Conjunctival congestion'], 'percentage': [87.9, 67.7, 38.1, 33.4, 18.6, 14.8, 13.9, 13.6, 11.4, 5.0, 4.8, 3.7, 0.9, 0.8]}

symptoms = pd.DataFrame(data=symptoms, index=range(14))


def symptoms_data():
    fig = px.bar(symptoms[['symptom', 'percentage']].sort_values('percentage', ascending=False),
                 x="percentage", y="symptom", color='symptom', color_discrete_sequence=px.colors.cyclical.IceFire, title='Symptom of Coronavirus', orientation='h')
    fig.update_layout(plot_bgcolor='rgb(275, 270, 273)')
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_layout(barmode='stack')
    fig.update_layout(plot_bgcolor='rgb(275, 270, 273)',
                      yaxis_title='Symptoms', xaxis_title='Percentages')
    fig.update_layout(template='plotly_white')
    return fig


home_app6.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='symptoms bar',
            figure=symptoms_data(),
        )
    ])
])

# age graph
home_app7 = DjangoDash('home_app7')
age_df = pd.read_csv('static/AgeGroupDetails.csv')


def age_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=age_df['AgeGroup'], y=age_df['TotalCases'],
                             line_shape='spline', fill='tonexty', fillcolor='steelblue'))
    fig.update_layout(title="Age wise Confirmed Case Trend(India as of 19 March 20)",
                      yaxis_title="Total Number of cases", xaxis_title="Age Group")
    fig.update_layout(width=490, height=480)
    return fig


home_app7.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='age graph',
            figure=age_data()
        )
    ])
])

# age deaths graph
home_app8 = DjangoDash('home_app8')
age_death_df = pd.read_csv('static/deaths.csv')


def age_death_data():
    fig = px.pie(labels=age_death_df['AgeGroup'],
                 names=age_death_df['AgeGroup'], values=age_death_df['Percentage'])
    fig.update_layout(title="Death Risk by Age ", title_x=0.5,)
    fig.update_layout(width=490, height=480)
    return fig


home_app8.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='age_death_graph',
            figure=age_death_data()
        )
    ])
])
