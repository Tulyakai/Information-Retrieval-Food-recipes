from flask import Flask, request, jsonify
from flask_cors import cross_origin
from bm25_model import BM25
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
from services.SpellCorrectionService import spell_corr
from services.RecipeService import searchByTitle, searchByIngredients, getAllMenu, getMenuById
from services.AuthenticationService import addUser, login
from services.BookmarkService import addBookmark, removeBookmark, getBookmark, searchBookmark

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = '953481'
app.config['MYSQL_PORT'] = 3366
app.config['SECRET_KEY'] = 'Bearer'
mysql = MySQL(app)


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
    message, status = addUser(body, mysql)
    return jsonify({'message': message}), status

@app.route('/auth', methods=['POST'])
@cross_origin()
def auth():
    body = request.get_json()
    data, status = login(body, mysql)
    if (status == 400):
        return jsonify({'message': data}), 400
    else:
        token = jwt.encode({'user': data, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'user': data, 'token': token}), 200

@app.route('/getAllMenu/<page>', methods=['GET'])
@cross_origin()
@token_required
def get_all_menu(page):
    data, X = getAllMenu(int(page))
    return jsonify({'menus': data, 'page': X}), 200

@app.route('/getMenu/<id>', methods=['GET'])
@cross_origin()
@token_required
def get_menu_id(id):
    data, status = getMenuById(int(id))
    if status == 404:
        return jsonify({'message': data}), 404
    else:
        return jsonify({'menu': data}), 200

@app.route('/search-title', methods=['POST'])
@cross_origin()
@token_required
def search_title():
    body = request.get_json()
    query = body['query']
    data, status = searchByTitle(query)
    if status == 400:
        return jsonify({'message': data}), 400
    else:
        spell = spell_corr(query)
        return jsonify({'menus': data, 'candidate_query': spell}), 200

@app.route('/search-ingredients', methods=['POST'])
@cross_origin()
@token_required
def search_ingredients():
    body = request.get_json()
    query = body['query']
    data, status = searchByIngredients(query)
    if status == 400:
        return jsonify({'message': data}), 400
    else:
        spell = spell_corr(query)
        return jsonify({'menus': data, 'candidate_query': spell}), 200

@app.route('/add-bookmark', methods=['POST'])
@cross_origin()
@token_required
def add_bookmark():
    body = request.get_json()
    message, status = addBookmark(body, mysql)
    return jsonify({'message': message}), status

@app.route('/remove-bookmark', methods=['POST'])
@cross_origin()
@token_required
def remove_bookmark():
    body = request.get_json()
    message, status = removeBookmark(body, mysql)
    return jsonify({'message': message}), status

@app.route('/get-bookmark', methods=['POST'])
@cross_origin()
@token_required
def get_bookmark():
    body = request.get_json()
    data, status = getBookmark(body, mysql)
    if status == 400:
        return jsonify({'message': data}), 400
    else:
        return jsonify({'men us': data['menus'], 'suggestion':data['suggestion']}), 200

@app.route('/search-bookmark', methods=['POST'])
@cross_origin()
@token_required
def search_bookmark():
    body = request.get_json()
    data, status = searchBookmark(body, mysql)
    if status == 400:
        return jsonify({'message': data}), 400
    else:
        return jsonify({'menus': data['menus'], 'candidate_query': data['candidate_query']}), 200

if __name__ == '__main__':
    app.run(debug=True)
