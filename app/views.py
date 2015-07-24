from flask import render_template, request
from app import app
import pymysql as mdb
import pandas as pd
import sys, re
import program_rankings as rank
import numpy as np

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
def input():
    return render_template("input.html")

@app.route('/output')
def output():
    # pull input fields and store required features
    disease = request.args.get('disease')
    clean_disease_name = '_'.join(disease.lower().replace('\'s disease','').replace('\'s','').split())
    the_focus = disease.lower()

    req_state = request.args.get('state')
    req_string = 'state = "' + str(req_state) + '"' # string of preferences to plug into SQL query

    # pull input fields and store preferred features
    tax_pref = float(request.args.get('tax_exempt'))
    bbb_pref = float(request.args.get('bbb_accred'))
    cn_pref = float(request.args.get('cn_rated'))
    age_pref = float(request.args.get('age'))
    staff_pref = float(request.args.get('staff_size'))
    board_pref = float(request.args.get('board_size'))
    cont_pref = float(request.args.get('total_contributions'))
    expense_pref = float(request.args.get('total_expenses'))
    program_pref = float(request.args.get('percent_program'))
    twitter_pref = float(request.args.get('twitter_followers'))


    # Choose features
    feature_names = ['bbb_accred', 'tax_exempt', 'cn_rated', 'cn_overall', 'cn_acct_transp', 'cn_financial', 'percent_admin', 
                     'percent_fund', 'percent_program', 'staff_size', 'board_size',
                     'age', 'total_contributions', 'total_expenses', 'total_revenue', 'twitter_followers']

    # Hard-code user preferences for code development
    pref_list = {'bbb_accred' : bbb_pref, 
                              'cn_rated' : cn_pref, 
                              'tax_exempt' : tax_pref,
                              'cn_overall' : 100., 
                              'cn_acct_transp' : 100., 
                              'cn_financial' : 100., 
                              'percent_program' : program_pref, 
                              'staff_size' : staff_pref, 
                              'board_size' : board_pref,
                              'age' : age_pref, 
                              'total_contributions' : cont_pref, 
                              'total_expenses' : expense_pref,
                              'total_revenue' : 0.,
                              'twitter_followers' : twitter_pref }
    ideal_char = rank.convert_prefs_to_ideal(pref_list)
    """
    ideal_char = pd.DataFrame({'bbb_accred' : True, 
                              'cn_rated' : True, 
                              'tax_exempt' : True,
                              'cn_overall' : 100., 
                              'cn_acct_transp' : 100., 
                              'cn_financial' : 100, 
                              'percent_admin' : 10., 
                              'percent_fund' : 0., 
                              'percent_program' : 90., 
                              'staff_size' : 100, 
                              'board_size' : 10,
                              'age' : 10, 
                              'total_contributions' : 100000, 
                              'total_expenses' : 100000, 
                              'total_revenue' : 0, 
                              'twitter_followers' : 10000 },
                             index={1000})
    """
    # Put columns in fixed order
    ideal_char = ideal_char[feature_names]

    # read SQL table into pandas data frame and convert to list of dictionaries
    # Base case, where user has not specified preferences.
    if req_state == '':
        try:
            with con:
                panda_char = pd.read_sql("SELECT * FROM " + str(clean_disease_name), con)
        except:
            print sys.exc_info()
            custom_error = "Sorry, that disease is not in our database."
            charities = []
            the_result = 0
            return render_template("output.html", charities = charities, the_result = the_result, custom_error = custom_error)
    # Expected case, where user has entered preferences.
    else:
        try:
            with con:
                panda_char = pd.read_sql("SELECT * FROM " + str(clean_disease_name) + " WHERE " + str(req_string), con)
        except:
            print sys.exc_info()
            custom_error = "Sorry, that disease is not in our database."
            charities = []
            the_result = 0
            return render_template("output.html", charities = charities, the_result = the_result, the_focus = the_focus, custom_error = custom_error)
    if len(panda_char) == 0:
        custom_error = "Sorry, no organizations meet your criteria. Try removing some of your filters."
        charities = []
        the_result = 0
        return render_template("output.html", charities = charities, the_result = the_result, the_focus = the_focus, custom_error = custom_error)
    else:
        top_charities = rank.rank_programs(panda_char, ideal_char)
        
    the_result = str(0) #placeholder for now - the_result is only used for debugging
  
    # return info to print 
    """
    For final version, want to return:
    (1) ranked list of charities that meet user's specified preferences ('charities')
    (2) if no programs in (1), ranked list of charities that are don't meet user's preferences ('close_charities')
    (3) alternative suggestions based on different choices
    Which tables to print will be determined in output.html based on what lists are returned.
    """


    # CLEAN DATAFRAME FOR NICE PRINTING HERE


    charities = top_charities.to_dict(outtype='records')
    return render_template("output.html", charities = charities, the_result = the_result, the_focus = the_focus, custom_error = '')
