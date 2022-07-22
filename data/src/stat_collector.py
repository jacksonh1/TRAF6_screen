'''
This script allows other Python scripts to easily collect and write statistics
about their runs.

Usage:
>>> import stat_collector as sc

To keep a counter:
>>> sc.counter(1, "my_stat_group", "my_substat")

To keep a count of unique objects:
>>> sc.unique_counter(item, "my_stat_group", "my_unique_stat")

To increment some or all of a list of keys:
>>> sc.apply_counter(range(5), lambda x: 1 if my_value < x else 0, "my_stat_group")

To write the statistics to a directory, where each file name is prefixed by
'my_program':
>>> sc.write("/my/path/to/output/stats", prefix="my_program")
'''
import os

def singleton(cls):
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance

@singleton
class StatCollector(object):

    def __init__(self):
        self.statistics = {}
        self.separator = ','

    def __str__(self):
        return str(self.statistics)

    def get(self, *path):
        '''
        Returns the value of the statistic at the given key path. If there is no
        such key path, returns None.
        '''
        current_item = self.statistics
        for key in path:
            assert type(current_item) is dict, "The key path leads to a premature non-dictionary type: {}".format("->".join(path))

            if key in current_item:
                current_item = current_item[key]
            else:
                return None
        return current_item

    def create(self, item, *path):
        '''
        Puts the given item at the given key path, creating as many dictionaries
        as necessary between the last existing key path and the given one.
        '''
        assert len(path) > 0, "Cannot create a value at root key path"

        current_item = self.statistics
        for key in path[:-1]:
            assert type(current_item) is dict, "The key path leads to a premature non-dictionary type: {}".format("->".join(path))
            if key not in current_item:
                current_item[key] = {}
            current_item = current_item[key]
        current_item[path[-1]] = item

    def set(self, item, *path):
        '''
        Puts the given item at the given key path. Raises an assertion if the
        key path does not already exist.
        '''
        assert len(path) > 0, "Cannot set a value at root key path"

        current_item = self.statistics
        for key in path[:-1]:
            assert type(current_item) is dict, "The key path leads to a premature non-dictionary type: {}".format("->".join(path))
            assert key in current_item, "Non-existent key path: {}".format("->".join(path))
            current_item = current_item[key]
        current_item[path[-1]] = item

    def create_or_set(self, item_function, *path):
        '''
        Creates the given key path if necessary. Calls item_function with the old
        value at the key path (or None if it did not exist), and puts the return
        value at the key path.
        '''
        assert len(path) > 0, "Cannot set a value at root key path"

        current_item = self.statistics
        for key in path[:-1]:
            assert type(current_item) is dict, "The key path leads to a premature non-dictionary type: {}".format("->".join(path))
            if key not in current_item:
                current_item[key] = {}
            current_item = current_item[key]
        if path[-1] in current_item:
            current_item[path[-1]] = item_function(current_item[path[-1]])
        else:
            current_item[path[-1]] = item_function(None)


def counter(amount, *path):
    '''
    Increments the statistic at the given key path by amount.
    '''
    collector = StatCollector()
    collector.create_or_set(lambda old: (old if old is not None else 0) + int(amount), *path)

def apply_counter(child_keys, amount_function, *path):
    '''
    For each key in child_keys, adds the amount given by amount_function to the
    child of the object at path with that key. amount_function should take the
    terminating key as argument, and return an integer.
    '''
    collector = StatCollector()
    for key in child_keys:
        counter(amount_function(key), *(list(path) + [key]))

def _permute_apply_counter(child_key_lists, amount_function, path, prefix=[]):
    if len(child_key_lists) == 1:
        apply_counter([tuple(prefix + [x]) for x in child_key_lists[0]], amount_function, path)
    elif len(child_key_lists) > 1:
        for key in child_key_lists[0]:
            _permute_apply_counter(child_key_lists[1:], amount_function, path, prefix + [key])

def permute_apply_counter(child_key_lists, amount_function, *path):
    '''
    For each permutation of keys k = [a, b, ...] in the list of lists
    child_key_lists, adds the amount given by amount_function to the child of the
    object at path with list key k. amount_function should take this list key
    as argument, and return an integer.
    '''
    _permute_apply_counter(child_key_lists, amount_function, path)

def unique_counter(item, *path):
    '''
    Increments the counter at the given key path if the given item has not been
    seen before by that key path.
    '''
    collector = StatCollector()
    new_set = set([item])
    collector.create_or_set(lambda old: (old | new_set) if old is not None else new_set, *path)

def fraction(amount, total_amount, *path):
    '''
    Increments the fraction at the given key path by adding amount to the
    numerator, and total_amount to the denominator. Both the numerator and the
    denominator values will be written out. The amounts must be integers or booleans.
    '''
    collector = StatCollector()
    old_value = collector.get(*path)
    if old_value is None:
        collector.create([int(amount), int(total_amount)], *path)
    else:
        assert old_value is list and len(old_value) == 2, "Key path {} cannot be used as a fraction with current value {}".format("->".join(path), old_value)
        collector.set([old_value[0] + int(amount), old_value[1] + int(total_amount)], *path)

def _is_iterable(item):
    try:
        _ = iter(item)
    except:
        return False
    else:
        return type(item) is not str

def _format_item(value):
    collector = StatCollector()
    if type(value) is set:
        return str(len(value))
    elif _is_iterable(value):
        return collector.separator.join([str(x) for x in value])
    else:
        return str(value)

def write(out_dir, prefix="", statistics=None):
    '''
    Writes each child of the stat collector's dictionary to its own
    file within out_dir, prefixing each file name with prefix if applicable. For
    instance, if the prefix is "mystats", the files will be named "mystats_key1",
    "mystats_key2", etc. where key1 and key2 are the key paths to your statistics.
    '''
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    collector = StatCollector()
    if statistics is None:
        statistics = collector.statistics
    if any(not _is_iterable(x) for x in statistics.values()):
        # Write this dictionary to file
        with open(os.path.join(out_dir, prefix + ".txt"), "w") as file:
            for key in sorted(statistics.keys()):
                file.write(collector.separator.join([_format_item(key), _format_item(statistics[key])]) + '\n')
    else:
        for key in sorted(statistics.keys()):
            write(out_dir, prefix + "_" + _format_item(key), statistics[key])

def reset():
    '''
    Resets the stat collector.
    '''
    StatCollector().statistics = {}

def write_input_parameters(params, out_path):
    '''
    Convenience function that writes out the given dictionary of input parameter
    names to parameter values to the given file path.
    '''
    with open(out_path, 'w') as file:
        for name, value in params:
            file.write("{} = {}\n".format(name, value))

if __name__ == '__main__':
    for i in xrange(10):
        counter(1, "test-1")
    for i in xrange(5):
        counter(1, "test-2")
    for i in xrange(50):
        apply_counter(range(0, 50, 5), lambda x: i if i < x else 0, "test-3")
    import random
    for i in xrange(50):
        num = random.randint(0, 10)
        unique_counter(num, "unique")
        counter(1, "unique-dist", num)
    print(StatCollector())
