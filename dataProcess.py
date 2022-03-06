import fnmatch
from zipfile import ZipFile

import pandas as pd
import string
import re
import pickle

import rarfile
from nltk import word_tokenize, PorterStemmer
from nltk.corpus import stopwords
import pint

def preProcess(s):
    ps = PorterStemmer()
    s = re.sub('[^A-za-z]', ' ', s)
    s = word_tokenize(s)
    stopwords_set = set(stopwords.words())
    stop_dict = {s: 1 for s in stopwords_set}
    s = [w for w in s if w not in stop_dict]
    s = [ps.stem(w) for w in s]
    s = ' '.join(s)
    s = s.translate(str.maketrans('', '', string.punctuation + u'\xa0'))
    return s

def get_and_clean_data():
    #DataFrame
    df = pd.read_csv('resources/Food Ingredients and Recipe Dataset with Image Name Mapping.csv', index_col=0)
    df.columns = [i.lower() for i in df.columns]
    #list of unit
    ureg = list(pint.UnitRegistry())
    #Ingredient
    clean_ingredient = df['cleaned_ingredients']
    clean_ingredient = clean_ingredient.apply(lambda s: s.translate(str.maketrans('', '', string.punctuation + u'\xa0')))
    clean_ingredient = clean_ingredient.apply(lambda s: re.sub('[^A-za-z]', ' ', s.lower()))
    clean_ingredient = clean_ingredient.apply(lambda s: re.sub("\s+", " ", s.strip()))
    clean_ingredient = clean_ingredient.apply(lambda s: s.split())
    clean_ingredient = clean_ingredient.apply(lambda s: ' '.join([w for w in s if w not in ureg]))
    clean_ingredient = clean_ingredient.apply(lambda s: s.translate(str.maketrans('', '', string.punctuation + u'\xa0')))
    #Title
    clean_title = df['title']
    clean_title = clean_title.apply(lambda s: str(s).lower())
    clean_title = clean_title.apply(lambda s: s.translate(str.maketrans('', '', string.punctuation + u'\xa0')))
    #Merge
    df['title'] = clean_title
    df['cleaned_ingredients'] = clean_ingredient

    pickle.dump(df, open('resources/cleaned_df.pkl' ,'wb'))
    return df


def clean_data_wiki_100k():
    f = open("resources/spell_corr/eng-simple_wikipedia_2021_100K-sentences.txt", "r", encoding='utf8')
    text = f.read()
    text = re.sub('[^A-za-z]', ' ', text.lower() )
    text = re.sub('\s+', ',', text)
    text = text.split(',')
    text = [w for w in text if len(w)>1]
    text = ' '.join(text)
    return text

def clean_data_wiki_100k_2016():
    f = open("resources/spell_corr/eng_wikipedia_2016_100K-sentences.txt", "r", encoding='utf8')
    text = f.read()
    text = re.sub('[^A-za-z]', ' ', text.lower() )
    text = re.sub('\s+', ',', text)
    text = text.split(',')
    text = [w for w in text if len(w)>1]
    text = ' '.join(text)
    return text

def clean_data_wiki_300k():
    f = open("resources/spell_corr/eng-simple_wikipedia_2021_300K-sentences.txt", "r", encoding='utf8')
    text = f.read()
    text = re.sub('[^A-za-z]', ' ', text.lower() )
    text = re.sub('\s+', ',', text)
    text = text.split(',')
    text = [w for w in text if len(w)>1]
    text = ' '.join(text)
    return text

def clean_data_wiki_1M():
    f = open("resources/spell_corr/eng_wikipedia_2016_1M-sentences.txt", "r", encoding='utf8')
    text = f.read()
    text = re.sub('[^A-za-z]', ' ', text.lower())
    text = re.sub('\s+', ',', text)
    text = text.split(',')
    text = [w for w in text if len(w)>1]
    text = ' '.join(text)
    return text

def clean_iula():
    with ZipFile('resources/spell_corr/IULA_Spanish-English_Technical_Corpus_data.zip') as zipfiles:
        files = fnmatch.filter(zipfiles.namelist(), "EN/*/*plain.txt")
        raw_IULA = [zipfiles.open(file_name).read().decode('utf8') for file_name in files]
    text = ' '.join(raw_IULA)
    text = re.sub('[^A-za-z]', ' ', text.lower())
    text = re.sub('\s+', ',', text)
    text = text.split(',')
    text = [w for w in text if len(w) > 1]
    text = ' '.join(text)
    return text


def group_wiki():
    wiki_1 = clean_data_wiki_100k()
    wiki_2 = clean_data_wiki_300k()
    wiki_3 = clean_data_wiki_100k_2016()
    wiki_4 = clean_data_wiki_1M()
    iula = clean_iula()
    wiki_1 += ' ' + wiki_2
    wiki_1 += ' ' + wiki_3
    wiki_1 += ' ' + wiki_4
    wiki_1 += ' ' + iula
    save_text = open('resources/spell_corr/clean_wiki.txt', 'w')
    save_text.write(wiki_1)


if __name__ == '__main__':
    get_and_clean_data()
    group_wiki()
