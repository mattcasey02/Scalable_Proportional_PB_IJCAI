#!/bin/bash
#SBATCH --account=p33118  ## Required: your Slurm account name, i.e. eXXXX, pXXXX or bXXXX
#SBATCH --partition=small ## Required: buyin, short, normal, long, gengpu, genhimem, etc.
#SBATCH --time=00:01:00       ## Required: How long will the job need to run?  Limits vary by partition
#SBATCH --nodes=1             ## How many computers/nodes do you need? Usually 1
#SBATCH --array=0-775     ## Parallelizing by creating a slurm job for each file. Use command (ls ../Data/*.pb | wc -l) to count how many files
#SBATCH --cpus-per-task=1    # Do not have to use --ntasks since we are parallelizing with array (embarassingly parallel)
#SBATCH --mem-per-cpu=2G              ## How much RAM do you need per computer/node? G = gigabytes
#SBATCH --job-name=approval_waterflow_non_exhaustive     ## Used to identify the job 
#SBATCH --mail-type=ALL ## BEGIN, END, FAIL, or ALL
#SBATCH --mail-user=mattcasey@u.northwestern.edu
#SBATCH --output=../slurm_outputs/%x/%A/%a.out  ## This gives job_name/master_job_id/array_task_index

# Path to the script with your custom function
CUSTOM_FUNCTION_PATH="../PB_scripts/run_approval_waterflow_non_exhaustive.py"

sh master_script.sh $SLURM_ARRAY_TASK_ID $CUSTOM_FUNCTION_PATH