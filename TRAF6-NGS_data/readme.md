# NGS data
In this folder (`TRAF6_screen/TRAF6-NGS_data`) is the NGS data associated with the manuscript entitled: **Molecular determinants of TRAF6 binding specificity suggest that native interaction partners are not optimized for affinity**. [BioRxiv link](https://www.biorxiv.org/content/10.1101/2022.05.08.491058v3) <br>


## setup
To process the NGS data, you need python2. 
python2 is no longer supported. There are currently no plans to convert this pipeline 
into python 3 but it would probably be pretty straightforward if you wanted to try that.
If you are using conda, you can create an environment with the same
modules that I used to run the scripts:<br>
`conda env create -f py2_traf6_NGS_full.yml`<br>
then:<br>
`conda activate py2_traf6_NGS`<br>
to use the environment.<br>

if you are on linux or windows, you should probably use:<br>
`conda env create -f ./py2_traf6_NGS_compatible.yml`<br>
then:<br>
`conda activate py2_traf6_NGS`<br>
instead.<br>
`py2_traf6_NGS_full.yml` is the exact environment I used on macbut the dependencies and their versions will probably be different on other operating systems. The "compatible" version (`py2_traf6_NGS_compatible.yml`) was generated with `conda env export --from-history` and should work for any operating system

<br>
The pipeline also uses the `reformat` tool from the bbtools suite [link](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/)


## using the scripts
`./src/aligner.py`, `./src/count_sequences.py`, and `./src/stat_collector.py` were written by Venkat Sivaraman and slightly modified by Jackson Halpin. The rest of the scripts/pipeline was written by Jackson Halpin


to rerun the analysis, first unzip the compressed fastq files:<br>
`bash ./uncompress_fastqs.sh`


open `run_fastq_processing_scripts.sh` and change the `reformat_command` variable to the path of the `reformat.sh` script from bbtools that you downloaded. If you installed bbtools scripts in your PATH, then you do not have to change the `reformat_command` variable.


Then just run the driver bash script:<br>
`bash ./run_fastq_processing_scripts.sh`

the pipeline de-interleaves the fastq files, filters out low quality reads, and counts the number of reads for each sequence in each fastq file. See the manuscript for details

## output
The read count files will be located in `./fastq_files/sequence_counts/`. They are tab delimited and contain the following columns (without column names):<br> 
read counts, read counts (duplicate column), nucleotide sequence<br>
In downstream analysis, I just remove the duplicate read count column. It is left over from a different hierarchical read counting procedure. <br>
here is a preview of the read count files:
```bash
$ head -n5 fastq_files/sequence_counts/barcode_0_f_nts_only
110166  110166  AAACAAGAACCTCAGGAAATCGATTTCCCGG
4812    4812    TATAATGCTCCTACGGAAAATGAGTGGCCGG
4157    4157    GGGAATCAGCCTGTGGAAGATGATTGGCCGG
3093    3093    CTTAATTTGCCTGAGGAATCTGATTGGCCGG
2807    2807    GTGAATTATCCTACGGAAACTGATTGGCCGG
```
