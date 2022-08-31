#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --error=myJobWithExtraLossDump.err
#SBATCH --output=myJobWithExtraLossDump.out
#SBATCH --gres=gpu:1
#SBATCH --partition=g100_usr_interactive
#SBATCH --account=uBS21_InfGer_0
#SBATCH --time=00:20:00
#SBATCH --mem=32G




./train_kltune.py dump_actions puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv with_NOextra_loss 3562df9d521f6d600dfc374ac6bd87f6
# ./train_kltune.py testing puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv
# ./train_kltune.py learn puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv with_extra_loss