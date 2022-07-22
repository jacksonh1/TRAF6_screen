'''
This script takes the output of the 02_align_reads script that consists of lines
containing a single DNA sequence each, and produces a "sequence hierarchy" file
that expresses the counts of various fragments of sequence. For instance, if this
script is asked (in SORTING_TASKS) to count first by bases 0-10, then by bases
11-15, the output would be a text file with the following format:

5   3   AAAAAAAAAA
        2   2   BBBBB
        2   2   CCCCC
        1   1   DDDDD
4   1   EEEEEEEEEE
        4   4   FFFFF
...

The first number in each top-level item indicates the total number of reads that
had the given sequence in bases 0-10; the second number indicates the number of
unique sequences found in the range 11-15 that had this 0-10 sequence. A similar
pattern holds for the next-level items. This file format is used by the 04 and 05
scripts as well, so the tools can be swapped out as necessary. Tools to read and
write this file format can be found in seq_hierarchy_tools.py.
# =================== added by Jackson ===============================================
The hierarchy thing is basically a way to make sort of a multi-level dataframe like in 
pandas but from scratch and without using pandas at all. I think the seq_hierarchy_tools.py 
is a library to deal with this data structure. I am guessing that either
Venkat didn't know about pandas at the time that he wrote this, or, it's necessary for
speed. 

In my version of this pipeline I bypass the entire "sequence hierarchy" data structure 
by counting with only 1 task.
# ====================================================================================
'''

import os, sys
import stat_collector as sc
import time
import argparse

# =========== added by Jackson =======================
# FYI, it's best to never import like this (import *)
# it can cause some confusion to other people reading code
# ====================================================
from aligner import *

OUTPUT_DELIMITER = '\t'
STAT_SCORES = "scores"

'''
If the score of the alignment is less than the length of the template minus
this amount, the sequence will be discarded.
'''
DISCARD_THRESHOLD = 2



''' SORTING_TASKS
Method 1: position based counting
Provides the criteria by which the input file will be sorted. If the task is a
tuple of integers (start, end), the script will search for the unique sequences
at those positions in each sequence. 
I would not recommend this method

Method 2: alignment based counting using templates - RECOMMENDED
If the task is a tuple of strings (template, output_template), the script will
attempt to align the template to each sequence in the file. The positions that
are denoted by VARIABLE_REGION_TOKEN in the output_template, which must be the
same length as template, will be assembled as the unique string for that sequence.
For example, if the sequence were ABCDEFGH, the template were AB**E*, and the
output template were A*****, the returned generic sequence would be '.BCDEF'.

Example:
ABCDEFGH - sequence (merged read)
AB**E*   - template 
A*****   - output template
---------------------------------
.BCEDF   - RETURNED OUTPUT


Added by Jackson:
# ====================================================================================
IMPORTANT - if you only use 1 task, YOU MUST USE --complete PARAMETER WITH OUTPUT FOR
 COMPLETE FILE


SORTING_TASKS = [TASK1, TASK2, ....]
TASK1, TASK2, .... are the "tasks" for counting. They are essentially different ways of 
aligning to the merged read and then counting the region next to it.
# ====================================================================================

'''
SORTING_TASKS = [('*********CCT***GAA*********CCGG', VARIABLE_REGION_TOKEN * 31)]


'''Added by Jackson:
SORTING_TASKS = [('*********CCT***GAA*********CCGG', VARIABLE_REGION_TOKEN * 31)]
NOTE: VARIABLE_REGION_TOKEN = *


*********CCT***GAA*********CCGG - template.
Aligns to sequence. Only specified nucleotides will "align" to read and "*" positions are
allowed to mismatch with read 
******************************* - output template
This means that all of the sequence that matches the template will be exported
'''





'''
List of expression strings which will be evaluated and written out to the
params.txt file.
'''
PARAMETER_LIST = ["args.input", "args.output", "args.complete", "SORTING_TASKS", "DISCARD_THRESHOLD"]

def count_unique_sequences(input_file, match_task, indexes=None):
    '''
    If indexes is None, returns two items. First, a dictionary where each key
    corresponds to a set of sequences with the same nucleotides at the given
    position, and the value is a list of indexes in input_file where those
    sequences may be found. Second, the length of the file in lines.
    input_file may be any iterable of strings.

    If indexes is not None, it should be a list of the same length as the number
    of lines in the input. The return value in this case, will be a dictionary where
    each key is one of the values of the indexes list. The value at that key will
    be the unique sequences for all lines that have that given index value.

    Added by Jackson:
    match_task = one of the elements of the SORTING_TASKS list. Should be a tuple
    input_file = merged read sequences (ex. dnaframe)
    '''

    input_file.seek(0)
    ret = {}
    num_lines = 0
    for i, line in enumerate(input_file):
        num_lines = i

        if indexes is not None:
            if indexes[i] is None:
                continue
            if indexes[i] not in ret:
                ret[indexes[i]] = {}
            ret_to_write = ret[indexes[i]]
        else:
            ret_to_write = ret

        if type(match_task[0]) is str:
            # Align the match_task template

            # ======= added by Jackson ===============
            # get_generic_sequence_by_alignment arguments:
            # sequence = line.strip() - single merged read
            # template = match_task[0]
            # output_template = match_task[1]
            # generic = output string of matching section of read using output_template
            # =========================================
            generic = get_generic_sequence_by_alignment(line.strip(), match_task[0], match_task[1])
        else:
            # Use the bases at the given positions
            generic = get_generic_sequence_by_position(line.strip(), [match_task])
        if generic is None:
            continue

        if generic in ret_to_write:
            ret_to_write[generic].add(i)
        else:
            ret_to_write[generic] = set([i])

    return ret, num_lines + 1

def get_generic_sequence_by_position(sequence, match_ranges):
    '''
    Returns a generic sequence where the bases outside match_ranges are denoted
    with the GENERIC_SEQUENCE_TOKEN symbol.
    '''
    match_ranges = sorted([(start % len(sequence), end % len(sequence)) for start, end in match_ranges])
    ret = ""
    ret_start = 0
    for start, end in match_ranges:
        if len(ret) == 0:
            ret_start = start
        else:
            while len(ret) < start - ret_start:
                ret += GENERIC_SEQUENCE_TOKEN
        ret += sequence[start:end]
    return ret

def get_generic_sequence_by_alignment(sequence, template, output_template):
    '''
    Returns a generic sequence by aligning template to sequence, and including
    only the bases in positions marked with VARIABLE_REGION_TOKEN in the template.

    For example, if the sequence were ABCDEFGH and the template were AB**E*, the
    returned generic sequence would be 'CD.F'.
    '''
    aligner = Aligner(different_score=0)
    offset, score = aligner.align(sequence, template, min_overlap=len(template))
    num_matching_bases = len([c for c in template if c not in NON_SCORED_TOKENS])
    sc.counter(1, STAT_SCORES, score)
    if score < num_matching_bases - DISCARD_THRESHOLD:
        return None

    ret = ""
    ret_start = 0
    # =============== added by Jackson ===========================================
    # the below loop just exports the aligning region according to output_template
    # ============================================================================
    for i, (base_1, base_2) in enumerate(aligner.enumerate(sequence, output_template, offset)):
        if base_2 == VARIABLE_REGION_TOKEN:
            if len(ret) == 0:
                ret_start = i
            else:
                while len(ret) < i - ret_start:
                    ret += GENERIC_SEQUENCE_TOKEN
            ret += base_1
    return ret

def write_hierarchical_unique_sequences(in_file, match_ranges, out_file, indent=0, complete_file=None, uniques=None, file_length=None):
    '''
    Groups the file in_file by the first match range, then each group by the
    second match range, and so on. Writes the distribution of each match to
    out_file (a file object).

    By default, the last group's keys will not be written to file. If desired,
    specify complete_file to write those keys in another hierarchical level to a
    separate file.
    '''
    if len(match_ranges) == 0:
        return
    if uniques is None:
        uniques, file_length = count_unique_sequences(in_file, match_ranges[0])

    sorted_uniques = sorted(uniques.items(), reverse=True, key=lambda x: len(x[1]))

    if len(match_ranges) > 1:
        # Precompute the unique matches for the next match range to get the
        # number of unique items within each match at this round
        index_list = [None for _ in xrange(file_length)]
        for i, (match, indexes) in enumerate(sorted_uniques):
            for index in indexes:
                index_list[index] = i
        new_uniques, _ = count_unique_sequences(in_file, match_ranges[1], indexes=index_list)
    else:
        new_uniques = None

    # ================== added by Jackson ================================================
    # indexing is very confusing in loop below
    # it accesses next level matches by using i
    # enumerates `sorted_uniques` to get counts for first level sequences
    # `new_uniques` is created by enumerating `sorted_uniques` so you can access the correct entry
    # with `i` in the below script (by enumerating it again)
    # ====================================================================================
    for i, (match, indexes) in enumerate(sorted_uniques):
        if len(match_ranges) > 1:
            unique_submatches = len(new_uniques[i])
        else:
            unique_submatches = len(indexes)

        string_to_write = "\t\t" * indent + OUTPUT_DELIMITER.join([str(len(indexes)), str(unique_submatches), match]) + "\n"

        if complete_file is not None:
            complete_file.write(string_to_write)
        
        # ================== added by Jackson ================================================
        '''
        below conditional:
        runs write_hierarchical_unique_sequences with completely different parameters for just the
        sequences corresponding to new_uniques[i]. It already has uniques defined as input param
        so it skips the first call to count_unique_sequences and goes straight to sorting.
        skips any conditional where len(match_ranges)>1 if it's the last task b/c of the param
        match_ranges=match_ranges[1:]. It does however write the next line to complete_file
        because it's now using the complete_file parameter
        '''
        # ====================================================================================
        if len(match_ranges) > 1:
            out_file.write(string_to_write)
            write_hierarchical_unique_sequences(in_file, match_ranges[1:], out_file, indent=indent + 1, complete_file=complete_file, uniques=new_uniques[i], file_length=file_length)

### Main function

def main_count_sequences(input, output, tasks, complete_path=None):
    ''' added by Jackson 
    This function generates output files and opens input file (merged reads)
    It then passes files and tasks parameters to `write_hierarchical_unique_sequences`
    input = merged read sequences (ex. dnaframe)
    output = sequence counts output directory
    '''
    if not os.path.exists(output):
        os.mkdir(output)
    basename = os.path.basename(input)
    with open(input, 'r') as file, open(os.path.join(output, basename), 'w') as out_file:
        if complete_path is not None:
            if not os.path.exists(complete_path):
                os.mkdir(complete_path)
            complete_file = open(os.path.join(complete_path, basename), 'w')
        else:
            complete_file = None
        ''' added by Jackson 
        file = input file - merged read sequences (dnaframe)
        out_file = sequence counts output file
        complete_file = complete sequence counts output file
        '''
        write_hierarchical_unique_sequences(file, tasks, out_file, complete_file=complete_file)

        if complete_file is not None:
            complete_file.close()

    sc.write(os.path.join(output, "stats"), prefix=basename)

if __name__ == '__main__':
    a = time.time()  # Time the script started
    parser = argparse.ArgumentParser(description='Groups the sequences in the given file into hierarchies based on identical sequences in certain ranges.')
    parser.add_argument('input', metavar='I', type=str,
                        help='The path to the input file, where each line is a sequence')
    parser.add_argument('output', metavar='O', type=str,
                        help='The path to the output directory')
    parser.add_argument('-c', '--complete', type=str, default=None,
                        help='The path to an additional output directory for the complete set of unique sequences')
    args = parser.parse_args()

    main_count_sequences(args.input, args.output, SORTING_TASKS, complete_path=args.complete)

    b = time.time()
    print("Took {} seconds to execute.".format(b - a))

    # Write out the input parameters to file
    params_path = os.path.join(args.output, "params.txt")
    sc.write_input_parameters([(name, eval(name)) for name in PARAMETER_LIST], params_path)
