# analysis
In this folder (`TRAF6_screen/analysis`) is code for further processing the NGS data. It processes the sequence counts in `../data/fastq_files/sequence_counts/` to generate the tables/files in `../supplementary_data_files/`<br>


## setup
This part of the processing uses python 3
If you are using conda, you can create an environment with the same
modules that I used to run the scripts:<br>
`conda env create -f ./traf_analysis_env_full.yml`<br>
then:<br>
`conda activate traf_analysis_env`<br>
to use the environment.<br>

if you are on linux or windows, you should probably use:<br>
`conda env create -f ./traf_analysis_env_compatible.yml` <br>
then:
`conda activate traf_analysis_env`<br>
instead.<br>
`traf_analysis_env_full.yml` is the exact environment I used on mac but the dependencies and their versions will probably be different on other operating systems. The "compatible" version (`traf_analysis_env_compatible.yml`) was generated with `conda env export --from-history` and should work for any operating system

<br>


## using the scripts
all of the scripts here were written by Jackson Halpin<br>

run 
```bash
bash process_screening_data.sh
```
to run the scripts
