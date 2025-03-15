import streamlit as st
import pandas as pd
import mysql.connector


st.set_page_config(page_title="Sports Dashboard", page_icon="🎾", layout="wide")
st.subheader("🎾Tennis Competition Analytics")
st.markdown("##")

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="H1a2r3i4####",
    auth_plugin='mysql_native_password'
)

mycursor = mydb.cursor()

mycursor.execute("USE semi")


opt=st.sidebar.selectbox("Select an option for analysis", options=("Select","Competitions","Venues","Competitors"))
if opt=="Competitions":
    st.write('### Types of Competitions')
    sql= 'SELECT category_name FROM category'
    mycursor.execute(sql)
    result=mycursor.fetchall()
    df=pd.DataFrame(result, columns=["Type of Competitons"])
    st.dataframe(df,hide_index=True)
    st.write('### Competitions per Category')
    sql1='SELECT category_id, COUNT(*) AS number_of_competitions FROM competitions GROUP BY category_id'
    mycursor.execute(sql1)
    result1=mycursor.fetchall()
    df1=pd.DataFrame(result1, columns=["Category","No of Competitons"])
    st.dataframe(df1,hide_index=True)
elif opt=="Venues":
    st.write('### Countries Vs Venues')
    sql2='SELECT country_name, COUNT(*) FROM venues GROUP BY country_name'
    mycursor.execute(sql2)
    result2=mycursor.fetchall()
    df2=pd.DataFrame(result2, columns=["Country","No of Venues"])
    st.dataframe(df2,hide_index=True)
elif opt=="Competitors":
    choice=st.sidebar.radio("Select a sub option", options=("Select","Search By Competitor","Search By Rankings","Top Ranked Competitors","Competitors By Country"))
    if choice=="Search By Rankings":
        st.subheader("Rankings:")
        slider_range=st.slider("Select the Rankings Range",value=[0,500])
        mycursor.execute(f"Select name,rankk from comptr_rankings JOIN comptr_table ON comptr_rankings.competitor_id=comptr_table.competitor_id where rankk BETWEEN '{slider_range[0]}' AND '{slider_range[1]}' ORDER BY rankk;")
        result3=mycursor.fetchall()
        df3=pd.DataFrame(result3, columns=["Competitor Name","Rank"])
        st.dataframe(df3,hide_index=True)
    elif choice=="Search By Competitor":
         st.subheader("Competitor Full Details:")
         name=st.text_input("Enter Competitor Name:")
         mycursor.execute(f"Select comptr_table.competitor_id,name,country,rankk,movement,points,competitions_played from comptr_table JOIN comptr_rankings ON comptr_table.competitor_id=comptr_rankings.competitor_id where name='{name}';")
         result4=mycursor.fetchall()
         df4=pd.DataFrame(result4, columns=["Competitor_ID","Name","Country","Rankk","Movement","Points","Competitions Played"])
         st.dataframe(df4,hide_index=True)
    elif choice=="Top Ranked Competitors":
        st.subheader("Top Competitors:")
        sql= 'SELECT name,country,rankk,points,competitions_played FROM comptr_table JOIN comptr_rankings ON comptr_table.competitor_id=comptr_rankings.competitor_id WHERE rankk<=5 ORDER BY rankk'
        mycursor.execute(sql)
        result5=mycursor.fetchall()
        df5=pd.DataFrame(result5, columns=["Competitor_Name","Country","Rank","Points","Competitions Played"])
        st.dataframe(df5,hide_index=True)
    elif choice=="Competitors By Country":
        st.subheader("Competitors & Points by Country:")
        sql= 'SELECT country, COUNT(country), SUM(points) FROM comptr_table JOIN comptr_rankings ON comptr_table.competitor_id=comptr_rankings.competitor_id GROUP BY country'
        mycursor.execute(sql)
        result6=mycursor.fetchall()
        df6=pd.DataFrame(result6, columns=["Country","No of Competitors","Total Points"])
        st.dataframe(df6,hide_index=True)