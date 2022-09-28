#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --error=myJobLearnBis.err
#SBATCH --output=myJobLearnBis.out
#SBATCH --gres=gpu:1
#SBATCH --partition=g100_usr_interactive
#SBATCH --account=uBS21_InfGer_0
#SBATCH --time=08:00:00
#SBATCH --mem=32G



### Dump the actions in the specified folder
# ./train_kltune.py dump_actions puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d37f7

### Print out the output images (called imagg) of some transitions (to test if they are good or not)
#./train_kltune.py testing puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d37f7

### TRAINING
./train_kltune.py learn puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d3BIS
#./train_kltune.py learn puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv with_extra_loss d01c481c886db9b54c4ce52ca002ee96

### Generate categorical vectors representing the images (pre_cat_transitions et suc_cat_transitions)
# ./train_kltune.py dump_cat_transition puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d37f7



### Generate a new 'balanced' dataset
#./train_kltune.py return_new_dataset puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d37f7




### Some other stuff
# ./train_kltune.py plot_transition_images puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d37f7


### Evaluate the network
#./train_kltune.py evaluate puzzle mnist 3 3 40000 CubeSpaceAE_AMA4Conv withOUT_extra_loss c21764c27e99bdd900e708b87b5d37f7
