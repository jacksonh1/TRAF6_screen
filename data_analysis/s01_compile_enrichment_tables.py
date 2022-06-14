"""
I'm trying something new by keeping the sample and file directory information in a json file. I usually use a csv file so that it's easy to make a sample key in excel but I'm trying something different
"""
import json
import os

import src.traf_pepseq_tools as traf_tools


def get_experiment_filelist(count_file_dir, barcode_list):
    barcode_files = []
    for b in barcode_list:
        barcode_files.append(os.path.join(count_file_dir, "{}_f_nts_only".format(b),))
    return barcode_files


def col_rename_and_sort(df1, sample_renaming_key):
    df = df1.copy()
    df = df.rename(columns=sample_renaming_key)
    df = df[sorted(df.columns)]
    return df


def enrichment_merge(
    barcode_list, count_file_dir, sample_renaming_key
):
    # ===== LOAD AND MERGE DATA
    file_list = get_experiment_filelist(count_file_dir, barcode_list)
    R, _ = traf_tools.load_and_merge_data(file_list)

    # ===== RENAME COLUMNS to names that are more meaningful using `sample renaming key`
    R = col_rename_and_sort(R, sample_renaming_key=sample_renaming_key)
    return R.sort_values('seq').reset_index(drop=True)


def main(parameter_file):
    # open parameters.json file
    with open(parameter_file) as f:
        params = json.load(f)

    # extract arguments from parameters.json file
    count_file_dir = params["filepaths"]["sequence counts directory"]
    sample_renaming_key = params["barcode name key"]
    experiments = list(params["experiment barcode lists"].keys())

    # output file directory
    output_folder = params["filepaths"]["output directory"]
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # merge barcodes for each experiment and export to a csv file
    table_files=[]
    for exp in experiments:
        barcode_list = params["experiment barcode lists"][exp]
        R=enrichment_merge(
            barcode_list, count_file_dir, sample_renaming_key
        )
        R=R[['seq','pre-enrichment (MACSlib)','day_1','day_2','day_3','day_4','day_5']]
        output_file = os.path.join(output_folder, exp + "_readcounts.csv")
        table_files.append(output_file)
        R.to_csv(output_file, index=False)
        print('file saved to {}'.format(output_file))

    # update parameter json file to include new files
    params['filepaths']['merged enrichment tables']=table_files
    with open(parameter_file, 'w') as f:
        json.dump(params, f, indent=4)


if __name__ == "__main__":
    main("./parameters.json")
