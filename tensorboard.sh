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

#echo "?token=" >&2

#tensorboard --logdir $TENSORBOARD_DIR --port=$PORT 



!tensorboard dev upload --logdir ./samples/puzzle_mnist_3_3_40000_CubeSpaceAE_AMA4Conv/logs/8dd53f4ca49f65444250447a16903f86 \
  --name "Simple experiment with MNIST" \
  --description "Training results from https://colab.sandbox.google.com/github/tensorflow/tensorboard/blob/master/docs/tbdev_getting_started.ipynb" \
  --one_shot