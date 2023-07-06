#importing relevant libraries for the code
from pandas.core.frame import DataFrame
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from fractions import Fraction
import math

#function to save the data to a new DF
def NewDF():
    print("please enter new DF name")
    NewDfName = input()


    #these are the lists that will become the cols of the dataframe:
    game_name_list = [] #game names
    game_date_list = [] #game eelease dates
    game_developer_list = [] #game developer
    game_publisher_list = [] #game publisher
    game_genres_list = [] #genres
    game_price_list = [] #price
    game_langs_list = [] #languages the game is avilable in
    game_dlc_flag_list = [] #flag if a game has any dlc or not
    game_mature_flag_list = [] #flag if a game has any mature content or not
    game_single_flag_list = [] #flag if a game can be played single player of not
    game_score_list = [] #the score we predict for the game based on reviews

    #these will be used to calc the score of each game:
    game_review_count_list = [] #all reviews
    game_review_positive_list = [] #positive reviews
    game_review_negative_list = [] #negative reviews
    
    #get each games data and append the respective lists
    page_flag = True
    flag_first_page = True
    i = 1
    #get the games from all the pages and not give it a range because its very dynamic
    while(page_flag):
        print(i) #print page number for when you follow the code run
        
        #defining parameters to help with get requests from the site
        links = [] #list of links
        baseurl = "https://store.steampowered.com/search/?sort_by=Reviews_DESC&category1=998&filter=topsellers"
        paramater = "&page="+str(i)
        response = requests.get(baseurl+paramater)
        website_soup = BeautifulSoup(response.content,'html.parser')
        
        #get requests from each steam page
        #we checked if there are 2 buttons on the page (back and next) and the first page only has next
        if flag_first_page:
            flag_first_page = False
        else:
            #finding the number of buttons on the page
            button_tag = website_soup.find_all('a',attrs={'class':'pagebtn'})
            #checking if it has 2 buttons
            if len(button_tag)!= 2 :
                page_flag = False
                
                #adding each link to the list of links
        for link in website_soup.find('div', attrs={'id': 'search_resultsRows'}).find_all('a'):
            links.append(link['href'])
            
            #getting each game attributes
        for game_url in links:
            curr_game_name, curr_game_date, curr_game_developer, curr_game_pub, curr_game_genre, curr_game_review_count, curr_game_review_positive, curr_game_review_negative, curr_game_price, curr_game_langs, curr_game_dlc, curr_game_mature, curr_game_single = GetDataFromGame(game_url)
            #not adding games with missing information on the list
            #if(curr_game_name in [np.nan]):
                #continue
                
            print("last game cleared was",curr_game_name) #print for following the code run
            game_name_list.append(curr_game_name) #adding game name to game names list
            game_date_list.append(curr_game_date) #adding game release date to the dates list
            game_developer_list.append(curr_game_developer) #adding game developer to developers list
            game_publisher_list.append(curr_game_pub) #adding game publisher to publishers list
            game_genres_list.append(curr_game_genre) #adding game genres to the genres list
            game_review_count_list.append(curr_game_review_count) #adding review count to the list
            game_review_positive_list.append(curr_game_review_positive) #adding positive reviews count to the list
            game_review_negative_list.append(curr_game_review_negative) #adding negative reviews count to the list
            game_price_list.append(curr_game_price) #adding game price to prices list
            game_langs_list.append(curr_game_langs) #adding game languages to languages list
            game_dlc_flag_list.append(curr_game_dlc) #adding dlc flag to the list
            game_mature_flag_list.append(curr_game_mature) #adding mature flag to list
            game_single_flag_list.append(curr_game_single) #adding single flag to list
            
            #to address the nan instances
            if np.isnan(curr_game_review_count):
                result_score = np.nan
                #the score calcultion based on the formula from steamDB
            else:
                Review_Score = Fraction(curr_game_review_positive,curr_game_review_count)
                result_score = Review_Score - ((Review_Score - 0.5)*(2**(-(math.log10(curr_game_review_count + 1)))))
            game_score_list.append(result_score)
        i += 1
        #save to the dataframe every 10 pages(requests)
        #if i%10 == 0:
        print('now creating temp df') #print for following code
        #inserting info to df
        GameDF = pd.DataFrame({'Name':game_name_list,'Date':game_date_list,'Developer':game_developer_list,'Publisher':game_publisher_list,'Genre':game_genres_list,'Price':game_price_list,'Langs':game_langs_list,'DLC':game_dlc_flag_list,'Mature':game_mature_flag_list,'Single':game_single_flag_list,'Total Review Cnt':game_review_count_list,'Pos Review Cnt':game_review_positive_list,'Neg Review Cnt':game_review_negative_list,'Score':game_score_list})
        print('=============') #print for following code
        print(NewDfName," shape is:",GameDF.shape) #print for following code
        GameDF.to_csv(NewDfName+'.csv') #saving df to csv file
            

#function to continue adding to the same df if the code run is interrupted (like from bad request)
def ContinueDF(GameDF:DataFrame,i:int):
    #these are the lists that will become the cols of the dataframe:
    game_name_list = []
    game_date_list = []
    game_developer_list = []
    game_publisher_list = []
    game_genres_list = []
    game_price_list = []
    game_langs_list = []
    game_dlc_flag_list = []
    game_mature_flag_list = []
    game_single_flag_list = []
    game_score_list = []
    
    #these will be used to calc the score of each game:
    game_review_count_list = []
    game_review_positive_list = []
    game_review_negative_list = []
    
    #get each games data and append the respective lists
    if i == 1:
        flag_first_page = True
    else:
        flag_first_page = False
    page_flag = True   
    
    #same as the previous function
    while(page_flag):
        print(i) #print for following code
        links = []
        baseurl = "https://store.steampowered.com/search/?sort_by=Reviews_DESC&filter=topsellers"
        paramater = "&page="+str(i)
        response = requests.get(baseurl+paramater)
        website_soup = BeautifulSoup(response.content,'html.parser')

        if flag_first_page:
            flag_first_page = False
        else:
            button_tag = website_soup.find_all('a',attrs={'class':'pagebtn'})
            if len(button_tag)!= 2 :
                page_flag = False

        for link in website_soup.find('div', attrs={'id': 'search_resultsRows'}).find_all('a'):
            links.append(link['href'])

        for game_url in links:
            curr_game_name, curr_game_date, curr_game_developer, curr_game_pub, curr_game_genre, curr_game_review_count, curr_game_review_positive, curr_game_review_negative, curr_game_price, curr_game_langs, curr_game_dlc, curr_game_mature, curr_game_single = GetDataFromGame(game_url)
            if(curr_game_name in [np.nan]):
                continue
            print("last game cleared was",curr_game_name) #print for following code
            game_name_list.append(curr_game_name)
            game_date_list.append(curr_game_date)
            game_developer_list.append(curr_game_developer)
            game_publisher_list.append(curr_game_pub)
            game_genres_list.append(curr_game_genre)
            game_review_count_list.append(curr_game_review_count)
            game_review_positive_list.append(curr_game_review_positive)
            game_review_negative_list.append(curr_game_review_negative)
            game_price_list.append(curr_game_price)
            game_langs_list.append(curr_game_langs)
            game_dlc_flag_list.append(curr_game_dlc)
            game_mature_flag_list.append(curr_game_mature)
            game_single_flag_list.append(curr_game_single)
            
            #to address the nan instances
            if np.isnan(curr_game_review_count):
                result_score = np.nan
            else:
                Review_Score = Fraction(curr_game_review_positive,curr_game_review_count)
                result_score = Review_Score - ((Review_Score - 0.5)*(2**(-(math.log10(curr_game_review_count + 1)))))
            game_score_list.append(result_score)
        i += 1
        
        if i%10 == 0:
            print('now creating temp df') #print for following code
            TempDF = pd.DataFrame({'Name':game_name_list,'Date':game_date_list,'Developer':game_developer_list,'Publisher':game_publisher_list,'Genre':game_genres_list,'Price':game_price_list,'Langs':game_langs_list,'DLC':game_dlc_flag_list,'Mature':game_mature_flag_list,'Single':game_single_flag_list,'Score':game_score_list})
            GameDF = pd.concat([GameDF, TempDF], ignore_index=True)
            print("GameDF shape is:",GameDF.shape) #print for following code
            GameDF.to_csv('SteamGamesDF.csv')
            game_name_list = []
            game_date_list = []
            game_developer_list = []
            game_publisher_list = []
            game_genres_list = []
            game_price_list = []
            game_langs_list = []
            game_dlc_flag_list = []
            game_mature_flag_list = []
            game_single_flag_list = []
            game_score_list = []

            #these will be used to calc the score of each game:
            game_review_count_list = []
            game_review_positive_list = []
            game_review_negative_list = []
        
#function that goes over the html tags on the game steam page and gets the info about the game
def GetDataFromGame(game_url):
    
    response = requests.get(game_url)
    game_soup = BeautifulSoup(response.content,'html.parser')
    age_check_tag = game_soup.find('div',attrs={'id':'app_agegate'})
    #working around age gate
    if age_check_tag:
        response = requests.get(game_url,cookies={'birthtime':'1'})
        game_soup = BeautifulSoup(response.content,'html.parser')
    
    #if the page is for a subscription (like EA pass)
    sub_tag = game_soup.find('div',attrs={'class':'game_area_purchase_game_wrapper game_purchase_sub_dropdown'})
   
    #if the game is a package page
    package_tag = game_soup.find('div', attrs={'id':'package_header_container'})

    """
    response = requests.get(game_url) #get request with the link the func gets
    game_soup = BeautifulSoup(response.content,'html.parser')
    
    #we had a lot of edge cases that stopped the code so we found tags to skip them in the run
    #addressing if the page is a bundle page
    bundle_tag = game_soup.find('div', attrs={'class':'game_area_purchase_game bundle ds_no_flags'})
    #if the game is dlc
    dlc_tag = game_soup.find('div',attrs={'class':'game_area_bubble game_area_dlc_bubble'})
    #if the page is for a soundtrack
    soundtrack_tag = game_soup.find('div',attrs={'class':'game_area_bubble game_area_soundtrack_bubble '})
    #some soundtracks have diffrent tags so another soundtrack flag if the page is for a soundtrack
    try:
        soundtrack_tag2 = game_soup.find('div', attrs={'id': 'game_area_purchase'}).find('div', attrs={'class': 'content'}).h1.string.strip()
    except:
        soundtrack_tag2 = ''
        
        #if the page has an age check to get to
    age_check_tag = game_soup.find('div',attrs={'id':'app_agegate'})
    #if the game is in pre-order it's not relevant because it doesn't have reviews yet
    preorder_tag = game_soup.find('div',attrs={'class':'game_area_comingsoon game_area_bubble'})
    
    #if the webpage if for a movie (behind the scenes of making a game for example)
    try:
        movie_tag = game_soup.find('div',attrs={'class':'blockbg'}).find('a').string.strip()
    except:
        movie_tag = ''
        
        #setting the attributes to nan before run, and if any of the above tags are found on the page- return nan

     #if any of the above outlier tags are found on the page, return nan 
    if bundle_tag or package_tag or dlc_tag or soundtrack_tag or age_check_tag or preorder_tag:
        return game_name,game_date,game_developer,game_publisher,game_genre,game_review_count,game_review_positive,game_review_negative,game_price,game_langs,game_dlc,game_mature,game_single
    
    or (soundtrack_tag2 == 'Downloadable Soundtrack') or (movie_tag == 'All Videos') 
    """
    
   
    
    game_name = np.nan
    game_date = np.nan
    game_developer = np.nan
    game_publisher = np.nan
    game_genre = np.nan
    game_review_count = np.nan
    game_review_positive = np.nan
    game_review_negative = np.nan
    game_price = np.nan
    game_langs = np.nan
    game_dlc = np.nan
    game_mature = np.nan
    game_single = np.nan

   
    if (game_soup.title.string == 'Welcome to Steam') or package_tag:
        return game_name,game_date,game_developer,game_publisher,game_genre,game_review_count,game_review_positive,game_review_negative,game_price,game_langs,game_dlc,game_mature,game_single
    
    #we used try-except to not stop mid-run if some attributes are not found, because we had a lot of edge cases
    try:
        game_name = game_soup.find('div',attrs={'class':'apphub_AppName'}).string.strip() #find game name in page
    except:
        pass
    
    try:
        game_date = game_soup.find('div',attrs={'class':'date'}).string.strip() #find release date in page
    except:
        pass    
    
    try:
        game_developer = game_soup.find('div',attrs={'id':'developers_list'}).find('a').string.strip() #find developer in page
    except:
        pass
    
    try:
        for pub in game_soup.find('div',attrs={'class':'glance_ctn_responsive_left'}).find_all('div',attrs={'class':'dev_row'}): #find publisher in page
            game_publisher = (pub.find('a').string.strip()) #always ends on the 2nd string, which is the relevant publisher
    except:
        pass
    
    try:
        game_genre = [] #a game can have more than one genre so we saved it in a list
        for i in game_soup.find('span',attrs={'data-panel':'{"flow-children":"row"}'}).find_all('a'): #finding a game genres in page
            game_genre.append(i.string.strip())
    except:
        pass
    
    try:
        #getting reviews count from page and cleaning data numbers
        game_review_count = game_soup.find('label',attrs={'for':'review_type_all'}).find('span',attrs={'class':'user_reviews_count'}).string.strip()
        game_review_count = game_review_count.replace(')','').replace('(','')
        game_review_count = game_review_count.replace(',','')
        game_review_count = int(game_review_count)
    except:
        pass
    
    try:
        #getting positive reviews count from page and cleaning data numbers
        game_review_positive = game_soup.find('label',attrs={'for':'review_type_positive'}).find('span',attrs={'class':'user_reviews_count'}).string.strip()
        game_review_positive = game_review_positive.replace(')','').replace('(','')
        game_review_positive = game_review_positive.replace(',','')
        game_review_positive = int(game_review_positive)
    except:
        pass
    
    try:
        #getting negative reviews count from page and cleaning data numbers
        game_review_negative = game_soup.find('label',attrs={'for':'review_type_negative'}).find('span',attrs={'class':'user_reviews_count'}).string.strip()
        game_review_negative = game_review_negative.replace(')', '').replace('(', '')
        game_review_negative = game_review_negative.replace(',','')
        game_review_negative = int(game_review_negative)
    except:
        pass
    
    game_price = None #setting price to none because some games are free
    #checking if a page is for a game pass subscription
    if sub_tag:
        purchase_tag = game_soup.find('div',attrs={'id':'game_area_purchase'}) #finding game price in page and cleaning number data
        without_sub_purchase_tag = purchase_tag.find(lambda tag: tag.name == 'div' and tag.get('class') == ['game_area_purchase_game_wrapper'])
        #checking regular game price (not discounted)
        try:
            game_price = without_sub_purchase_tag.find('div',attrs={'class':'game_purchase_price price'}).string.strip()
        except:
            pass
        #checking regular price if game is currently discounted
        try:
            game_price = without_sub_purchase_tag.find('div',attrs={'class':'discount_original_price'}).string.strip()
        except:
            pass
    #getting game price and cleaning data
    else:
        purchase_tag = game_soup.find('div',attrs={'id':'game_area_purchase','class':'game_area_purchase'}).find('div',attrs={'class':'game_area_purchase_game_wrapper'})
        #checking regular game price (not discounted)
        try:
            game_price = purchase_tag.find('div',attrs={'class':'game_purchase_price price'}).string.strip()
        except:
            pass
        #checking regular price if game is currently discounted
        try:
            game_price = purchase_tag.find('div',attrs={'class':'discount_original_price'}).string.strip()
        except:
            pass


    if game_price is not None:
        # if price is free to play, set it to 0
        if game_price == 'Free to Play':
            game_price = 0
        else:
            game_price = game_price.replace('₪', '')  # Remove non-numeric character '₪'
            game_price = game_price.replace(',', '')  # Remove any commas
            game_price = ''.join(c for c in game_price if c.isdigit() or c == '.')  # Keep only digits and decimal point
            game_price = float(game_price)  # Convert the cleaned string to a float
    else:
        game_price = 0.0  # Set default value to 0 if price is still None
    
    try:
        game_langs = [] # a game can be avilable to play in multiple languages so it's a list
        for lang in game_soup.find('div',attrs={'id':'languageTable'}).find_all('td',attrs={'class':'ellipsis'}):
            game_langs.append(lang.string.strip()) #get all languages from page
    except:
        pass
    
    #set the dlc flag if a game has dlc or not
    if game_soup.find('div',attrs={'id':'gameAreaDLCSection'}):
        game_dlc = 1
    else:
        game_dlc = 0
        
        #set the mature content flag if a game has it or not
    if game_soup.find('div',attrs={'id':'game_area_content_descriptors'}):
        game_mature = 1
    else:
        game_mature = 0
        
    #dealing with very special case where there is no cat_block
    try:
        single_tag = game_soup.find('div',attrs={'id':'category_block'}).find('div',attrs={'class':'label'}).string.strip()
        if single_tag == 'Single-player':
            game_single = 1
        else:
            game_single = 0
    except:
        pass

    return game_name,game_date,game_developer,game_publisher,game_genre,game_review_count,game_review_positive,game_review_negative,game_price,game_langs,game_dlc,game_mature,game_single

    

#main function to crawl on the steam site with the above functions
if __name__ == '__main__':
    print('hello please enter 1 to start a new DF or 2 to continue an existing one') #choose between new or existing df to insert data to
    choice = int(input())
    if choice == 1:
        NewDF()
    elif choice == 2:
        print('please input the Df Name you would like to continue from')
        Name = input()
        print('please input the page number you would like to continue from')
        i = int(input())
        GameDF = pd.read_csv(Name+'.csv',index_col=0)
        #GameDF = pd.read_csv('D:\Python projects\Steam - Visual\SteamGamesDF.csv',index_col=0)
        ContinueDF(GameDF,i)
        
        
