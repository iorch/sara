#!/usr/bin/env python
# coding=utf-8
#  Taken from: Angela Chapman
#  Date: 8/6/2014
#  Modified by: Jorge Martinez-Ortega
#  Date: 5/14/2015
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
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/'))
from KaggleWord2VecUtility import KaggleWord2VecUtility
import pandas as pd
from bs4 import BeautifulSoup
import re
import MySQLdb
import pandas.io.sql as sql
from nltk.corpus import stopwords
from sklearn.externals import joblib
import json
import os


class Trainer:
    def __init__(self, file=None):
        # Connecting to mysql database
        db_conn = MySQLdb.connect(host=os.environ['MODEL_PORT_3306_TCP_ADDR'], user="root", passwd="", db="sacdb")
        cursor = db_conn.cursor()
        cursor.execute('SET NAMES utf8')

        # Query for all peticiones
        query_portal = "SELECT folioSAC,nomDependencia,dependencia_id,descripcion FROM \
                portal,peticion,dependencia WHERE dependenciaId=dependencia_id \
                and folioSAC=folioPeticion"

        # Perform the query and remove NULL
        self.all_portal = sql.read_sql(query_portal, db_conn).dropna()

        # Query for dependencias
        query_dependencias = "SELECT dependencia_id FROM peticion GROUP BY dependencia_id \
               ORDER BY dependencia_id"
        self.dependencias = sql.read_sql(query_dependencias, db_conn).dropna()
        if file is None:
            self.corpus = self.all_portal['descripcion'].values
        else:
            self.corpus = open(file, 'r')

    # Set dependencies to train against
    def set_dependencies(self, a_list=None):
        my_deps = None
        if a_list is int:
            my_deps = [a_list]
        elif a_list is list:
            my_deps = alist
        elif a_list is None:
            my_deps = [40, 7, 48, 25, 19, 28, 29, 5, 10, 22, 8]
        self.freq_deps = my_deps

    # Method to remove accents, stop words and encode in utf-8
    def review_words(self, raw_text):
        review_text = BeautifulSoup(raw_text).get_text()
        letters_only = re.sub("^(\w+)[0-9]@", " ", review_text)
        callback = lambda pat: pat.group(0).decode('utf-8').lower()
        iac = re.sub(u"Ă", u"í", letters_only)
        ene = re.sub(u"Ñ", u"ñ", iac)
        words = re.sub("(\w+)", callback, ene).split()
        stops = set(stopwords.words("spanish"))
        meaningful_words = [w for w in words if not w in stops]
        return (u" ".join(meaningful_words))

    def set_sample_size(self, train_fraction=None):
        self.train_fraction = 0.5 if train_fraction is None else train_fraction
        self.test_fraction = 1.0 - self.train_fraction

    def get_training_sample(self, train_fraction=None):
        all_portal = self.all_portal
        try:
            self.freq_deps
            print 'Using list: ['+','.join(map(str,self.freq_deps))+']'

        except:
            print "List of most frequent dependencies is not defined."
            self.set_dependencies()
            print 'Using default list: ['+','.join(map(str,self.freq_deps))+']'
        else:
            print "List of depenciencies defined previously"
        training_sample = None
        self.set_sample_size(train_fraction)
        for i in self.dependencias["dependencia_id"].tolist():
            num_lines = len(all_portal[all_portal.dependencia_id == i])
            training_size = int(math.floor(num_lines * self.train_fraction))
            subsample = all_portal[all_portal.dependencia_id == i].head(training_size)
            subsample.loc[~subsample['dependencia_id'].isin(self.freq_deps), 'dependencia_id'] = 0
            training_sample = subsample if training_sample is None else training_sample.append(subsample)
        training_sample.reset_index(inplace=True, drop=True)
        return training_sample

    def get_testing_sample(self):
        all_portal = self.all_portal
        testing_sample = None
        try:
            for i in self.dependencias["dependencia_id"].tolist():
                num_lines = len(all_portal[all_portal.dependencia_id == i])
                testing_size = int(math.ceil(num_lines * self.test_fraction))
                subsample = self.all_portal[all_portal.dependencia_id == i].tail(testing_size)
                subsample.loc[~subsample['dependencia_id'].isin(self.freq_deps), 'dependencia_id'] = 0
                testing_sample = subsample if testing_sample is None else testing_sample.append(subsample)
        except:
            print "The training sample size is not defined:", sys.exc_info()[0]
            raise
        testing_sample.reset_index(inplace=True, drop=True)
        return testing_sample

    def prepare_training_sample(self, train_fraction=None):
        self.training_sample = self.get_training_sample(train_fraction)
        self.clean_train_descripciones = []
        print "Cleaning and parsing the training set descripcions...\n"
        for i in xrange(0, len(self.training_sample["descripcion"])):
            clean_text_train = self.review_words(self.training_sample["descripcion"][i])
            self.training_sample["nomDependencia"][i] = re.sub(" ", "", self.training_sample["nomDependencia"][i])
            self.clean_train_descripciones.append(
                u" ".join(KaggleWord2VecUtility.review_to_wordlist(clean_text_train, True)))
        print "Now, the training sample is clean.\n"

    def prepare_testing_sample(self):
        self.testing_sample = self.get_testing_sample()
        self.clean_test_descripciones = []
        print "Cleaning and parsing the testing set descripcions...\n"
        for i in xrange(0, len(self.testing_sample["descripcion"])):
            clean_text_train = self.review_words(self.testing_sample["descripcion"][i])
            self.testing_sample["nomDependencia"][i] = re.sub(" ", "", self.testing_sample["nomDependencia"][i])
            self.clean_test_descripciones.append(
                u" ".join(KaggleWord2VecUtility.review_to_wordlist(clean_text_train, True)))
        print "Now, the testing sample is clean.\n"

    def train_classifier(self, ngrams=1, features=1000, estimators=100):
        g = ngrams
        f = features
        e = estimators
        # Defines the vectorization of peticiones
        vectorizer = TfidfVectorizer(analyzer="word", \
                                     tokenizer=None, \
                                     smooth_idf=True, \
                                     sublinear_tf=True, \
                                     preprocessor=None, \
                                     ngram_range=(1, g), \
                                     stop_words=None, \
                                     strip_accents='unicode', \
                                     max_features=f)

        # Define the classifier
        forest = RandomForestClassifier(n_estimators=e)

        # Define a pipeline that comprisses the vectorization ad the
        # classifier. Perform the fitting of the models and transform the
        # input training peticiones to vectors of features.
        clean_train_descripciones = self.clean_train_descripciones
        self.pipe = pipeline.Pipeline([('vectorizer', vectorizer), ('forest', forest)])
        train_data_features = self.pipe.named_steps['vectorizer'].fit_transform(clean_train_descripciones).toarray()
        self.pipe.named_steps['forest'].fit(train_data_features, self.training_sample["dependencia_id"])

        # Save model
        file_name = 'models/bow_ng{ng}_nf{nf}_ne{ne}.pkl'.format(ng=g, nf=f, ne=e)
        joblib.dump(self.pipe, file_name)

    def test_classifier(self):
        clean_test_descripciones = self.clean_test_descripciones
        # Get a bag of words for the test set, and convert to a numpy array
        test_data_features = self.pipe.named_steps['vectorizer'].transform(clean_test_descripciones)
        test_data_features = test_data_features.toarray()

        # Use the random forest to make sentiment label predictions
        print "Predicting test labels...\n"
        result = self.pipe.named_steps['forest'].predict(test_data_features)

        # Copy the results to a pandas dataframe with an "folioSAC" column,
        # a "dependencia_id" column, a "test_id" column, a "nomDependencia" column,
        self.output = pd.DataFrame(data={"folioSAC": self.testing_sample["folioSAC"], \
                                         "dependencia_id": result, \
                                         "test_id": self.testing_sample["dependencia_id"], \
                                         "nomDependencia": self.testing_sample["nomDependencia"]})

    def save_testing_output(self, ngrams=1, features=1000, estimators=100, file_name="test.csv"):
        self.output.to_csv(file_name, index=False, quoting=2, encoding='utf-8')
        print "Wrote results to file_name".format(file_name=file_name)

    def optimize_classifier(self, params):
        max_ngrams = params['max_ngrams']
        nfeatures = params['nfeatures']
        nestimators = params['nestimators']
        best = {1: {"model": "test", "errprod": 10000.0}, \
                2: {"model": "test", "errprod": 10001.0}, \
                3: {"model": "test", "errprod": 10002.0}}
        for g in max_ngrams:
            for f in nfeatures:
                for e in nestimators:
                    self.train_classifier(g, f, e)
                    self.test_classifier()
                    file_name = 'Bag_of_Words_model_ng{ng}_nf{nf}_ne{ne}.csv'.format(ng=g, nf=f, ne=e)
                    path_and_filename = os.path.join(os.path.dirname(__file__), 'data', file_name)
                    self.save_testing_output(g, f, e, path_and_filename)
                    df = pd.read_csv(path_and_filename)
                    total = 1.0 * df.count()
                    real_vs_test_total = 1.0 * df[(df.test_id == df.dependencia_id)].count()
                    fraction_by_dep = {}
                    eff_by_dep = {}
                    err1_by_dep = {}
                    err2_by_dep = {}
                    for d in self.freq_deps:
                        real_dep = 1.0 * df[(df.dependencia_id == d)].count()
                        test_dep = 1.0 * df[(df.test_id == d)].count()
                        real_vs_test_bydep = 1.0 * df[(df.dependencia_id == d) & (df.test_id == d)].count()
                        err1 = 1.0 * df[(df.dependencia_id != d) & (df.test_id == d)].count()
                        err2 = 1.0 * df[(df.dependencia_id == d) & (df.test_id != d)].count()
                        fraction_by_dep[d] = real_dep / total
                        eff_by_dep[d] = real_vs_test_bydep / real_dep
                        err1_by_dep[d] = err1 / test_dep
                        err2_by_dep[d] = err2 / real_dep
                    try:
                        print zip(err1_by_dep.values(), err2_by_dep.values())
                        error = reduce(lambda x, y: x + math.sqrt(y[1] * y[1] + y[0] * y[0]),
                                   zip(err1_by_dep.values(), err2_by_dep.values()), 0)
                    except TypeError as e:
                        print e
                        error = 2.0
                    if best[3]["errprod"] > error:
                        if best[2]["errprod"] > error:
                            if best[1]["errprod"] > error:
                                best[3] = best[2]
                                best[2] = best[1]
                                best[1] = {"model": 'ng{ng}_nf{nf}_ne{ne}'.format(ng=g, nf=f, ne=e), \
                                           "errprod": error}
                            else:
                                best[3] = best[2]
                                best[2] = {"model": 'ng{ng}_nf{nf}_ne{ne}'.format(ng=g, nf=f, ne=e), \
                                           "errprod": error}
                        else:
                            best[3] = {"model": 'ng{ng}_nf{nf}_ne{ne}'.format(ng=g, nf=f, ne=e), \
                                       "errprod": error}
        with open(os.path.join(os.path.dirname(__file__), 'best_models.json'), 'w') as file_name:
            json.dump(best, file_name)


if __name__ == '__main__':
    t = Trainer()
    t.prepare_training_sample(0.55)
    t.prepare_testing_sample()
    params = {'max_ngrams': [6], \
              'nfeatures': [9400, 9500, 9600], \
              'nestimators': [740]}
    t.optimize_classifier(params)
