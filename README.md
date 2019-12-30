# Recyclr
**Recyclr** is a multi-module suite for automated trash & recyclable (T&R) detection & sorting. Recyclr provides a toolkit for building out T&R functionalities through models, sorting heirarchies, and enlisted descriptors.

recyclr is a WIP and currently contains server logic for crowdsourced labeling functionality and the base of a T&R label heirarchy for higher-level usage.

# Modules

## labels
Labels and classes in recyclr are treated as a dynamic tree and use a json-formatted syntax to control detection logic. Classes are very flexible and may be added/removed from the labels/nodes directory according to the user's needs.

See the label module [README.md](labels/README.md) for more info

## streams
Material streams are represented as streams in recyclr. Each class can have a designated stream which it belongs to, including post-processed logic for further operations and sorting.

Streams can be used to filter classes into groups based on the availability of certain streams in the user's area. During detection and retrieval, the agent will sort each item into a stream, and deliver the item to the appropriate stream.

See the streams module [README.md](streams/README.md) for more info

## server
Stands up a server which serves unlabeled data in a labeling studio. This allows users to build datasets over the internet via crowsourcing, or over a local network with trusted labelers.

Live demo: http://recyclr.net

> [![screenshot][1]][1]

  [1]: inc/demo.png

#### Server Instructions
**Standing up the server:**

    virtualenv recyclr
    source recyclr/venv/bin/activate
    (venv) user@local $ cd server
    (venv) user@local $ ./setup.sh
    python server.py

**Adding data to be labeled**
Simply place your raw videos or images in the **server/data/raw** directory. Videos will be selected when necessary and converted into individual frames to be served for labeling. Images will be randomly selected and served as frames.
