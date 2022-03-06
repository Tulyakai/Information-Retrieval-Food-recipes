from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
from spellchecker import SpellChecker

app = Flask(__name__)
CORS(app)

#Cleaned Dataframe
cleaned_df = pickle.load(open('resources/cleaned_df.pkl', 'rb'))
#BM25 title
bm25_title = pickle.load(open('models/bm25_title.pkl', 'rb'))
#BM25 ingredient
bm25_ingred = pickle.load(open('models/bm25_ingred.pkl', 'rb'))

#spell correction dataset
spell = SpellChecker(language='en')
spell.word_frequency.load_text_file('resources/spell_corr/clean_wiki.txt')


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/search', methods=['POST'])
def searchByName():
    body = request.get_json()
    if(body['title'] and not body['ingredients']):
        query = body['title']
    elif(body['ingredients'] and not body['title']):
        query = body['ingredients']
    else:
        return jsonify({'error': 'The JSON body is required title or ingredient at a time'})


    return



if __name__ == '__main__':
    app.run(debug=True)
