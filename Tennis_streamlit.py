import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Sports Dashboard", page_icon="🎾", layout="wide")
st.header("🎾Tennis Competition Analytics")
st.markdown("##")

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="H1a2r3i4####",
    auth_plugin='mysql_native_password'
)

mycursor = mydb.cursor()

mycursor.execute("USE semi")

def run_query(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return pd.DataFrame(data)


st.sidebar.subheader("Choose an option for analysis")
opt=st.sidebar.selectbox("", options=("Select","Competitors","Competitions","Venues"))
if opt == "Select":

    col1, col2, col3,col4 = st.columns(4, gap='large')
    
    with col1:
        total_competitors = run_query('SELECT COUNT(*) FROM comptr_table').iloc[0, 0]
        st.info('Total Competitors')
        st.metric("", total_competitors,border=True)

    with col2:
        total_countries = run_query('SELECT COUNT(DISTINCT country) FROM comptr_table').iloc[0, 0]
        st.info('Total Countries ')
        st.metric("", total_countries,border=True)

    with col3:
        highest_points = run_query('SELECT MAX(points) FROM comptr_rankings').iloc[0, 0]
        st.info('Highest Points Scored')
        st.metric("", highest_points,border=True)
    
    with col4:
        total_venues = run_query('SELECT COUNT(venue_id) FROM venues').iloc[0, 0]
        st.info('Total Venues')
        st.metric("", total_venues,border=True)




if opt=="Competitions":
    st.subheader('Types of Competitions')
    sql= 'SELECT category_name FROM category'
    mycursor.execute(sql)
    result=mycursor.fetchall()
    df=pd.DataFrame(result, columns=["Type of Competitons"])
    st.dataframe(df,hide_index=True,width=450,height=500)
    st.subheader('Competitions per Category')
    sql1='SELECT category_id, COUNT(*) AS number_of_competitions FROM competitions GROUP BY category_id'
    mycursor.execute(sql1)
    result1=mycursor.fetchall()
    df1=pd.DataFrame(result1, columns=["Category","No of Competitons"])
    st.dataframe(df1,hide_index=True,width=450,height=500)



elif opt=="Venues":
    st.subheader('Countries Vs Venues')
    sql2='SELECT country_name, COUNT(*) FROM venues GROUP BY country_name'
    mycursor.execute(sql2)
    result2=mycursor.fetchall()
    df2=pd.DataFrame(result2, columns=["Country","No of Venues"])
    st.dataframe(df2,hide_index=True,width=350,height=500)



elif opt=="Competitors":
    choice=st.sidebar.radio("Select a sub option", options=("Search By Competitor Name","Search By Rankings","Top Ranked Competitors","Country wise Analysis","Search by Points","Competitors by Country","Competitors with Highest Points"))
    if choice=="Search By Rankings":
        st.subheader("Rankings:")
        slider_range=st.slider("Select the Rankings Range",value=[0,500])
        mycursor.execute(f"Select name,rankk from comptr_rankings JOIN comptr_table ON comptr_rankings.competitor_id=comptr_table.competitor_id where rankk BETWEEN '{slider_range[0]}' AND '{slider_range[1]}' ORDER BY rankk;")
        result3=mycursor.fetchall()
        df3=pd.DataFrame(result3, columns=["Competitor Name","Rank"])
        st.dataframe(df3,hide_index=True,width=450,height=500)
        
    elif choice=="Search By Competitor Name":
         show_competitors='SELECT name FROM comptr_table'
         mycursor.execute(show_competitors)
         comp_list=mycursor.fetchall()
         comp_list.insert(0,'Select') ## To make the default option as 'Select' while the page loads
       
         select=st.selectbox(label= 'Choose the Competitor', options=comp_list)
         select = ''.join(select) ##Converting tuple to a string
         mycursor.execute(f"Select comptr_table.competitor_id,name,country,rankk,movement,points,competitions_played from comptr_table JOIN comptr_rankings ON comptr_table.competitor_id=comptr_rankings.competitor_id where name='{select}';")
         result4=mycursor.fetchall()
         df4=pd.DataFrame(result4, columns=["Competitor_ID","Name","Country","Rankk","Movement","Points","Competitions Played"])
         st.write('Details of the Competitor')
         st.dataframe(df4,hide_index=True)
         

    elif choice=="Top Ranked Competitors":
        st.subheader("Top Competitors:")
        sql= 'SELECT name,country,rankk,points,competitions_played FROM comptr_table JOIN comptr_rankings ON comptr_table.competitor_id=comptr_rankings.competitor_id WHERE rankk<=5 ORDER BY rankk'
        mycursor.execute(sql)
        result5=mycursor.fetchall()
        df5=pd.DataFrame(result5, columns=["Competitor_Name","Country","Rank","Points","Competitions Played"])
        st.dataframe(df5,hide_index=True)

    elif choice=="Country wise Analysis":
        st.subheader("Country wise Analysis:")
        sql= 'SELECT country, COUNT(country), ROUND(AVG(points)) FROM comptr_table JOIN comptr_rankings ON comptr_table.competitor_id=comptr_rankings.competitor_id GROUP BY country'
        mycursor.execute(sql)
        result6=mycursor.fetchall()
        df6=pd.DataFrame(result6, columns=["Country","No of Competitors","Average Points Scored"])
        st.dataframe(df6,hide_index=True,width=450,height=500)


    elif choice=="Competitors by Country":
         show_country='SELECT DISTINCT country FROM comptr_table'
         mycursor.execute(show_country)
         country_list=mycursor.fetchall()
         country_list.insert(0,'Select') ## To make the default option as 'Select' while the page loads
       
        
         select=st.selectbox(label= 'Choose the Country', options=country_list)
         select = ''.join(select) ##Converting tuple to a string
         mycursor.execute(f"Select name FROM comptr_table where country='{select}';")
         result7=mycursor.fetchall()
         df7=pd.DataFrame(result7, columns=["Name of the Competitors"])
         st.write('Competitors who belong to the country you have selected')
         st.dataframe(df7,hide_index=True,width=450,height=500)

    elif choice=="Search by Points":
         st.subheader("Points:")
         slider_range=st.slider("Select the Points Range",value=[100,1100])
         mycursor.execute(f"Select name,points from comptr_rankings JOIN comptr_table ON comptr_rankings.competitor_id=comptr_table.competitor_id where points BETWEEN '{slider_range[0]}' AND '{slider_range[1]}' ORDER BY points;")
         result8=mycursor.fetchall()
         df8=pd.DataFrame(result8, columns=["Competitor Name","Points"])
         st.dataframe(df8,hide_index=True,width=350,height=500)

    elif choice=="Competitors with Highest Points":
         st.subheader("Competitors with Highest Points:")
         sql= 'SELECT name,rankk,points,competitions_played FROM comptr_rankings JOIN comptr_table ON comptr_table.competitor_id=comptr_rankings.competitor_id ORDER BY points DESC LIMIT 10'
         mycursor.execute(sql)
         result9=mycursor.fetchall()
         df9=pd.DataFrame(result9, columns=["Competitor_Name","Rank","Points","Competitions Played"])
         st.dataframe(df9,hide_index=True,width=800,height=500)
