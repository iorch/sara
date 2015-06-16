#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module that provides a class that filters profanities

"""

__author__ = "leoluk"
__modifiedby__ = "iorch"
__version__ = '0.0.2'

import random
from bs4 import BeautifulSoup
import re
import unicodedata
import os
import sys
sys.path.append(os.path.dirname(__file__))
import malas_palabras

my_list = malas_palabras.__una_palabra__


class ProfanitiesFilter(object):
    def __init__(self, filterlist, ignore_case=True, replacements="$@%-?!", 
                 complete=True, inside_words=False):
        """
        Inits the profanity filter.

        filterlist -- a list of regular expressions that
        matches words that are forbidden
        ignore_case -- ignore capitalization
        replacements -- string with characters to replace the forbidden word
        complete -- completely remove the word or keep the first and last char?
        inside_words -- search inside other words?

        """

        self.badwords = filterlist
        self.ignore_case = ignore_case
        self.replacements = replacements
        self.complete = complete
        self.inside_words = inside_words
        
    def remove_accents(self, input_str):
        nkfd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    
    def review_words(self, raw_text):
        review_text = BeautifulSoup(raw_text).get_text()
        letters_only = re.sub("^(\w+)[0-9]@", " ", review_text) 
        callback = lambda pat: pat.group(0).decode('utf-8').lower()
        iac = re.sub(u"Ă", u"í", letters_only)
        ene = re.sub(u"Ñ", u"ñ", iac)
        no_accents = self.remove_accents(ene)
        meaningful_words = re.sub("(\w+)", callback, no_accents).split()
        return u" ".join(meaningful_words)
    
    def profanity_score(self, my_string0):
        # The score is the number of bad words in the string. The bad words are 
        # defined in the malas_palabras.py file. 
        compiled_bw = {}
        isabadword = {}
        to_test = re.compile(".*-.*")
        my_string = self.review_words(my_string0)
        for j in my_string.split(' '):
            isabadword[j] = 0
            for i in self.badwords:
                i = self.remove_accents(i)
                compiled_bw[i] = re.compile(i)
                if isabadword[j] == 0:
                    __replacement__ = compiled_bw[i].sub(self.__replacer,j)
                    test = to_test.match(__replacement__)
                    isabadword[j] = 0 if test is None else 1
                else:
                    next
                
        print isabadword
        return reduce(lambda x, y: x+y, isabadword.values(), 0)

    def _make_clean_word(self, length):
        """
        Generates a random replacement string of a given length
        using the chars in self.replacements.

        """
        return ''.join([random.choice(self.replacements) for i in
                        range(length)])

    def __replacer(self, match):
        value = match.group()
        if self.complete:
            return self._make_clean_word(len(value))
        else:
            return value[0]+self._make_clean_word(len(value)-2)+value[-1]

    def clean(self, text):
        """Cleans a string from profanity."""

        regexp_insidewords = {
            True: r'(%s)',
            False: r'\b(%s)\b',
            }

        regexp = (regexp_insidewords[self.inside_words] % 
                  '|'.join(self.badwords))

        r = re.compile(regexp, re.IGNORECASE if self.ignore_case else 0)

        return r.sub(self.__replacer, text)


if __name__ == '__main__':

    f = ProfanitiesFilter(my_list, replacements="-")    
    example = u"I am doing pendejadas chingonas encabronadas porque ese maldito coño de funcionario me hizo emputar, " \
              u"y es un pinche maricón mirón de mierda."
    
    print f.clean(example)
    # Returns "I am doing --- ------ badlike things."

    f.inside_words = True    
    print f.clean(example)
    # Returns "I am doing --- ------ ---like things."

    f.complete = False    
    print f.clean(example)
    # Returns "I am doing b-d u----d b-dlike things."`
    print f.profanity_score(example)
