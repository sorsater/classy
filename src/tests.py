test_names = ['example', 'uni', 'meta', 'stopwords', 'words', 'words_limited']
# Structure of a test set
tests_example = [
    # Will be the json filename when storing
    'Small-example',
    # Common arguments for all tests
    ['billboard.json', '--iterations', '3', '--genres', 'pop', 'rap', '--count', '50'],
    # List of all tests, must atleast be one element
    [],
    ['--features', 'stopwords'],
]

tests_uni = [
    'Unigram-threshold-precision',
    ['billboard.json', '--iterations', '5', '--uni_thresh'],
    ['2'],
    ['3'],
    ['4'],
    ['5'],
    ['6'],
    ['7'],
    ['8'],
    ['9'],
    ['10'],
    ['15'],
]

tests_meta = [
    'Meta-feature-pop-electronic',
    ['billboard.json', '--genres', 'pop', 'electronic', '--iterations', '5', '--uni_thresh'],
    ['1'],
    ['1', '--features', 'meta'],
    ['2'],
    ['2', '--features', 'meta'],
    ['5'],
    ['5', '--features', 'meta'],
    ['10'],
    ['10', '--features', 'meta'],
    ['20'],
    ['20', '--features', 'meta'],
    ['50'],
    ['50', '--features', 'meta'],
    ['100'],
    ['100', '--features', 'meta'],
    ['250'],
    ['250', '--features', 'meta'],
    ['500'],
    ['500', '--features', 'meta'],
    ['1000'],
    ['1000', '--features', 'meta'],
]

tests_stopwords = [
    'Stopwords-all-genres',
    ['billboard.json', '--iterations', '5', '--uni_thresh'],
    ['5'],
    ['5', '--features', 'stopwords'],
    ['10'],
    ['10', '--features', 'stopwords'],
    ['20'],
    ['20', '--features', 'stopwords'],
    ['50'],
    ['50', '--features', 'stopwords'],
    ['100'],
    ['100', '--features', 'stopwords'],
    ['250'],
    ['250', '--features', 'stopwords'],
    ['500'],
    ['500', '--features', 'stopwords'],
    ['1000'],
    ['1000', '--features', 'stopwords'],
]

tests_words = [
    'Stopwords_and_tokenizations',
    ['billboard.json', '--iterations', '5'],
    [],
    ['--features', 'tokenize'],
    ['--features', 'stopwords'],
    ['--features', 'stem'],

    ['--features', 'tokenize', 'stopwords'],
    ['--features', 'tokenize', 'stem'],
    ['--features', 'stopwords', 'stem'],

    ['--features', 'tokenize', 'stopwords', 'stem'],
]

tests_words_limited = [
    'Stopwords_and_tokenizations_limited_words',
    ['billboard.json', '--iterations', '5', '--max_words', '100'],
    [],
    ['--features', 'tokenize'],
    ['--features', 'stopwords'],
    ['--features', 'tokenize', 'stopwords'],
]