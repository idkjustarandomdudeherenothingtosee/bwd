import json
from urllib.parse import parse_qs
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords

def calculate_languages_ratios(text):
    languages_ratios = {}
    tokens = wordpunct_tokenize(text)
    words = [word.lower() for word in tokens]

    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)
        languages_ratios[language] = len(common_elements)
    return languages_ratios

def detect_language(text):
    ratios = calculate_languages_ratios(text)
    most_rated_language = max(ratios, key=ratios.get)
    return most_rated_language

def load_bad_words(language):
    if language.upper() in ['ENGLISH','FRENCH','SPANISH','GERMAN']:
        try:
            badwords_list=[]
            with open('datasets/'+language.lower()+'.csv','r', encoding='utf-8') as lang_file:
                for word in lang_file:
                    badwords_list.append(word.lower().strip('\n'))
            return badwords_list
        except:
            return []
    else:
        return []

def handler(request, response):
    try:
        # Handle GET with query ?text=
        if request.method == "GET":
            query = parse_qs(request.query_string)
            text = query.get('text', [''])[0]
        else:
            # Or POST with JSON body
            body = json.loads(request.body)
            text = body.get('text', '')

        if not text:
            return response.status(400).json({ "error": "No text provided." })

        language = detect_language(text)
        badwords = set(load_bad_words(language))

        results = []
        lines = text.split('\n')

        for idx, sentence in enumerate(lines, start=1):
            clean = sentence
            for key in ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}']:
                clean = clean.replace(key,'')
            abuses = [w for w in clean.lower().split() if w in badwords]
            if abuses:
                results.append({
                    "line": idx,
                    "words": abuses
                })

        return response.status(200).json({
            "language": language,
            "bad_words": results
        })

    except Exception as e:
        return response.status(500).json({ "error": str(e) })
