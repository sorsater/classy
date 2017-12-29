
import nltk
from nltk import NaiveBayesClassifier
from collections import Counter
from w8m8 import progressbar

class Classy(NaiveBayesClassifier):
    def __init__(self, corpus, genres, freq_thresh):
        '''
        Initializer for the class.
        Input arguments is:
            'corpus': A list of all songs together with their genre
            'genres': A list of the genres to be considered
            'freq_thresh: Integer of how many times a word need to be available in corpus to be considered
        '''
        # List of lyrics with their correct tag (genre)
        self.corpus = corpus

        self.num_songs = len(self.corpus)

        # List of all genres
        self.genres = genres

        # The threshold for the word frequencies
        self.freq_thresh = freq_thresh

        # All words with their frequency
        self.all_unique_words = Counter([word.lower() for song in self.corpus for word in song['lyric']])

        # Words with a higher frequency
        self.common_words = [word for word, value in self.all_unique_words.items() if value > self.freq_thresh]

        self.feature_corpus = []

    def get_features(self, document, n):
        '''
        The features extracted are defined here.
        '''
        words_in_document = set(document)
        features = {}
        # Occurency of a word or not in a song
        for word in self.common_words:
            features['word({})'.format(word)] = (word in words_in_document)
        return features

    def extract_features(self):
        '''
        For each song, extract all features and add to "feature_corpus"
        '''
        for idx, song in enumerate(self.corpus):
            progressbar((idx+1)/len(self.corpus), 'Extracting features {}/{}'.format(idx+1, self.num_songs))
            self.feature_corpus.append([
                self.get_features(song['lyric'], song['n']),
                #self.get_features(song['lyric']),
                song['genre'],
            ])
        print()

    def show_features(self, n):
        '''
        Show the n most important features
        '''
        self.model.show_most_informative_features(n)

    def split_train_test(self, percent):
        len_train = int(percent/100*len(self.feature_corpus))
        self.train_set = self.feature_corpus[:len_train]
        self.test_set = self.feature_corpus[len_train:]

    def train(self):
        '''
        Train the model by using the built in trainer.
        '''
        print('Training', end='\r')
        self.model = nltk.NaiveBayesClassifier.train(self.train_set)
        print('Training: done')

    def test_all(self):
        '''
        Use nltk to classify all documents in 'test_set'.
        Replaced by 'test_documents' below.
        '''
        print('Testing', end='\r')
        self.accuracy = nltk.classify.accuracy(self.model, self.test_set)
        print('Testing: done')
        print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        print()

    def test_documents(self, documents):
        '''
        Evaluate all documents and calculate accuracy for them.
        Is used instead of built in because possible to show progress.
        '''
        result = []
        for idx, document in enumerate(documents):
            progressbar((idx+1)/len(documents), 'Testing {}/{}'.format(idx+1,len(documents)))
            res = self.model.classify(document[0])
            result.append(res==document[1])
        print()
        self.accuracy = sum(result)/len(result)

        # Validate the testing by using built in test
        #true_accuracy = nltk.classify.accuracy(self.model, self.test_set)
        #print('Accuracy: {:.2f}%, ({:.2f}%)'.format(100*self.accuracy, 100*true_accuracy))

        print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        print()
