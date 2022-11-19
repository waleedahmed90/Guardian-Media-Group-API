import requests
import datetime
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
import schedule
from os import path
from datetime import datetime as dt
import csv

# Data cleaning function
def total_articles_dataCleaning(start_date, query, title_flag):

# API endpoint     
    endPoint = "https://content.guardianapis.com/search"
# Default page number to start with
    page_no = 1
# counter for total articles
    total_articles = 0

# Query input parameters along with it's filters
    params = {
        "from-date": str(start_date),
        "to-date": str(start_date),
        "api-key": "test",
        "q": str(query),
        "order-by": "oldest",
        "page": str(page_no)
    }
# Obtaining the response from the GuardianAPI
    response = requests.get(endPoint, params)
    
    Articles_List = response.json()['response']['results']
    articles_count = len(Articles_List)
    
    
    section_names = []
    article_titles = []
    valid_articles = 0
    
    while ((response.status_code ==200) and (articles_count != 0)):
        
        Articles_List = response.json()['response']['results']
        
        for article in Articles_List:
            webTitle = article['webTitle']
            
            if (("trudeau" in webTitle.lower()) or (title_flag)):
                section_names.append(article['sectionName'])
                article_titles.append(webTitle)
                valid_articles = valid_articles + 1
        
        page_no = page_no + 1
        params['page'] = str(page_no)
        
        response = requests.get(endPoint, params)
        
        articles_count = len(Articles_List)
        
    
    return valid_articles, article_titles, section_names

# Information Extraction and cleaning function
def date_query(start_date, query, title_flag):
    
    
#Today is the end date
    end_date = datetime.datetime.now().date()
    delta = datetime.timedelta(days=1)

# This dictionary will be converted to a Dataframe later on
# This dictionary saves the information on the given query for the range of dates
    ts_guardian = {
        "Date": [],
        "No. of Articles": [],
        "Article_Names": [],
        "Section": []
    } 
    while start_date <= end_date:

        Total_articles, Names, Sections = total_articles_dataCleaning(start_date, query, title_flag)

        ts_guardian['Date'].append(start_date)
        ts_guardian['No. of Articles'].append(Total_articles)
        ts_guardian['Article_Names'].append(Names)
        ts_guardian['Section'].append(Sections)

        print('date:' , start_date, "Articles: ", Total_articles)

        start_date += delta

    return ts_guardian

# Function to count sections
def count_sections(df):
    section_counts = {}
    sections = list(df.iloc[:,3])

    for L in sections:
        for s in L:
            if s in section_counts.keys():
                section_counts[s] = section_counts[s] + 1 
            else:
                section_counts[s] = 1


    section_counts
    section_counts = sorted(section_counts.items(), key = lambda x: x[1], reverse=True)

    return section_counts[0]

# graphing function -1

def plot_graph_frames(df1, df2):
    
    plt.figure(figsize=(16, 9), dpi=360)
    
    MEDIUM_SIZE = 4
    POST_MEDIUM_SIZE = 6
    plt.rc('font', size=MEDIUM_SIZE)
    plt.rc('axes', titlesize=MEDIUM_SIZE)

    plt.subplot(2,1,1)

    plt.title("Articles mentioning Justin Trudeau", fontsize=POST_MEDIUM_SIZE)
    plt.xlabel("Time Progression", fontsize=MEDIUM_SIZE)
    plt.ylabel("No. of articles", fontsize=MEDIUM_SIZE)
    plt.plot(df1.iloc[:,0], df1.iloc[:,1], linewidth='1.25')

    plt.subplot(2,1,2)

    plt.title("Articles about Justin Trudeau", fontsize=POST_MEDIUM_SIZE)
    plt.xlabel("Time Progression", fontsize=MEDIUM_SIZE)
    plt.ylabel("No. of articles", fontsize=MEDIUM_SIZE)
    plt.plot(df2.iloc[:,0], df2.iloc[:,1], linewidth='1.25')

    plt.subplots_adjust(wspace=None, hspace=0.25)

    fig1 = plt.gcf()
    fig1.savefig("EVOLUTION_PLOT_NORMAL.png", dpi = 720)
    plt.show()


# graphing function - 2
def scatter_graph_frames(df1, df2):
    
    plt.figure(figsize=(16, 9), dpi=360)

    MEDIUM_SIZE = 4
    POST_MEDIUM_SIZE = 6
    plt.rc('font', size=MEDIUM_SIZE)
    plt.rc('axes', titlesize=MEDIUM_SIZE)

    plt.subplot(2,1,1)

    plt.title("Articles mentioning Justin Trudeau", fontsize=POST_MEDIUM_SIZE)
    plt.xlabel("Time Progression", fontsize=MEDIUM_SIZE)
    plt.ylabel("No. of articles", fontsize=MEDIUM_SIZE)
    plt.scatter(df1.iloc[:,0], df1.iloc[:,1], s=1.5)

    plt.subplot(2,1,2)

    plt.title("Articles about Justin Trudeau", fontsize=POST_MEDIUM_SIZE)
    plt.xlabel("Time Progression", fontsize=MEDIUM_SIZE)
    plt.ylabel("No. of articles", fontsize=MEDIUM_SIZE)
    plt.scatter(df2.iloc[:,0], df2.iloc[:,1], s=1.5)

    plt.subplots_adjust(wspace=None, hspace=0.25)

    fig1 = plt.gcf()
    fig1.savefig("EVOLUTION_PLOT_SCATTER.png", dpi = 720)
    plt.show()




################# DAILY AUTOMATED JOB ### (EXECUTES AT (9:00 am ) EVERYDAY) ############
def dailyAutomatedJob():

    #### execution starts here
    query = "Justin Trudeau"



    if (path.exists('./df_mentions.pkl') and path.exists('./df_titles.pkl')):
        print("here")
        temp_mentions = pd.read_pickle('df_mentions.pkl')
        temp_titles = pd.read_pickle('df_titles.pkl')

        start_date = temp_mentions.iloc[len(temp_mentions)-1,0]

        results_dict_1 = date_query(start_date, query, True)
        results_dict_2 = date_query(start_date, query, False)

        frame_df_1 = pd.DataFrame(results_dict_1)
        frame_df_2 = pd.DataFrame(results_dict_2)



        df_mentions = temp_mentions.append(frame_df_1, ignore_index = True)
        df_titles = temp_titles.append(frame_df_2, ignore_index = True)

        print(df_mentions.tail())
        print(df_titles.tail())
        

        df_mentions.to_pickle("df_mentions.pkl")
        df_titles.to_pickle("df_titles.pkl")
    else:
        start_date = datetime.date(2018,1,1)
    
        # Articles which contain Justin Truduea's Name
        results_dict_1 = date_query(start_date, query, True)

        # Articles which have Justin Trudeau's name in their Title
        results_dict_2 = date_query(start_date, query, False)


        df_mentions = pd.DataFrame(results_dict_1)
        df_titles = pd.DataFrame(results_dict_2)

        df_mentions.to_pickle("df_mentions.pkl")
        df_titles.to_pickle("df_titles.pkl")

    output_mentions = df_mentions[['Date', 'No. of Articles']] 
    output_titles = df_titles[['Date', 'No. of Articles']]

    # To see the output format
    print(output_mentions.head())
    print(output_titles.head())

    # print("mentions:", list(df_mentions[:,1]))

    # input()


    # Averages -1 
    print("Articles which Contain Justin Trudeau in their Title OR in their Body")
    print("Total posted articles until today: ", sum(df_mentions.iloc[:,1]))
    average_mentions = sum(df_mentions.iloc[:,1])/len(df_mentions)
    print("Average articles per day: ", average_mentions)

    # Averages -2 
    print("Articles which Contain Justin Trudeau in their Title Only")
    print("Total posted articles until today: ", sum(df_titles.iloc[:,1]))
    average_titles = sum(df_titles.iloc[:,1])/len(df_titles)
    print("Average articles per day: ", average_titles)

    # Sections with most articles
    print("For the DataFrame where Articles mention Justin Trudeau in Title OR Body")
    print("Section with Most Articles: ", count_sections(df_mentions))
    print()
    print("For the DataFrame where Articles mention Justin Trudeau in Title")
    print("Section with Most Articles: ", count_sections(df_titles))

    # Plotting both frames to see time evolution of the articles
    plot_graph_frames(df_mentions,df_titles)
    scatter_graph_frames(df_mentions,df_titles)

    # Maximum of articles_count where Justin Trudeau has been mentioned either in the title or in the body of article
    max_mentions = df_mentions['No. of Articles'].max()

    # Maximum of articles_count where Justin Trudeau has been mentioned in the title
    max_titles = df_titles['No. of Articles'].max()


    prob_list_mentions = []
    x_axis_mentions = []
    articles_mentions = df_mentions['No. of Articles']

    for i in range(0, max_mentions+1):
        Count = articles_mentions[articles_mentions >= i].count()
        x_axis_mentions.append(str(">="+str(i)))
        prob_list_mentions.append(Count/len(df_mentions))

    #### Articles where Trudeau is mentioned in the Title

    prob_list_titles = []
    x_axis_titles = []
    title_mentions = df_titles['No. of Articles']

    for i in range(0, max_titles+1):
        Count = title_mentions[title_mentions >= i].count()
        x_axis_titles.append(str(">="+str(i)))
        prob_list_titles.append(Count/len(df_titles))


        
    #### Plotting Both ###
    plt.figure(figsize=(16, 9), dpi=360)

    MEDIUM_SIZE = 4
    POST_MEDIUM_SIZE = 6
    plt.rc('font', size=MEDIUM_SIZE)
    plt.rc('axes', titlesize=MEDIUM_SIZE)

    plt.subplot(2,1,1)

    plt.title("Articles mentioning Justin Trudeau", fontsize=POST_MEDIUM_SIZE)
    plt.xlabel("Articles Count", fontsize=MEDIUM_SIZE)
    plt.ylabel("Probability of Count", fontsize=MEDIUM_SIZE)
    plt.plot(x_axis_mentions, prob_list_mentions, linewidth='1.25')

    plt.subplot(2,1,2)

    plt.title("Titles Mentioning Justin Trudeau", fontsize=POST_MEDIUM_SIZE)
    plt.xlabel("Articles Count", fontsize=MEDIUM_SIZE)
    plt.ylabel("Probability of Count", fontsize=MEDIUM_SIZE)
    plt.plot(x_axis_titles, prob_list_titles, linewidth='1.25')

    plt.subplots_adjust(wspace=None, hspace=0.25)
    plt.show()


    # unusual events

    unusual_mentions = df_mentions[df_mentions['No. of Articles'] > 2]
    unusual_titles = df_titles[df_titles['No. of Articles'] > 2]

    # printing articles in unusual events
    for d in list(unusual_titles['Date']):
        print("Date : ", d)
        mentions_row = unusual_mentions.loc[unusual_mentions['Date'] == d]
        titles_row = unusual_titles.loc[unusual_titles['Date'] == d]

        article_names_mentions_set = set(list(np.concatenate(list(mentions_row['Article_Names']))))
        article_names_titles_set = set(list(np.concatenate(list(titles_row['Article_Names']))))
        
        common_articles = list(article_names_titles_set.intersection(article_names_mentions_set))
        print("COMMON ARTICLES: ")
        print('\n'.join(common_articles))
        print()


#EXECUTION CALL
# Execute the task everyday at 9am

schedule.every().day.at("09:00").do(dailyAutomatedJob)

# # SCHEDULER LOOP

while True:
    schedule.run_pending()
    time.sleep(1)