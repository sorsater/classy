'''
To evaluate the performance.
Run the specified tests and store the result in file 'args.result_file' and a separate result file

When adding a test, follow the naming standard and add it to the 'choices' in the argument parser
'''

import json
import os
from classify import parse_args, main
from time import strftime
from copy import deepcopy
import time
import argparse
import tests
import datetime

def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('test', type=str, nargs='*', choices=list(tests.tests.keys()), help='Name of test to run.')
    parser.add_argument('--result_file', type=str, default='result.json', help='Name of result json file')
    parser.add_argument('--folder_name', type=str, default='result', help='Name of folder to store result')
    parser.add_argument('--output', action='store_false', help='Suppress output from "classify.py"')

    return parser.parse_args()

def run_tests(result_dict, tests, t_0, args):
    test_name, test_base, tests = tests[0], tests[1], tests[2:]
    output_name = '{}.json'.format(test_name.replace(' ', '-'))
    output_path = os.path.join(args.folder_name, output_name)
    print('Saving to file: "{}"'.format(output_name))
    print('Name of tests: "{}"'.format(test_name))
    print('Number of tests: {}'.format(len(tests)))
    print()
    print('Parameters are: \n {}'.format(test_base))
    for test in tests:
        print('   {}'.format(test))
    result = []
    diff = []
    current_result = {
        'best': {
            'accuracy': '0',
            'name': 'init',
            'full': 'init',
        }
    }

    # File with just the current tests, overwrite old file
    json.dump(current_result, open(output_path, 'w'), indent=4, sort_keys=True)
    for idx, test in enumerate(tests):
        text_to_show = 'TEST NUMBER: {} / {}'.format(idx+1, len(tests))
        print()
        print('########{}########'.format('#' * len(text_to_show)))
        print('####    {}    ####'.format(text_to_show))
        print('########{}########'.format('#' * len(text_to_show)))
        print(test_base + test)
        f_accuracy, stats, elapsed = main(parse_args(test_base + test), args.output)

        result.append([f_accuracy, elapsed, test])

        key = '|'.join(test_base + test)


        accuracy = '{:.4f}'.format(100*f_accuracy)
        elapsed = '{:.1f}'.format(elapsed)
        date = strftime('%Y-%m-%d')
        clock = strftime('%H:%M')

        if 100 * f_accuracy > float(current_result['best']['accuracy']):
            current_result['best'] = {
                'accuracy': accuracy,
                'test': test,
                'name': key,
            }

        # Test already tried, add to the result
        if key in result_dict:
            result_dict[key]['accuracy'].append(accuracy)
            result_dict[key]['elapsed'].append(elapsed)
            result_dict[key]['date'].append(date)
            result_dict[key]['clock'].append(clock)

        else:
            result_dict[key] = {
                'test': test,
                'name': test_name,
                'base': test_base,
                'full': test_base + test,
                'date': [date],
                'clock': [clock],
                'accuracy': [accuracy],
                'elapsed': [elapsed],
            }
        current_result[key] = {
            'test': test,
            'name': test_name,
            'base': test_base,
            'full': test_base + test,
            'date': [date],
            'clock': [clock],
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
        # Big file with all results
        json.dump(result_dict, open(args.result_path, 'w'), indent=4, sort_keys=True)

        # File with just the current tests, overwrite old file
        json.dump(current_result, open(output_path, 'w'), indent=4, sort_keys=True)

        print()
        print('Total time: {:.1f} seconds'.format(time.time()-t_0))


    return result, diff

def show_result(result, tests):
    best = (result[0][0], result[0][2])
    print('Parameters are: \n {}'.format(tests[1]))
    for idx, (accuracy, elapsed, test) in enumerate(result):
        print()
        print('   {}'.format(test))
        print('   Accuracy: {:.3f}%, Time: {:.1f} seconds'.format(100 * accuracy, elapsed))

        best = (accuracy, test) if accuracy > best[0] else best

    print()
    print('Best iteration: {}'.format(best[1]))
    print('  Accuracy: {:.3f}%'.format(100*best[0]))

    print()
    print('Saving to file: "{}.json"'.format(tests[0].replace(' ', '-')))

    return best

if __name__ == '__main__':
    try:
        t_0 = time.time()
        args = _parse_args()

        all_results = {}

        if not os.path.exists(args.folder_name):
            os.makedirs(args.folder_name)

        args.result_path = os.path.join(args.folder_name, args.result_file)
        print('Total number of big tests: {}'.format(len(args.test)))
        for idx, test_name in enumerate(args.test):
            big_text_to_show = 'BIG TEST: {} / {}'.format(idx+1, len(args.test))
            print()
            print('============={}============='.format('=' * len(big_text_to_show)))
            print('=========    {}    ========='.format(big_text_to_show))
            print('============={}============='.format('=' * len(big_text_to_show)))
            print(test_name)

            test_list = deepcopy(eval('{}'.format(tests.tests[test_name])))

            result_dict = json.load(open(args.result_path)) if os.path.exists(args.result_path) else {}
            result, diff = run_tests(result_dict, test_list, t_0, args)
            best_iter = show_result(result, test_list)

            all_results[test_name] = [test_list[0], best_iter]

        print()
        print('Total time: {:.1f} seconds'.format(time.time()-t_0))

        print('============================================')
        for test_name, (file_name, best_iter) in all_results.items():
            print('============================================')
            print('Name: ', test_name)
            print('Saved to: "{}.json"'.format(file_name.replace(' ', '-')))
            print('Best iteration: {}'.format(best_iter[1]))
            print('  Accuracy: {:.3f}%'.format(100*best_iter[0]))

        print('============================================')

        print('Total time: "{}"'.format(datetime.timedelta(seconds=int(time.time()-t_0))))

    except KeyboardInterrupt:
        print('KEYBOARD INTERRUPT')
