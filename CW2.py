# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 20:28:43 2022

@author: jordan.ottewill
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

"""DATA PREPARATION AND VISUALISATION"""
"""Q1"""
##Import dataset and then pre-processing
#case data
oxsummary = pd.read_csv(r'C:\Users\jordan.ottewill\OneDrive - Wesco Aircraft Hardware Corporation\Apprenticeship\DEVA\CW2\OxCGRT_summary20200520.csv')
#country data
country_cont = pd.read_csv(r'C:\Users\jordan.ottewill\OneDrive - Wesco Aircraft Hardware Corporation\Apprenticeship\DEVA\CW2\country-and-continent.csv')

#merge country_cont onto oxsummary as oxsummary is the key data...
oxdata = oxsummary.merge(country_cont, how='left', on='CountryCode')
#rearrange df
oxdata = oxdata[['CountryName','CountryCode','Continent_Name','Date','School closing',
                'Stay at home requirements','ConfirmedCases','ConfirmedDeaths','StringencyIndex']]

#find rows with missing countries
missingcountry = []
#iterrate through rows
for x,y in oxdata.iterrows():
#x = index, y = row data. countries is the third column. iterrows changes column index to row, so third index.
#Country Name and Code is always populated in parent DF, so can use series property .isnull()
    rowhasNaN = y[0:3].isnull()
    if rowhasNaN.any():
        missingcountry.append(x)

#review missing data        
nancontinent = oxdata.iloc[missingcountry,:].CountryName.drop_duplicates()
print(nancontinent)
print(oxdata.iloc[missingcountry,2])
#Just Kosovo missing.
#populate missing continent
oxdata.iloc[missingcountry,2] = 'Europe'

"""Q2"""
"""Prepare data for visualisation - missing values for ConfirmedCases and ConfirmedDeaths"""
"""desired fill method...fill with the next available record for the same country"""
"""Once backfill completed in group, expect any values with missing final values to be present, will ffill in group to do last dates if present"""
##backfill within the group.

oxdatagrouped = oxdata.copy(deep=True)

dist_country = (oxdata['CountryName'].drop_duplicates())

#create empty dictionary
data = {}
#create empty keys within dictionary for each country
for country in dist_country:
    data["{0}".format(country)] = oxdata.loc[(oxdata['CountryName']==country)].sort_values('Date',ascending=True).copy(deep=True)
    
#now we can backfill each dictionary key individually
for country in dist_country:
        data["{0}".format(country)].fillna(method='backfill',inplace=True)
  
#Convert back to DF and analyse remaining na values
df = pd.concat(data,axis=0)
print(df.isnull())

df.reset_index(drop=True,inplace=True)

#find rows with missing values
missingvalues = []
   
for x,y in df.iterrows():
    rowhasNaN = y.isnull()
    if rowhasNaN.any():
        missingvalues.append(x)

nancountry = df.iloc[missingvalues,:].CountryName.drop_duplicates()
print(nancountry)

#only 2 countries and have entire dataset missing. No comparison can be made so will be dropped.
df.dropna(inplace=True)

"""Q3"""
"""Bubble map w confirmed cases w animation per date. Color = Continent"""

figq3 = px.scatter_geo(df, locations="CountryCode", color="Continent_Name",
                     hover_name="CountryName", size="ConfirmedCases", size_max=40,
                     animation_frame="Date", # to create animation frame based on year attribute
                     projection="natural earth")
figq3.update_layout(title_text = 'Confirmed COVID-19 Cases by Country and Contient between March 1st and May 20th 2020',title_x=0.5)

figq3.update_geos(projection_type="natural earth", scope="world", showcountries=True,
                #showland=True, landcolor="LightGreen",
                showocean=True, oceancolor="LightBlue",
                #showrivers=True, rivercolor="Blue")
                )

figq3.write_html('./Q3_ConfirmedCases.html', auto_open=True)

###############################################################################
"""Q4 and 5"""
"""Dash web app."""

##Data prep
"""Q5 Data Prep"""
#find top 5
print(df[df["Date"]==20200520].ConfirmedCases.nlargest(6))
#store index
dftop5idx = df[df["Date"]==20200520].ConfirmedCases.nlargest(6).index

for x in dftop5idx:
    print(df.CountryName[x])
#print top 5 names. As Russia is twice, we need to look at top 6.
#store names
top5name = []
for x in dftop5idx:
    top5name.append(df.CountryName[x])
    
#Filter DF
dftop5 = df[df['CountryName'].isin(top5name)].copy(deep=True)

"""Amend Date Field to be date"""
#df['Date'] = pd.to_datetime(df['Date'],format='%Y%m%d',exact=True).dt.date  ##this impacts the app.
dftop5['Date'] = pd.to_datetime(dftop5['Date'],format='%Y%m%d',exact=True).dt.date


#line graph for fig2
fig2 = px.line(data_frame=dftop5, x='Date', y='ConfirmedCases', color='CountryName')
fig2.write_html('./Q5_ConfirmedCases.html', auto_open=True)
#y can be configured in callback.

#scatter for fig1
fig1 = px.scatter_geo(df, locations="CountryCode", color="Continent_Name",
                     hover_name="CountryName", size="ConfirmedCases", size_max=40,
                     animation_frame="Date", # to create animation frame based on year attribute
                     projection="natural earth")
fig1.update_geos(projection_type="natural earth", scope="world", showcountries=True,
                #showland=True, landcolor="LightGreen",
                #showocean=True, oceancolor="LightBlue",
                #showrivers=True, rivercolor="Blue")
                )


"""Create App"""
# Creating a dash web app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#define colours for later use
colors = {
    'background': '#2A3F54',
    'back': '#CBD4DC',
    'text': '#F5F5F5',
    'Htext':'#FF7F50',
    'font-family':'open sans'
    }

#fig needs to exist in order to populat
fig = px.scatter_geo(df, locations="CountryCode", color="Continent_Name",
                     hover_name="CountryName", size="ConfirmedCases", size_max=40,
                     animation_frame="Date", # to create animation frame based on year attribute
                     projection="natural earth").update_layout(title_x = 0.5,
                                                               plot_bgcolor=colors['background'],
                                                               paper_bgcolor=colors['background'],
                                                               font_color=colors['text'])
fig.update_geos(projection_type="natural earth", scope="world", showcountries=True,
                #showland=True, landcolor="LightGreen",
                #showocean=True, oceancolor="LightBlue",
                #showrivers=True, rivercolor="Blue")
                )

#formatting
app.layout = dbc.Container(html.Div(style={'backgroundColor':colors['back']},
                      children=[
                          dbc.Card(
                              dbc.CardBody([
            dbc.Row([#header
                    html.Div(style={'backgroundColor':colors['back']},
                             children=[dbc.Card(
                                 dbc.CardBody(
                                     html.H1("COVID-19 Analysis Dashboard", style={'textAlign':'center',
                                                                                   'color':'#66FF66',
                                                                                   'font-family':colors['font-family']}
                                             )
                                     ),color=colors['background']
                                 )]
                             )
                    ]),
            html.Br(),
            dbc.Row([#row 1
                     dbc.Col([#options
                         html.Div(style={'backgroundColor':colors['back']},#'width':250},
                                          children=[dbc.Card(
                                              dbc.CardBody([
                                                  html.Label('Scope',style={'color':colors['Htext'],
                                                                            'fontWeight':'bold',
                                                                            'font-family':colors['font-family']}),
                                                  dcc.Dropdown(id='Scope',
                                                               options=[
                                                                   {'label': 'World', 'value': 'world'},
                                                                   {'label': 'Asia', 'value': 'asia'},
                                                                   {'label': 'Africa', 'value': 'africa'},
                                                                   {'label': 'Europe', 'value': 'europe'},
                                                                   {'label': 'North America', 'value': 'north america'},
                                                                   {'label': 'South America', 'value': 'south america'},
                                                                   ], value='world',
                                                               style={'font-family':colors['font-family']},#'width':200}
                                                               ),
                                                  html.Br(),
                                                  html.Label('Data Input',style={'color':colors['Htext'],
                                                                                 'fontWeight':'bold',
                                                                                 'font-family':colors['font-family']}),
                                                  dcc.RadioItems(id='Data Input',
                                                                 options=[{'label': 'Confirmed Cases', 'value': 'ConfirmedCases'},
                                                                          {'label': 'Confirmed Deaths', 'value': 'ConfirmedDeaths'},
                                                                          {'label': 'Stringency Index', 'value': 'StringencyIndex'}
                                                                          ], value='ConfirmedCases',
                                                                 style={'backgroundColor':colors['background'],
                                                                        'color':colors['text'],
                                                                        'font-family':colors['font-family']},
                                                                 labelStyle={'display': 'block'}
                                                                 ),
                                                  html.Br(),
                                                  html.Label('Policy',style={'color':colors['Htext'],
                                                                             'fontWeight':'bold',
                                                                             'font-family':colors['font-family']}),
                                                  dcc.RadioItems(id="Policy",
                                                                 options=[
                                                                     {'label': 'Not Selected', 'value': 'NA'},
                                                                     {'label': 'School Closing', 'value': 'School closing'},
                                                                     {'label': 'Staying at home', 'value': 'Stay at home requirements'}
                                                                     ], value='NA',
                                                                 style={'backgroundColor':colors['background'],
                                                                        'color':colors['text'],
                                                                        'font-family':colors['font-family']},
                                                                 labelStyle={'display': 'block'}
                                                                 ),
                                                  ]),color=colors['background']
                                              )]
                                          )
                         ],width=3),
                     dbc.Col([#graph2
                              html.Div(style={'backgroundColor':colors['back']},
                                       children=[dbc.Card(
                                           dbc.CardBody(
                                               dcc.Graph(id="fig2", figure=fig,
                                                        style={'backgroundColor':colors['background'],
                                                              'color':colors['text'],
                                                             'font-family':colors['font-family']})#,
                                               #'height':500})#, 'width':800}))
                                                   ),color=colors['background']
                                           )]
                                      )
                              ],width=9)
                     ]),
            html.Br(),
            dbc.Row([#graph 1
                    html.Div(style={'backgroundColor':colors['back']},
                             children=[dbc.Card(
                                 dbc.CardBody(
                                     dcc.Graph(id="fig1", figure=fig,
                                               style={'backgroundColor':colors['background'],
                                                      'color':colors['text'],
                                                      'font-family':colors['font-family'],
                                                      'height':900})# 'width':800})
                                     ),color=colors['background']
                                 )]
                             )
                    ])
            ]),color=colors['back']
            )])
                           )

#Functionality based on user input
#callback function 1
"""Selecting graph option based on user feedback"""
@app.callback(Output('fig1', 'figure'),[Input('Scope', 'value'), Input('Data Input', 'value'), Input('Policy','value')])
def updatefig1(s,d,p):
    if p=='NA' and d=='StringencyIndex':
        return px.scatter_geo(df, locations='CountryCode', color="Continent_Name",
                             hover_name="CountryName", size=d, size_max=10,
                             animation_frame="Date", # to create animation frame based on year attribute
                             title = ''+s+' COVID-19 '+d+' by Country and Contient between March 1st and May 20th 2020',
                             projection="natural earth").update_geos(scope=s, 
                                                                     showcountries=True, 
                                                                     showocean=True, 
                                                                     oceancolor="LightBlue").update_layout(title_x = 0.5,
                                                                                                               plot_bgcolor=colors['background'],
                                                                                                               paper_bgcolor=colors['background'],
                                                                                                               font_color=colors['text'])
    elif p=="NA":
        return px.scatter_geo(df, locations='CountryCode', color="Continent_Name",
                             hover_name="CountryName", size=d, size_max=40,
                             animation_frame="Date", # to create animation frame based on year attribute
                             title = ''+s+' COVID-19 '+d+' by Country and Contient between March 1st and May 20th 2020',
                             projection="natural earth").update_geos(scope=s, 
                                                                     showcountries=True, 
                                                                     showocean=True, 
                                                                     oceancolor="LightBlue").update_layout(title_x = 0.5,
                                                                                                               plot_bgcolor=colors['background'],
                                                                                                               paper_bgcolor=colors['background'],
                                                                                                               font_color=colors['text'])
    elif p!="NA": 
        return px.choropleth(df, locations='CountryCode', hover_name='CountryName',
                             color=p, color_continuous_scale=px.colors.sequential.Plasma,
                             animation_frame="Date",
                             title = ''+s+' COVID-19 '+d+' by Country and Contient between March 1st and May 20th 2020',
                             projection='natural earth').update_geos(scope=s,
                                                                      showcountries=True,
                                                                      showocean=True,
                                                                      oceancolor="LightBlue").update_layout(title_x = 0.5,
                                                                                                                plot_bgcolor=colors['background'],
                                                                                                                paper_bgcolor=colors['background'],
                                                                                                                font_color=colors['text'])
                                                                                                           
#2nd callback to avoid axes becoming subplots.
@app.callback(Output('fig2', 'figure'),[Input('Data Input', 'value'), Input('Policy','value')])
def updatefig2(d,p):
    if p=='NA' and d=='ConfirmedCases':
        return px.line(data_frame=dftop5,
                       x='Date', 
                       y=d, 
                       color='CountryName',
                       log_y=True,
                       title=''+d+' in the top five countries').update_layout(title_x = 0.5,
                                                                                  plot_bgcolor=colors['background'],
                                                                                  paper_bgcolor=colors['background'],
                                                                                  font_color=colors['text'])
    
    elif p=='NA':
        return px.line(data_frame=dftop5,
                       x='Date', 
                       y=d, 
                       color='CountryName',
                       title=''+d+' in the top five countries').update_layout(title_x = 0.5,
                                                                                  plot_bgcolor=colors['background'],
                                                                                  paper_bgcolor=colors['background'],
                                                                                  font_color=colors['text'])
    elif p!="NA": 
        return px.line(data_frame=dftop5,
                       x='Date', 
                       y=p, 
                       color='CountryName',
                       title=''+p+' in the top five countries').update_layout(title_x = 0.5,
                                                                                  plot_bgcolor=colors['background'],
                                                                                  paper_bgcolor=colors['background'],
                                                                                  font_color=colors['text'])
                                                     
# Run the app in a local server 127.0.0.1 (port=8050 by default but you can change)
app.run_server(debug=True, use_reloader=False)
# Run http://127.0.0.1:8050/ in browser to test the app

##############################################################################

"""Q6 person drove from London to Dover, took a ferry from Dover to Calais, 
and drove from Calais to Charles de Gaulle Airport in Paris. The person then took a flight to Istanbul Airport. 
Use Mapbox to visualise the whole journey."""

"""MAPBOX MAPS"""

##tokens
pub_token = 'pk.eyJ1Ijoiam9yZGFub3R0ZXdpbGwiLCJhIjoiY2wzZTl1NTd2MGZuMzNmbDU2NGR1M2lrMCJ9.dsIlbHaoSVCnkSNe8fqxig'
my_token = 'pk.eyJ1Ijoiam9yZGFub3R0ZXdpbGwiLCJhIjoiY2wzZTl6MG42MGdjeDNscHJ6eXkzY3c1ZiJ9.vPJupwoKwnC6bS_Rtkjm6g'

px.set_mapbox_access_token(my_token)

#save the token in "mapbox.token" file
f = open("./mapbox.token", "w")
f.write(my_token)
f.close()

# read the token
token=open("./mapbox.token").read()

#style to use: "carto-darkmatter" OR "stamen-terrain"
#locations = ['Dover','Calais','Charles de Gaulle','Istanbul']

fig = go.Figure(go.Scattermapbox(mode = "markers+lines+text",
    lon = ['-0.12760','1.33122', '1.86932', '2.55083', '28.73009'],
    lat = ['51.50736','51.12782', '50.97264', '49.00800', '41.27682'],
    marker = {'size': 9, 'symbol': ["circle","car", "ferry", "car", "airport"]},
    text = ['London','Dvr','Calais','Charles de Gaulle','Istanbul'],
    #textfont = {'size':8},
    textposition ='top right'
    ))
fig.update_layout(mapbox = {'accesstoken': token,
                            'style': "outdoors",
                            'zoom': 5},
                  mapbox_center_lat = 46.59209,
                  mapbox_center_lon=15.30125,
                  )
fig.write_html('./CW2_Q6.html', auto_open=True)