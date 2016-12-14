# coding: utf-8
import binascii
import sys
sys.setrecursionlimit(1000000)

with open("practice_midi/UN.mid", 'rb') as f:
    str = f.read()
    hexlify = binascii.hexlify(str)

midi_ary = [hexlify[i:i+2].decode('utf-8').upper() for i in range(0, len(hexlify), 2)]
print(midi_ary)

class MidiParser():
    def __init__(self,midi_ary):
        self.midi_ary = midi_ary
        self.truck_ary = []
        self.data_ary = []
        self.header = {}
        self.truck = {}
        self.meta = {}
        self.result = []

    def parse_head(self):
        if self.midi_ary[0] == "4D" and self.midi_ary[1] == "54" and \
                        self.midi_ary[2] == "68" and self.midi_ary[3] == "64":
            self.header = {
                'chunk_type': self.midi_ary[0:4],
                'header_size': self.midi_ary[4:8],
                'format': self.midi_ary[8:10],
                'track': self.midi_ary[10:12],
                'time_unit': self.midi_ary[12:14]
            }
            self.truck_ary = self.midi_ary[14:]
        else:
            print('形式エラーです')

    def parse_truck(self):
        if self.truck_ary[0] == "4D" and self.truck_ary[1] == "54" \
                and self.truck_ary[2] == "72" and self.truck_ary[3] == "6B":
            self.truck = {
                'truck_chunk': self.truck_ary[0:4],
                'data_length': self.truck_ary[4:8],
            }
            self.data_ary = self.truck_ary[8:]

    def parse_data(self):
        delta_time = self.get_deltatime()
        event_data = self.get_event()
        print(delta_time)
        print(event_data)
        self.result.append({
            'delta_time': delta_time,
            'event_data': event_data
        })
        #print(self.result)
        if len(self.data_ary) > 0:
            self.parse_data()
        else:
            print("Done!")


    def get_deltatime(self):
        i = 0
        tmp_bit = 0
        while eval('0x' + self.data_ary[i]) >= 0x80:
            a = eval('0x' + self.data_ary[i]) ^ (1 << 7)
            tmp_bit = (a << 7)
            i += 1
        delta_bit = tmp_bit | eval('0x' + self.data_ary[i])
        print(self.data_ary[i])
        print(delta_bit)
        self.data_ary = self.data_ary[i+1:]
        return delta_bit

    def get_event(self):
        data = {}
        status_byte = self.data_ary[0]
        bin2int = eval('0x' + status_byte)
        if bin2int == 0xFF:
            size = eval('0x' + self.data_ary[2])
            self.data_ary = self.data_ary[3+size:]

        elif 0x80 <= bin2int <= 0x9F:
            data["bool"] = True
            data["channel"] = self.data_ary[0]
            data["note"] = self.data_ary[1]
            data["velocity"] = self.data_ary[2]
            self.data_ary = self.data_ary[3:]

        elif 0x9F < bin2int:
            if 0xA0 <= bin2int <= 0xAF:
                self.data_ary = self.data_ary[3:]

            if 0xB0 <= bin2int <= 0xBF:
                if self.data_ary[1] == 0x00 and self.data_ary[4] == 0x20:
                    self.data_ary = self.data_ary[6:]
                else:
                    self.data_ary = self.data_ary[3:]

            if 0xC0 <= bin2int <= 0xDF:
                self.data_ary = self.data_ary[2:]

            if 0xE0 <= bin2int <= 0xEF:
                self.data_ary = self.data_ary[3:]

            if bin2int == 0xF0:
                i = 0
                while eval(self.data_ary[i]) != 0xF7:
                    i += 1
                self.data_ary = self.data_ary[i+2:]

            if bin2int == 0xF1 or bin2int == 0xF3:
                self.data_ary = self.data_ary[2:]

            if bin2int == 0xF2:
                self.data_ary = self.data_ary[3:]

        if len(data) == 0:
            data["bool"] = False

        return data

midi = MidiParser(midi_ary)
midi.parse_head()
midi.parse_truck()
print("-------header-------")
print(midi.header)
print("-------chunk--------")
print(midi.truck)
print("--------------------")
print("-------midi---------")
midi.parse_data()
print(midi.result)
print("--------------------")
print("Done!")