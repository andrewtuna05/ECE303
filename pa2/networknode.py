import sys
import threading
import time

from Node import Node

ip = "localhost"

def process_input(argv):

    if len(argv) < 2:
        print(f"Usage: {argv[0]} <my_port> [receive <ports>...] [send <ports>...]")
        sys.exit(1)

    last_seen = False
    my_port = int(argv[1])
    send_ports = []
    recv_ports = []

    i = 2
    # print(sys.argv)
    while i < len(argv):
        if argv[i] == "receive":
            i += 1
            while i < len(argv) and argv[i].isdigit():
                recv_ports.append((int(argv[i]), float(argv[i+1])))
                i += 2
        elif argv[i] == "send":
            i += 1

            while i < len(argv) and argv[i].isdigit():
                send_ports.append(int(argv[i]))
                i += 1

            # for the "last" keyword to start node exchange
            if i < len(argv) and argv[i] == "last":
                last_seen = True
                i += 1
        else:
            print(f"Warning: unrecognized token '{argv[i]}', skipping")
            i += 1

    return my_port, send_ports, recv_ports, last_seen

if __name__ == "__main__":
    my_port, send_ports, recv_ports, last_seen = process_input(sys.argv)

    print(f"my port is: {my_port}")
    print(f"send ports are: {send_ports}")
    print(f"recv ports are: {recv_ports}")

    # create a different thread for each of the recievers
    node = Node(ip, my_port, send_ports, recv_ports)

    # start global receiver which won't recieve messages
    # just here so that it will get the kick to start sending
    t0 = threading.Thread(target=node.run_receiver, args=(my_port, 0), daemon=True, name=f"recv-{my_port}-GLOBAL")
    t0.start()

    # start receiver threads unconditionally
    for port, p in recv_ports:
        # is not daemon thread so will always listen as long as program doesn't exit
        t = threading.Thread(target=node.run_receiver, args=(port, p), daemon=True, name=f"recv-{my_port}-{port}")
        t.start()
        print(f"[{my_port}] Started recv-thread on port {port} (p={p})")

    # if not "last" node, wait for signal
    if not last_seen:
        print(f"[{my_port}] waiting for global START …")
        node.start_event.wait()
    else:
        # sleep to make sure all receivers are running
        time.sleep(1)
        node.broadcast_start()
        node.start_event.set()
    
    #once started fire senders*exactly once per neighbor
    for port in send_ports:
        #print(f"[{my_port}] Starting sender to port {port}")
        node.run_sender(port)