# TEXT ANALYSER
from flair.data import Sentence
from flair.models import TextClassifier
from flair.models import SequenceTagger
from transformers import AutoTokenizer, AutoModel, pipeline

# TRANSLATION
from deep_translator import GoogleTranslator
from deep_translator import single_detection


tokenizer = AutoTokenizer.from_pretrained("avichr/heBERT_sentiment_analysis")  # same as 'avichr/heBERT' tokenizer
model = AutoModel.from_pretrained("avichr/heBERT_sentiment_analysis")
# init embedding
tagger = SequenceTagger.load('flair/ner-english-ontonotes-large')
tagger_keywords = SequenceTagger.load('pos')

classifier = TextClassifier.load('en-sentiment')


def transtale_to_eng(non_eng_text) -> tuple:
    # Use a breakpoint in the code line below to debug your script.
    try:
        lang = single_detection(non_eng_text[0:40], 'b6dda1881a372913f69d29190ab9e975')
    except Exception:
        lang = 'en'
    eng = GoogleTranslator(source='auto', target='en').translate(non_eng_text)
    return eng, lang


def transtale_back(lang, eng_words) -> str:
    source_lang = GoogleTranslator(source='en', target=lang).translate(eng_words)
    return source_lang


def flair_prediction(eng_text) -> tuple:
    sentence = Sentence(eng_text)
    classifier.predict(sentence)
    score = sentence.labels[0].score
    label = sentence.labels[0].value
    return label, score


def flair_prediction_hebrew(text) -> tuple:
    sentiment_analysis = pipeline(
        "sentiment-analysis",
        model="avichr/heBERT_sentiment_analysis",
        tokenizer="avichr/heBERT_sentiment_analysis",
        top_k=1)
    result = sentiment_analysis(text[:512])[0][0]
    return result['label'], result['score']


def flair_keywords(lang, eng_text) -> list:
    sentence = Sentence(eng_text)
    tagger_keywords.predict(sentence)
    keywords = {}
    noun_keywords = []
    noun_keys = ('NN', 'NNS')
    for entity in sentence.get_labels('pos'):
        word = entity.shortstring.split('"', 1)[1].split('"')[0]
        group = entity.value
        if group in keywords:
            keywords[group].append(word)
        else:
            keywords[group] = []
            keywords[group].append(word)
        if group in set(noun_keys):
            noun_keywords.append(transtale_back(lang, word.strip()))
    return list(set(noun_keywords))


def flair_names(lang, eng_text) -> list:
    sentence = Sentence(eng_text)
    tagger.predict(sentence)
    names = []
    names_keys = ('PERSON', 'ORG')
    for entity in sentence.get_labels('ner'):
        word = entity.shortstring.split('"', 1)[1].split('"')[0]
        group = entity.value
        if group in set(names_keys):
            names.append(transtale_back(lang, word.strip()))
    return list(set(names))


def return_data_flair(text) -> tuple | list:
    try:
        post = f'''{text}'''
        eng_text, lang = transtale_to_eng(post)
        if lang == 'iw':
            label, score = flair_prediction_hebrew(post)
        else:
            label, score = flair_prediction(eng_text)
        names = flair_names(lang, eng_text)
        noun_keywords = flair_keywords(lang, eng_text)
        label = label.upper()
        return str(eng_text), str(names), list(noun_keywords), str(label), float(score), str(lang)
    except Exception as ex:
        print(ex)
        return [None] * 6
