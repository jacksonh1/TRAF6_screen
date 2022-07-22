import os
import numpy as np
import pandas as pd
from Bio import Seq


def trans_string(s):
    l = int(len(s)/3)*3
    return str(Seq.Seq(s[0:l]).translate())


def df_import_1(file):
    """
    imports barcode_x_f_nts_only file.
    returns a dataframe of the nt sequences (`seq`) and their counts (column named after file name `barcode_x`)
    """
    base = os.path.basename(file)
    basenoext = os.path.splitext(base)[0].replace("_f_nts_only", "")
    df = pd.read_csv(
        file,
        sep="\t",
        header=None,
        names=[basenoext, "useless", "seq"]
    ).drop("useless", axis=1)
    return df


def load_and_merge_data(file_list, excluded_barcodes=None):
    """
    TODO: output from: {script name}
    load NGS data (output from: ) and merge into a single DataFrame
    DataFrame will be the nt sequences (`seq`) and their counts for each barcode file in `file_list`
    each barcode file in `file_list` should correspond to 1 column in the Dataframe.
    columns are sorted in numerical order (ex: `seq` | `barcode_1` | `barcode_2` | ...)
    """
    # R will be the read counts for each sequence in each gate
    R = pd.DataFrame(columns=["seq"])
    for f in file_list:
        if excluded_barcodes:
            if (
                os.path.splitext(os.path.basename(f))[0].replace("_f_nts_only", "")
                in excluded_barcodes
            ):
                continue
        print("processing file: {}".format(f))
        df1 = df_import_1(f)
        R = pd.merge(R, df1, on="seq", how="outer")
    R = R.fillna(0)
    # reorder columns
    barcode_cols = [col for col in R.columns]
    barcode_cols.sort()
    barcode_cols.remove("seq")
    R = R[["seq"] + barcode_cols]
    return R, barcode_cols


def collapse_counts(df1, cols):
    '''
    remove last 4 nt from sequences corresponding to the static region of the template plasmid.
    Then collapse readcounts for duplicate sequences present after removing static region. 
    then re-translate the sequences (since only the `cols` and `seq` columns are saved when it's collapsed)
    '''
    df = df1.copy()
    df['seq'] = df.seq.str[:-4]
    df=df.groupby('seq')[cols].sum()
    df=df.reset_index()
    df['AA_seq'] = df['seq'].apply(trans_string)
    df = df.sort_values(cols, ascending=False)
    return df



def filter_nonsense_seqs(df1):
    '''
    return list of nt sequences not containing * or X and matching regex ...P.E...
    '''
    df = df1.copy()
    df = df[~df.AA_seq.str.contains(r"[\*X]")]
    df = df[df.AA_seq.str.contains(r"...P.E...")]
    return df


def seqfile2list(seqs_file):
    with open(seqs_file) as handle:
        f = handle.readlines()
        sequence_list = [i.strip() for i in f]
    return sequence_list


def write_seqlist(seqlist, filename):
    with open(filename, 'w') as handle:
        for seq in seqlist:
            handle.write(seq + '\n')


def union_2_lists(l1, l2):
    '''converts each list into a set. finds the union of the 2 sets and returns it as a list'''
    sl1 = set(l1)
    sl2 = set(l2)
    return list(sl1.union(sl2))


