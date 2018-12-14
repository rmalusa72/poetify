# poetifier.py
# class w/parameters to construct poems

import random
import re
import psv
import thesaurus
import scraper
from helper_fns import *

scr = scraper.Scraper()

STRESSED = True
UNSTRESSED = False

class poetifier:

    def __init__(self, PHONETIC_SIMILARITY_WEIGHT=5, LINE_LENGTH_SYLLABLES=10,
     POEM_LENGTH=100, SCORE_THRESHOLD=6, SWITCH_ODDS=3, DEFAULT_TEXT=True, TEXT=None):

        self.phonetic_similarity_weight = PHONETIC_SIMILARITY_WEIGHT
        self.metric_conformity_weight = 10 - PHONETIC_SIMILARITY_WEIGHT
        self.line_length_syllables = LINE_LENGTH_SYLLABLES
        self.poem_length = POEM_LENGTH
        self.score_threshold = SCORE_THRESHOLD
        self.switch_odds = SWITCH_ODDS

        if DEFAULT_TEXT:
            self.text = process_source_text(scr.scrape("poetry"))
        else:
            self.text = process_source_text(TEXT)

        self.num_words = len(self.text)
        self.poem = []
        self.next_syllable = UNSTRESSED
        self.index = 0
        self.index_history = []

    def randomize_parameters(self):
        self.phonetic_similarity_weight = random.randint(0,10)
        self.metric_conformity_weight = 10 - self.phonetic_similarity_weight
        self.line_length_syllables = random.randint(8,12)
        self.poem_length = random.randint(20, 100)
        self.score_threshold = random.randint(0, 10)
        self.switch_odds = random.randint(0, 10)

    def set_phonetic_similarity_weight(self, psw):
        self.phonetic_similarity_weight = psw
        self.metric_conformity_weight = 10 - psw

    def set_metric_conformity_weight(self, mcw):
        self.metric_conformity_weight = mcw
        self.phonetic_similarity_weight = 10 - mcw

    def set_score_threshold(self, st):
        self.score_threshold = st

    def set_switch_odds(self, so):
        self.switch_odds = so

    def set_text(self, text):
        self.text = process_source_text(TEXT)
        self.num_words = len(self.text)
        self.index = 0

    def score_options(self):
        word = self.text[self.index]
        potential_words = {word:0}

        w = thesaurus.Word(word)
        synonyms = w.synonyms()
        for synonym in synonyms:
            potential_words[synonym] =  0

        for nextword in potential_words.keys():
            if len(self.poem) > 0: 
                phonetic_similarity = score_phonetic_similarity(self.poem[-1], nextword)
            else:
                phonetic_similarity = 0.5

            if self.next_syllable == UNSTRESSED: 
                meter = "01"
            else:
                meter = "10"
            metric_conformity = score_metric_conformity(meter, nextword)

            score = phonetic_similarity * self.phonetic_similarity_weight + metric_conformity * self.metric_conformity_weight
            potential_words[nextword] = score

        return potential_words

    def step(self):

        successful_step = False
        options = {}

        while not successful_step: 
            options = self.score_options()
            maxscore = 0
            maxscoreword = ""
            for word, score in options.items():
                if score > maxscore:
                    maxscore = score
                    maxscoreword = word
        
            if maxscore < self.score_threshold:
                dice = random.randint(0, 9)
                if dice < self.switch_odds:
                    self.index = random.randint(0, self.num_words-1)
                    continue

            successful_step = True

            self.poem.append(maxscoreword)
            stresses = get_stresses(maxscoreword)
            if len(stresses) % 2 == 1:
                self.next_syllable = not self.next_syllable

            self.index_history.append(self.index)
            if len(self.index_history) > 20:
                self.index_history = self.index_history[-20:len(self.index_history)]

            self.index = self.index + 1
            if self.index >= self.num_words:
                self.index = random.randint(0, self.num_words-1)

        return options

    def steps(self, steps):
        for i in range(0, steps):
            self.step()

    def backtrack(self, steps):

        if steps > len(self.index_history):
            steps = len(self.index_history)

        self.poem = self.poem[0:(-1*steps)]
        if len(self.poem) > 0:
            stresses = get_stresses(self.poem[-1])
            if stresses[-1] in "12":
                self.next_syllable = UNSTRESSED
            else:
                self.next_syllable = STRESSED
        else:
            self.next_syllable = UNSTRESSED

        self.index = self.index_history[-1*steps]
        self.index_history = self.index_history[0:-1*steps]








