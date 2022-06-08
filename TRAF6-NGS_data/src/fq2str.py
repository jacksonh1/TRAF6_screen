from Bio import SeqIO, Seq
import sys
import os
Input_name = str(sys.argv[1])
output_name = os.path.splitext(Input_name)[0] + '_nts_only'


seqs = []
with open(Input_name) as handle:
    reads = SeqIO.parse(handle, 'fastq')
    for read in reads:
        seqs.append(str(read.seq))


with open(output_name, 'w') as output:
    for seq in seqs:
        output.write(seq + '\n')
