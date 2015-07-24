import pandas as pd
import numpy as np
import pymysql as mdb

mysqlauth = pd.DataFrame.from_csv('/home/kristy/Documents/auth_codes/mysql_user.csv')
sqluser = mysqlauth.username[0]
sqlpass = mysqlauth.password[0]

con = mdb.connect(user=sqluser, host="localhost", db="charity_data", password=sqlpass, charset='utf8')

# Convert user input to actual targets.
def main():
    # Get features to analyze.
    feature_names = ['cn_overall', 'cn_acct_transp', 'cn_financial', 'percent_admin', 
                 'percent_fund', 'percent_program', 'staff_size', 'board_size',
                 'age', 'total_contributions', 'total_expenses', 'total_revenue', 'twitter_followers']

    # Read in SQL data.
    combined_panda = pd.DataFrame()
    disease_list = ['alzheimer', 'blindness', 'breast_cancer', 'colon_cancer', 'crohn', 'diabetes',
                    'dyslexia', 'leukemia', 'lung_cancer', 'multiple_sclerosis', 'osteoporosis',
                    'parkinson', 'prostate_cancer', 'cancer', 'tumor', 'melanoma', 'lymphoma']
    with con:
        for disease in disease_list:
            pandadf = pd.read_sql("SELECT  year_incorporated, age, twitter_followers, percent_program, total_contributions, total_expenses, staff_size, board_size FROM " + str(disease), con)
            if len(pandadf) > 0:
                combined_panda = pd.concat([combined_panda, pandadf], 0, ignore_index=True)

    # Fix NaNs that were originally encoded as -1.
    for idx in range(len(combined_panda)):
        if combined_panda['year_incorporated'][idx] == -1:
            combined_panda[idx:(idx+1)]['age'] = np.nan
            combined_panda[idx:(idx+1)]['year_incorporated'] = np.nan
        for col in combined_panda.columns:
            if combined_panda[col][idx] == -1:
                combined_panda[idx:(idx+1)][col] = np.nan
    reduceddf =  combined_panda[:][feature_names]

    # Set up distributions.
    for col in distribution.columns:
        quantiles = combined_panda[col].describe(percentile_width=50.)
        distribution.loc['p25',col] = quantiles['25%']
        distribution.loc['p75',col] = quantiles['75%']
        
        quantiles = combined_panda[col].describe(percentile_width=66.7)    
        distribution.loc['p17',col] = quantiles['16.6%']
        distribution.loc['p50',col] = quantiles['50%']
        distribution.loc['p83',col] = quantiles['83.4%']
        
    # Save distribution in SQL.
    table_name = 'distribution'
    
    with con:
        cur = con.cursor()
        
        # set up table
        cur.execute("DROP TABLE IF EXISTS " + str(table_name))
        cur.execute("\
            CREATE TABLE " + str(table_name) + "(\
                 cn_overall FLOAT(8,4), cn_acct_transp FLOAT(8,4), cn_financial FLOAT(8,4), percent_admin FLOAT(8,4), 
                 percent_fund FLOAT(8,4), percent_program FLOAT(8,4), staff_size FLOAT(12,0), board_size FLOAT(12,0),
                 age FLOAT(12,0), total_contributions FLOAT(12,0), total_expenses FLOAT(12,0), total_revenue FLOAT(12,0), twitter_followers FLOAT(12,0)
            )"\
        ) 
    
        for idx in range(len(distribution)):
            try:
                # START HERE
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

            except:
                print "\nProblem converting " + str(idx) + " to SQL."
                print sys.exc_info()
                continue
                
        cur.execute("SELECT * FROM " + str(table_name))
        rows = cur.fetchall()



# Boilerplate to call main()
if __name__ == '__main__':
    main()

