## ECE303 Programming Assignment #1

This is an implementation of a TCP Port Scanner for Professor Levin's Spring 2025 ECE303

To run this program, enter into the command line:
```console
python3 scanner.py [option1, option2, ..., optionN]
```

This program comes with few options listed down below:

- `--ports <ports to scan>`
    - By default, ports `1-1024` will be scanned
    - Please separate port numbers by commas 
        - e.g. To select port 20 and 80: `--port 20, 80`

- `--ip <IP address to scan>`
    - By default, the ports of `localhost` will be scanned
    - Please input the listed target host 

 - `--input <filename>`
    - Please have the input as a `.txt file` in the same directory
    - This program will read a list of IP addresses and port ranges specified
    - Please have the contents of the input file in this format: <IP address> \t <port start> \t <port end>

- `--output <filename>`
    - By default, the output will be printed to the console, otherwise will generate a plain-text file with the listed file name

- `--help`
    - Use this command to display a brief message listing functionality, available features, and usage syntax

Files:
---
- PortScanner.py: Contains functions and main code to run TCP Port Scanner

Resources Used: 
---
https://docs.python.org/3/library/socket.html
https://docs.python.org/3/library/argparse.html#argparse.Namespace
https://www.stationx.net/common-ports-cheat-sheet/