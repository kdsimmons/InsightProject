from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt
import pandas as pd

mysqlauth = pd.DataFrame.from_csv('/home/kristy/Documents/auth_codes/mysql_user.csv')
sqluser = mysqlauth.username[0]
sqlpass = mysqlauth.password[0]

con = mdb.connect(user=sqluser, host="localhost", db="charity_data", password=sqlpass, charset='utf8')

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home', user = { 'nickname': 'Miguel' },
        )

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

    the_result = str(0) #placeholder for now - the_result is only used for debugging
  
    return render_template("charity_output.html", charities = charities, the_result = the_result, custom_error = '')

