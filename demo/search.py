from inverted_index import create_index, create_n_grams
from crawl_news import to_ix
from model import Event_tagger

import pymorphy2
import torch
import torch.nn as nn
import torch.nn.functional as F

from constants import MODEL_PATH


def normalize(input_entities, morph):
    input_normalized = []         
    for entity in input_entities:
        word = entity
        word_info = morph.parse(word)[0]
        word_norm = word_info.normal_form
        input_normalized.append(word_norm)

    return input_normalized


def get_doc_indices(input_phrase, inverted_ix):
    docs = []
    for words in inverted_ix.values():
        bigrams = create_n_grams(input_phrase)
        input_phrase.extend(bigrams)

        for word in input_phrase:
            if word in words.keys():
                print(words)
                docs.extend(words[word])
    return list(set(docs))


def create_message(input_normalized, docs, data_splitted, morph, links): 
    messages = []

    for doc in docs:
        message = ''
        for sent in data_splitted[doc]:
            for i, word in enumerate(sent):
                word_info = morph.parse(word)[0]
                word_norm = word_info.normal_form
            
                if word_norm != ' ' and word_norm in input_normalized:
                    message += '<b>' + word + '</b>'
                else:
                    message += word
                message += '. ' if i == len(sent) - 1 else ' '
        messages.append(message + '\n <a href="' + links[doc] + '">читать далее</a>' )
    return messages
    

def search(input_text):    
    input_list = input_text.split()
    inverted_ix, data_splitted, morph, links = create_index()
    
    input_normalized = normalize(input_list, morph)
    print(input_normalized)
    
    docs = get_doc_indices(input_normalized, inverted_ix) 
    messages = create_message(input_normalized, docs, data_splitted, morph, links)

    return messages
