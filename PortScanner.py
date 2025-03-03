import socket
import argparse
import sys

#Function to perform port scan
def scan_port(ip, port):
    #AF_INET = internet address family for IPv4 and SOCK_STREAM = socket type for TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1) #1 Second Timeout
    result = sock.connect_ex((ip, port))
    sock.close() #close the socket
    return result == 0

#Function to display help_msg
def help_msg():
    help_text = """
    Input to run the Port Scanner on Command Line: python3 PortScanner.py [option1, ..., option N]

    Available options:
        --ports <[ports to scan: port1, port2, ...]>                    (Scans Ports [1-1024] by default)
        --ip <IP address to scan>                                       (Scans localhost by defualt)
        --input <file name>
        --output <file name>                                            (Outputs to console by default)
        --help                                                          (Display this prompt again!)
    """
    print(help_text)

#Function to retrieve port number and common name associated
def get_service_port(port):
    try:
        return socket.getservbyport(port, 'tcp')
    except OSError: #If no common name for port number- leave blank
        return ""

#Function to get ports from input list
def get_ports(args):
    if args.ports:
        try:
            #Record the input ports from list
            return [int(p.strip()) for p in args.ports.split(',')]
        except ValueError:
            print("Error: Please separate INTEGER inputs with commas")
            sys.exit(1)
    else:
        #Default ports 1 to 1024
        return list(range(1, 1025))

#Function to parse through input file
def process_input_file(filename):
    targets = []
    with open(filename, "r") as file: #parse through file and record content
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t') #Split line into 3 parts
            ip, port_start, port_end = parts 

            try:
                port_start = int(port_start)
                port_end = int(port_end)
            except ValueError: #Assuming the file is valid and follows proper structure
                continue
            targets.append((ip, port_start, port_end))
    return targets

#Function to format output for multiple inputs
def scan_targets_input(ip, start_port, end_port):
    out_lines = []
    out_lines.append(f"Address: {ip}")
    out_lines.append(f"Ports: {start_port}--{end_port}")
    out_lines.append(f"Displaying open ports on: {ip}")
    open_ports = []
    for port in range(start_port, end_port + 1): #Check which ports are open
        if scan_port(ip, port):
            open_ports.append(port)
    if open_ports:
        for p in open_ports:
            service = get_service_port(p) #If we can find a common name, append it to display
            if service:
                out_lines.append(f"Port {p}: OPEN {service}")
            else:
                out_lines.append(f"Port {p}: OPEN")
    else:
        out_lines.append("No open ports found")
    out_lines.append("")
    return out_lines

#Function to format output for one input
def scan_target(ip, ports, port_display):
    out_lines = []
    out_lines.append(f"Address: {ip}")
    out_lines.append(f"Ports: {port_display}")
    out_lines.append(f"Showing open ports on: {ip}") 
    open_ports = []
    for port in ports:
        if scan_port(ip, port):
            open_ports.append(port)
    if open_ports:
        for p in open_ports:
            service = get_service_port(p) #If we can find a common name, append it to display
            if service:
                out_lines.append(f"Port {p}: OPEN {service}")
            else:
                out_lines.append(f"Port {p}: OPEN")
    else:
        out_lines.append("No open ports found")
    out_lines.append("")
    return out_lines
    
def main():
    parser = argparse.ArgumentParser(add_help = False)
    parser.add_argument("--ports", type=str)
    parser.add_argument("--ip", type =str, default = "127.0.0.1") #Default IP address of localhost
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--help", action="store_true")
    
    args = parser.parse_args()

    if args.help:
        help_msg()
        sys.exit(0) #Terminate program
    
    results = [] #Contain content to display or add to output file at the end

    if args.input:
        targets = process_input_file(args.input)
        for ip, start_port, end_port in targets:
            results.extend(scan_targets_input(ip, start_port, end_port))
    
    else:
        ip = args.ip
        ports_list = get_ports(args)
        if args.ports is None:
            port_display = "1-1024"
        else:
            port_display = args.ports
        results.extend(scan_target(ip, ports_list, port_display))

    output_text = "\n".join(results)
    if args.output:
        with open(args.output, "w") as outfile:
            outfile.write(output_text + "\n")
    else:
        print(output_text)

if __name__ == "__main__":
    main()
