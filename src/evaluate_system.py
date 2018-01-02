'''
To evaluate the performance.
Run the specified tests and store the result in file 'result_file'
'''

import json
import os
from classify import parse_args, main
from time import strftime

# Toggle to display more information during execution
suppress_output = True

# File where results are stored
result_file = 'result.json'

# It is important to maintain the order of the arguments
# (when looking for previuos tests is matches against the exact match)
# Use full names in the order specified in classify.py
'''
file
--genres
--iterations
--features: (all, baseline, bigram, meta, stopwords, stem)
--uni_thresh
--bi_thresh
--split
--output
--folder_name
--show
'''
tests = [
    #['billboard.json', '--genres', 'pop', 'rap', '--iterations', '3'],
    #['billboard.json', '--genres', 'pop', 'rap', '--iterations', '3', '--features', 'meta'],
    #['billboard.json', '--iterations', '3', '--uni_thresh', '500'],
    #['billboard.json', '--iterations', '3', '--uni_thresh', '500', '--features', 'meta'],
    #['billboard.json', '--iterations', '5', '--uni_thresh', '1'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '2'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '5'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '10'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '20'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '50'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '100'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '250'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '500'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '1000'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '5000'],
    ['billboard.json', '--iterations', '5', '--uni_thresh', '10000'],
    # pop and rap, different unigram thresholds
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '1'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '2'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '5'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '10'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '20'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '50'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '100'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '250'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '500'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '1000'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '5000'],
    #['billboard-all.json', '--genres', 'pop', 'rap', '--iterations', '5', '--uni_thresh', '10000'],
]

def run_tests(result_dict):
    result = []
    diff = []
    for idx, test in enumerate(tests):
        text_to_show = 'TEST NUMBER: {} / {}'.format(idx+1, len(tests))
        print()
        print('########{}########'.format('#' * len(text_to_show)))
        print('####    {}    ####'.format(text_to_show))
        print('########{}########'.format('#' * len(text_to_show)))
        print(test)
        accuracy, elapsed = main(parse_args(test), suppress_output)
        result.append([accuracy, elapsed, test])

        key = '|'.join(test)

        accuracy = '{:.4f}'.format(100*accuracy)
        elapsed = '{:.1f}'.format(elapsed)
        date = strftime('%Y-%m-%d')
        clock = strftime('%H:%M')

        # Test already tried, add to the result
        if key in result_dict:
            result_dict[key]['accuracy'].append(accuracy)
            result_dict[key]['elapsed'].append(elapsed)
            result_dict[key]['date'].append(date)
            result_dict[key]['clock'].append(clock)

        else:
            result_dict[key] = {
                'test': test,
                'date': [date],
                'clock': [clock],
                'file': test[0],
                'features': test[1:],
                'accuracy': [accuracy],
                'elapsed': [elapsed],
            }

        accs = result_dict[key]['accuracy']
        # Different result for same parameters
        if len(set(accs)) > 1:
            diff.append([key, accs])
            print('Different result.')
            for idx, acc in enumerate(accs):
                print(' {}: Acc: {}'.format(idx, acc))

        # Dump data after each run
        json.dump(result_dict, open(result_file, 'w'), indent=4, sort_keys=True)

    return result, diff

def show_result(result):
    for idx, (accuracy, elapsed, test) in enumerate(result):
        print()
        print(' {}'.format(test))
        print('  Accuracy: {:.2f}%, Time: {:.1f} seconds'.format(100 * accuracy, elapsed))

if __name__ == '__main__':
    try:
        result_dict = json.load(open(result_file)) if os.path.exists(result_file) else {}
        result, diff = run_tests(result_dict)
        show_result(result)

        if diff:
            print()
            print('These test are inconsistent')
            for name, accs in diff:
                print()
                print('Name: {}'.format(name))
                print(accs)

    except KeyboardInterrupt:
        print('KEYBOARD INTERRUPT')
