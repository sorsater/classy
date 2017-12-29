
import nltk
from nltk import NaiveBayesClassifier
from collections import Counter
from w8m8 import progressbar

class Classy(NaiveBayesClassifier):
    def __init__(self, corpus, genres, freq_thresh=10):
        print('Classifier with threshold value: "{}"'.format(freq_thresh))
        # List of lyrics with their correct tag (genre)
        self.corpus = corpus

        # List of all genres
        self.genres = genres

        self.freq_thresh = freq_thresh

        # All words with their frequency
        self.all_unique_words = Counter([word.lower() for song in self.corpus for word in song['lyric']])

        # Words with a higher frequency
        self.common_words = [word for word, value in self.all_unique_words.items() if value > self.freq_thresh]

        self.feature_corpus = []
        print()

    def get_features(self, document, n):
        words_in_document = set(document)
        features = {}
        for word in self.common_words:
            features['word({})'.format(word)] = (word in words_in_document)
        return features

    def extract_features(self):
        '''
        For each song, extract all features and add to "feature_corpus"
        '''
        print('Extracting features')
        for idx, song in enumerate(self.corpus):
            progressbar((idx+1)/len(self.corpus))
            self.feature_corpus.append([
                self.get_features(song['lyric'], song['n']),
                #self.get_features(song['lyric']),
                song['genre'],
            ])
        print()
        print()

    def show_features(self, n):
        self.model.show_most_informative_features(n)

    def split_train_test(self, percent):
        print('Splitting in train and test: {:.0f}:{:.0f}'.format(percent, (100-percent)))
        len_train = int(percent/100*len(self.feature_corpus))
        self.train_set = self.feature_corpus[:len_train]
        self.test_set = self.feature_corpus[len_train:]

        print('Total songs: {}'.format(len(self.feature_corpus)))
        print('Train: {}, test: {}'.format(len(self.train_set), len(self.test_set)))

    def train(self):
        print(self.genres)
        print('Training')
        self.model = nltk.NaiveBayesClassifier.train(self.train_set)
        print('Training done')
        print()

    def test_all(self):
        print('Testing')
        self.accuracy = nltk.classify.accuracy(self.model, self.test_set)
        print('Testing done')
        print()
        print('Accuracy of {} songs: {:.2f}%'.format(len(self.test_set), 100*self.accuracy))

    def test_documents(self, documents, verbose=False):
        result = []
        print('Testing manually')
        for idx, document in enumerate(documents):
            progressbar((idx+1)/len(documents))
            res = self.model.classify(document[0])
            result.append(res==document[1])
            if verbose:
                print('{}: {} / {} '.format(res == document[1],document[1], res))
        print()
        self.accuracy = sum(result)/len(result)
        true_accuracy = nltk.classify.accuracy(self.model, self.test_set)

        print('Accuracy of {} songs: {:.2f}%, ({:.2f}%)'.format(len(documents), 100*self.accuracy, 100*true_accuracy))
