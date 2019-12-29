# Recyclr
**Recyclr** is a multi-module suite for automated trash & recyclable (T&R) detection & sorting. Recyclr provides a toolkit for building out T&R functionalities through models, sorting heirarchies, and enlisted descriptors.

recyclr is a WIP and currently contains server logic for crowdsourced labeling functionality and the base of a T&R label heirarchy for higher-level usgae.

# Modules


## Labeling Server
Stands up a server which serves unlabeled data in a labeling studio. This allows users to build datasets over the internet via crowsourcing, or over a local network with trusted labelers.

Live demo: http://recyclr.net

> [![screenshot][1]][1]

  [1]: inc/demo.png

#### Server Instructions
**Standing up the server:**

    virtualenv recyclr
    source recyclr/venv/bin/activate
    (venv) user@local $ ./setup.sh
    python server.py

**Adding data to be labeled**
Simply place your raw videos in the **server/data/raw** directory. These videos will be selected when necessary and converted into individual frames to be served for labeling.
