#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --error=myJob.err
#SBATCH --output=myJob.out
#SBATCH --gres=gpu:1
#SBATCH --partition=g100_all_serial
#SBATCH --account=uBS21_InfGer_0
#SBATCH --time=00:20:00
#SBATCH --mem=28G




./pddl-ama3.sh