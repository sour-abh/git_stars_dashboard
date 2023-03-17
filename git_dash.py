#importing all the libraries
import numpy as np
import pandas as pd
import dash
from dash import dcc,html,Input,Output
import plotly.express as px
import seaborn as sns
from collections import Counter
#reading the data 
df=pd.read_csv('git_stars.csv')
df2=df[['Forks','Stars','Language','Domain']]
group1=pd.DataFrame(df2.groupby( 'Language',as_index=False).sum(numeric_only=True).sort_values('Stars',ascending=False))
group2=pd.DataFrame(df2.groupby( 'Domain',as_index=False).sum(numeric_only=True).sort_values('Stars',ascending=False))


def pivot(df):
    filtered_df=df[['Domain','Language']]
    pivot_df=pd.pivot_table(filtered_df,index='Domain',columns='Language',aggfunc=len)
    pivot_df.replace(np.nan,0,inplace=True)
    pivot_df.loc['total']=pivot_df.sum(axis=0)
    pivot_df.sort_values('total',axis=1,ascending=False,inplace=True)
    return pivot_df

def org_df(df):
    organisation=[]
    for i in range(0,len(df)):
        text=df['Name'][i]
        words=text.split("/")
        organisation_name=words[0]
        organisation.append(organisation_name)
    most_common = Counter(organisation).most_common(20)
    most_common_df=pd.DataFrame(most_common)
    most_common_df.reset_index()
    most_common_df.columns=['Organisation','repository']
    return most_common_df
#Creating the App and setting the Layout

app=dash.Dash(__name__)

app.layout=html.Div(children=[html.H1('GitHub Most popular repositories',style={'textAlign':'center','color':'#43bccd','font-size':40}),
                              html.Div([html.Div(dcc.Dropdown(id="language_dropdown",
                                                              options=[{'label':'All','value':'ALL'}]+[{'label':language,'value':language} for language in group1['Language'][:10]],
                                                              value='ALL',searchable=True,placeholder='search the language',
                                                              style={'width':'500px','padding-left':'250px','font-size':'20px','textAlign':'center','display':'flex'})),
                                       html.Div(dcc.Dropdown(id="domain_dropdown",
                                                             options=[{'label':'ALL Domains','value':'ALL'}]+[{'label':domain,'value':domain} for domain in df['Domain'].unique()],
                                                             value='ALL',searchable=True,placeholder='Search the specific Domain',
                                                             style={'width':'500px','padding-left':'100px','font-size':'20px','textAlign':'center','display':'flex'}))], style={'display':'flex'}),
html.Div(dcc.Interval(
    id="load_interval", 
    n_intervals=0, 
    max_intervals=0, #<-- only run once
    interval=1
)),
html.Br(),
html.Div([dcc.Graph(id='top_language')]),
html.Div([html.Div([dcc.Graph(id='domain_lang')]),html.Div([dcc.Graph(id='lang_domain')])],style={'display':'flex','justify-content':'space-around','flex-direction':'column'}),
html.Div([html.Div([dcc.Graph(id='scatter_lang',style={'display':'flex'})]),html.Div([dcc.Graph(id='scatter_domain',style={'display':'flex'})])],style={'display':'flex','flex-direction':'column','justify-content':'space-around'}),
html.Div([dcc.Graph(id='tree_lang')],style={'width':'100%','height':'500px'}),
html.Div([html.Div(dcc.Graph(id='pie_stars',style={'display':'flex','justify-content':'space-around'})),html.Div(dcc.Graph(id='pie_forks',style={'display':'flex','justify-content':'space-around'}))],style={'display':'flex','justify-content':'space-around','padding-bottom':'100px'}),
html.Div([html.Div([dcc.Graph(id='pie_stars_domain',style={'display':'flex','justify-content':'space-around'})]),html.Div([dcc.Graph(id='pie_forks_domain',style={'display':'flex','justify-content':'space-around'})])],style={'display':'flex','justify-content':'space-around','padding-bottom':'100px'}),
html.Div([dcc.Graph(id='org_repo')]),

],style={"background-image": 'url("/assets/img2.jpg")',"background-repeat": "no-repeat",'display':'flex','flex-direction':'column','justify-content':'space-around',"Padding-top":"-20px"})

@app.callback(
    (Output(component_id='top_language',component_property='figure'),
     Input(component_id="load_interval", component_property="n_intervals"))
)
def top_lang(n_intervals:int):
    fig=px.bar(group1[:10],x="Stars",y='Language',color='Language',title='Top 10 Language with most stars',text_auto='0.2s',orientation='h')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#6d6875'),titlefont=dict(color='#6d6875'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#6d6875'),titlefont=dict(color='#6d6875'))
    return (fig,)

#pie chart

@app.callback([
    Output(component_id='pie_stars',component_property='figure'),
    Output(component_id='pie_forks',component_property='figure'),
    Input(component_id="load_interval", component_property="n_intervals"),
])
def pie_star(n_intervals:int):
    filtered_df=group1.sort_values('Forks',ascending=False)
    fig=px.pie(group1[:10],names='Language',values='Stars',title='Total Stars accross different language')
    fig2=px.pie(filtered_df[:10],names='Language',values='Forks',title='Total Forks accross different language')
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig2.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#2b2d42'),titlefont=dict(color='#2b2d42'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#2b2d42'),titlefont=dict(color='#2b2d42'))
    fig2.update_xaxes(showgrid=False,tickfont=dict(color='#8d99ae'),titlefont=dict(color='#8d99ae'))
    fig2.update_yaxes(showgrid=False,tickfont=dict(color='#8d99ae'),titlefont=dict(color='#8d99ae'))
    return [fig,fig2]

#pie chart domain for stars and forks

@app.callback([
    Output(component_id='pie_stars_domain',component_property='figure'),
    Output(component_id='pie_forks_domain',component_property='figure'),
   Input(component_id="load_interval", component_property="n_intervals"),
])
def pie_star(n_intervals:int):
    filtered_df=group2.sort_values('Forks',ascending=False)
    fig=px.pie(group2[:10],names='Domain',values='Stars',title='Total Forks accross different Domains')
    fig2=px.pie(filtered_df[:10],names='Domain',values='Forks',title='Total Forks accross different Domains')
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig2.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#fb6f92'),titlefont=dict(color='#fb6f92'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#fb6f92'),titlefont=dict(color='#fb6f92'))
    fig2.update_xaxes(showgrid=False,tickfont=dict(color='#fb6f92'),titlefont=dict(color='#fb6f92'))
    fig2.update_yaxes(showgrid=False,tickfont=dict(color='#fb6f92'),titlefont=dict(color='#fb6f92'))
    return [fig,fig2]


#tree language and domain

@app.callback(
    Output(component_id='tree_lang',component_property='figure'),
    Input(component_id="load_interval", component_property="n_intervals"),
)
def tree(n_intervals:int):
    tree_fig=px.treemap(df,path=['Domain','Language'],color='Language',color_continuous_scale='RdBu',title='Language in different domains')
    return tree_fig

#domain and language count 

@app.callback(
    Output(component_id='domain_lang',component_property='figure')
,Input(component_id='language_dropdown',component_property='value')
)
def domain_lang(entered_lang):
    pivot_df=pivot(df)
    if entered_lang =='ALL':
        fig=px.bar(pivot_df.iloc[:,:10],title='No of Repository count accross Languages')
    else:
        fig=px.bar(pivot_df[entered_lang],title='No of Repository count accross Languages')
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#f28482'),titlefont=dict(color='#f28482'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#f28482'),titlefont=dict(color='#f28482'))
    return fig

#lang and domain count 

@app.callback(
    Output(component_id='lang_domain',component_property='figure')
,Input(component_id='domain_dropdown',component_property='value')
)
def domain_lang(entered_domain):
    pivot_df=pivot(df)
    if entered_domain =='ALL':
        fig=px.bar(pivot_df.T[:10],title='No of Repository count accross Domains')
    else:
        fig=px.bar(pivot_df.T[entered_domain],title='No of Repository count accross Domains')
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#ff70a6'),titlefont=dict(color='#ff70a6'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#ff70a6'),titlefont=dict(color='#ff70a6'))    
    return fig

#scatter plot

@app.callback(
    Output(component_id='scatter_lang',component_property='figure'),
    Input(component_id='language_dropdown',component_property='value')
)
def scatter_lang(entered_lang):
    filtered_df=df[(df['Forks']<30000) & (df['Stars']<60000)]
    if entered_lang == "ALL":
        fig=px.scatter(filtered_df,x='Stars',y='Forks',color='Language',hover_name="Name", hover_data=["Name", "Stars"],title='Stars vs Forks')
    else:
        fig=px.scatter(filtered_df[filtered_df['Language']== entered_lang],x='Stars',y='Forks',color='Language',hover_name="Name", hover_data=["Name", "Stars"],title="Stars V/S Forks")
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#01497c'),titlefont=dict(color='#01497c'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#01497c'),titlefont=dict(color='#01497c'))       
    return fig

# scatter plot domain 

@app.callback(
    Output(component_id='scatter_domain',component_property='figure'),
    Input(component_id='domain_dropdown',component_property='value')
)
def scatter_lang(entered_domain):
    filtered_df=df[(df['Forks']<30000) & (df['Stars']<60000)]
    if entered_domain == "ALL":
        fig=px.scatter(filtered_df,x='Stars',y='Forks',color='Domain',hover_name="Name", hover_data=["Name", "Stars"],title="Stars V/S Forks accross different Domains")
        
    else:
        
        fig=px.scatter(filtered_df[filtered_df['Domain']== entered_domain],x='Stars',y='Forks',color='Domain',hover_name="Name", hover_data=["Name", "Stars"],title="Stars V/S Forks accross different Domains")
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#7678ed'),titlefont=dict(color='#7678ed'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#7678ed'),titlefont=dict(color='#7678ed')) 
    return fig

# org info 

@app.callback(
    Output(component_id='org_repo',component_property='figure'),
    Input(component_id="load_interval", component_property="n_intervals"),
)
def org_bar(n_intervals:int):
    org=org_df(df)
    
    fig=px.bar(org,x='Organisation',y='repository',color_discrete_sequence =['crimson'],title="Count of Popular repository of Organisation")
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)",
                  plot_bgcolor = "rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False,tickfont=dict(color='#fdffb6'),titlefont=dict(color='#fdffb6'))
    fig.update_yaxes(showgrid=False,tickfont=dict(color='#fdffb6'),titlefont=dict(color='#fdffb6'))
    return fig

if __name__ =="__main__":
    app.run_server(debug=True)