# Information-Retrieval-Food recipes + authentication system + suggestion system 
This is a final project of 622115012 for IR part - 953481 Information Retrieval course, CAMT, CMU.

### Technology Tools
- Python
- Flask
### IR technique
- BM25
# Setting guide
1. Dowload required lyric dataset from [here](https://www.kaggle.com/pes12017000148/food-ingredients-and-recipe-dataset-with-images), then extract and paste into resources folder.
2. Dowload required wiki datasets(100K 2020, 300K, 100K 2016, 1M 2016) from [here](https://wortschatz.uni-leipzig.de/en/download/English?fbclid=IwAR3bjZtPuJiAdXus-oPEImcU7E0ErzH7onI2ih4cAVjMPisFOBFBlYitQno), then paste into resources/spell_corr folder.
3. Run main in dataProcess.py to create parsed_data.pkl and clean_wiki.txt.
4. Run main in bm25_model.py to create fitted mdoel and vectorizer.
5. Run main in main.py, then go to http://localhost:5000/.
6. Enjoy Searching 🥣
