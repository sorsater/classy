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
    def __init__(self, corpus, args):
        '''
        Initializer for the class.
        Input arguments is:
            'corpus': A list of all songs together with their genre. Shuffled.
            'args: Arguments from the argumentparser.
        '''
        # List of lyrics with their correct genre
        self.corpus = corpus

        # Features used in the model
        self.features = args.features

        # The threshold for the gram frequencies
        self.freq_thresh_uni = args.uni_thresh
        self.freq_thresh_bi = args.bi_thresh

        # Percent to be train, rest is test
        self.percent = args.split / 100

    def features_grams(self, lyrics):
        unigrams = set()
        bigrams = set()
        meta_data = []
        for line in lyrics.split('\n'):
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

        return unigrams, bigrams, meta_data

    def features_meta(self, meta_data):
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
        return meta_members

    def get_features_for_song(self, song):
        '''
        The features extracted are defined here.
        '''

        unigrams, bigrams, meta_data = self.features_grams(song['lyrics'])

        features = {}
        # Occurency of a unigram or not in a song
        for unigram in self.common_unigrams:
            features['uni({})'.format(unigram)] = (unigram in unigrams)

        # Occurency of a bigram or not in a song
        if 'bigram' in self.features:
            for bigram in self.common_bigrams:
                features['bi({})'.format(bigram)] = (bigram in bigrams)

        # Types of metadata in lyrics. Count all of them to keep tack of how song is structured.
        if 'meta' in self.features:
            for item, cnt in self.features_meta(meta_data).items():
                features[item] = cnt

        return features

    def extract_features(self, data_set, name):
        '''
        For each song in the dataset, extract all features.
        '''
        features = []
        names = []
        for idx, song in enumerate(data_set):
            progressbar((idx+1)/len(data_set), 'Features {} {}/{}'.format(name, idx+1, len(data_set)))
            features.append([
                self.get_features_for_song(song),
                song['genre'],
            ])
            names.append(song['name'])
        print()
        return names, features

    def split_train_test(self):
        len_train = int(self.percent * len(self.corpus))
        self.train_raw = self.corpus[:len_train]
        self.test_raw = self.corpus[len_train:]

        # All words with their frequency in the train set.
        # Avoid to look at test data (no cheating)
        unigrams = []
        bigrams = []
        for idx, song in enumerate(self.train_raw):
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

        unique_unigrams = Counter(unigrams)
        unique_bigrams = Counter(bigrams)

        # Words with a higher frequency than 'freq_thresh' is stored in 'common_unigrams'
        self.common_unigrams = set([word for word, value in unique_unigrams.items() if value >= self.freq_thresh_uni])
        self.common_bigrams = set([word for word, value in unique_bigrams.items() if value >= self.freq_thresh_bi])

        # Create train and test set
        self.train_names, self.train_set = self.extract_features(self.train_raw, 'train')
        self.test_names, self.test_set = self.extract_features(self.test_raw, 'test')

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

    def test_old(self):
        '''
        Use nltk to classify all documents in 'test_set'.
        Replaced by 'test' below.
        '''
        self.accuracy = nltk.classify.accuracy(self.model, self.test_set)
        print('Testing')
        print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        print()

    def test(self):
        '''
        Evaluate all documents and calculate accuracy for them.
        Is used instead of built in because possible to show progress.
        '''
        # List with 'True'/'False' if correctly guessed or not
        result = []
        for idx, (lyrics_features, true_genre) in enumerate(self.test_set):
            progressbar((idx+1)/len(self.test_set), 'Testing {}/{}'.format(idx+1, len(self.test_set)))

            result.append(true_genre == self.model.classify(lyrics_features))

            # Name of current test song
            #self.test_names[idx]

        print()
        self.accuracy = sum(result) / len(result)

        print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        print()