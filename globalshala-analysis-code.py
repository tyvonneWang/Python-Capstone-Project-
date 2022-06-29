from collections import OrderedDict
from pycountry import countries as Co

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots as ms
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate


external_stylesheets = [dbc.themes.BOOTSTRAP]
app= dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title= "Globalshala project proposal"

#=================================================================

def getCountryCode(countryName):
    return Co.get(name=countryName)

def addCountryCode(dataF):
    countriesCodes = []
    for ro in list(OrderedDict.fromkeys(dataF['Country'])):
        country = getCountryCode(ro)
        if country is not None:
            countriesCodes.append(str(country.alpha_3))
        else:
            countriesCodes.append("None")
    result= dataF["Country_code"] = countriesCodes
    return result

# import scv data into pandas

df_NewSubAll=pd.read_csv("NewSubmissionReport.csv",encoding='windows-1252')
df_NewSubAll.columns=df_NewSubAll.columns.str.replace(' ', '_')
df_NewSub= df_NewSubAll.groupby(['Country', 'Submission_Status']).Submission_ID.count()
df_submissionsAll=df_NewSubAll.groupby(['Country']).Submission_ID.count()
df_submissionsAll= df_submissionsAll.reset_index()
df_NewSub = df_NewSub.reset_index()
# print(df_NewSub.head())

#Add country code to submissions================================
addCountryCode(df_submissionsAll)

subCopy=df_NewSub.copy()

withDraws=subCopy[subCopy['Submission_Status'] == 'Withdrawn']
is_max_withdraw=withDraws['Submission_ID']==withDraws.Submission_ID.max()
is_max_withdraw_country=withDraws[is_max_withdraw]
is_max_withdraw_country=str(is_max_withdraw_country).split(' ')[9]

#Add country code to withdraws================================
withDraws=withDraws.reindex()
addCountryCode(withDraws)

drafts=subCopy[subCopy['Submission_Status'] == 'Draft']
is_max_draft=drafts['Submission_ID']==drafts.Submission_ID.max()
is_max_draft_country=drafts[is_max_draft]
is_max_draft_country=str(is_max_draft_country).split(' ')[9]

#Add country code to withdraws================================
drafts=drafts.reindex()
addCountryCode(drafts)


is_max_submissions=df_submissionsAll['Submission_ID']==df_submissionsAll.Submission_ID.max()
is_max_submissions_country=df_submissionsAll[is_max_submissions]
is_max_submissions_country=str(is_max_submissions_country).split(' ')[9]


countries = []
countries.append({"label":"--select country--", "value": 'All'})
countries.append({"label":"All countries", "value": 'All'})

for row in list(OrderedDict.fromkeys(df_NewSub['Country'])):
    countries.append({"label":str(row), "value": str(row)})

df_Sup_U_adds=pd.read_csv("Superhero-U-Ads-Report-Sep-23-2020-to-Sep-28-2020.csv")
df_wpforms=pd.read_csv("wpforms-3186-Round-1-Feedback-Superhero-U-2021-02-04-18-05-26.csv")


df_Sup_U_adds = df_Sup_U_adds.reset_index()
df_wpforms = df_wpforms.reset_index()

#========================================================

#APP Layout

# 1. HEADER
#---------------------------------------------
colors = {
    'background': '#111111',
    'bodyColor':'#F5F5F5',
    'text': '#7FDBFF',
    # 'bodyColor':'#222411',
}
def get_page_heading_style():
    return {'backgroundColor': colors['background']}


def get_page_heading_title():
    return html.H1(children='Globalshala project proposal Dashboard',
                                        style={
                                        'textAlign': 'center',
                                        'color': colors['text']
                                    })

def get_page_heading_subtitle():
    return html.Div(children='Visualization of gloibalshala data generated from 2020 Superhero U competition conducted by Globalshala.',
                                         style={
                                             'textAlign':'center',
                                             'color':colors['text']
                                         })

def generate_page_header():
    main_header =  dbc.Row(
                            [
                                dbc.Col(get_page_heading_title(),md=12, className="mt-2")
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    subtitle_header = dbc.Row(
                            [
                                dbc.Col(get_page_heading_subtitle(),md=12,className="mb-3")
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    header = (main_header,subtitle_header)
    return header
#--------------------------------------------------------------
#2. generate cards
#----------------------------------------------------------------
def generate_card_content(card_header,label, card_value,overall_value):
    card_head_style = {'textAlign':'center','fontSize':'150%'}
    card_body_style = {'textAlign':'center','fontSize':'200%'}
    card_header = dbc.CardHeader(card_header,style=card_head_style)
    card_body = dbc.CardBody(
        [
            html.H5("{}".format(card_value), className="card-title",style=card_body_style),
            html.P(
                "{}: {}".format(label,overall_value),
                className="card-text",style={'textAlign':'center'}
            ),
            html.Br(),
        ]
    )
    card = [card_header,card_body]
    return card
#------------------------------------------------------------
def generate_cards():
    cards = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(generate_card_content("Country with most submissions",
                                                           'Submissions',
                                                            is_max_submissions_country,
                                                           df_submissionsAll.Submission_ID.max()
                                                           ),
                                     color="success", inverse=True),
                            md=dict(size=4,offset=0)
                            ),
                    dbc.Col(dbc.Card(generate_card_content("Country with most drafts",
                                                           'Drafts',
                                                           is_max_draft_country,
                                                           drafts.Submission_ID.max(),
                                                           ),
                                     color="warning", inverse=True),
                            md=dict(size=4)),
                    dbc.Col(dbc.Card(generate_card_content("Country with most withdraws",
                                                           'Withdraws',
                                                           is_max_withdraw_country,
                                                           withDraws.Submission_ID.max(),
                                                           ),
                                     color="dark", inverse=True),
                            md=dict(size=4)),
                ],
                className="mb-1",
            ),
        ],id='card1'
    )
    return cards
#-----------------------------------------------------------------------------------------

# GENERAE LAYOUT Function
#------------------------------------------------------------------------------------
def generate_layout():
    page_header = generate_page_header()
    layout = dbc.Container(
        [
            page_header[0],
            page_header[1],
            html.Hr(),
            generate_cards(),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(id="select_value",
                                     options=countries,
                                     multi=False,
                                     value="All",

                                     ),
                        md=dict(size=6, offset=3)
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.H3(id="output_container", children={}),md=dict(size=6, offset=4))
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id='my_data_graph', figure={}), md=dict(size=10, offset=1))
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id='my_data_map', figure={}), md=dict(size=10, offset=1))
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id='two_split_map', figure={}), md=dict(size=10, offset=1))
                ],
                align="center",
            ),

        ], fluid=True, style={'backgroundColor': colors['bodyColor']}
    )
    return layout
#-----------------------------------------------
# GENERATE LAYOUT
#------------------------------------------------------------------------------------
app.layout= generate_layout()

#=========================================================
#Connect the plotly prapgh with Dash components

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_data_graph', component_property='figure'),
     Output(component_id='my_data_map', component_property='figure'),
     Output(component_id='two_split_map', component_property='figure')],
    [Input(component_id='select_value', component_property='value')]
)
def update_graph(option_selected):
    if option_selected is None:
        raise PreventUpdate
    else:

        container = " The country you selected is: {}".format(option_selected)

        df1Copy = df_NewSub.copy()
        all_countries= True
        if option_selected !="All":
            df1Copy=df1Copy[df1Copy['Country'] == option_selected]
            all_countries = False

        #plotly express

        # 1. figure

        data=df1Copy
        barmode="group"
        if all_countries:
            data=df_NewSub
            barmode="relative"
        fig=px.bar(
              data_frame=data,
            x="Country",
            y="Submission_ID",
            color="Submission_Status",
            opacity=0.9,
            orientation="v",
            barmode=barmode,
            labels={"Submission_ID": "Submissions in 2020 superhero",
                    "Submission_Status":"Submission_Status"},
            title="2020 Superhero submissions",
            width=1400,
            height=720,
            template="gridon"
        )

        # 2. map

        datamap=px.choropleth(df_submissionsAll, locations="Country_code",

                              color="Submission_ID",
                              hover_name="Country",
                              projection="natural earth",
                              title="Globalshala Superhero 2020 Competition Attendancy",
                              color_continuous_scale=px.colors.sequential.Plasma)
        datamap.update_layout(title=dict(font=dict(size=28), x=0.5, xanchor='center'),
                              margin=dict(l=10, r=10, t=100,b=50))

        # 3. two split map

        sub_status=pd.DataFrame({'Withdraws': 'Withdraws', 'Drafts': 'Drafts'}, index=[0])
        rows=1
        cols=2
        split_map=ms(rows=rows, cols=cols,
                     specs=[[{'type': 'choropleth'} for co in np.arange(cols)] for ro in np.arange(rows)],
                     subplot_titles=list(sub_status.loc[0,:]))

        for i, status in enumerate(sub_status):
            data=withDraws
            if status =="Drafts":
                data = drafts
            split_map.add_trace(go.Choropleth(locations=data.Country_code,
                                              z=data.Submission_ID,
                                              colorbar_title="Withdraws / Drafts",
                                              marker_line_color="white",
                                              zmin=0,
                                              zmax=max(data.Submission_ID),
                                              ), row=1, col=i+1

            )


        split_map.update_layout(title_text="Globalshala Superhero 2020 Competition Attendancy. Withdraws VS Drafsts")
        for index, trace in enumerate(split_map.data):
            split_map.data[index].hovertemplate ='Country: %{location}<br>%{z:.0f} <extra></extra>'


    return container, fig, datamap,split_map

#========================================
#Run the app
if __name__== '__main__':
    app.run_server(debug=True)
