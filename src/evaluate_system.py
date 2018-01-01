'''
To evaluate the performance.
Run the specified tests
'''

from classify import parse_args, main

# Toggle to display more information during execution
suppress_output = True

tests = [
    ['billboard.json', '--uni_thresh', '1000'],
    ['billboard.json', '--uni_thresh', '1000', '-i', '4'],
    ['billboard.json', '--uni_thresh', '100', '--genres', 'pop', 'rap'],
    ['billboard.json', '--uni_thresh', '100', '--genres', 'pop', 'rap', '--iterations', '20'],
]

results = []
for idx, test in enumerate(tests):
    text_to_show = 'TEST NUMBER: {} / {}'.format(idx+1, len(tests))
    print()
    print('########{}########'.format('#' * len(text_to_show)))
    print('####    {}    ####'.format(text_to_show))
    print('########{}########'.format('#' * len(text_to_show)))
    print(test)
    accuracy, time = main(parse_args(test), suppress_output)
    results.append([accuracy, time, test])

for accuracy, time, test in results:
    print()
    print(' {}'.format(test))
    print('  Accuracy: {:.2f}%, Time: {:.1f} seconds'.format(100 * accuracy, time))
