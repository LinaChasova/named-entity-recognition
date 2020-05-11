from crawl_news import crawl_news

import pymorphy2

def remove_unannotated_words(data_tagged):
    answer_entities = [[[entity for entity in sentence if entity[0] != 'O']
                        for sentence in doc] for doc in data_tagged]
    return answer_entities


def normalize(text, morph):
    entities_normalized = []
    for doc in text:
        entities_sentence = []
        for sentence in doc:
            entities = []
            for entity in sentence:
                word = entity[1]
                word_info = morph.parse(word)[0]
                word_norm = word_info.normal_form
                entities.append((entity[0], word_norm))
            entities_sentence.append(entities)
        entities_normalized.append(entities_sentence)
    return entities_normalized


def unite_BIO_tags(text):
    entities_phrase = []   
    for doc in text:      
        entities_sentence = []
        for sentence in doc:
            entities = []
            word = -1
            for entity in sentence:
                if 'B-' in entity[0]:
                    if word != -1:
                        entities.append((word, tag))
                    # start tag
                    word = str(entity[1])
                    tag = entity[0][4:]
                else:
                    # end tag
                    if word != -1:
                        word += ' ' + str(entity[1])
                    else:
                        word = str(entity[1])
                        tag = entity[0][4:]
            entities.append((word, tag))
            entities_sentence.append(entities)
        entities_phrase.append(entities_sentence)
    return entities_phrase


def create_inverted_index(text):
    inverted_index = {}
    for i, doc in enumerate(text):
        print(i, doc)
        for sentence in doc:
            for entity in sentence:
                tag = entity[1]
                if tag not in inverted_index:
                    inverted_index[tag] = {}

                words = entity[0].split()
                for word in words:
                    if word not in inverted_index[tag]:
                        inverted_index[tag][word] = []
                    inverted_index[tag][word].append(i)

                bigrams = create_n_grams(words)
                for bigram in bigrams:
                    if bigram not in inverted_index[tag]:
                        inverted_index[tag][bigram] = []
                    inverted_index[tag][bigram].append(i)
    return inverted_index


def create_n_grams(words):
    bigrams = []
    for i in range(len(words) - 1):
        bigram = words[i] + ' ' + words[i + 1]
        bigrams.append(bigram)
    return bigrams


def create_index():
    morph = pymorphy2.MorphAnalyzer()
    data_tagged, data_splitted, links = crawl_news()

    # remove 'O' words
    data_entities = remove_unannotated_words(data_tagged)
    # lemmatization of words
    data_normalized = normalize(data_entities, morph)
    # remove intermediate annotation BIO
    data = unite_BIO_tags(data_normalized)

    # create inverted index
    inverted_ix = create_inverted_index(data)
    return inverted_ix, data_splitted, morph, links
