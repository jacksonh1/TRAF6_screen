# NGS data
In this folder (`TRAF6_screen/TRAF6-NGS_data`) is the NGS data associated with the manuscript entitled: **Molecular determinants of TRAF6 binding specificity suggest that native interaction partners are not optimized for affinity**. [BioRxiv link](https://www.biorxiv.org/content/10.1101/2022.05.08.491058v3) <br>


## setup
To process the NGS data, you need python2. 
python2 is no longer supported. There are currently no plans to convert this pipeline 
into python 3 but it would probably be pretty straightforward if you wanted to do that.
If you are using conda, you can create an environment with the same
modules that I used to run the scripts:
`conda env create -f py2_traf6_NGS.yml`
then `conda activate py2_traf6_NGS` to use the environment

The pipeline also uses the `reformat` tool from the bbtools suite [link](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/)


## using the scripts
`./src/aligner.py`, `./src/count_sequences.py`, and `./src/stat_collector.py` were written by Venkat Sivaraman and slightly modified by Jackson Halpin. The rest of the scripts/pipeline was written by Jackson Halpin


to rerun the analysis, first unzip the compressed fastq files:
`bash ./uncompress_fastqs.sh`


open `run_fastq_processing_scripts.sh` and change the `reformat_command` variable to the path of the `reformat.sh` script from bbtools that you downloaded. If you installed bbtools scripts in your PATH, then you do not have to change the `reformat_command` variable.


Then just run the driver bash script:
`bash ./run_fastq_processing_scripts.sh`

it de-interleaves the fastq files, filters out low quality reads, and tabulates the sequences. See the manuscript for details

