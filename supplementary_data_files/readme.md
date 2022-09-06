# Manuscript supplementary data files:

file | description
--- | ---
`./Supplementary_Information.pdf` | main supplementary information from manuscript
`./supplementary_data_file_key.xlsx` | table containing descriptions of the supplementary files provided here
`./enrichment_rep1_readcounts.csv` | merged read counts for enrichment replicate 1
`./enrichment_rep2_readcounts.csv` | merged read counts for enrichment replicate 2
`./enrichment_rep1_readcounts-processed.csv` | enrichment replicate 1 - read counts after filtering*
`./enrichment_rep2_readcounts-processed.csv` | enrichment replicate 2 - read counts after filtering*
`./nonbinder_readcounts-processed.csv` | nonbinder pool - read counts after filtering*; final 1200 nonbinders
`./final_binder_list.txt` | final set of 236 binder sequences‡
`./MD_sequences.xlsx` | sequences used in structural modeling studies
`./Supplementary_Table_S4.xlsx` | TRAF6 motifs in the human proteome with PSSM score

\*Filtering: Nucleotide sequences were collapsed to just the motif (\*\*\*\*\*\*\*\*\*CCT\*\*\*GAA\*\*\*\*\*\*\*\*\*) and then translated into amino acid sequence. Peptides which did not match the motif (xxxPxExxx) or which contained a “\*” or “X” character were removed. Any sequences that didn’t have a read count of 20 or more in at least one of the read count columns were removed.<br>
‡See manuscript methods section and `../analysis/s04_binder_processing.py` for details on processing