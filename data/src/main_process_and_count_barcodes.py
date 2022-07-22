'''
Run script with python2
python main_process_and_count_barcodes.py [barcode_directory] [reformat command]

barcode_directory = path to fastq files (de-multiplexed files with no extension: `barcode_x`)
reformat command = file path to bbtools `reformat.sh` executable


I haven't added much documentation to this b/c it's a pretty short script
it's basically just a driver script that runs:
    - bbtools reformat.sh command to de-interleave the fastqs
    - fq2str.py to remove fastq formatting from reads leaving just the nucleotide strings
    - count_sequences.py to tabulate the reads in each sample

Read count tables (counts for each read) are saved in [barcode_directory]/sequence_counts/
'''


import subprocess
import glob, os
import multiprocessing
import sys

# TODO use argparser instead of positional arguments


def run(file, reformat_command):
    # run BBduk reformat command to quality filter and de-interleave paired reads
    subprocess.call("{} in={} out1={}_f.fq out2={}_r.fq minavgquality=20".format(reformat_command, file, file, file), shell=True)
    # subprocess.call("rm {}_r.fq".format(file), shell=True)

    # convert fastq to plain list of seqs (for Venkat's script)
    subprocess.call('python ./src/fq2str.py {}_f.fq'.format(file), shell=True)
    # subprocess.call("rm {}_f.fq".format(file), shell=True)

def run_count_sequences(file):
    # run Venkat's script
    output_path = os.path.dirname(file)
    subprocess.call('python ./src/count_sequences.py {}_f_nts_only "{}/temp" -c "{}/sequence_counts"'.format(file,output_path,output_path), shell=True)
    subprocess.call('rm -r "{}/temp"'.format(output_path), shell=True)


def main(parallel=False):
    barcode_directory = str(sys.argv[1])
    reformat_command = str(sys.argv[2])
    print('running bbtools reformating and converting fastq to string')
    if parallel:
        p = multiprocessing.Pool()
    for f in glob.glob(os.path.join(barcode_directory, "barcode*")):
        # skip files ending in ".fq". Makes it easier if you rerun this script
        if f.endswith(".gz"):
            continue
        if f.endswith("_r.fq"):
            continue
        if f.endswith("_f.fq"):
            continue
        if f.endswith("_nts_only"):
            continue
        if parallel:
            # launch a process for each file (ish).
            # The result will be approximately one process per CPU core available.
            p.apply_async(run, [f, reformat_command])
        else:
            run(f, reformat_command)
    if parallel:
        p.close()
        p.join() # Wait for all child processes to close.

    if parallel:
        p = multiprocessing.Pool()
    print("running count_sequences.py")
    for f in glob.glob(os.path.join(barcode_directory, "barcode*")):
        # skip files ending in ".fq". Makes it easier if you rerun this script
        if f.endswith(".gz"):
            continue
        if f.endswith("_r.fq"):
            continue
        if f.endswith("_f.fq"):
            continue
        if f.endswith("_nts_only"):
            continue
        if parallel:
            # launch a process for each file (ish).
            # The result will be approximately one process per CPU core available.
            p.apply_async(run_count_sequences, f)
        else:
            run_count_sequences(f)
    if parallel:
        p.close()
        p.join() # Wait for all child processes to close.

if __name__ == "__main__":
    main()
