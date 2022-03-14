from spellchecker import SpellChecker

spell = SpellChecker(language='en')
spell.word_frequency.load_text_file('resources/spell_corr/clean_wiki.txt')

def spell_corr(query):
    spell_corr = [spell.correction(w) for w in query.split()]
    return ' '.join(spell_corr)
