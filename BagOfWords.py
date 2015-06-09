#!/usr/bin/env python
# coding=utf-8
#  Author: Angela Chapman
#  Date: 8/6/2014
#
#  This file contains code to accompany the Kaggle tutorial
#  "Deep learning goes to the movies".  The code in this file
#  is for Part 1 of the tutorial on Natural Language Processing.
#
# *************************************** #

import math
import os
from sklearn import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import sys
sys.path.append( os.path.join(os.path.dirname(__file__), 'DeepLearningMovies/' ))
from KaggleWord2VecUtility import KaggleWord2VecUtility
import pandas as pd
from pandas import DataFrame 
import numpy as np
from bs4 import BeautifulSoup
import re
import MySQLdb
import pandas.io.sql as sql
from nltk.corpus import stopwords
from sklearn.externals import joblib

# connect
db_conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="sacdb")
cursor = db_conn.cursor()
cursor.execute('SET NAMES utf8')

query_portal = "SELECT folioSAC,nomDependencia,dependencia_id,descripcion FROM portal,peticion,dependencia WHERE dependenciaId=dependencia_id and folioSAC=folioPeticion"

#query_portal = "SELECT folioSAC,tema_id,CONCAT_WS('_',nomTema,nomsubtema) as nomTema_nomsubtema,descripcion FROM portal,peticion,temas WHERE folioSAC=folioPeticion AND temaId=tema_id"
all_portal = sql.read_sql(query_portal,db_conn).dropna()
query_temas = "SELECT dependencia_id FROM peticion GROUP BY dependencia_id ORDER BY dependencia_id"
temas = sql.read_sql(query_temas,db_conn).dropna()

def review_words( raw_text ):
    review_text = BeautifulSoup(raw_text).get_text()
    letters_only = re.sub("^(\w+)[0-9]@", " ", review_text) 
    callback = lambda pat: pat.group(0).decode('utf-8').lower()
    iac = re.sub(u"Ă",u"í",letters_only)
    ene = re.sub(u"Ñ",u"ñ",iac)
    words = re.sub("(\w+)", callback, ene).split()
    stops = set(stopwords.words("spanish")) 
    meaningful_words = [w for w in words if not w in stops] 
    return( u" ".join( meaningful_words ))  

if __name__ == '__main__':
    train=None
    test=None
    for i in temas["dependencia_id"].tolist():
        num_lines = 0
        num_lines = len(all_portal[all_portal.dependencia_id==i])
        fraction_for_test = 1/3.0
        train0 = all_portal[all_portal.dependencia_id==i].head(num_lines-math.floor(num_lines*fraction_for_test))
        train0.loc[~train0['dependencia_id'].isin([40,7,48,25,19,28,29,5,10,22,8]), 'dependencia_id'] = 0
        train = train0 if train is None else train.append(train0)
        test0 = all_portal[all_portal.dependencia_id==i].tail(math.floor(num_lines*fraction_for_test))
        test0.loc[~test0['dependencia_id'].isin([40,7,48,25,19,28,29,5,10,22,8]), 'dependencia_id'] = 0
        test = test0 if test is None else test.append(test0)


    train.reset_index(inplace=True,drop=True)
    test.reset_index(inplace=True,drop=True)

    print train.shape
    print test.shape
    print 'The first descripcion is:'
    print review_words(train["descripcion"][0])
    print review_words(train["descripcion"][1])
    print review_words(test["descripcion"][0])
    print review_words(test["descripcion"][1])

    raw_input("Press Enter to continue...")


    print 'Download text data sets. If you already have NLTK datasets downloaded, just close the Python download window...'
    #nltk.download()  # Download text data sets, including stop words

    # Initialize an empty list to hold the clean descripcions
    clean_train_descripcions = []

    # Loop over each descripcion; create an index i that goes from 0 to the length
    # of the movie descripcion list
    

    

    print "Cleaning and parsing the training set movie descripcions...\n"
    for i in xrange( 0, len(train["descripcion"])):
        clean_text_train = review_words( train["descripcion"][i] )
        train["nomDependencia"][i] = re.sub(" ","",train["nomDependencia"][i] )
        clean_train_descripcions.append(u" ".join(KaggleWord2VecUtility.review_to_wordlist(clean_text_train, True)))


    # ****** Create a bag of words from the training set
    #
    print "Creating the bag of words...\n"


    # Initialize the "CountVectorizer" object, which is scikit-learn's
    # bag of words tool.
    num_grams = [6]
    num_features = [9500]
    num_estimators = [750]
    
    for g in num_grams:
        for f in num_features:
            for e in num_estimators:
                
                vectorizer = TfidfVectorizer(analyzer = "word",   \
                                            tokenizer = None,    \
                                            smooth_idf = True,   \
                                            sublinear_tf = True, \
                                            preprocessor = None, \
                                            ngram_range = (1,g), \
                                            stop_words = None,   \
                                            strip_accents='unicode',  \
                                            max_features = f)

                # fit_transform() does two functions: First, it fits the model
                # and learns the vocabulary; second, it transforms our training data
                # into feature vectors. The input to fit_transform should be a list of
                # strings.
                #train_data_features = vectorizer.fit_transform(clean_train_descripcions)
                #file_df = 'models/bow_ng{ng}_nf{nf}_ne{ne}.joblib'.format(ng=g,nf=f,ne=e)
                #joblib.dump(train_data_features, file_df, compress=0)
                # Numpy arrays are easy to work with, so convert the result to an
                # array
                #train_data_features = train_data_features.toarray()
    
                #print(train_data_features.shape)

                # ******* Train a random forest using the bag of words
                #
                #print "Training the random forest (this may take a while)..."


                # Initialize a Random Forest classifier with 100 trees
                forest = RandomForestClassifier(n_estimators = e)

                # Fit the forest to the training set, using the bag of words as
                # features and the sentiment labels as the response variable
                #
                # This may take a few minutes to run
                #forest = forest.fit( train_data_features, train["dependencia_id"] )
                
                pipe = pipeline.Pipeline([('vectorizer',vectorizer),('forest',forest)])
                train_data_features = pipe.named_steps['vectorizer'].fit_transform(clean_train_descripcions).toarray()
                pipe.named_steps['forest'].fit(train_data_features,train["dependencia_id"])
                
                #Save model
                file_name = 'models/bow_ng{ng}_nf{nf}_ne{ne}.pkl'.format(ng=g,nf=f,ne=e)
                joblib.dump(pipe, file_name) 


                # Create an empty list and append the clean descripcions one by one
                clean_test_descripcions = []

                print "Cleaning and parsing the test set movie descripcions...\n"
                for i in xrange(0,len(test["descripcion"])):
                    clean_text_test = review_words( test["descripcion"][i] )
                    test["nomDependencia"][i] = re.sub(" ","",test["nomDependencia"][i] )
                    clean_test_descripcions.append(u" ".join(KaggleWord2VecUtility.review_to_wordlist(clean_text_test, True)))

                # Get a bag of words for the test set, and convert to a numpy array
                test_data_features = pipe.named_steps['vectorizer'].transform(clean_test_descripcions)
                test_data_features = test_data_features.toarray()

                # Use the random forest to make sentiment label predictions
                print "Predicting test labels...\n"
                result = pipe.named_steps['forest'].predict(test_data_features)

                # Copy the results to a pandas dataframe with an "folioSAC" column,
                # a "dependencia_id" column, a "test_id" column, a "nomDependencia" column, 
                output = pd.DataFrame( data={"folioSAC":test["folioSAC"], "dependencia_id":result, "test_id":test["dependencia_id"], "nomDependencia":test["nomDependencia"]} )

                # Use pandas to write the comma-separated output file
                file_name = 'Bag_of_Words_model_ng{ng}_nf{nf}_ne{ne}.csv'.format(ng=g,nf=f,ne=e)
                output.to_csv(os.path.join(os.path.dirname(__file__), 'data', file_name), index=False, quoting=2,encoding='utf-8')
                print "Wrote results to file_name".format(file_name=file_name)
