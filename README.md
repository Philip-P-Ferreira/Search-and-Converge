# Search and Signal
Repo for Search and Signal: final project for EECE 4376 course at Vanderbilt University

## Installing dependencies
Run ```./install_dep```. Works in ubuntu and other apt-get systems.

You may have to run ```sudo pip install -U numpy``` if the app fails (error output will mention numpy). I have no idea why this is


## Running the application
To run as "master car", ```./master.sh```. There can only be one master

To run as "follower car", ```./follower.sh <car number>```. Each car should have a unique car number that is not 1 (reserved for master). The host name of the master should be specified in [followerMain.py](src/followerMain.py)

All cars (1 master and n followers) must be on the same WiFi network. For best results, run the followers first then the master.


## Staring the search
Wave your hand in front of the master car's camera/sensor module.

## Ending Search
Search ends when one of the cars find the objective (currently just a stop sign). Then all cars will stop and beep according the number of the car that found the objective.
