import json
import os
import sys

import src.traf_pepseq_tools as traf_tools


def filter_rename_single_column_table(df1, count_cutoff=0, col='barcode_5'):
    df = df1.copy()
    df = traf_tools.collapse_counts(df, col)
    df = traf_tools.filter_nonsense_seqs(df)
    df = df[df[col]>=count_cutoff]
    df = df.sort_values(col, ascending=False)
    df = df[['seq', 'AA_seq', col]]
    df = df.rename(columns={col:'read counts'})
    return df


def main(parameter_file,save2file=False):
    # open parameters.json file
    with open(parameter_file) as f:
        params = json.load(f)

    non_binder_counts_file = params['filepaths']['nonbinder sequence counts file']
    nbdf = traf_tools.df_import_1(non_binder_counts_file)

    nb_df_20rcc = filter_rename_single_column_table(nbdf, count_cutoff=20, col='barcode_5')

    print('number of sequences with >=20 reads: ', len(nb_df_20rcc['AA_seq'].unique()))

    if save2file:
        output_file = os.path.join(params['filepaths']['output directory'], 'nonbinder_readcounts-processed.csv')
        print('file saved to {}'.format(output_file))
        nb_df_20rcc.to_csv(output_file, index=False)

        params['filepaths']['processed nonbinder table']=output_file
        with open('parameters.json', 'w') as f:
            json.dump(params, f, indent=4)
    else:
        return nb_df_20rcc


if __name__ == "__main__":
    main(parameter_file='./parameters.json', save2file=True)












