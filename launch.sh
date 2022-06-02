#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --error=myJob.err
#SBATCH --output=myJob.out
#SBATCH --gres=gpu:1
#SBATCH --partition=g100_usr_interactive
#SBATCH --account=uBS21_InfGer_0
#SBATCH --time=60
#SBATCH --mem=32G


# !./train_kltune.py learn_summary_plot_dump puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Plus

# ! ./train_kltune.py reproduce puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Plus

./train_kltune.py reproduce puzzle mnist 3 3 5000 ConcreteDetNormalizedLogitAddEffectTransitionAE

# !CubeSpaceAE_AMA4Conv