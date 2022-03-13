import pandas as pd
import pickle

cleaned_df = pickle.load(open('resources/cleaned_df.pkl', 'rb'))
bm25_title, bm25_ingred = pickle.load(open('models/bm25.pkl', 'rb'))

def searchByTitle(query):
    score = bm25_title.transform(query)
    if query is None:
        return 'The JSON body is required title.', 400
    df_bm = pd.DataFrame({'bm25': list(score), 'id':list(cleaned_df.index), 'title': list(cleaned_df['title']), 'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']), 'image_name': list(cleaned_df['image_name']),}).nlargest(columns='bm25', n=10)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    return df_bm.to_dict('records'), 200

def searchByIngredients(query):
    score = bm25_ingred.transform(query)
    if query is None:
        return 'The JSON body is required title.', 400
    df_bm = pd.DataFrame({'bm25': list(score), 'id': list(cleaned_df.index), 'title': list(cleaned_df['title']),
                          'ingredients': list(cleaned_df['ingredients']),
                          'instructions': list(cleaned_df['instructions']),
                          'image_name': list(cleaned_df['image_name']), }).nlargest(columns='bm25', n=10)
    df_bm['rank'] = df_bm['bm25'].rank(ascending=False)
    df_bm = df_bm.drop(columns='bm25', axis=1)
    return df_bm.to_dict('records'), 200

def getAllMenu(page):
    X = int(page)
    df = pd.DataFrame({'id': list(cleaned_df.index), 'title': list(cleaned_df['title']),
                       'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']),
                       'image_name': list(cleaned_df['image_name']), })
    if X > 1:
        return df[(X - 1) * 10:X * 10].to_dict('records'), X
    else:
        return df[:10].to_dict('records'), 1


def getMenuById(id):
    X = int(id)
    df = pd.DataFrame({'id': list(cleaned_df.index), 'title': list(cleaned_df['title']),
                       'ingredients': list(cleaned_df['ingredients']), 'instructions': list(cleaned_df['instructions']),
                       'image_name': list(cleaned_df['image_name']), })
    df = df[df['id'] == X]
    if (df.empty):
        return 'Menu is not found.', 404
    else:
        return df.to_dict('records'), 200
