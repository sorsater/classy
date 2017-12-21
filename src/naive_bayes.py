
import nltk
from nltk import NaiveBayesClassifier
import pickle
from collections import Counter

word_freq_threshold = 40
#word_freq_threshold = 2
class Classy(NaiveBayesClassifier):
    def __init__(self, corpus, genres):
        # List of lyrics with their correct tag (genre)
        self.corpus = corpus

        # List of all genres
        self.genres = genres

        # All words with their frequency
        self.all_unique_words = Counter([word.lower() for song in self.corpus for word in song['lyric']])

        # Words with a higher frequency
        self.common_words = [word for word, value in self.all_unique_words.items() if value > word_freq_threshold]
       
    def get_features(self, document):
        words_in_document = set(document)
        features = {}
        for word in self.common_words:
            features['word({})'.format(word)] = (word in words_in_document)
        return features

    def extract_features(self):
        self.feature_corpus = []
        for song in self.corpus:
            # TODO, switch to this form instead, to improve testing
            # self.feature_corpus.append({
            #     'name': song['name'],
            #     'genre': song['genre'],
            #     'features': self.get_features(song['lyric'])
            # })

            self.feature_corpus.append([
                self.get_features(song['lyric']),
                song['genre'],
            ])

    def split_train_test(self, percent=0.7):
        print('Splitting in train and test: {} {}'.format(100*percent, 100*(1-percent)))
        len_train = int(0.7*len(self.feature_corpus))
        self.train_set = self.feature_corpus[:len_train]
        self.test_set = self.feature_corpus[len_train:]

        print('Total songs: {}'.format(len(self.feature_corpus)))
        print('Train: {}, test: {}'.format(len(self.train_set), len(self.test_set)))
        
    def train(self):
        print('Training')
        self.model = nltk.NaiveBayesClassifier.train(self.train_set)
        print('Training done')
    
    def test_all(self):
        print('Testing')
        self.accuracy = nltk.classify.accuracy(self.model, self.test_set)
        print('Testing done')
        print('Accuracy of {} songs: {:.2f}%'.format(len(self.test_set), 100*self.accuracy))


    def test_documents(self, documents, verbose=False):
        result = []
        for document in documents:
            res = self.model.classify(document[0])
            result.append(res==document[1])
            if verbose:
                print('{}: {} / {} '.format(res == document[1],document[1], res))

        accuracy = nltk.classify.accuracy(self.model, documents)
        print('Accuracy of {} songs: {:.2f}%, ({:.2f}%)'.format(len(documents), 100*sum(result)/len(result), 100*accuracy))

    def save_classifier(self):
        pass