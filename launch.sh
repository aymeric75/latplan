#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --error=myJob.err
#SBATCH --output=myJob.out
#SBATCH --gres=gpu:1
#SBATCH --partition=g100_usr_interactive
#SBATCH --account=uBS21_InfGer_0
#SBATCH --time=0:30:00
#SBATCH --mem=32G




#./train_kltune.py dump_actions puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d37f7
# ./train_kltune.py testing puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv
./train_kltune.py learn puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv with_extra_loss