import torch
import torch.nn as nn
import torch.nn.functional as F
import feedparser

from model import Event_tagger
from constants import MODEL_PATH


def to_ix(word, word_to_ix):
    return word_to_ix[word] if word in word_to_ix else word_to_ix[
        '`']  # ` - being pad word


def prepare_data():
    NewsFeed = feedparser.parse("https://news.yandex.ru/politics.rss")
    data = []
    links = []
    for entry in NewsFeed.entries:
        data.append(entry['summary'].replace('&quot;',
                                             '').replace('»', '').replace('«', ''))
        links.append(entry['link'])
    return data, links


def tokenize_data(data, word_to_ix):
    data_splitted = []
    data_ix = []
    for text in data:
        data_splitted.append([a.split() for a in text.split(".")][:-1])
        last = data_splitted[-1]
        text_ix = []
        for sent in last:
            text_ix.append(torch.tensor([to_ix(word, word_to_ix) for word in sent], dtype=torch.long))
        data_ix.append(text_ix)
    return data_splitted, data_ix


def entity_extraction(data_ix, model):
    all_tags = []
    for word_indices in data_ix:
        predicted_tags = []
        for i in range(len(word_indices)):
            tag_scores = model(torch.stack([word_indices[i]]))
            out_probs = torch.squeeze(tag_scores)
            tmp = []
            for j, pset in enumerate(out_probs):
                if j >= len(word_indices[i]):
                    break
                _, predicted_ix = torch.max(pset, 0)
                tmp.append(predicted_ix.item())
            predicted_tags.append(tmp)
        all_tags.append(predicted_tags)
    return all_tags


def transform_result(tags, data_splitted, ix_to_tag):
    ans_dict = []
    for text in range(len(tags)):
        ans_text = []
        for sent in range(len(tags[text])):
            ans_sent = []
            for word in range(len(tags[text][sent])): 
                ans_sent.append((ix_to_tag[tags[text][sent][word]],
                             data_splitted[text][sent][word]))
            ans_text.append(ans_sent)
        ans_dict.append(ans_text)
    return ans_dict


def crawl_news():
    model = torch.load(MODEL_PATH)

    word_to_ix = model.word_to_ix
    ix_to_tag = model.ix_to_tag

    # clean data - [doc, doc]
    data, links = prepare_data()
    data_splitted, data_ix = tokenize_data(data, word_to_ix)
    
    # extract entities
    tags = entity_extraction(data_ix, model)
    ans_dict = transform_result(tags, data_splitted, ix_to_tag)
    return ans_dict, data_splitted, links
