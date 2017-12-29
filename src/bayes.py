
import nltk
from nltk import NaiveBayesClassifier
from collections import Counter
from w8m8 import progressbar

class Classy(NaiveBayesClassifier):
    def __init__(self, corpus, genres, args):
        '''
        Initializer for the class.
        Input arguments is:
            'corpus': A list of all songs together with their genre. Shuffled.
            'genres': A list of the genres to be considered
            'args: Arguments from the argumentparser.
        '''
        # List of lyrics with their correct genre
        self.corpus = corpus

        # List of all genres
        self.genres = genres

        # The threshold for the word frequencies
        self.freq_thresh = args.thresh

        # Percent to be train, rest is test
        self.percent = args.split / 100

    def get_features_for_document(self, document, n):
        '''
        The features extracted are defined here.
        '''
        words_in_document = set(document)
        features = {}
        # Occurency of a word or not in a song
        for word in self.common_words:
            features['word({})'.format(word)] = (word in words_in_document)
        return features

    def extract_features(self, data_set, name):
        '''
        For each song in the dataset, extract all features.
        '''
        features = []
        for idx, song in enumerate(data_set):
            progressbar((idx+1)/len(data_set), 'Features for: "{}" {}/{}'.format(name, idx+1, len(data_set)))
            features.append([
                self.get_features_for_document(song['lyric'], song['n']),
                song['genre'],
            ])
        print()
        return features

    def split_train_test(self):
        len_train = int(self.percent * len(self.corpus))
        self.train_raw = self.corpus[:len_train]
        self.test_raw = self.corpus[len_train:]

        # All words with their frequency in the train set.
        # Avoid to look at test data (no cheating)
        self.unique_words = Counter([word.lower() for song in self.train_raw for word in song['lyric']])

        # Words with a higher frequency than 'freq_thresh' is stored in 'train_common_words'
        self.common_words = set([word for word, value in self.unique_words.items() if value > self.freq_thresh])

        # Create train and test set
        self.train_set = self.extract_features(self.train_raw, 'train')
        self.test_set = self.extract_features(self.test_raw, 'test')

    def show_features(self, n):
        '''
        Show the n most important features
        '''
        self.model.show_most_informative_features(n)

    def train(self):
        '''
        Train the model by using the built in trainer.
        '''
        print('Training', end='\r')
        self.model = nltk.NaiveBayesClassifier.train(self.train_set)

        # TODO: might uncomment print, read description
        # I have locally added a progressbar in the nltk training method.
        # You probably need to uncomment the print if you don't do the same
        # print('Training: done')

    def test_all(self):
        '''
        Use nltk to classify all documents in 'test_set'.
        Replaced by 'test' below.
        '''
        self.accuracy = nltk.classify.accuracy(self.model, self.test_set)
        print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        print()

    def test(self):
        '''
        Evaluate all documents and calculate accuracy for them.
        Is used instead of built in because possible to show progress.
        '''
        result = []
        for idx, document in enumerate(self.test_set):
            progressbar((idx+1)/len(self.test_set), 'Testing {}/{}'.format(idx+1,len(self.test_set)))
            res = self.model.classify(document[0])
            result.append(res==document[1])
        print()
        self.accuracy = sum(result)/len(result)

        # Validate the testing by using built in "test"
        #true_accuracy = nltk.classify.accuracy(self.model, self.test_set)
        #print('Accuracy: {:.2f}%, ({:.2f}%)'.format(100*self.accuracy, 100*true_accuracy))

        print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        print()
