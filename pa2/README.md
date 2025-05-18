# Programming Assignment 2 - Go-Back-N and Distance Vector Algorithms

Completed under supervision of Professor Levin during the Spring 2025 Semester at The Cooper Union.

This program implements a simple Python-based network simulator where nodes (uniquely identified by a UDP listening port number) first synchronize via a START flood and then use Go-Back-N to send reliable probe packets and estimate per-link loss which are treated as link weights. Finally a Bellman–Ford distance-vector routing protocol is run with these link-weights to build and update each node’s routing tables using UDP to exchange the routing table information among the nodes in the network. These routing tables are then written to different text files.


To run this program, open up 4 terminals for each of the 4 nodes to run. Then use the following syntax on the command line:
```console
python3 networknode.py <local-port> receive <neighbor1-port> <loss-rate-1> ... <neighbor-M-port> <loss-rate-M> send <neighbor(M+1)-port> ... <neighbor(N)-port> [last]
```

### Syntax:
- `<local-port>`: UDP listening port number of the node (must be >1024).
- `receive`: Current node will be the **probe receiver** from the following neighbors.
- `<neighbor#-port>`: UDP listening port number of one of the neighboring nodes
- `<loss-rate-#>` Probability to drop the probe backets from this neighbor
    - Loss rate # is directly tied to the neighbor port #
- `send`: Current node will be the **probe sender** to the following neighbors
- `last`: Indication of the last node being loaded to the network. With this input, the network is considered complete and all nodes will begin exchanging packets.
- `ctrl+C`: Used to exit program

### Example usage:
![Example Network Config](images/example_network.png)

The network above will be applied to four different terminal instances with the following strucutre:
```console
Terminal 1: $ python3 networknode.py 1111 receive send 2222 3333 (receiving list is empty)
Terminal 2: $ python3 networknode.py 2222 receive 1111 .1 send 3333 4444
Terminal 3: $ python3 networknode.py 3333 receive 1111 .5 2222 .2 send 4444
Terminal 4: $ python3 networknode.py 4444 receive 2222 .8 3333 .5 send last (sending list is empty)
```
- Credit to Professor Levin for the syntax and example usage

Files:
---
- Node.py: Implements `Node` class with Go-Back-N logic and Bellman Ford distance vector routing
- Packet.py: Defines a fixed-length packet header and routines to pack/unpack DATA, ACK, START, and DV messages over UDP.  
- networknode.py: Contains functions to parses through command-line arguments, initilize network, and main to run this program.
- terminal**X**output.txt: Contains the Terminal output for each node where **X** is from 1 ... 4.

References:
---
- Kurose & Ross, Computer Networking: A Top-Down Approach, Chapter 3.4.3 (Go-Back-N Algorithm) and 4.2.2 (Distance-Vector Algorithm)
