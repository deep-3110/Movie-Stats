################ IMPORTING IMPORTANT MODULES STARTS#########################
import numpy as np
import pprint
from imdb import IMDb
import pandas as pd
from math import pi
from flask import Flask, render_template, request,redirect
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
from datetime import date
import time
from tmdbv3api import TMDb
import tweepy
import time
import csv
from tmdbv3api import Movie
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
import numpy as np
import smtplib
from email.message import EmailMessage
################ IMPORTING MODULES ENDS ############################
#------------------------------------------------------------------#
################ GLOBAL VARIABLES DECLARATION STARTS ################
vote_count=""
count_good=0
count_bad=0
review_content=[]
imdb_id=""
user=[]
loc=[]
text=[]
time1=[]
ptweets=[]
ntweets=[]
movie=""
img_path=""
poster=""
movie_name=""

################ GLOBAL VARIABLE ENDS ##############################
#------------------------------------------------------------------#
#################### TMDB API KEY INITIALIZATION  ###################
tmdb = TMDb()
tmdb.api_key = '1b27399eeae3f9a568aee0f4f6044198'

#################### TMDB API KEY INITIALIZATION  ####################
#------------------------------------------------------------------#
####################### TWEET API KEYS STARTS ###############################
consumer_key = 'mqbfImXrFWhdLVEEoMCNX6jcj'
consumer_secret = 'plFDX5DYQUDXEKfa0kCpPt59T5izIbpv5BEjITP3GN4UE8Lb2Z'
access_token = '1317050432154439680-HaE5kFdts38dO03ytt9bHMcWlVzqP2'
access_token_secret = 'aeZKAy47x4HLVTJCzdQuWGBwFcxCQddIk7kAFdMPOOwIU'
################################# TWEET API KEYS ENDS ###################
#------------------------------------------------------------------#
#################### TWITTER API INITIALIZATION STARTS ####################
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

#################### TWITTER API INITIALIZATION ENDS ####################


#################### clean_tweet:It Cleans the tweets of any random chracters and returns a list of strings in it  ####################
def clean_tweet(tweet): 
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 


#################### get_tweet_sentiment(tweet): It returns sentiment of a tweet using Text Blob Library;if polarity>0:Positive  and if polarity=1:Neutral ####################
def get_tweet_sentiment(tweet): 
    analysis = TextBlob(clean_tweet(tweet)) 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'

#################### get_movie_rating(imdb_id): It returns the IMDB rating of a movie from its IMDB ID  ####################
def get_movie_rating(imdb_id):
    ia=IMDb()
    string=imdb_id
    substring=imdb_id[2:]
    movie= ia.get_movie(substring)
    rating =movie.data['rating'] 
    return(rating)

#################### calculate_dassh_offset_rating(rating):It calculates dash offset rating used to animate the IMDB rating chart  ####################
def calculate_dassh_offset_rating(rating):
    rate=502-(502*rating)/10
    return(int(rate))


#################### get_tweets(query, count = 25):It gets 25 tweets based on the Movie Name(query)  ####################
def get_tweets(query, count = 25): 
    tweets = [] 
    try: 
		# call twitter api to fetch tweets 
        fetched_tweets = api.search(q = query, count = count) 
        for tweet in fetched_tweets: 
            parsed_tweet = {} 
            parsed_tweet['text'] = tweet.text 
            parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text) 
            if tweet.retweet_count > 0: 
                if parsed_tweet not in tweets: 
                    tweets.append(parsed_tweet) 
            else:
                tweets.append(parsed_tweet) 
        return tweets 
    except tweepy.TweepError as e: 
        print("Error : " + str(e)) 



#################### WE LOAD NLP MODEL AND TFIDF VECTORIZER FROM DISK OVER HERE  ####################
filename = 'nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('tranform.pkl','rb'))

#################### WE LOAD NLP MODEL AND TFIDF VECTORIZER FROM DISK OVER HERE  ####################

#---------------------------------------------------------------------------------------------------#

#################### def create_sim(): NOT USED ->FINDS THE SIMILAR MOVIES OVER HERE WE USE OUR VECTORIZER OVER HERE  ####################
def create_sim():
    data = pd.read_csv('./dataset/main_data.csv')
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    sim = cosine_similarity(count_matrix)
    return data,sim

#################### rcmd(m) : NOT USED ->IT IS NOT USED IN THE CODE  ####################
def rcmd(m):
    m = m.lower()
    try:
        data.head()
        sim.shape
    except:
        data, sim = create_sim()
    if m not in data['movie_title'].unique():
        return('Sorry! The movie your searched is not in our database. Please check the spelling or try with some other movies')
    else:
        i = data.loc[data['movie_title']==m].index[0]
        lst = list(enumerate(sim[i]))
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
        lst = lst[1:11]
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        return l

#################### ListOfGenres(genre_json):IT RETURNS THE LIST OF GENRES ####################
def ListOfGenres(genre_json):
    if genre_json:
        genres = []
        genre_str = ", " 
        for i in range(0,len(genre_json)):
            genres.append(genre_json[i]['name'])
        return genre_str.join(genres)

####################def MinsToHours(duration):IT CONVERTS YOUR TIME FROM MINUTES TO HOURS/MIN FORMAT EG.140 MIN->2Hr10Min ####################
def MinsToHours(duration):
    if duration%60==0:
        return "{:.0f} hours".format(duration/60)
    else:
        return "{:.0f} hours {} minutes".format(duration/60,duration%60)

#################### def get_suggestions():RETURNS movie_title FROM THE 'main_data.csv' FOR AUTOCOMPLETION ####################
def get_suggestions():
    data = pd.read_csv('dataset/main_data.csv')
    return list(data['movie_title'].str.capitalize())


#################### def get_directorsname(imdb_id): IT RETURNS DIRECTORS NAME FROM THE THE imdb_id ####################
def get_directorsname(imdb_id):
    ia=IMDb()
    string=imdb_id
    substring=imdb_id[2:]
    movie= ia.get_movie(substring)
    for director in movie['directors']:
        print(director['name'])
    return(director['name'])


#################### def get_year(imdb_id): : IT RETURNS THE RELEASE YEAR OF THE MOVIE ####################
def get_year(imdb_id):
    ia = IMDb() 
    string=imdb_id
    substring=imdb_id[2:]
    movie= ia.get_movie(substring)
    year = movie['year']
    return(year) 

####################def IMDB_link(): NOT USED -> RETURNS THE IMDB LINK OF THE MOVIE ####################
def IMDB_link():
    data=pd.read_csv('./dataset/movie_metadata.csv')
    imdblink=data['movie_imdb_link']
    return(imdblink)

####################def write_to_csv(): INSERTS THE USERS NAME,EMAIL AND MESSAGE IN THE database.csv ####################
def write_to_csv(name,email,message):
    with open('database.csv',newline='',mode='a') as database2:
        name=name
        email=email
        message=message
        csv_writer = csv.writer(database2,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([name,email,message])
        email=EmailMessage()
        email['from']=name
        email['to']='deepshah3110@gmail.com'
        email['subject']='A MovieStat User'
        email.set_content(message)
        #For email to work you need to make changes
        with smtplib.SMTP(host='smtp.gmail.com',port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login('projectwork2023@gmail.com','nmims123')
            smtp.send_message(email)
            print('--Sent Mail--')

############################################## FLASK SECTION #####################################################
app = Flask(__name__)

############################################## / - home.html ######################################
@app.route("/")
def home():
    print("--Entered Home--")
    suggestions = get_suggestions()
    return render_template('home.html',suggestions=suggestions)


############################################## RECOMMENDATION - Dashboard.html ######################################
@app.route("/recommend")
def recommend():
    
    print("--Entered the Recommend Section--")
    global movie
    movie = request.args.get('movie') # get movie name from the URL
    print("--Recieved Movie Title:"+str(movie)+"--")
    r = rcmd(movie)
    movie = movie.upper()
    if True:
        tmdb_movie = Movie()
        result = tmdb_movie.search(movie)

        # get movie id and movie title
        
       
        try:
            movie_id = result[0].id
            movie_name = result[0].title
        except IndexError:
            return render_template('404.html')
        global imdb_id
       
        # making API call
        response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
        data_json = response.json()
        imdb_id = data_json['imdb_id']
        poster = data_json['poster_path']
        global img_path
        #img_path returns the poster of image from tmdb
        img_path = 'https://image.tmdb.org/t/p/original{}'.format(poster)
        #poster is unused
        poster = []

        # getting list of genres form json
        genre = ListOfGenres(data_json['genres'])
        

        #web scraping to get user reviews from IMDB site
        sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
        soup = bs.BeautifulSoup(sauce,'lxml')
        soup_result = soup.find_all("div",{"class":"text show-more__control"})
        
        global review_content
         # list of reviews
        reviews_list =[]
        reviews_status = [] # list of comments (good or bad)
        ia1 = IMDb() 
        string=imdb_id
        substring=imdb_id[2:]
        movie1= ia1.get_movie(substring,['reviews'])
        revw=movie1['reviews']
        reviews_list_dash=[ sub['content'] for sub in revw ]

        for reviews in reviews_list_dash:
            if reviews:
                reviews_list.append(reviews)
                # passing the review to our model
                movie_review_list = np.array([reviews])
                movie_vector = vectorizer.transform(movie_review_list)
                pred = clf.predict(movie_vector)
                reviews_status.append('Good' if pred else 'Bad')

        # combining reviews and comments into dictionary
        movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))} 
        #counting number of bad and good reviews
        
        global count_good
        global count_bad
        num_rev=len(movie_review_list)
        for i in range(len(reviews_status)):
            if 'Good' in reviews_status[i] :
                count_good+=1
            elif 'Bad' in reviews_status[i]:
                count_bad+=1

        print("--Entered the Review Analysis Section--")
        print("Good Reviews:",count_good)
        print("Reviews Status: Working")
        #print("Reviews Status: Working",reviews_status)
        print("Bad Reviews:",count_bad)   
        review_content=list(movie_reviews.keys())
        

       

        # getting votes with comma as thousands separators
        global vote_count
        vote_count = "{:,}".format(result[0].vote_count)
        
       
        #getting director name
        director=get_directorsname(imdb_id)
     
        #getting release year of move
        year=get_year(imdb_id)

        # convert minutes to hours minutes (eg. 148 minutes to 2 hours 28 mins)
        runtime = MinsToHours(data_json['runtime'])
        #get imdb links
        imdblink=IMDB_link()


    
    good=count_good
    bad=count_bad
    value=[]
    value.append(int(good))
    value.append(int(bad))
    if value[0]>value[1]:
        review_str="Positive Reviews"
    else:
        review_str="Negative Reviews"


    #twitter review check
     
    print("--Entered the Tweet Analysis Section--")
    global user
    global loc
    global text
    global time1
    user_prof=[]
    tweet_id=[]
    user.clear()
    loc.clear()
    text.clear()
    time1.clear()
    tweets = tweepy.Cursor(api.search, 
                           q=movie,
                           lang="en").items(25)
    for tweet in tweets:
        user.append(tweet.user.screen_name)
        loc.append(tweet.user.location)
        time1.append(str(tweet.user.created_at))

        user_prof.append(tweet.user.profile_image_url)
        text.append(tweet.text) 
        review=review_content
        tweet_id.append(tweet.id)
        #print(review)
    global ptweets
    global ntweets
    tweets = get_tweets(query =movie+" "+"movie", count = 200) 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
    print("Neutral tweets percentage: {} % ".format(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets))) 
    positive_tweet_count=round((100*len(ptweets)/len(tweets)))
    neutral_tweet_count=round((100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets)))
    negative_tweet_count=round((100*len(ntweets)/len(tweets)))
    """ print("\n\nPositive tweets:") 
    for tweet in ptweets[:10]: 
        print(tweet['text']) 
    print("\n\nNegative tweets:") 
    for tweet in ntweets[:10]: 
        print(tweet['text'])  """
    rating=get_movie_rating(imdb_id)
    dash=calculate_dassh_offset_rating(int(rating))
    return render_template('dashboard.html',movie=movie,mtitle=r,t='l',rating=rating,dash_offset=dash,
            result=result[0],reviews=movie_reviews,img_path=img_path,genres=genre,vote_count=vote_count,
      runtime=runtime,director=director,year=year,imdblink=imdblink,value=value,review=review_str,user=user,user_profile_pic=user_prof,location=loc,time=time1,text=text,tweet_id=tweet_id,reviews_list=reviews_list_dash,positive_tweet_count=positive_tweet_count,neutral_tweet_count=neutral_tweet_count,negative_tweet_count=negative_tweet_count,tweet=tweets)

############################################## /contact_us- contactus.html ######################################
@app.route('/contact_us',methods=['POST','GET'])
def contact_us():
    print("---Entered the CONTACT US Section--")
    message = ''
    if request.method == 'POST':
        name = request.form.get('name')  # access the data inside 
        email = request.form.get('email')
        message=request.form.get('message')
        
        write_to_csv(name,email,message)
        return redirect('/thankyou.html')
    return render_template('contactus.html', message=message,movie=movie)

############################################## /thankyou.html - thankyou.html ######################################
@app.route('/thankyou.html')
def thankyou():
    print("--Entered the Thank You Section--")
    return render_template('thankyou.html',movie=movie)

############################################## /tweets.html - tweets.html ######################################
@app.route('/tweets.html')
def tweets():
    print("--Entered tweets.html--")
    return render_template('tweets.html',user=user,location=loc,time=time1,text=text,movie=movie)


############################################## /moviereviews.html - moviereviews.html ######################################
@app.route('/moviereviews.html')
def moviereviews():
    print("--Entered movierevies.html--")
    ia = IMDb() 
    string=imdb_id
    substring=imdb_id[2:]
    movie1= ia.get_movie(substring,['reviews'])
    reviews=movie1['reviews']
    author_name = [ sub['author'] for sub in reviews ] 
    content=[ sub['content'] for sub in reviews ] 
    review_date=[ sub['date'] for sub in reviews ] 
    return render_template('moviereviews.html',author=author_name,content=content,date=review_date,movie=movie)



############################################## /aboutus.html- aboutus.html ######################################
@app.route('/aboutus.html')
def aboutus():
    print("--Entered aboutus.html--")
    return render_template('aboutus.html',movie=movie)


############################################## 404 - 404.html ######################################
@app.errorhandler(404)
def page_not_found(e):
    print("--Entered the 404 page--")
    return render_template('404.html')



if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(threaded=True)
    app.run(debug=True)