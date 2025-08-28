#!/bin/bash

#SBATCH --job-name=velocyto 
#SBATCH --account=indikar1
#SBATCH --partition=largemem,standard
#SBATCH --mail-user=cstansbu@umich.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --mem=150G
#SBATCH --time=36:00:00
#SBATCH --nodes=1                     
#SBATCH --ntasks=1                    
#SBATCH --cpus-per-task=32

snakemake --use-conda --cores 32