from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt
import pandas as pd

mysqlauth = pd.DataFrame.from_csv('/home/kristy/Documents/auth_codes/mysql_user.csv')
sqluser = mysqlauth.username[0]
sqlpass = mysqlauth.password[0]

citydb = mdb.connect(user=sqluser, host="localhost", db="world_innodb", password=sqlpass, charset='utf8')
con = mdb.connect(user=sqluser, host="localhost", db="charity_data", password=sqlpass, charset='utf8')

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home', user = { 'nickname': 'Miguel' },
        )

@app.route('/db')
def cities_page():
    with citydb: 
        cur = citydb.cursor()
        cur.execute("SELECT Name FROM City LIMIT 15;")
        query_results = cur.fetchall()
    cities = ""
    for result in query_results:
        cities += result[0]
        cities += "<br>"
    return cities

@app.route("/db_fancy")
def cities_page_fancy():
    with citydb:
        cur = citydb.cursor()
        cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")

        query_results = cur.fetchall()
    cities = []
    for result in query_results:
        cities.append(dict(name=result[0], country=result[1], population=result[2]))
    return render_template('cities.html', cities=cities)

"""
@app.route('/input')
def cities_input():
    return render_template("input.html")

@app.route('/output')
def cities_output():
    #pull 'ID' from input field and store it
    city = request.args.get('ID')

    with db:
        cur = db.cursor()
        #just select the city from the world_innodb that the user inputs
        cur.execute("SELECT Name, CountryCode,  Population FROM City WHERE Name='%s';" % city)
        query_results = cur.fetchall()

    cities = []
    for result in query_results:
        cities.append(dict(name=result[0], country=result[1], population=result[2]))
    #call a function from a_Model package. note we are only pulling one result in the query
    if len(cities) > 0:
        pop_input = cities[0]['population']
        the_result = ModelIt(city, pop_input)
    else:
        the_result = 'unknown because you entered a city not included in the database'

    return render_template("output.html", cities = cities, the_result = the_result)
"""

@app.route('/input')
def charity_input():
    return render_template("charity_input.html")

@app.route('/output')
def charity_output():
    # pull 'ID' from input field and store it as the target disease
    disease = request.args.get('ID')
    clean_disease_name = '_'.join(disease.lower().replace('\'s disease','').split())

    # read SQL table into pandas data frame and convert to list of dictionaries
    try:
        with con:
            panda_char = pd.read_sql("SELECT * FROM " + str(clean_disease_name), con)

        charities = panda_char.to_dict(outtype='records')
    except:
        custom_error = "Sorry, that disease is not in our database."
        charities = []
        the_result = 0
        return render_template("charity_output.html", charities = charities, the_result = the_result, custom_error = custom_error)

    """
    if len(charities) > 0:
        pop_input = charities[0]['population']
        the_result = ModelIt(city, pop_input)
    else:
        the_result = 'unknown because you entered a city not included in the database'
    """

    the_result = str(0) #placeholder for now - the_result isn't used in current output template
  
    return render_template("charity_output.html", charities = charities, the_result = the_result, custom_error = '')

