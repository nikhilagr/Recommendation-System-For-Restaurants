# Yelp-Reviews-Analytics-For-Recommendation-System

Yelp Reviews Analytics | San Jose State University | Jun-2018 to Dec 2018

Tech Stack: NLP | Text Mining | Recommendation System | Python | Flask | Angular JS

One Line Description: Using user reviews to predict the rating for items by doing sentiment analysis and topic modeling.

Multi-line Description:
Modular development conceived — components of the project viz.

1. Data preparation & preprocessing
    1. This was the most important and challenging module. Around 6 Million reviews were present in the dataset for 2 lac businesses, considered 1 million reviews only for the restaurants business.
    2. The reviews was present in different languages used pythons lang detect package to separate out only english reviews. Some reviews have urls and symbols such reviews were dropped.
    3. Created bag of words after doing text preprocessing which involved tokenizing, removal of stop words, converting text to lower case, removing punctuation.
2. Sentiment Analysis and Topic Modeling
    1. Used sentiment intensity analyzer to obtain positive and negative scores for each review.This scores were considered as features for training supervised ml model. 
    2. Performed topic modeling on all the reviews and found 10 topics. Each review belonged to one of the above topics. Each topic had probability of word distribution for 10 key words. These 10 probabilities were multiplied with positive and negative scores from sentiment analysis and each product were considered as unique feature for training supervised ML regression algorithm. 
3.  Predict user ratings for items
    1. This module is focussed on building and evaluating regression model. Build and compared performance of four different regressors Ridge Regression model, Lasso regression model, RandomForestRegressor, ExtraTreeRegressor. ExtraTreeRegressor gave best results with RMSE as low as 0.9094. 
4. Building Recommendation System
    1. Used SKLearn’s surprise library which provides packages for building recommendation system with collaborative filtering.
    2. Build item-based recommendation system to predict items rating.
    3. Also build a ranking list for restaurant owners which can work as recommendation for owners as it provides insights to owners about there performance in each quarter.
5. Deployment:
    1. Created rest api using flask and exposed recommendation system as a service which was consumed from front-end Web Application.

Challenges:
1. Data Preprocessing, handling imbalanced data the ratio of 5,4,3,2,1 star rating was different had many 5,4 star rating but few 1,2 start rating reviews.
2. Sentiment analyzer fails to capture sarcastic reviews.

Key Learning:
Sentiment Analysis, LDA Topic Modeling, Unsupervised learning technique, Recommendation system. 
