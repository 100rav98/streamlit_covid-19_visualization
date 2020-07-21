import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


st.title("COVID-19 Analytics Dashboard")
st.sidebar.title("User Input Board")
st.markdown("This application is a COVID-19 dashboard that displays some insights from COVID-19 pandemic")
data_url="covid_19_india.csv"
@st.cache(allow_output_mutation=True,persist=True)
def load_data():
    data= pd.read_csv(data_url,sep=",")

    data.dropna()
    #data['Date']=pd.to_datetime(data['Date'])
    data.drop(data[data['State/UnionTerritory'].str.startswith('Cases')].index,inplace=True)
    data.drop(data[data['State/UnionTerritory'].str.startswith('Daman')].index,inplace=True)
    chng=list(data[data['State/UnionTerritory']=='Dadar Nagar Haveli'].index)
    cnj=list(data[data['State/UnionTerritory']=='Telengana'].index)
    for i in cnj:
        data['State/UnionTerritory'].loc[i]='Telangana'
    for i in chng:
        data['State/UnionTerritory'].loc[i]='Dadra and Nagar Haveli and Daman and Diu'
    data.rename(columns={'State/UnionTerritory':'States'},inplace=True)
    data['Active_Cases']= data['Confirmed'] - data['Cured']
    data['Death_to_Case_Ratio'] = np.round(data['Deaths']/data['Confirmed'],3)
    Foreign=list(data[data['ConfirmedForeignNational'] == '-'].index)
    for i in Foreign:
        data['ConfirmedForeignNational'].loc[i]=0
    data['ConfirmedForeignNational']=data['ConfirmedForeignNational'].astype(int)
    data['Foreign_perc']=np.round(data['ConfirmedForeignNational']/data['Confirmed'],3)
    data['Recov_perc']=np.round(data['Cured']/data['Confirmed'],3)
    data['Active_perc']=np.round(data['Active_Cases']/data['Confirmed'],3)
    return data

df=load_data()

locations=list(df['States'].drop_duplicates())
# all_loc = ['Select an option','All States & UTs ']
# all_loc.extend(locations)


st.sidebar.subheader("Covid-19 LIVE Count")
choose_one = st.sidebar.radio('Choose one option', ('World', 'India'))
if not st.sidebar.checkbox("Hide Report", False,key='3'):

    import requests
    import urllib.request
    from bs4 import BeautifulSoup
    import time
    url="https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data"
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "html5lib")


    Nama=[]
    fou=soup.find_all('tr',attrs={'class':'sorttop'})
    for row in fou[0].find_all('th',attrs={'style':'text-align:right; font-weight: normal; padding: 0 2px;'}):
        Nama.append(row.text)

    World_Cases=int(Nama[0].strip('\n').replace("," , ""))
    World_Deaths=int(Nama[1].strip('\n').replace("," , ""))
    World_Recovered=int(Nama[2].strip('\n').replace("," , ""))
    World_Active = World_Cases - World_Deaths - World_Recovered

    if choose_one=='World':

        st.markdown("### World covid-19 LIVE count")
        st.markdown("### %i Covid-19 Cases have been confirmed worldwide" %World_Cases)
        st.markdown("### %i lives have been lost due to Covid-19 worldwide" %World_Deaths)
        st.markdown("### %i people have recovered from Covid-19 worldwide" %World_Recovered)
        st.markdown("### %i Covid-19 cases are currently active worldwide" %World_Active)


        cou={'Category':['World_Cases','World_Deaths','World_Recovered','World_Active'] , 'Value':[World_Cases,World_Deaths,World_Recovered,World_Active]}
        dr=pd.DataFrame(cou)
        figu=px.bar(dr,x='Category',y='Value')
        st.plotly_chart(figu)

        percent_active = np.round((World_Active / World_Cases) , 3)
        percent_deaths = np.round((World_Deaths / World_Cases) , 3)
        percent_reco = np.round((World_Recovered / World_Cases) , 3)
        mou={'Category':['Active Cases','Deaths','Recovered'] , 'Values':[percent_active,percent_deaths,percent_reco]}
        dw=pd.DataFrame(mou)


        fig = px.pie(dw, values='Values', names='Category', title='Percentage of Active Cases , Recoveries and Deaths Worldwide')
        st.plotly_chart(fig)
    else:
        every_table=soup.find_all("table",attrs={'class':"wikitable plainrowheaders sortable"})
        cells=[]

        for row in every_table[0].find_all('tr'):
               for col in row.find_all('td'):
                    cells.append(col.text)
        Cases_=int(cells[11-3].strip('\n').replace("," , ""))
        Deaths_=int(cells[11-2].strip('\n').replace("," , ""))
        Reco_=int(cells[11-1].strip('\n').replace("," , ""))
        Active_ = Cases_ - Deaths_ - Reco_


        st.markdown("### India covid-19 LIVE count")
        st.markdown("### %i Covid-19 Cases have been confirmed in India" %Cases_)
        st.markdown("### %i lives have been lost due to Covid-19 in India" %Deaths_)
        st.markdown("### %i people have recovered from Covid-19 in India" %Reco_)
        st.markdown("### %i Covid-19 cases are currently active in India" %Active_)


        cou={'Category':['Confirmed_Cases','Deaths','Recoveries','Active_Cases'] , 'Value':[Cases_,Deaths_,Reco_,Active_]}
        dr=pd.DataFrame(cou)
        figu=px.bar(dr,x='Category',y='Value')
        st.plotly_chart(figu)

        percent_active = np.round((Active_ / Cases_) , 3)
        percent_deaths = np.round((Deaths_ / Cases_) , 3)
        percent_reco = np.round((Reco_ / Cases_) , 3)
        mou={'Category':['Active Cases','Deaths','Recovered'] , 'Values':[percent_active,percent_deaths,percent_reco]}
        dw=pd.DataFrame(mou)


        fig = px.pie(dw, values='Values', names='Category', title='Percentage of Active Cases , Recoveries and Deaths in India')
        st.plotly_chart(fig)

        Every=df.groupby(['Date'],as_index=False,sort=False).sum()
        st.markdown("The graph for line chart shown is based on data collected till 13th July,2020")
        fig=px.line(Every,x=Every['Date'],y=[Every['Confirmed'],Every['Active_Cases'],Every['Cured'],Every['Deaths']],hover_data=['Deaths'],height=600,width=900)

        st.plotly_chart(fig)


st.sidebar.markdown("### Statewise Covid-19 Case Distribution till 13th July 2020")
select = st.sidebar.selectbox('States/UnionTerritory',locations, key='1')
if st.sidebar.checkbox("Show Line Chart",False, key='21'):

        st.markdown("## Covid-19 Case Analysis for %s  as of 13th July,2020" %select)
        st.markdown("The datasets used for creating the reports have been taken from kaggle ")

        Every=df.query('States== @select').groupby(['Date'],as_index=False,sort=False).sum()
        fig=px.line(Every,x=Every['Date'],y=[Every['Confirmed'],Every['Active_Cases'],Every['Cured'],Every['Deaths']],hover_data=['Deaths'],height=600,width=900)
        st.plotly_chart(fig)



st.sidebar.subheader("Choose Key metrics to display for %s" %select)
choice = st.sidebar.multiselect('Key Metrics', ('Active_Cases','Deaths','Cured','Death_to_Case_Ratio'), key='5')
Entire=df.query("States ==@select").groupby(['Date'],as_index=False,sort=False).sum()

if len(choice) > 0:
    st.subheader("Key Metrics for Covid-19 Visualization for %s" %select)
    fig = make_subplots(rows=len(choice), cols=1, subplot_titles=choice)
    for i in range(len(choice)):
             for j in range(1):

                 # fig = px.line(Entire,x=Entire['Date'],y=Entire[choice[i]],height=500)
                 fig.append_trace(go.Scatter(x=Entire['Date'], y=Entire[choice[i]],mode='lines',name=choice[i]),row=i+1, col=j+1)

    fig.update_layout(height=900, width=900)
    st.plotly_chart(fig)
