from flask import jsonify
import pandas as pd
import pickle
from services.SpellCorrectionService import spell_corr

cleaned_df = pickle.load(open('resources/cleaned_df.pkl', 'rb'))
bm25_title, bm25_ingred = pickle.load(open('models/bm25.pkl', 'rb'))

def addBookmark(data, mysql):
    user_id = data['user_id']
    menu_id = data['menu_id']
    cur = mysql.connection.cursor()
    try:
        if (int(menu_id) <= max(cleaned_df.index) and int(menu_id) >= min(cleaned_df.index)):
            cur.execute("INSERT INTO bookmarks (user_id, menu_id) VALUES (%s, %s)", (user_id, menu_id,))
            mysql.connection.commit()
        else:
            raise KeyError
    except:
        return 'Something went wrong!', 400
    cur.close()
    return 'Add menu to bookmark successfully', 200

def removeBookmark(data, mysql):
    user_id = data['user_id']
    menu_id = data['menu_id']
    cur = mysql.connection.cursor()
    try:
        if (int(menu_id) <= max(cleaned_df.index) and int(menu_id) >= min(cleaned_df.index)):
            cur.execute("DELETE FROM bookmarks WHERE user_id = %s AND menu_id = %s ", (user_id, menu_id,))
            mysql.connection.commit()
        else:
            raise KeyError
    except:
        return 'Something went wrong!', 400
    cur.close()
    return 'Remove bookmark successfully', 200

def getBookmark(data, mysql):
    user_id = data['user_id']
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT menu_id FROM bookmarks WHERE user_id = %s", (user_id,))
        response = cur.fetchall()
        idx = [i[0] for i in list(response)]
    except:
        return  'Something went wrong!', 400
    cur.close()
    df = pd.DataFrame({'id': list(cleaned_df.index), 'title': list(cleaned_df['title']),
                       'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']),
                       'image_name': list(cleaned_df['image_name'])})
    df = df.iloc[idx]
    return {'menus': df.to_dict('records'), 'suggestion': []}, 200

def searchBookmark(data, mysql):
    user_id = data['user_id']
    query = data['query']
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT menu_id FROM bookmarks WHERE user_id = %s", (user_id,))
        response = cur.fetchall()
        idx = [i[0] for i in list(response)]
    except:
        return jsonify({'message': 'Something went wrong!'}), 400
    cur.close()
    score = bm25_title.transform(query)
    df_bm = pd.DataFrame({'bm25': list(score), 'id': list(cleaned_df.index), 'title': list(cleaned_df['title']),
                          'ingredients': list(cleaned_df['ingredients']),
                          'instructions': list(cleaned_df['instructions']),
                          'image_name': list(cleaned_df['image_name']), })
    df_bm = df_bm.iloc[idx].nlargest(columns='bm25', n=5)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    spell = spell_corr(query)
    return {'menus': df_bm.to_dict('records'), 'candidate_query': spell}, 200