'''
The bayes classifier.
Uses the nltk NaiveBayesClassifier.
Takes list of songs with their genre, list of all genres and som settings arguments
'''
import nltk
from nltk import NaiveBayesClassifier, word_tokenize
from nltk.metrics.scores import precision, recall, f_measure
from nltk.stem.snowball import SnowballStemmer
from collections import Counter, defaultdict
from w8m8 import progressbar
import operator
import string

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

        self.feat_baseline = 'baseline' in self.features
        self.feat_bi_gram = 'bigram' in self.features
        self.feat_tri_gram = 'trigram' in self.features
        self.feat_four_gram = 'fourgram' in self.features
        self.feat_five_gram = 'fivegram' in self.features
        self.feat_n_gram = any(n_gram in self.features for n_gram in ['bigram', 'trigram', 'fourgram', 'fivegram'])

        self.feat_meta = 'meta' in self.features
        self.feat_stopwords = 'stopwords' in self.features
        self.feat_tokenize = 'tokenize' in self.features
        self.feat_stem = 'stem' in self.features

        # The threshold for the n-grams
        self.num_features_uni = args.uni_thresh
        self.num_features_bi = args.bi_thresh
        self.num_features_tri = args.tri_thresh
        self.num_features_four = args.tri_thresh
        self.num_features_five = args.tri_thresh

        # Percent to be train, rest is test
        self.percent = args.split / 100

        # Extract stopwords
        self.stopwords = nltk.corpus.stopwords.words('english') + list(string.punctuation) if self.feat_stopwords else set()

        self.stemmer = SnowballStemmer('english')

        self.num_chars = int(args.num_chars)
        self.num_words = int(args.num_words)
        self.num_unique = int(args.num_unique)

        self.show_stats = args.stats

        self.num_prints = 0

    def _print(self, msg='', end='\n'):
        '''
        Used to keep track of number of prints
        '''
        print(msg, end=end)
        self.num_prints += 1

    def features_grams(self, lyrics):
        uni_grams = []
        bi_grams = set()
        tri_grams = set()
        four_grams = set()
        five_grams = set()
        meta_data = []
        no_meta_lyrics = ""
        for line in lyrics.split('\n'):
            line = line.rstrip()
            if len(line) <= 1:
                continue
            if line[0] + line[-1] == '[]':
                meta_data.append(line[1:-1].lower())
                continue
            no_meta_lyrics += line + ' '
            words = line.split(' ')
            for idx, word in enumerate(words):
                word = word.rstrip()
                # Ignore double space
                if len(word) > 0:
                    uni_grams.append(word)
                    # Speed up by not checking further
                    if not self.feat_n_gram:
                        continue
                    if idx >= 1:
                        bi_grams.add('|'.join(words[idx-1:idx+1]))
                    if idx >= 2:
                        tri_grams.add('|'.join(words[idx-2:idx+1]))
                    if idx >= 3:
                        four_grams.add('|'.join(words[idx-3:idx+1]))
                    if idx >= 4:
                        five_grams.add('|'.join(words[idx-4:idx+1]))

        if self.feat_tokenize:
            words_tokenize = word_tokenize(no_meta_lyrics)
        else:
            words_tokenize = uni_grams

        if self.feat_stem:
            words_stem = [self.stemmer.stem(word) for word in words_tokenize]
        else:
            words_stem = words_tokenize

        return set(words_stem), bi_grams, tri_grams, four_grams, five_grams, meta_data

    def features_meta(self, meta_data):
        meta_members = {
            'verse': 0, 'chorus': 0, 'intro': 0, 'outro': 0,
            'break':0, 'bridge': 0, 'skit': 0, 'hook': 0,
            'drop': 0, 'interlude': 0, 'breakdown': 0,
            'pre-chorus': 0,
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

        uni_grams, bi_grams, tri_grams, four_grams, five_grams, meta_data = self.features_grams(song['lyrics'])

        features = {}
        # Occurency of a unigram or not in a song
        for uni_gram in self.common_uni_grams:
            features['uni({})'.format(uni_gram)] = (uni_gram in uni_grams)

        # Occurency of a bigram or not in a song
        if self.feat_bi_gram:
            for bi_gram in self.common_bi_grams:
                features['bi({})'.format(bi_gram)] = (bi_gram in bi_grams)

        # Occurency of a trigram or not in a song
        if self.feat_tri_gram:
            for tri_gram in self.common_tri_grams:
                features['tri({})'.format(tri_gram)] = (tri_gram in tri_grams)

        # Occurency of a four-gram or not in a song
        if self.feat_four_gram:
            #print('JJJJJ?')
            #input()
            for four_gram in self.common_four_grams:
                features['four({})'.format(four_gram)] = (four_gram in four_grams)

        # Occurency of a five-gram or not in a song
        if self.feat_five_gram:
            for five_gram in self.common_five_grams:
                features['five({})'.format(five_gram)] = (five_gram in five_grams)

        # Types of metadata in lyrics. Count all of them to keep tack of how song is structured.
        if self.feat_meta:
            for item, cnt in self.features_meta(meta_data).items():
                features[item] = cnt

        # Considers number of characters, number of words and number of unique words
        # If the values are provided that number is the threshold value
        tokenized_lyrics = nltk.wordpunct_tokenize(song['lyrics'])

        _chars = len(song['lyrics'])
        _words = len(tokenized_lyrics)
        _unique = len(set(tokenized_lyrics))

        if self.num_chars > 0:
            features['chars({})'.format(self.num_chars)] = (_chars <= self.num_chars)

        if self.num_words > 0:
            features['words({})'.format(self.num_words)] = (_words <= self.num_words)

        if self.num_unique > 0:
            features['unique({})'.format(self.num_unique)] = (_unique <= self.num_unique)

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
        self._print()
        return names, features

    def extract_data_training(self):
        # All words with their frequency in the train set.
        # Avoid to look at test data (no cheating)
        uni_grams = []
        bi_grams = []
        tri_grams = []
        four_grams = []
        five_grams = []
        no_meta_lyrics = ''
        for idx, song in enumerate(self.train_raw):
            for line in song['lyrics'].split('\n'):
                if len(line) <= 1:
                    continue
                line = line.rstrip()
                # Exist metadata about structure of song.
                # This data can contain name of artist (which is cheating to train on)
                if line[0] + line[-1] == '[]':
                    continue
                no_meta_lyrics += line + ' '

                words = line.split(' ')
                for idx, word in enumerate(words):
                    word = word.rstrip()
                    # Ignore double space
                    if len(word) >= 1:
                        uni_grams.append(word)
                        # Speed up by not checking further
                        if not self.feat_n_gram:
                            continue
                        if idx >= 1:
                            bi_grams.append('|'.join(words[idx-1:idx+1]))
                        if idx >= 2:
                            tri_grams.append('|'.join(words[idx-2:idx+1]))
                        if idx >= 3:
                            four_grams.append('|'.join(words[idx-3:idx+1]))
                        if idx >= 4:
                            five_grams.append('|'.join(words[idx-4:idx+1]))

        return uni_grams, bi_grams, tri_grams, four_grams, five_grams, no_meta_lyrics

    def split_train_test(self):
        self._print('Preprocessing data')
        len_train = int(self.percent * len(self.corpus))
        self.train_raw = self.corpus[:len_train]
        self.test_raw = self.corpus[len_train:]

        uni_grams, bi_grams, tri_grams, four_grams, five_grams, no_meta_lyrics = self.extract_data_training()

        if self.feat_tokenize:
            words_tokenize = word_tokenize(no_meta_lyrics)
        else:
            words_tokenize = uni_grams

        if self.feat_stem:
            words_stem = [self.stemmer.stem(word) for word in words_tokenize]
        else:
            words_stem = words_tokenize

        unique_uni_grams = Counter(words_stem)
        unique_bi_grams = Counter(bi_grams)
        unique_tri_grams = Counter(tri_grams)
        unique_four_grams = Counter(four_grams)
        unique_five_grams = Counter(five_grams)

        # unique_unigrams is dict with (word: count). Is sorted by count and adds features until the number of features are fulfilled
        # Ignores stopwords.
        self.common_uni_grams = set()
        for word, value in sorted(unique_uni_grams.items(), key=operator.itemgetter(1), reverse=True):
            if value == 1:
                continue
            if len(self.common_uni_grams) >= self.num_features_uni:
                break
            if (self.feat_stopwords) and (word.lower() in self.stopwords):
                continue
            self.common_uni_grams.add(word)

        # Bigrams
        self.common_bi_grams = set()
        for word, value in sorted(unique_bi_grams.items(), key=operator.itemgetter(1), reverse=True):
            if value == 1:
                continue
            if len(self.common_bi_grams) >= self.num_features_bi:
                break
            self.common_bi_grams.add(word)

        # Trigrams
        self.common_tri_grams = set()
        for word, value in sorted(unique_tri_grams.items(), key=operator.itemgetter(1), reverse=True):
            if value == 1:
                continue
            if len(self.common_tri_grams) >= self.num_features_tri:
                break
            self.common_tri_grams.add(word)

        # Four-grams
        self.common_four_grams = set()
        for word, value in sorted(unique_four_grams.items(), key=operator.itemgetter(1), reverse=True):
            if value == 1:
                continue
            if len(self.common_four_grams) >= self.num_features_four:
                break
            self.common_four_grams.add(word)

        # Five-grams
        self.common_five_grams = set()
        for word, value in sorted(unique_five_grams.items(), key=operator.itemgetter(1), reverse=True):
            if value == 1:
                continue
            if len(self.common_five_grams) >= self.num_features_five:
                break
            self.common_five_grams.add(word)

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

        I have locally added a progressbar in the nltk training method.
        '''
        self._print('Training', end='\r')
        self.model = nltk.NaiveBayesClassifier.train(self.train_set)

    def test_old(self):
        '''
        Use nltk to classify all documents in 'test_set'.
        Replaced by 'test' below.
        '''
        self.accuracy = nltk.classify.accuracy(self.model, self.test_set)
        self._print('Testing')
        self._print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        self._print()

    def test(self):
        '''
        Evaluate all documents and calculate accuracy for them.
        Is used instead of built in because possible to show progress.

        Calculates the precision, recall and f_measure.
        Is shown if the argument 'output' is passed to 'classify.py'
        Isn't saved in the result file.
        '''
        # List with 'True'/'False' if correctly guessed or not
        result = []
        true_set = defaultdict(set)
        pred_set = defaultdict(set)
        for idx, (lyrics_features, true_genre) in enumerate(self.test_set):
            progressbar((idx+1)/len(self.test_set), 'Testing {}/{}'.format(idx+1, len(self.test_set)))
            pred_genre = self.model.classify(lyrics_features)

            true_set[true_genre].add(idx)
            pred_set[pred_genre].add(idx)
            result.append(true_genre == pred_genre)

            # Name of current test song
            #self.test_names[idx]

        self._print()
        self.accuracy = sum(result) / len(result)

        self._print('Accuracy: {:.2f}%'.format(100*self.accuracy))
        self._print()

        self.stats = []
        if self.show_stats:
            for genre in list(true_set.keys()):
                _precision = precision(true_set[genre], pred_set[genre])
                _recall = recall(true_set[genre], pred_set[genre])
                _f_measure = f_measure(true_set[genre], pred_set[genre])
                self.stats.append([genre, _precision, _recall, _f_measure])

                # If some of them is not set (too little data probably)
                if not any(a is None for a in [_precision, _recall, _f_measure]):
                    self._print(genre)
                    self._print(' Precision: {:.2f}%'.format(100*_precision))
                    self._print(' Recall   : {:.2f}%'.format(100*_recall))
                    self._print(' F-measure: {:.2f}%'.format(100*_f_measure))
                    self._print()
