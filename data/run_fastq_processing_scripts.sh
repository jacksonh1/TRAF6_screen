# ==============================================================================
# // parameters
# ==============================================================================

#== path to fastq files ==#
barcode_directory="./fastq_files/"

#== bbmap `reformat` executable ==#
reformat_command="reformat.sh"

# ==============================================================================
# // Run scripts
# ==============================================================================

python ./src/main_process_and_count_barcodes.py $barcode_directory $reformat_command
