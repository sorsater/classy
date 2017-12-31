'''
The bayes classifier.
Uses the nltk NaiveBayesClassifier.
Takes list of songs with their genre, list of all genres and som settings arguments
'''
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
        self.freq_thresh_uni = args.thresh
        self.freq_thresh_bi = args.thresh

        # Percent to be train, rest is test
        self.percent = args.split / 100

    def get_features_for_song(self, song):
        '''
        The features extracted are defined here.
        '''
        meta_data = []
        unigrams = set()
        bigrams = set()
        for line in song['lyrics'].split('\n'):
            line = line.rstrip()
            if len(line) <= 1:
                continue
            if line[0] + line[-1] == '[]':
                meta_data.append(line[1:-1].lower())
            #line = line.replace(',', '')
            words = line.split(' ')
            for idx, word in enumerate(words):
                word = word.rstrip()
                # Ignore double space
                if len(word) > 0:
                    unigrams.add(word)
                    if idx > 0:
                        bigrams.add(words[idx - 1] + word)
        features = {}
        # Occurency of a unigram or not in a song
        for word in self.common_unigrams:
            features['uni({})'.format(word)] = (word in unigrams)

        # Occurency of a bigram or not in a song
        #for word in self.common_bigrams:
        #    features['bi({})'.format(word)] = (word in bigrams)

        # Types of metadata in lyrics. Count all of them to keep tack of how song is structured.
        meta_members = {
            'verse': 0, 'chorus': 0, 'intro': 0, 'outro': 0,
            'hook': 0, 'bridge': 0, 'interlude': 0, 'break': 0, 'breakdown': 0,
            'skit': 0,'drop': 0,
        }
        for item in meta_data:
            if 'refrain' in item:
                item = 'chorus'
            for key in meta_members.keys():
                if key in item:
                    meta_members[key] += 1

        for item, cnt in meta_members.items():
            #features[item] = cnt
            pass

        return features

    def extract_features(self, data_set, name):
        '''
        For each song in the dataset, extract all features.
        '''
        features = []
        for idx, song in enumerate(data_set):
            progressbar((idx+1)/len(data_set), 'Features "{}" {}/{}'.format(name, idx+1, len(data_set)))
            features.append([
                self.get_features_for_song(song),
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
        unigrams = []
        bigrams = []
        for song in self.train_raw:
            for line in song['lyrics'].split('\n'):
                if len(line) <= 1:
                    continue
                line = line.rstrip()
                # Exist metadata about structure of song.
                # This data can contain name of artist (which is cheating to train on)
                if line[0] + line[-1] == '[]':
                    continue
                #line = line.replace(',', '')
                words = line.split(' ')
                for idx, word in enumerate(words):
                    word = word.rstrip()
                    # Ignore double space
                    if len(word) >= 1:
                        unigrams.append(word)
                        if idx > 0:
                            bigrams.append(words[idx - 1] + word)

        self.unique_unigrams = Counter(unigrams)
        self.unique_bigrams = Counter(bigrams)

        # Words with a higher frequency than 'freq_thresh' is stored in 'common_unigrams'
        self.common_unigrams = set([word for word, value in self.unique_unigrams.items() if value > self.freq_thresh_uni])
        self.common_bigrams = set([word for word, value in self.unique_bigrams.items() if value > 5])#self.freq_thresh_bi])

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

        # TODO: uncomment print
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
