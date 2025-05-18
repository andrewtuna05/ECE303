import struct
import time

class Packet():
    PROBE, ACK, START, DV = range(4)

    def __init__(self, source_port, dest_port, seq_num, packet_type, data=None):
        self.source_port = int(source_port)
        self.dest_port = int(dest_port)
        self.seq_num = int(seq_num)
        self.packet_type = packet_type # 0 for probe, 1 for ACK, 2 for start, 3 for DV
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
        elif self.packet_type == Packet.ACK or self.packet_type == Packet.START:
            self.data = None

        elif self.packet_type == Packet.DV:  # DV
            # data is a dict mapping dest_port to cost
            if not isinstance(data, dict):
                raise ValueError("DV packet needs dict {destPort: cost}")
            self.dv_entries = data
            self.data = None
            self.dv_time = time.time()

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

        if self.packet_type == Packet.ACK or self.packet_type == Packet.START:  # ACK or START
            return struct.pack(">BHHIB", self.packet_type, self.source_port,  self.dest_port, self.seq_num, 0)
        
        if self.packet_type == Packet.DV:  # DV
            entries = self.dv_entries
            k = len(entries)
            header = struct.pack( ">BHHH", Packet.DV, self.source_port, self.dest_port, k)
            payload = b"".join(struct.pack(">Hf", dest, cost)
                for dest, cost in entries.items()
            )

            return header + payload
        # ACK and start packets have no data
        header = struct.pack(">BHHIB", self.packet_type, self.source_port, self.dest_port, self.seq_num, 0)
        return header

    def bytes_to_packet(data_bytes): 
        ptype = data_bytes[0]
        if ptype == Packet.DV:  # DV
            _, src, dst, k = struct.unpack(
                ">BHHH", data_bytes[:7]
            )
            entries = {}
            off = 7
            for _ in range(k):
                dest, cost = struct.unpack(
                    ">Hf", data_bytes[off:off+6]
                )
                entries[dest] = cost
                off += 6
            pkt = Packet(src, dst, 0, Packet.DV, entries)
            return pkt

        if len(data_bytes) != 10:
            raise ValueError(f"Invalid packet length: {len(data_bytes)} bytes")

        packet_type, source_port, dest_port, seq_num, data_val = struct.unpack(">BHHIB", data_bytes)

        # check packet types ==> if probe -> add data, if ack -> return
        if packet_type == Packet.PROBE:
            data = bytes([data_val])
            return Packet(source_port, dest_port, seq_num, Packet.PROBE, data)
        elif packet_type == Packet.ACK:
            return Packet(source_port, dest_port, seq_num, Packet.ACK, None)
        elif packet_type == Packet.START:
            return Packet(source_port, dest_port, seq_num, Packet.START, None)
        else:
            raise ValueError(f"unknown packet type: {packet_type}")