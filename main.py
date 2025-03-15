
## Establishing connection between Python and SQL for querying
import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="H1a2r3i4####",
    auth_plugin='mysql_native_password'
)
mycursor = mydb.cursor()
mycursor.execute("USE tennis")

## Importing Pandas
import pandas as pd


def create_category_competitions_table():
    ## Pulling data from Json to Dataframe through API
    import requests
    url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=rkDc94z5KnU5xSbHmUHtWeuOHauh7seE1TWpkxQr"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    import json
    data = json.loads(response.text)

    Normalized_data = pd.json_normalize(data['competitions']) ## Normalising the Dataframe since a column is of dictionary type
    df1=pd.DataFrame(Normalized_data)
    df1.rename(columns={'category.id':'category_id',}, inplace=True) ## Renaming columns to remove dots in the name
    df1.rename(columns={'category.name':'category_name',}, inplace=True)

    ## Creating a dataframe for Category table
    category_df=df1[df1.columns[4:6]]
    unique_category_df = category_df.drop_duplicates()

    ## Creating a dataframe for Competitions table
    df4=df1
    Competitions_df = df4.drop(['category_name','level'], axis=1)



    ## Creating Tables for Category & Competitions in MySql Server

    mycursor.execute("CREATE TABLE category (category_id VARCHAR(50) PRIMARY KEY, category_name VARCHAR(100) NOT NULL)")
    mycursor.execute("CREATE TABLE competitions (competitions_id VARCHAR(50) PRIMARY KEY, competition_name VARCHAR(100) NOT NULL, parent_id VARCHAR (50), type VARCHAR(20), gender VARCHAR(10), category_id VARCHAR(50), FOREIGN KEY(category_id) REFERENCES category(category_id))")

    category_query=("INSERT INTO category (category_id, category_name) VALUES(%s,%s)")
    category_data=unique_category_df[['category_id','category_name']].values.tolist()
    mycursor.executemany(category_query, category_data)
    mydb.commit()

    competitions_query=("INSERT INTO competitions (competitions_id, competition_name, parent_id, type, gender, category_id) VALUES(%s,%s,%s,%s,%s,%s)")
    Competitions_df=Competitions_df.fillna('Not Available')
    competitions_data=Competitions_df[['id','name','parent_id','type','gender','category_id']].values.tolist()
    mycursor.executemany(competitions_query, competitions_data)
    mydb.commit()

def create_complexes_and_venues_table():
    ## Pulling data from Json to Dataframe through API
    import requests
    url2 = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=rkDc94z5KnU5xSbHmUHtWeuOHauh7seE1TWpkxQr"
    headers2 = {"accept": "application/json"}
    response2 = requests.get(url2, headers=headers2)
    import json
    data2 = json.loads(response2.text)

    ## Creating a dataframe for Complexes table
    complexes=data2['complexes']
    complexes_list=[]
    for comp in complexes:
        complexes_list.append({
            "id": comp["id"],
            "name": comp["name"]
        })
    complexes_df=pd.DataFrame(complexes_list)

    ## Creating a dataframe for Venues table
    test_venues_list=[]
    for comp in complexes:
        for venue in comp.get("venues", []):
            test_venues_list.append({
                "venues_id": venue["id"],
                "name": venue["name"],
                "city name": venue["city_name"],
                "country name": venue["country_name"],
                "country code": venue["country_code"],
                "timezone":venue["timezone"],
                "complex_id": comp["id"]
            })
    test_venues_df = pd.DataFrame(test_venues_list)

    ## Creating Complexes and Venues tables in MySql Server
    mycursor.execute("CREATE TABLE complexes (complex_id VARCHAR(50) PRIMARY KEY, complex_name VARCHAR(100) NOT NULL)")
    complex_query=("INSERT INTO complexes (complex_id, complex_name) VALUES(%s,%s)")
    complex_data=complexes_df[['id','name']].values.tolist()
    mycursor.executemany(complex_query, complex_data)
    mydb.commit()

    mycursor.execute("CREATE TABLE venues (venue_id VARCHAR(50) PRIMARY KEY, venue_name VARCHAR(100) NOT NULL, city_name VARCHAR (100) NOT NULL, country_name VARCHAR (100) NOT NULL, country_code CHAR(3) NOT NULL, timezone VARCHAR(100) NOT NULL, complex_id VARCHAR(50), FOREIGN KEY(complex_id) REFERENCES complexes(complex_id))")
    venues_query=("INSERT INTO venues (venue_id, venue_name, city_name, country_name, country_code, timezone, complex_id) VALUES(%s,%s,%s,%s,%s,%s,%s)")
    venues_data=test_venues_df[['venues_id','name','city name','country name','country code','timezone','complex_id']].values.tolist()
    mycursor.executemany(venues_query, venues_data)
    mydb.commit()

def create_competitiors_and_rankings_table():
    ## Pulling data from Json to Dataframe through API
    import requests
    url3 = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=rkDc94z5KnU5xSbHmUHtWeuOHauh7seE1TWpkxQr"
    headers3 = {"accept": "application/json"}
    response3 = requests.get(url3, headers=headers3)
    import json
    data3 = json.loads(response3.text)

    ## Normalising the dataframe since a column is in the form of dictionary
    a=data3['rankings'][0]
    b=a['competitor_rankings']
    Normalized_data_1 = pd.json_normalize(b)
    Normalized_data_1=Normalized_data_1.assign(type_id=2,name='ATP', year=2025, week=11, gender='men')

    x=data3['rankings'][1]
    y=x['competitor_rankings']
    Normalized_data_2 = pd.json_normalize(y)
    Normalized_data_2=Normalized_data_2.assign(type_id=2,name='WTA', year=2025, week=10, gender='women')

    Doubles_Comp_Nor_Full_Table=pd.concat([Normalized_data_1,Normalized_data_2], axis=0)
    Doubles_Comp_Nor_Full_Table.rename(columns={'competitor.id':'competitor_id','competitor.name':'competitor_name','competitor.country':'competitor_country','competitor.country_code':'competitor_country_code','competitor.abbreviation':'competitor_abbreviation'}, inplace=True)


    ## Creating Competitor and Competitor Rankings tables in MySql Server
    mycursor.execute("CREATE TABLE comptr_table (competitor_id VARCHAR(50) PRIMARY KEY, name VARCHAR(100) NOT NULL, country VARCHAR(100) NOT NULL, country_code CHAR(3) NOT NULL, abbreviation VARCHAR(10) NOT NULL)")
    mycursor.execute("CREATE TABLE comptr_rankings (rank_id INT AUTO_INCREMENT PRIMARY KEY , rankk INT NOT NULL, movement INT NOT NULL, points INT NOT NULL, competitions_played INT NOT NULL, competitor_id VARCHAR(50), FOREIGN KEY(competitor_id) REFERENCES comptr_table(competitor_id))")
    Doubles_Comp_Nor_Full_Table=Doubles_Comp_Nor_Full_Table.fillna('---')

    comptr_table_query=("INSERT INTO comptr_table (competitor_id, name, country, country_code, abbreviation) VALUES(%s,%s,%s,%s,%s)")
    comptr_table_data=Doubles_Comp_Nor_Full_Table[['competitor_id','competitor_name','competitor_country','competitor_country_code','competitor_abbreviation']].values.tolist()
    mycursor.executemany(comptr_table_query, comptr_table_data)
    mydb.commit()

    comptr_rankings_query=("INSERT INTO comptr_rankings (rankk, movement, points, competitions_played, competitor_id) VALUES(%s,%s,%s,%s,%s)")
    comptr_rankings_data=Doubles_Comp_Nor_Full_Table[['rank','movement','points','competitions_played','competitor_id']].values.tolist()
    mycursor.executemany(comptr_rankings_query, comptr_rankings_data)
    mydb.commit()


## Function Calling
create_category_competitions_table()
create_complexes_and_venues_table()
create_competitiors_and_rankings_table()






























