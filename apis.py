from flask import Flask, jsonify, request, make_response, abort
import sys
import pickle
from collections import defaultdict
import numpy as np
import pandas as pd
from geopy import distance
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

print('Loading model 1........ '+'\n')
model = pickle.load(open("model.pkl","rb"))
print('Loading model 2.....')
modelafterrec = pickle.load(open("modelafterrec.pkl","rb"))
print('Model 2 loaded...')
returnedList = pickle.load(open("modelTopRec.pkl","rb"))
reviewData = returnedList[0]
restaurantData = returnedList[1]
@app.errorhandler(404)
def unable_to_locate(error):
    print("test statement to detect failure")
    #make_response - converts the return value to proper response objects
    return make_response(jsonify({'error':'Unable to locate'})),404



#Utilities methods
def getQuarter(quarter,year):
    if(quarter == 'quarter1'):
        month = [1,2,3]
    elif(quarter == 'quarter2'):
        month = [4,5,6]
    elif(quarter == 'quarter3'):
        month = [7,8,9]
    elif(quarter == 'quarter4'):
        month = [10,11,12]

    temp =  reviewData[(reviewData['year'] == year)]
    quarterDF = temp[temp['month'].isin(month)] 
    return quarterDF

def createBusinessRatingsListDict(dataFra):
    business_reviews = defaultdict()
    lis = []
    for i,row in dataFra.iterrows():
        a = row['business_id']
        if a not in business_reviews.keys():
            business_reviews[row['business_id']] = lis
        else:
            lis = business_reviews.get(row['business_id'])
        lis.append(row['PredictedRating'])
        business_reviews[row['business_id']] = lis
        lis = []
    return  business_reviews

def createBusinessRatingMeanList(business_reviews):
    final_business_ratings = {}
    for val in business_reviews:
        final_business_ratings[val] = np.mean(business_reviews[val]) 
    return final_business_ratings

def getLatLong(ipbusiness_id):
    for i,row in restaurantData.iterrows():
        if row['business_id'] == ipbusiness_id:
            return float(row['latitude']) , float(row['longitude'])
        
def getNeighbours(latitude,longitude,distance1):
    latitude = float(latitude)
    longitude = float(longitude)
    distance1 = float(distance1)
    curr_loc = (latitude,longitude)
    dist = []
    for i,row in restaurantData.iterrows():
        dist.append(distance.distance((row['latitude'],row['longitude']),curr_loc).miles)
    restaurantData['dist'] = dist
    new_df = restaurantData[restaurantData.dist <= distance1]
    return new_df

def countPosNeg(quarterDf):
    d = {}
    for i,row in quarterDf.iterrows():
        if row['business_id'] not in d.keys():
            d[row['business_id']] = [0,0]
            li = d.get(row['business_id']) 
            if row['PostiveScore'] <= row['NegativeScore']:  
                li[1] = li[1]+1
                d[row['business_id']] = li
            else:
                li[0] = li[0]+1
                d[row['business_id']] = li

        else:
            
            li = d.get(row['business_id']) 
            if row['PostiveScore'] <= row['NegativeScore']:  
                li[1] = li[1]+1
                d[row['business_id']] = li
            else:
                li[0] = li[0]+1
                d[row['business_id']] = li
    return d

@app.route('/get_recommendation/<string:client_id>', methods=['GET'])
def get_recommendation_for_uid(client_id):
    for uid, user_ratings in model.items():
        if (uid == client_id):
            valueToSend =  uid, ([iid for (iid, _) in user_ratings])
            userId = valueToSend[0]
            business_ids = valueToSend[1]
            df_restaurant = restaurantData.loc[restaurantData['business_id'].isin(business_ids)]

    
            restaurant_details = dict()
            restaurant_details['user_id'] = userId
            for index, row in df_restaurant.iterrows():
                
                restaurant_details[row['business_id']] = {
                    'name':row['name'],
                    'postal_code':row['postal_code'],
                    'categories' :row['categories'],
                    'is_open' : row['is_open'],
                    'city':row['city'],
                    'state':row['state'],
                    'stars':row['stars'],
                    'lat':row['latitude'],
                    'longi':row['longitude']  
                     } 

            return  jsonify({"response": restaurant_details
                    }),200
    return 'Not found'


@app.route('/get_recommendation_after_topic_modelling/<string:user_id>', methods=['GET'])
def get_recommendation(user_id):
    for uid, user_ratings in modelafterrec.items():
        if (uid == user_id):
            valueToSend =  uid, ([iid for (iid, _) in user_ratings])
            userId = valueToSend[0]
            business_ids = valueToSend[1]
            df_restaurant = restaurantData.loc[restaurantData['business_id'].isin(business_ids)]

    
            restaurant_details = dict()
            restaurant_details['user_id'] = userId
            for index, row in df_restaurant.iterrows():
                
                restaurant_details[row['business_id']] = {
                    'name':row['name'],
                    'postal_code':row['postal_code'],
                    'categories' :row['categories'],
                    'is_open' : row['is_open'],
                    'city':row['city'],
                    'state':row['state'],
                    'stars':row['stars'],
                    'lat':row['latitude'],
                    'longi':row['longitude']  
                     } 

            return  jsonify({"response": restaurant_details
                    }),200
    return 'Not found'    

@app.route('/get_top_restaurants_quarter_qy/<string:quarter>/<int:year>', methods=['GET'])
def getReviews(quarter,year): 
    quarterDF = getQuarter(quarter,year)
    business_rating_dict = createBusinessRatingsListDict(quarterDF)
    business_rating_mean_dict = createBusinessRatingMeanList(business_rating_dict)

    dfg = sorted(business_rating_mean_dict.items(), key=lambda x: x[1],reverse=True)

    rank_dict = {}
    for i in range(1,len(dfg)+1):
        rank_dict[dfg[i-1][0]]= i

    business_list = list()
    for d in dfg[0:10]:
           business_list.append(d[0])
    df_restaurant = restaurantData.loc[restaurantData['business_id'].isin(business_list)]

    restaurant_details = dict()
    for index, row in df_restaurant.iterrows():
        restaurant_details[row['business_id']] = {
           'name':row['name'],
           'postal_code':row['postal_code'],
           'categories' :row['categories'],
           'is_open' : row['is_open'],
           'city':row['city'],
           'state':row['state'],
           'stars':row['stars'],
           'lat':row['latitude'],
           'longi':row['longitude'] ,
           'rank':rank_dict.get(row['business_id'])
        }        
#postal_code,categories,name,is_open,hours,city,state
    return jsonify({"business_list": restaurant_details})

@app.route('/get_top_restaurants_location/<string:latitude>/<string:longitude>/<string:quarter>/<int:year>', methods=['GET'])
def getReviewsDistance(latitude,longitude,quarter,year):
    latitude = float(latitude)
    longitude = float(longitude)
    #distance1 = float(distance1)
    curr_loc = (latitude,longitude)
    dist = []
    for i,row in restaurantData.iterrows():
        dist.append(distance.distance((row['latitude'],row['longitude']),curr_loc).miles)
    restaurantData['dist'] = dist
    new_df = restaurantData[restaurantData.dist <= 5]
    new_df_list = list(new_df['business_id'])
    
    quarterDF = getQuarter(quarter,year)
    quarterDF = quarterDF.loc[quarterDF['business_id'].isin(new_df_list)]
   
    business_rating_dict = createBusinessRatingsListDict(quarterDF)
    business_rating_mean_dict = createBusinessRatingMeanList(business_rating_dict)
    dfg = sorted(business_rating_mean_dict.items(), key=lambda x: x[1],reverse=True)
    rank_dict = {}
    for i in range(1,len(dfg)+1):
        rank_dict[dfg[i-1][0]]= i

    business_list = list()
    for d in dfg[0:10]:
           business_list.append(d[0])

    df_restaurant = restaurantData.loc[restaurantData['business_id'].isin(business_list)]
    restaurant_details = dict()
    for index, row in df_restaurant.iterrows():
        restaurant_details[row['business_id']] = {
           'name':row['name'],
           'postal_code':row['postal_code'],
           'categories' :row['categories'],
           'is_open' : row['is_open'],
           'city':row['city'],
           'state':row['state'],
           'rank' : rank_dict.get(row['business_id']),
           'stars':row['stars'],
           'lat':row['latitude'],
           'longi':row['longitude'] 
              
        }            
    return jsonify({'response':restaurant_details})


@app.route('/get_insights/<string:business_id>/<string:quarter>/<int:year>', methods=['GET'])
def getBusinessInsights(business_id,quarter,year):
    lat,longi = getLatLong(business_id)
    quarterDF = getQuarter(quarter,year)
    neighbours_df = getNeighbours(lat,longi,3)
    li = list(neighbours_df['business_id'])
    quarterDF = quarterDF.loc[quarterDF['business_id'].isin(li)]
    print(len(quarterDF))
    di = createBusinessRatingsListDict(quarterDF)
    di1 = createBusinessRatingMeanList(di)
    dfg = sorted(di1.items(), key=lambda x: x[1],reverse=True)
    
    rank_dict = {}
    for i in range(1,len(dfg)+1):
        rank_dict[dfg[i-1][0]]= i
        
    business_list = list()
    business_list.append(business_id)
    for d in dfg[0:10]:
           business_list.append(d[0])
    quarterDF = quarterDF.loc[quarterDF['business_id'].isin(business_list)]
    print(quarterDF.shape)
    dl = countPosNeg(quarterDF)
    
    business_list = list(quarterDF['business_id'])
    df_restaurant = restaurantData.loc[restaurantData['business_id'].isin(business_list)]
    restaurant_details = {}
    for index, row in df_restaurant.iterrows():
        ps = dl.get(row['business_id'])[0]
        ns = dl.get(row['business_id'])[1]
        tot = ps + ns
        restaurant_details[row['business_id']] = {
           'name':row['name'],
           'postal_code':row['postal_code'],
           'categories' :row['categories'],
           'is_open' : row['is_open'],
           'city':row['city'],
           'state':row['state'],
           'rank' : rank_dict.get(row['business_id']),
           'reviews' : tot,
           'psCount':ps,
           'nsCount':ns,
           'stars':row['stars']} 

    return jsonify({'response':restaurant_details})

app.run(debug=True, port = 8080)