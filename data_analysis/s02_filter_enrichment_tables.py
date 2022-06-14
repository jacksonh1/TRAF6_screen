import json
import os

import pandas as pd

import src.traf_pepseq_tools as traf_tools


def filter_across_multiple_columns(df1, count_cutoff, cols):
    df = df1.copy()
    df = traf_tools.collapse_counts(df, cols)
    df = traf_tools.filter_nonsense_seqs(df)
    df = df[(df[cols] >= count_cutoff).any(1)]
    df = df.sort_values('seq')
    df = df[['seq','AA_seq']+cols]
    return df


def main(parameter_file):
    # open parameters.json file
    with open(parameter_file) as f:
        params = json.load(f)

    table_files = params['filepaths']['merged enrichment tables']
    new_files = []

    count_cutoff = params["readcount cutoff"]
    cols = params["enrichment count columns"]

    for file in table_files:
        exp, ext = os.path.splitext(file)
        output_file = f'{exp}-processed{ext}'
        new_files.append(output_file)
        table = pd.read_csv(file)
        table = filter_across_multiple_columns(table, count_cutoff, cols)
        table.to_csv(output_file, index=False)
        print('file saved to {}'.format(output_file))

    # update parameter json file to include new files
    params['filepaths']['processed merged enrichment tables']=new_files
    with open(parameter_file, 'w') as f:
        json.dump(params, f, indent=4)


if __name__ == "__main__":
    main("./parameters.json")
