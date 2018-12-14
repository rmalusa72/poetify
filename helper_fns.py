import re
import pronouncing 
import psv
import random
from num2words import num2words

psvs = psv.PSV_Space()

# Estimate the number of syllables in a word (poorly)
def dirtysyllables(word):
    vowels = "aeiouy"
    invowelblock = False
    syllables = 0
    for letter in word:
        if letter in vowels:
            if not invowelblock:
                invowelblock = True
                syllables = syllables + 1
        else:
            invowelblock = False

    if syllables != 0: 
        return syllables
    else:
        return 1

# Get stresses for each word in a phrase and concatenate them
def get_stresses(phrase):
    words = phrase.split(" ")
    if len(words) == 1:
        return get_stresses_oneword(phrase)
    else:
        stresses = ""
        for word in words:
            stresses = stresses + get_stresses_oneword(word)
        return stresses

# Use pronouncing to get stresses for a word
# Or return string of as many 3s as there are syllables if word is not in pronouncing dict
def get_stresses_oneword(word):
    phones_list = pronouncing.phones_for_word(word)
    if len(phones_list) > 0:
        phones = phones_list[0]
        stresses = pronouncing.stresses(phones)
        if len(stresses) == 0 or len(stresses) == 1:
            stresses = "3"
    else:
        num_syllables = dirtysyllables(word)
        stresses = '3' * num_syllables
    return stresses

def score_metric_conformity(meter, word):
    position_in_meter = 0
    stresses = get_stresses(word)

    hits = 0
    misses = 0

    for stress in stresses:

        if meter[position_in_meter] == "0":
            options = "03"
        elif meter[position_in_meter] == "1":
            options = "123"

        if stress in options:
            hits = hits + 1
            position_in_meter = position_in_meter + 1
            if position_in_meter >= len(meter):
                position_in_meter = 0
        else:
            misses = misses + 1

    if (hits + misses) == 0:
        print("problem scoring conformity of " + word)
    return (hits / (hits + misses))

# Gets cosine similarity of two vectors and converts to value between 0 and 1
def score_phonetic_similarity(word1, word2):
    return ((psvs.get_phonetic_similarity(word1,word2) + 1 )/ 2)

def process_source_text(text):
    preprocessed_words = re.findall(r"([\d]+[,\d]+|\w+\'?\w*)", text)
    words = []
    for word in preprocessed_words:
        if not re.search(r"\d", word):
            words.append(word)
        else:
            word = re.sub(",", "", word)
            split_by_numbers = re.split(r"(\d+)", word)
            for piece in split_by_numbers: 
                if re.fullmatch(r"\d+", piece):
                    word_version = num2words(int(piece), lang="en")
                    words = words + re.findall(r"\w+", word_version)
                elif piece != "":
                    words.append(piece)
    return words

def poem_to_string(poem):
    output = ""
    running_syllable_count = 0
    for item in poem:
        words = item.split(" ")
        for word in words:
            stresses = get_stresses(word)
            syllable_count = len(stresses)
            output = output + word + " "
            running_syllable_count += syllable_count
            if running_syllable_count >= LINE_LENGTH_SYLLABLES:
                running_syllable_count = 0
                output = output + "\n"
    output = output + "\n"
    return output

