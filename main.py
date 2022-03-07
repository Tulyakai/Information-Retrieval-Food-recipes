from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
from spellchecker import SpellChecker
from bm25_model import BM25
from flask_mysqldb import MySQL
import bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = '953481'
app.config['MYSQL_PORT'] = 3366

app.config['SECRET_KEY'] = 'Bearer'
mysql = MySQL(app)

#Cleaned Dataframe
cleaned_df = pickle.load(open('resources/cleaned_df.pkl', 'rb'))
#BM25 title and ingredient
bm25_title, bm25_ingred = pickle.load(open('models/bm25.pkl', 'rb'))
#spell correction dataset
spell = SpellChecker(language='en')
spell.word_frequency.load_text_file('resources/spell_corr/clean_wiki.txt')


@app.route('/search-title', methods=['POST'])
def searchByName():
    body = request.get_json()
    query = body['query']
    score = bm25_title.transform(query)
    if body['query'] is None:
        return jsonify({'message': 'The JSON body is required title.'})
    df_bm = pd.DataFrame({'bm25': list(score), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),}).nlargest(columns='bm25', n=10)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    spell_corr = [spell.correction(w) for w in body['query'].split()]
    return jsonify({'menus': df_bm.to_dict('records',), 'candidate_query':' '.join(spell_corr)})


@app.route('/search-ingredients', methods=['POST'])
def searchByIngredients():
    body = request.get_json()
    query = body['query']
    score = bm25_ingred.transform(query)
    if body['query'] is None:
        return jsonify({'message': 'The JSON body is required ingredient.'})
    df_bm = pd.DataFrame({'bm25': list(score), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),}).nlargest(columns='bm25', n=10)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    spell_corr = [spell.correction(w) for w in body['query'].split()]
    return jsonify({'menus': df_bm.to_dict('records'), 'candidate_query':' '.join(spell_corr)})

if __name__ == '__main__':
    app.run(debug=True)
