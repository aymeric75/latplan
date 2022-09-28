#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --error=myJobTensor.err
#SBATCH --output=myJobTensor.out
#SBATCH --gres=gpu:1
#SBATCH --partition=g100_usr_interactive
#SBATCH --account=uBS21_InfGer_0
#SBATCH --time=0:20:00
#SBATCH --mem=32G

#PORT=$1
#TENSORBOARD_DIR=$2 

module load profile/deeplrn autoload tensorflow/1.10.0--python--3.6.4



tensorboard dev upload --logdir ./samples/puzzle_mnist_3_3_40000_CubeSpaceAE_AMA4Conv_withOUT_extra_loss/logs/c21764c27e99bdd900e708b87b5d3BIS \
  --name "Simple experiment with MNIST" \
  --description "Training results from ...." \
  --one_shot