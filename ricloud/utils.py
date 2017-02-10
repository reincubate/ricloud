from __future__ import print_function

import os
import sys
import time
import json
import datetime
import requests
from multiprocessing.pool import ThreadPool

from clint.textui import prompt, puts, colored, indent

from .conf import settings, OUTPUT_DIR
from .samples import get_samples


def get_or_create_filepath(filename, directory=''):
    absolute_dir = os.path.join(OUTPUT_DIR, directory)

    if not os.path.exists(absolute_dir):
        os.makedirs(absolute_dir)

    return os.path.join(absolute_dir, filename)


def utf8(message):
    if isinstance(message, unicode):
        message = message.encode('utf-8')
    return message


def print_message(message, colour='white'):
    """Prints `message` to the console in the specified `colour`.
    Makes sure special characters are encoded properly (for example, emoticons
    in device names).
    """
    puts(getattr(colored, colour)(utf8(message)))


def info_message(message):
    """Prints info type messages in green."""
    print_message(message, colour='green')


def prompt_message(message):
    """Prints prompt type messages in blue."""
    print_message('\n' + message, colour='blue')


def pending_message(message):
    """Prints pending type messages in yellow."""
    print_message('\n' + message, colour='yellow')


def error_message(message):
    """Prints error type messages in red."""
    print_message('\n' + message, colour='red')


def error_message_and_exit(message, error_result):
    """Prints error messages in blue, the failed task result and quits."""
    error_message(message)
    puts(json.dumps(error_result, indent=2))
    sys.exit(1)


def print_prompt_values(values, message=None, sub_attr=None):
    """Prints prompt title and choices with a bit of formatting."""
    if message:
        prompt_message(message)

    for index, entry in enumerate(values):
        if sub_attr:
            line = '{:2d}: {}'.format(index, getattr(utf8(entry), sub_attr))
        else:
            line = '{:2d}: {}'.format(index, utf8(entry))

        with indent(3):
            print_message(line)


def prompt_for_input(message, input_type=None):
    """Prints prompt instruction and does basic input parsing."""
    while True:
        output = prompt.query(message)

        if input_type:
            try:
                output = input_type(output)
            except ValueError:
                error_message('Invalid input type')
                continue

        break

    return output


def prompt_for_choice(values, message, input_type=int, output_type=None):
    """Prints prompt with a list of choices to choose from."""
    output = None
    while not output:
        index = prompt_for_input(message, input_type=input_type)

        try:
            output = utf8(values[index])
        except IndexError:
            error_message('Selection out of range')
            continue

    if output_type:
        output = output_type(output)

    return output


def select_item(items, prompt_instruction, prompt_title, sub_attr=None, output_type=None):
    print_prompt_values(items, prompt_title, sub_attr)

    return prompt_for_choice(items, prompt_instruction, output_type=output_type)


def select_service(response):
    return select_item(
        response.services,
        'Please select a service index:',
        'Authorized services:',
        output_type=str
    )


def select_samples(response, service_name, payload):
    samples = get_samples(service_name)

    selected_sample = select_item(
        samples,
        'Please select a sample application index:',
        'Available sample applications:',
        sub_attr='display_name'
    )

    return selected_sample(response, payload)


def profile(timer_text=''):
    def inner(func):
        def wraps(*args, **kwargs):
            timer_start = time.time()
            ret = func(*args, **kwargs)
            timer_end = time.time()
            if settings.getboolean('logging', 'time_profile'):
                delta = timer_end - timer_start
                message = "{text} {delta:.2f}s".format(text=timer_text, delta=delta)
                puts(colored.magenta(message))
            return ret
        return wraps
    return inner


def append_profile_info(string, info):
    return string + colored.magenta(" completed in {0:.2f}s".format(info))


def _get_num_threads():
    num_threads = int(settings.get('performance', 'object_store_greenlets'))
    if not num_threads:
        num_threads = 1
    return num_threads


def threaded_get(request_instance):
    return requests.request(
        method='get',
        url=request_instance[0],
        headers=request_instance[1],
    )


def concurrent_get(request_list):
    max_threads = _get_num_threads()
    number_requests = len(request_list)
    if number_requests > 0:
        pool = ThreadPool(number_requests) if number_requests <= max_threads else ThreadPool(max_threads)
        results = pool.map(threaded_get, request_list)
        pool.close()
        pool.join()
        return results
    else:
        return []


class LogFile():

    def __init__(self, log_file, error_file=None):
        self.log_file = log_file

        if not os.path.exists(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file))
        open(self.log_file, 'w').close()
        if not error_file:
            self.error_file = self.log_file
        else:
            self.error_file = error_file
            open(self.error_file, 'w').close()

    def write(self, message, *args):
        # General logging
        with open(self.log_file, 'ab+') as f:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message, *args, file=f)

    def error(self, message, *args):
        # Error Logging
        with open(self.error_file, 'ab+') as f:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message, *args, file=f)
