#!/usr/bin/env python

import pymysql as mdb
import pandas as pd
import numpy as np
import re, sys

def clean_sql(disease):
    # Set up connection to SQL
    mysqlauth = pd.DataFrame.from_csv('/home/kristy/Documents/auth_codes/mysql_user.csv')
    sqluser = mysqlauth.username[0]
    sqlpass = mysqlauth.password[0]

    con = mdb.connect(user=sqluser, host="localhost", db="charity_data", password=sqlpass, charset='utf8')
    
    # Import data from SQL
    with con:
        pandadf = pd.read_sql("SELECT * FROM " + str(disease), con)
    
    # Get organization age
    
    pandadf['year_incorporated'][pandadf['year_incorporated'] == 0] = np.nan
    pandadf['age'] = 2015 - pandadf['year_incorporated']

    # Get state
    def extract_state(city_unicode):
        match = re.search(', ([A-Z][A-Z]) [0-9]+', city_unicode)
        if match:
            return match.group(1)
        else:
            return ''
    pandadf['state'] = pandadf['city'].apply(extract_state)

    # Convert tax-exempt status to 0/1
    pandadf['tax_exempt'] = pandadf['tax_status'].apply(lambda x: int(x.find('is tax-exempt under section 501(c)(3)') > -1))
    pandadf[:10][['tax_exempt','tax_status']]

    # Convert CN rating to 0/1
    pandadf['cn_rated'] = pandadf['cn_rated'].apply(lambda x: int(x == u'Rated'))

    # Convert BBB accreditation to 0/1
    pandadf['bbb_accred'] = pandadf['bbb_accred'].apply(lambda x: int(x == u'\nAccredited: Yes\n' or x == u'Accredited Charity'))
    
    # Save cleaned dataframe to SQL
    table_name = disease
    with con:
        cur = con.cursor()
    
        # set up table
        cur.execute("DROP TABLE IF EXISTS " + str(table_name))
        cur.execute("\
            CREATE TABLE " + str(table_name) + "(\
            id INT PRIMARY KEY AUTO_INCREMENT,\
            disease VARCHAR(255),\
            name VARCHAR(255),\
            address VARCHAR(255),\
            city VARCHAR(255),\
            state CHAR(2),\
            link VARCHAR(255),\
            bbb_link VARCHAR(255),\
            facebook_link VARCHAR(255),\
            twitter_link VARCHAR(255),\
            cn_link VARCHAR(255),\
            bbb_accred BOOLEAN,\
            year_incorporated INT,\
            age INT,\
            purpose VARCHAR(255),\
            board_size INT,\
            staff_size INT,\
            tax_status VARCHAR(255),\
            tax_exempt BOOLEAN,\
            cn_rated BOOLEAN,\
            cn_overall FLOAT(8,4),\
            cn_financial FLOAT(8,4),\
            cn_acct_transp FLOAT(8,4),\
            leader_compensation VARCHAR(255),\
            total_expenses INT,\
            total_contributions INT,\
            total_revenue INT,\
            percent_program FLOAT(6,2),\
            percent_admin FLOAT(6,2),\
            percent_fund FLOAT(6,2),\
            facebook_likes INT,\
            twitter_followers INT\
            )"\
        ) 
    
        facebook_likes_placeholder = np.nan # not scraped yet

        for idx in range(len(pandadf)):
            value_str = ("\"" + str(pandadf.name[idx]) + "\",\"" 
                         + str(pandadf.disease[idx]) + "\",\"" 
                         + str(pandadf.address[idx]) + "\",\"" 
                         + str(pandadf.city[idx]) + "\",\"" 
                         + str(pandadf.state[idx]) + "\",\"" 
                         + str(pandadf.link[idx]) + "\",\"" 
                         + str(pandadf.bbb_link[idx]) + "\",\"" 
                         + str(pandadf.facebook_link[idx]) + "\",\"" 
                         + str(pandadf.twitter_link[idx]) + "\",\"" 
                         + str(pandadf.cn_link[idx]) + "\",\"" 
                         + str(pandadf.bbb_accred[idx]) + "\",\"" 
                         + str(pandadf.year_incorporated[idx]) + "\",\"" 
                         + str(pandadf.age[idx]) + "\",\"" 
                         + str(pandadf.purpose[idx]) + "\",\"" 
                         + str(pandadf.board_size[idx]) + "\",\"" 
                         + str(pandadf.staff_size[idx]) + "\",\"" 
                         + str(pandadf.tax_status[idx]) + "\",\"" 
                         + str(pandadf.tax_exempt[idx]) + "\",\"" 
                         + str(pandadf.cn_rated[idx]) + "\",\"" 
                         + str(pandadf.cn_overall[idx]) + "\",\"" 
                         + str(pandadf.cn_financial[idx]) + "\",\"" 
                         + str(pandadf.cn_acct_transp[idx])  + "\",\"" 
                         + str(pandadf.leader_compensation[idx]) + "\",\"" 
                         + str(pandadf.total_expenses[idx]) + "\",\"" 
                         + str(pandadf.total_contributions[idx]) + "\",\"" 
                         + str(pandadf.total_revenue[idx]) + "\",\"" 
                         + str(pandadf.percent_program[idx]) + "\",\"" 
                         + str(pandadf.percent_admin[idx]) + "\",\"" 
                         + str(pandadf.percent_fund[idx]) + "\",\"" 
                         + str(facebook_likes_placeholder) + "\",\"" 
                         + str(pandadf.twitter_followers[idx]) + "\"")
            cur.execute("INSERT INTO " + str(table_name) + "(name, disease, address, city, state, link, \
                         bbb_link, facebook_link, twitter_link, cn_link, bbb_accred, \
                         year_incorporated, age, purpose, board_size, staff_size, tax_status, \
                         tax_exempt, cn_rated, cn_overall, cn_financial, cn_acct_transp, \
                         leader_compensation, total_expenses, \
                         total_contributions, total_revenue, percent_program, percent_admin, percent_fund, \
                         facebook_likes, twitter_followers) \
                         VALUES(" + value_str + ")")



        cur.execute("SELECT * FROM " + table_name)
        rows = cur.fetchall()
            
    return rows


# Main function
def main():
    # Cycle through diseases
    disease_list = ["alzheimer's disease", "blindness", "breast cancer", "colon cancer", "crohn's disease",
                    "dyslexia", "leukemia", "lung cancer", "multiple sclerosis", "diabetes",
                    "osteoporosis", "parkinson's disease", "prostate cancer", "brain cancer"]

    for disease in disease_list:
        clean_disease_name = '_'.join(disease.lower().replace('\'s disease','').split())
        print "\nCleaning " + disease + "...\n"
        
        sqlrows = clean_sql(clean_disease_name)
        
        print str(len(sqlrows)) + " organizations cleaned.\n"


# Boilerplate to call main()
if __name__ == '__main__':
    main()
