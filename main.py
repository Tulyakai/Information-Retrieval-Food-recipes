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

@app.route('/register', methods=['POST'])
def register():
    body = request.get_json()
    cur = mysql.connection.cursor()
    try:
        password_salt = bcrypt.hashpw(body['password'].encode('utf-8'), bcrypt.gensalt(10))
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (body['username'], password_salt.decode('utf-8')))
        mysql.connection.commit()
    except:
        return jsonify({'message': 'Something went wrong!'})

    cur.close()
    return jsonify({'message': 'Register successfully'})

@app.route('/auth', methods=['POST'])
def auth():
    body = request.get_json()
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE username = %s", (body['username'],))
        response = cur.fetchall()
        if(bcrypt.checkpw(body['password'].encode('utf-8'), bytes(response[0][2], 'utf-8'))):
            result = {'id': response[0][0], 'username': response[0][1]}
        else:
            raise ValueError
    except:
        return jsonify({'message': 'Username or password is incorrect'})
    cur.close()
    token = jwt.encode({'user': response[0][1], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

    return jsonify({'user': result, 'token': token})

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
