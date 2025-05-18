import struct

class Packet():
    PROBE, ACK, START, DV = range(4)

    def __init__(self, source_port, dest_port, seq_num, packet_type, data=None):
        self.source_port = int(source_port)
        self.dest_port = int(dest_port)
        self.seq_num = int(seq_num)
        self.packet_type = packet_type # 0 for probe, 1 for ACK, 2 for start
        
        if packet_type == Packet.PROBE:
            # if data is a string encode it
            if isinstance(data, str):
                if len(data) != 1:
                    raise ValueError("Probe packet data must be a single character")
                self.data = data.encode()

            # if data already in bytes keep it the same
            elif isinstance(data, bytes):
                if len(data) != 1:
                    raise ValueError("Probe packet data must be a single character")
                self.data = data

            else:
                raise ValueError(f"invalid data type for probe packet: {type(data)}")

        # data field empty for ACK packets
        elif packet_type in (Packet.ACK, Packet.START):
            self.data = None

        elif packet_type == Packet.DV:
            # data must be a dict {dest_port: cost}
            if not isinstance(data, dict):
                raise ValueError("DV packet needs a dict {dest_port: cost}")
            self.dv_entries = data
            self.data = None    
        
        else:
            raise ValueError(f"invalid packet type: {packet_type}")

    def packet_to_bytes(self):
        # >: big endian
        # h: short = 16 bits ==> 2 bytes
        # i: int = 32 bits ==> 4 bytes
        # b: char = 8 bits ==> 1 byte
        # caps = unsigned

        # add data if it's a probe packet
        if self.packet_type == Packet.PROBE:
            data_val = self.data[0] if self.data else 0
            header = struct.pack(">BHHIB", self.packet_type, self.source_port, self.dest_port, self.seq_num, data_val)
            return header
    
        # ACK and start packets have no data
        if self.packet_type in (Packet.ACK, Packet.START):
            header = struct.pack(">BHHIB", self.packet_type, self.source_port, self.dest_port, self.seq_num, 0)
            return header
        
        if self.packet_type == Packet.DV:
            entries = self.dv_entries
            k = len(entries)
            header = struct.pack(">BHHIH", Packet.DV, self.source_port, self.dest_port, self.seq_num, k)
            payload = b"".join(struct.pack(">Hf", dest, cost) for dest, cost in entries.items())
            return header + payload
        
        #should never get here
        raise ValueError(f"Cannot serialize packet type {self.packet_type}")
    
    @staticmethod
    def bytes_to_packet(data_bytes):
        
        ptype = data_bytes[0]
        
        if ptype == Packet.DV:
            #1 + 2 + 2 + 4 + 2 = 11 bytes before the entries
            _, src, dst, seq, k = struct.unpack(">BHHIH", data_bytes[:11])
            off = 11
            entries = {}
            for _ in range(k):
                dest, cost = struct.unpack(">Hf", data_bytes[off:off+6])
                entries[dest] = cost
                off += 6
            pkt = Packet(src, dst, seq, Packet.DV, entries)
            return pkt
        
        if len(data_bytes) != 10:
            raise ValueError(f"Invalid packet length: {len(data_bytes)} bytes")

        packet_type, source_port, dest_port, seq_num, data_val = struct.unpack(">BHHIB", data_bytes)

        # check packet types ==> if probe -> add data, if ack -> return
        if packet_type == Packet.PROBE:
            data = bytes([data_val])
            return Packet(source_port, dest_port, seq_num, 0, data)
        elif packet_type == Packet.ACK:
            return Packet(source_port, dest_port, seq_num, 1, None)
        elif packet_type == Packet.START:
            return Packet(source_port, dest_port, seq_num, 2, None)
        else:
            raise ValueError(f"unknown packet type: {packet_type}")