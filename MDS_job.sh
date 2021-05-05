# bin/bash

# set up environment
. /h/hngai/med-dialogue-system/env/bin/activate

# symlink checkpoint directory to run directory
ln -s /checkpoint/$USER/$SLURM_JOB_ID /h/hngai/MD-system/output

python3 ~/MD-system/train.py

