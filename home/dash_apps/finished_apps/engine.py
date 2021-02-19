from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import requests
import json
from datetime import date



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
total_world_active = (total_world_cases) - (total_world_recovered + total_world_deaths)


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

#world timeline slider
home_app1 = DjangoDash('home_app1')
worlddf = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv')
worlddf = worlddf[worlddf['Date']>'2020-02-25']
worldfig = px.choropleth(worlddf,               
              locations='Country',
              color = 'Confirmed',              
              locationmode="country names", 
              projection = 'natural earth',
              animation_frame = "Date",
              hover_data = ['Country','Confirmed','Recovered','Deaths'],
              color_continuous_scale='inferno_r'            
            ).update_layout(font=dict(family="Arial, Helvetica, sans-serif",size=24,), title='Covid Outbreak Timeline', title_x=0.5, paper_bgcolor='rgb(248,249,252)', geo=dict(bgcolor= 'rgb(248,249,252)'),coloraxis_colorbar=dict(title="No. of cases",),height=600)
home_app1.layout = html.Div([
    dcc.Graph(
        id = 'world timeline map',
        figure = worldfig,
        config={
        'displayModeBar': False
    }
    )
])


# Statewise Testing Bar Graph
wiki_df = pd.read_html('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/India_medical_cases_by_state_and_union_territory')[0].dropna(how='all',axis=1)
wiki_df = wiki_df.drop(wiki_df.tail(2).index)
wiki_df.columns = ['States','Cases','Deaths','Recovered','Active']
wiki_df['Cases'] = wiki_df['Cases'].apply(lambda x: x.split('[')[0]).apply(lambda x: x.replace(',',''))
wiki_df['Deaths'] = wiki_df['Deaths'].apply(lambda x: x.split('[')[0]).apply(lambda x: x.replace(',',''))
app = DjangoDash('SimpleExample')
fig1 = px.bar(x=wiki_df['States'], y=wiki_df['Cases'], title='State-wise Cases',
              color_discrete_sequence=px.colors.sequential.Plasma, )
fig1.update_layout(xaxis_title='', yaxis_title='Total Positive Cases', font=dict(family="Arial, Helvetica, sans-serif",size=24,),
                    title_x=0.5,paper_bgcolor='rgb(248,249,252)', plot_bgcolor='rgb(248,249,252)',)
app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='covid graph1',
            figure=fig1
        )
    ])

])

#india heatmap
state_app = DjangoDash('state_app')
def india_heatmap():
        wiki_df.drop(17,inplace=True)
        wiki_df['Date'] = date.today()
        india_geojson = json.load(open("static/india_geojson.geojson", "r"))
        state_id_map = {}
        for feature in india_geojson["features"]:
            feature["id"] = feature["properties"]["state_code"]
            state_id_map[feature["properties"]["st_nm"]] = feature["id"]
        wiki_df["id"] = wiki_df["States"].apply(lambda x: state_id_map[x])
        wiki_df[['Active','Cases','Deaths','Recovered']] = wiki_df[['Active','Cases','Deaths','Recovered']].apply(pd.to_numeric)
        fig = px.choropleth_mapbox(
            wiki_df,
            locations="id",
            geojson=india_geojson,
            color="Cases",
            hover_name="States",
            hover_data=["Cases","Active","Recovered","Deaths","Date"],
            title="",
            mapbox_style="carto-positron",
            color_continuous_scale='Inferno_r',
            center={"lat": 23, "lon": 88},
            zoom=3.45,
            opacity=1,
        )
        fig.update_layout(height=700, width=950, font=dict(family="Arial, Helvetica, sans-serif",size=24,), title_x=0.5, coloraxis_colorbar=dict(title="Covid cases"),)
        fig.update_layout(coloraxis_colorbar_x=-0.25,)
        return fig

state_app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id = 'state app',
            figure = india_heatmap()
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
                    'title_x':0.5,
                    'barmode': 'stack',
                    'plot_bgcolor': '#f8f9fc',
                    'paper_bgcolor': '#f8f9fc',
                    'font': dict(family="Arial, Helvetica, sans-serif",size=24,),               
                }

            }
        )
    ])

])

# daily positive line graph
home_app2 = DjangoDash('home_app2')
fig = px.line(x=date_list[:-2], y=daily_positive_list[:-2],
              color_discrete_sequence=['crimson'])
fig.update_layout(font=dict(family="Arial, Helvetica, sans-serif",size=24,), title='Daily Reported Positive Cases',title_x=0.5, xaxis_title=None, yaxis_title='No. of positive cases',paper_bgcolor='rgb(248,249,252)', plot_bgcolor='rgb(248,249,252)',)
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
fig = px.line(x=date_list[:-2], y=daily_death_list[:-2],
              color_discrete_sequence=['crimson'])
fig.update_layout(font=dict(family="Arial, Helvetica, sans-serif",size=24,), title='Daily Reported Covid-19 Deaths',title_x=0.5, xaxis_title=None, yaxis_title='No. of deaths due to covid-19',paper_bgcolor='rgb(248,249,252)', plot_bgcolor='rgb(248,249,252)',)
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
                layout=go.Layout(font=dict(family="Arial, Helvetica, sans-serif",size=24,), title = 'Active vs Deaths vs Recovered', title_x=0.5, paper_bgcolor='rgb(248,249,252)', plot_bgcolor='rgb(248,249,252)')
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
                layout=go.Layout(font=dict(family="Arial, Helvetica, sans-serif",size=24,), title='Total vs Active', title_x=0.48, paper_bgcolor='rgb(248,249,252)', plot_bgcolor='rgb(248,249,252)')
            )
        )
    ])
])

# Choropleth map
# home_app5 = DjangoDash('home_app5')

# countries_data = requests.get('https://api.covid19api.com/summary')
# countries_df = pd.DataFrame(countries_data.json()['Countries'])


# def globe_data():
#     fig = px.choropleth(countries_df, locations="Country",
#                         color="TotalConfirmed",
#                         hover_data=['NewConfirmed', 'TotalConfirmed',
#                                     'NewDeaths', 'TotalDeaths', 'NewRecovered',
#                                     'TotalRecovered', 'Date',
#                                     ],
#                         locationmode="country names",
#                         projection="orthographic",
#                         color_continuous_scale=px.colors.sequential.dense,
#                         width=590,

#                         ).update_layout(clickmode='event+select', font=dict(family="Arial, Helvetica, sans-serif",size=24,), title_text='Global Covid Heatmap',
#                                             title_x=0.5, paper_bgcolor='rgb(248,249,252)', plot_bgcolor='rgb(248,249,252)')
#     fig.update_layout(geo=dict(bgcolor= 'rgb(248,249,252)'))
#     return fig


# home_app5.layout = html.Div(children=[
#     dcc.Graph(
#         id='choropleth_map',
#         figure=globe_data(),
#         config={
#             'displayModeBar': False,
#         }
#     ),
# ])

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
    fig.update_traces(textposition='inside')
    fig.update_layout(barmode='stack')
    fig.update_layout(font=dict(size=16,), titlefont=dict(family="Arial, Helvetica, sans-serif",size=24,), plot_bgcolor='rgb(248,249,252)', paper_bgcolor='rgb(248,249,252)',
                      yaxis_title='Symptoms', xaxis_title='Percentages', title_x=0.5)
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
    fig.update_layout(font=dict(family="Arial, Helvetica, sans-serif",size=18.5,), title="Age wise Confirmed Case Trend(India as of 19 March 20)", title_x=0.5, yaxis_title="Total Number of cases", xaxis_title="Age Group")
    fig.update_layout(plot_bgcolor='rgb(248,249,252)', paper_bgcolor='rgb(248,249,252)',)
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
    fig.update_layout(font=dict(family="Arial, Helvetica, sans-serif",size=24,), title="Death Risk by Age ", title_x=0.5,)
    fig.update_layout(plot_bgcolor='rgb(248,249,252)', paper_bgcolor='rgb(248,249,252)',)
    return fig


home_app8.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='age_death_graph',
            figure=age_death_data()
        )
    ])
])

state_app3 = DjangoDash('state_app3')

def get_fig():
    fig = go.Figure()
    fig.add_trace(
        go.Scatter( x=date_list[63:85], y=daily_positive_list[63:85], name='Lockdown 1', mode='lines' ),
    )

    fig.add_trace(
        go.Scatter(x=date_list[84:104], y=daily_positive_list[84:104], name='Lockdown 2', mode='lines'),
    )

    fig.add_trace(
        go.Scatter(x=date_list[103:118], y=daily_positive_list[103:118], name='Lockdown 3', mode='lines'),
    )

    fig.add_trace(
        go.Scatter(x=date_list[117:132], y=daily_positive_list[117:132], name='Lockdown 4', mode='lines'),
    )

    fig.add_trace(
        go.Scatter(x=date_list[131:162], y=daily_positive_list[131:162], name='Unlock 1.0', mode='lines'),
    )

    fig.add_trace(
        go.Scatter(x=date_list[161:193], y=daily_positive_list[161:193], name='Unlock 2.0', mode='lines'),
    )

    fig.add_trace(
        go.Scatter(x=date_list[192:224], y=daily_positive_list[192:224], name='Unlock 3.0', mode='lines'),
    )

    fig.add_trace(
        go.Scatter(x=date_list[223:254], y=daily_positive_list[223:254], name='Unlock 4.0', mode='lines'),
    )

    fig.add_trace(
        go.Scatter(x=date_list[253:285], y=daily_positive_list[253:285], name='Unlock 5.0', mode='lines'),
    )
    fig.add_trace(
        go.Scatter(x=date_list[284:315], y=daily_positive_list[284:315], name='Unlock 6.0', mode='lines'),
    )
    fig.add_trace(
        go.Scatter(x=date_list[314:-2], y=daily_positive_list[314:346], name='December', mode='lines'),
    )
    fig.add_trace(
        go.Scatter(x=date_list[314:-2], y=daily_positive_list[346:378], name='January 2021', mode='lines'),
    )
    fig.add_trace(
        go.Scatter(x=date_list[314:-2], y=daily_positive_list[378:-1], name='February 2021', mode='lines'),
    )


    fig.update_layout(font=dict(family="Arial, Helvetica, sans-serif",size=24,), yaxis_title='No. of positive cases', title_text="Lockdown vs Unlock", title_x=0.5, plot_bgcolor='rgb(248,249,252)', paper_bgcolor='rgb(248,249,252)')
    return fig

state_app3.layout = html.Div([
    dcc.Graph(
        id = 'lockdownvsunlock',
        figure = get_fig()
    )
])
