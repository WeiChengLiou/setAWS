export LC_ALL="en_US.UTF-8"
sudo apt-get update
sudo apt-get install -y --force-yes build-essential python-dev gfortran python-pip
sudo apt-get install -y --force-yes libblas-dev liblapack-dev liblapacke-dev
sudo apt-get -y --force-yes upgrade
sudo apt-get -y --force-yes install cython python-numpy python-scipy
sudo pip install celery
