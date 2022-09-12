# before building the image: 1) download the 2 tars in the current dir 2) make sure the .yml is the good one

# ONCE image built: from PowerShell: docker run -it -d -v "$(pwd):/home/latplan" latplan-image

FROM continuumio/conda-ci-linux-64-python3.7

COPY . /home/latplan

RUN ["/bin/bash", "-c", "sudo chmod -R a+rw /home/latplan"]

RUN sudo apt-get update

RUN sudo apt-get install nano

WORKDIR /home/latplan

RUN ["/bin/bash", "-c", "conda env create --name latplan -f environment.yml"]

RUN ["/bin/bash", "-c", "sudo chmod -R 755 /home/latplan"]

#RUN ["/bin/bash", "-c", "conda init bash"]


RUN ["/bin/bash", "-c", ". /opt/conda/etc/profile.d/conda.sh && conda activate latplan && pip install tensorflow==1.15 && pip install protobuf==3.20.*"]


RUN ["/bin/bash", "-c", "( cd latplan/puzzles/ ; sudo tar xf ../../datasets.tar )"]


RUN ["/bin/bash", "-c", "( cd problem-generators/ ; sudo tar xf ../backup-propositional.tar.bz2 )"]