#!/usr/bin/env python

# <codecell>

import pandas as pd
import bs4
import re, numpy as np
import matplotlib.pyplot as plt
import requests, urllib2
import tweepy
import pymysql as mdb
import sys

#%matplotlib inline

# <codecell>

chosen_disease = sys.argv[1]
clean_disease_name = ' '.join(chosen_disease.lower().replace('\'s disease','').split())
# TO DO: allow synonymous names (e.g. colon vs colorectal cancer)

# <codecell>

def scrape_bbb_urls(disease):
    # import URL into beautiful soup object
    # TO DO: go through multiple pages of search results
    dis_as_str = '+'.join(disease.split())
    give_org_urls = ["http://give.org/search/?term=" + dis_as_str + "&location=&FilterAccredited=false&tobid="]

#    give_org_urls = ["http://give.org/search/?term=multiple+sclerosis&location=&FilterAccredited=false&tobid=", 
#                     "http://give.org/search/?page=2&term=multiple+sclerosis&location=&FilterAccredited=false&tobid=", 
#                     "http://give.org/search/?page=3&term=multiple+sclerosis&location=&FilterAccredited=false&tobid="]
    bbb_soups = []
    for give_org_url in give_org_urls:
        response = requests.get(give_org_url)
        bbb_soups.append(bs4.BeautifulSoup(response.text))
        
    return bbb_soups

# <codecell>

def clean_bbb_info(bbb_soups,disease):
    # pull out charity links and info
    # NOTE: May need permission to include links to BBB. I didn't find any info on restrictions in pulling information.
    charities = []
    for soup in bbb_soups:
        bbb_table = soup.select('div.search table')[0].tbody 
        for row in bbb_table.findAll('tr'):
            charity_data = {}
            charity_data['disease'] = disease
            charity_data['name'] = row.select('a.charity-link')[0].get_text()
            charity_data['bbb_link'] = row.select('a.charity-link')[0].attrs.get('href')
            accred_seal = row.select('img.charity-search-seal')
            if accred_seal:
                charity_data['bbb_accred'] = accred_seal[0].attrs.get('alt')
            else:
                charity_data['bbb_accred'] = row.select('div.accreditation-mobile')[0].get_text()
            charity_data['address'] = row.select('div.accreditation-mobile')[0].next_sibling.strip()
            charity_data['city'] = row.select('div.accreditation-mobile')[0].next_sibling.next_sibling.next_sibling.strip()
            
            charities.append(charity_data)
            
    return charities

# <codecell>

bbb_soups = scrape_bbb_urls(clean_disease_name)

# <codecell>

len(bbb_soups)

# <codecell>

bbb_charities = clean_bbb_info(bbb_soups,clean_disease_name)

# <codecell>

len(bbb_charities)

# <codecell>

def get_charity_links(charities):
    # Use BBB pages to get links to each charity's website
    
    for charity in charities:
        soup = bs4.BeautifulSoup(requests.get(charity['bbb_link']).text)
        if len(soup.select('div.charity-contact')) > 0:
            charity['link'] = soup.select('div.charity-contact')[0].a.attrs.get('href')
        elif len(soup.select('div.charity-detail-text')) > 0:
            charity['link'] = soup.select('div.charity-detail-text')[0].a.attrs.get('href')
        elif len(soup.select('a#ctl00_ContentPlaceHolder1_aWebUrl')) > 0:
            charity['link'] = soup.select('a#ctl00_ContentPlaceHolder1_aWebUrl')[0].attrs.get('href')
        else:
            charity['link'] = ''
    # TO DO: should add text search for websites printed as text rather than link
    
    return charities

# <codecell>

charities_with_links = get_charity_links(bbb_charities)

# <codecell>

len(charities_with_links)

# <codecell>

def scrape_social_media(charities):
    # Find Facebook likes and Twitter followers for each charity
    # TO DO: Find the right FB/Twitter account, e.g. for National MS Society chapters.
    for charity in charities:
        if charity['link'] == '':
            charity['facebook_link'] = ''
            charity['twitter_link'] = ''
        else: 
            try:
                page = urllib2.urlopen(urllib2.Request(charity['link'], headers={'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'}))
                target_soup = bs4.BeautifulSoup(page.read(), 'html.parser')
            except:
                print charity['name']
                charity['facebook_link'] = ''
                charity['twitter_link'] = ''
                continue
    
            try:
                fblink = target_soup.select('a[href*=facebook.com]')[0].attrs.get('href')
            except IndexError:
                fblink = ''
            charity['facebook_link'] = fblink 
            
            try:
                twlink = target_soup.select('a[href*=twitter.com]')[0].attrs.get('href')
            except IndexError:
                twlink = ''
            charity['twitter_link'] = twlink
            
    return charities

# <codecell>

charities_with_social = scrape_social_media(charities_with_links)

# <codecell>

len(charities_with_social)

# <codecell>

def get_twitter_followers(charities):
    # import authorization info 
    twauth = pd.DataFrame.from_csv('/home/kristy/Documents/auth_codes/twitter_access.csv')
    auth = tweepy.OAuthHandler(twauth.consumer_key['twitter'], twauth.consumer_secret['twitter'])
    auth.set_access_token(twauth.access_token['twitter'], twauth.access_secret['twitter'])
    
    api = tweepy.API(auth)
    
    for charity in charities:
        if charity['twitter_link'] == '':
            charity['twitter_followers'] = 0
        else:
            try:
                twitterid = re.findall('https://twitter.com/(.*)', charity['twitter_link'])[0]
                user = api.get_user(twitterid)
                charity['twitter_followers'] = user.followers_count
            except:
                charity['twitter_followers'] = 0
                continue
                
    return charities

# <codecell>

char_with_twitter = get_twitter_followers(charities_with_social)
len(char_with_twitter)

# <codecell>

def get_char_nav_info(dictlist): 
    for charity in dictlist:
        # get link to Charity Navigator's website on this charity
        words = '+'.join(charity['name'].split())
        url = ('https://www.charitynavigator.org/index.cfm?keyword_list=' + words 
               + '&nameonly=1&Submit2=Search&bay=search.results')
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text)
        if len(soup.select('p.rating')) > 0:
            charity['cn_link'] = soup.select('p.rating')[0].a.attrs.get('href')
            charity['cn_rated'] = 'Rated'
        else:
            url = ('https://www.charitynavigator.org/index.cfm?keyword_list=' + words 
                   + '&nameonly=1&Submit2=Search&bay=search.results2')
            response = requests.get(url)
            soup = bs4.BeautifulSoup(response.text)
            if len(soup.select('p.orgname')) > 0:
                charity['cn_link'] = soup.select('p.orgname')[0].a.attrs.get('href')
                charity['cn_rated'] = 'Unrated'                
            else:
                print charity['name'] + ": No Charity Navigator link."
                charity['cn_link'] = ''
                charity['cn_rated'] = ''
            charity['cn_overall'] = float('nan')
            charity['cn_financial'] = float('nan')
            charity['cn_acct_transp'] = float('nan')
            continue
        
        # get Charity Navigator data 
        charsoup = bs4.BeautifulSoup(requests.get(charity['cn_link']).text)
        strongtags = charsoup.select('strong')
        overall_cells = []
        fin_cells = []
        acct_cells = []
        for tg in strongtags:
            if tg.text == "Overall":
                overall_cells.append(float(tg.parent.nextSibling.nextSibling.text))
            elif tg.text == "Financial":
                fin_cells.append(float(tg.parent.nextSibling.nextSibling.text))
            elif tg.text == "Accountability & Transparency":
                acct_cells.append(float(tg.parent.nextSibling.nextSibling.text))
        # include overall rating
        if len(overall_cells) == 1:
            charity['cn_overall'] = overall_cells[0]
        elif len(overall_cells) > 1:
            print charity['name'] + ": Too many candidate cells for Overall."
            charity['cn_overall'] = overall_cells[0]
        else:
            print charity['name'] + ": No Overall cells."
            charity['cn_overall'] = 0
        # include financial rating
        if len(fin_cells) == 1:
            charity['cn_financial'] = fin_cells[0]
        elif len(fin_cells) > 1:
            print char['name'] + ": Too many candidate cells for Financial."
            charity['cn_financial'] = fin_cells[0]
        else:
            #print "No Financial cells"
            charity['cn_financial'] = 0
        # include accountability rating
        if len(acct_cells) == 1:
            charity['cn_acct_transp'] = acct_cells[0]
        elif len(acct_cells) > 1:
            print charity['name'] + ": Too many candidate cells for Accountability & Transparency."
            charity['cn_acct_transp'] = acct_cells[0]
        else:
            #print "No Accountability & Transparency cells"
            charity['cn_acct_transp'] = 0
    return dictlist

# <codecell>

char_with_nav_link = get_char_nav_info(char_with_twitter)

# <codecell>

panda_char = pd.DataFrame(char_with_nav_link)

# <codecell>

# make sure to do sudo mysqld_safe from command line first
def convert_to_sql(pandadf,disease):
    mysqlauth = pd.DataFrame.from_csv('/home/kristy/Documents/auth_codes/mysql_user.csv')
    user = mysqlauth.username[0]
    password = mysqlauth.password[0]

    con = mdb.connect('localhost', user, password, 'charity_data')
    
    table_name = '_'.join(disease.split())
    print table_name
    with con:
        cur = con.cursor()
        
        # set up table
#        cur.execute("DROP TABLE IF EXISTS charities_sql")
        cur.execute("DROP TABLE IF EXISTS " + str(table_name))
        cur.execute("\
            CREATE TABLE " + str(table_name) + "(\
                id INT PRIMARY KEY AUTO_INCREMENT,\
                disease VARCHAR(255),\
                name VARCHAR(255),\
                address VARCHAR(255),\
                city VARCHAR(255),\
                link VARCHAR(255),\
                bbb_link VARCHAR(255),\
                facebook_link VARCHAR(255),\
                twitter_link VARCHAR(255),\
                cn_link VARCHAR(255),\
                bbb_accred VARCHAR(255),\
                cn_rated VARCHAR(255),\
                cn_overall FLOAT(8,4),\
                cn_financial FLOAT(8,4),\
                cn_acct_transp FLOAT(8,4),\
                facebook_likes INT,\
                twitter_followers INT\
           )"\
        ) 
        
        facebook_likes_placeholder = 0 # not scaped yet
        
        for idx in range(len(pandadf)):
            value_str = ("\"" + str(pandadf.name[idx]) + "\",\"" + str(pandadf.disease[idx]) + "\",\"" + str(pandadf.address[idx]) + "\",\"" 
                         + str(pandadf.city[idx]) + "\",\"" + str(pandadf.link[idx]) + "\",\"" + str(pandadf.bbb_link[idx])
                         + "\",\"" + str(pandadf.facebook_link[idx]) + "\",\"" + str(pandadf.twitter_link[idx]) + "\",\"" 
                         + str(pandadf.cn_link[idx]) + "\",\"" + str(pandadf.bbb_accred[idx]) + "\",\"" + str(pandadf.cn_rated[idx])
                         + "\",\"" + str(pandadf.cn_overall[idx]) + "\",\"" + str(pandadf.cn_financial[idx]) + "\",\"" + str(pandadf.cn_acct_transp[idx]) 
                         + "\",\"" + str(facebook_likes_placeholder) + "\",\"" + str(pandadf.twitter_followers[idx]) + "\"")
            cur.execute("INSERT INTO " + str(table_name) + "(name, disease, address, city, link, bbb_link, facebook_link, twitter_link, cn_link, bbb_accred, \
                        cn_rated, cn_overall, cn_financial, cn_acct_transp, facebook_likes, twitter_followers) VALUES(" + value_str + ")")
        
        cur.execute("SELECT * FROM " + str(table_name))
        rows = cur.fetchall()
        #for row in rows:
            #print row

    return rows

# <codecell>

sqlrows = convert_to_sql(panda_char,clean_disease_name)

# <codecell>

len(sqlrows)

# <codecell>

print len(sqlrows)

# <codecell>

print clean_disease_name

# <codecell>


