from flask import Flask, request, jsonify
from flask_cors import cross_origin
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

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid'}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
@cross_origin()
def createDB():
    # create table
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("CREATE TABLE users (id INT NOT NULL AUTO_INCREMENT, username VARCHAR(45) NOT NULL, password VARCHAR(255) NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);")
        cursor.execute("CREATE TABLE bookmarks (user_id INT NOT NULL, menu_id INT NOT NULL, INDEX id_idx (user_id ASC) VISIBLE, PRIMARY KEY (user_id, menu_id), CONSTRAINT id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE);")
    except:
        return jsonify({'message': 'Database is already existed'}), 400
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Database is created successfully'}), 200

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    body = request.get_json()
    cur = mysql.connection.cursor()
    try:
        password_salt = bcrypt.hashpw(body['password'].encode('utf-8'), bcrypt.gensalt(10))
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (body['username'], password_salt.decode('utf-8')))
        mysql.connection.commit()
    except:
        return jsonify({'message': 'Something went wrong!'}), 400
    cur.close()
    return jsonify({'message': 'Register successfully'}), 200

@app.route('/auth', methods=['POST'])
@cross_origin()
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
        return jsonify({'message': 'Username or password is incorrect'}), 400
    cur.close()
    token = jwt.encode({'user': response[0][1], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'user': result, 'token': token})

@app.route('/getAllMenu/<page>', methods=['GET'])
@cross_origin()
@token_required
def getAllMenu(page):
    X = int(page)
    df = pd.DataFrame({'id':list(cleaned_df.index), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),})
    if X > 1:
        return jsonify({'menus': df[(X - 1) * 10:X * 10].to_dict('records'), 'page': X}), 200
    else:
        return jsonify({'menus': df[:10].to_dict('records'), 'page': 1}), 200

@app.route('/getMenu/<id>', methods=['GET'])
@cross_origin()
@token_required
def getMenuById(id):
    X = int(id)
    df = pd.DataFrame({'id':list(cleaned_df.index), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),})
    df = df[df['id'] == X]
    if(df.empty):
        return jsonify({'message': 'Menu is not found'}), 404
    else:
        return jsonify({'menu': df.to_dict('records')}), 200

@app.route('/search-title', methods=['POST'])
@cross_origin()
@token_required
def searchByName():
    body = request.get_json()
    query = body['query']
    score = bm25_title.transform(query)
    if body['query'] is None:
        return jsonify({'message': 'The JSON body is required title.'}), 400
    df_bm = pd.DataFrame({'bm25': list(score), 'id':list(cleaned_df.index), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),}).nlargest(columns='bm25', n=10)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    spell_corr = [spell.correction(w) for w in body['query'].split()]
    return jsonify({'menus': df_bm.to_dict('records',), 'candidate_query':' '.join(spell_corr)})

@app.route('/search-ingredients', methods=['POST'])
@cross_origin()
@token_required
def searchByIngredients():
    body = request.get_json()
    query = body['query']
    score = bm25_ingred.transform(query)
    if body['query'] is None:
        return jsonify({'message': 'The JSON body is required ingredient.'}), 400
    df_bm = pd.DataFrame({'bm25': list(score), 'id':list(cleaned_df.index), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),}).nlargest(columns='bm25', n=10)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    spell_corr = [spell.correction(w) for w in body['query'].split()]
    return jsonify({'menus': df_bm.to_dict('records'), 'candidate_query':' '.join(spell_corr)}), 200

@app.route('/add-bookmark', methods=['POST'])
@cross_origin()
@token_required
def addBookmark():
    body = request.get_json()
    user_id = body['user_id']
    menu_id = body['menu_id']
    cur = mysql.connection.cursor()
    try:
        if(int(menu_id) <= max(cleaned_df.index) and int(menu_id) >= min(cleaned_df.index)):
            cur.execute("INSERT INTO bookmarks (user_id, menu_id) VALUES (%s, %s)", (user_id,menu_id,))
            mysql.connection.commit()
        else:
            raise KeyError
    except:
        return jsonify({'message': 'Something went wrong!'}), 400
    cur.close()
    return jsonify({'message': 'Add menu to bookmark successfully'}), 200

@app.route('/remove-bookmark', methods=['POST'])
@cross_origin()
@token_required
def removeBookmark():
    body = request.get_json()
    user_id = body['user_id']
    menu_id = body['menu_id']
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM bookmarks WHERE user_id = %s AND menu_id = %s ", (user_id,menu_id,))
        mysql.connection.commit()
    except:
        return jsonify({'message': 'Something went wrong!'}), 400
    cur.close()
    return jsonify({'message': 'Remove menu to bookmark successfully'}), 200

@app.route('/get-bookmark', methods=['GET'])
@cross_origin()
@token_required
def getBookmark():
    body = request.get_json()
    user_id = body['user_id']
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT menu_id FROM bookmarks WHERE user_id = %s", (user_id,))
        response = cur.fetchall()
        idx = [i[0] for i in list(response)]
    except:
        return jsonify({'message': 'Something went wrong!'}), 400
    cur.close()
    df = pd.DataFrame({'id':list(cleaned_df.index), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name'])})
    df = df.iloc[idx]
    return jsonify({'menus': df.to_dict('records'), 'suggestion':[]}), 200

@app.route('/search-bookmark', methods=['POST'])
@cross_origin()
@token_required
def searchBookmark():
    body = request.get_json()
    user_id = body['user_id']
    query = body['query']
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT menu_id FROM bookmarks WHERE user_id = %s", (user_id,))
        response = cur.fetchall()
        idx = [i[0] for i in list(response)]
    except:
        return jsonify({'message': 'Something went wrong!'}), 400
    cur.close()
    score = bm25_title.transform(query)
    df_bm = pd.DataFrame({'bm25': list(score), 'id':list(cleaned_df.index), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),})
    df_bm = df_bm.iloc[idx].nlargest(columns='bm25', n=5)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    return jsonify({'menus': df_bm.to_dict('records'), 'suggestion': []}), 200

if __name__ == '__main__':
    app.run(debug=True)
