import torch
import torch.nn as nn
import torch.nn.functional as F

class Event_tagger(nn.Module):
    def __init__(self,
                 word_to_ix,
                 tag_to_ix,
                 ix_to_tag,
                 weights_matrix,
                 batch_size,
                 word_embed_dim=300,
                 bidirectional=True,
                 gru_num_layers=2,
                 dropout=.5):
        '''
            initialize models
            batch_size      - size of batches for traininig
            word_embed_dim  - dimension of word embeddings
            gru_num_layers - number of gru layers
            dropout         - rate for dropout layer
        '''
        super(Event_tagger, self).__init__()

        # dictionaries
        self.word_to_ix = word_to_ix
        self.tag_to_ix = tag_to_ix
        self.ix_to_tag = ix_to_tag

        # parameters
        self.batch_size = batch_size
        self.word_embed_dim = word_embed_dim
        self.gru_hidden_dim = self.word_embed_dim
        self.gru_num_layers = gru_num_layers
        self.dropout = dropout

        self.num_directions = 2 if bidirectional else 1

        self.word_embeds, num_embeds = create_embed_layer(weights_matrix, True)

        self.gru = nn.GRU(self.word_embed_dim,
                          self.gru_hidden_dim,
                          bidirectional=bidirectional,
                          num_layers=self.gru_num_layers,
                          batch_first=True)
        self.dense = nn.Linear(self.gru_hidden_dim * self.num_directions,
                               len(self.tag_to_ix))

    def forward(self, words_batch):
        '''
            words_batch - contains indices of words in current batch with shape
                        (batch_size, num_words_in_sentence)

            creates word level word embeddings from words_batch

            runs Bi-directional gru over input word representation to get
            final word representation which is fed to linear layer and softmax
            activation function to generate probability distribution for event
            tag set
        '''
        # create word-level word embeddings
        word_embed_word_level = words_batch.view(-1)
        word_embed_word_level = self.word_embeds(word_embed_word_level)
        batch_sent_embed = word_embed_word_level.view(
            words_batch.shape[0], -1, word_embed_word_level.shape[-1])

        # create final word representation from gru
        gru_out, _ = self.gru(batch_sent_embed)

        # get probabilities for event tag
        tag_space = self.dense(gru_out)
        tag_scores = F.log_softmax(tag_space, dim=2)
        return tag_scores
