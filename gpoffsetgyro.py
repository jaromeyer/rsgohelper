import re
import sys

if len(sys.argv) != 2:
    print("usage: gpoffsetgyro.py <inputfile.mp4>")
    sys.exit()

r = open(sys.argv[1], "r+b")
s = r.read()
index = [m.start() for m in re.finditer(b'\x47\x59\x52\x4F', s)]

for i in index:
    sample_count = int.from_bytes(s[i + 6:i + 8], "big")
    for l in range(sample_count):
        data_index = i + l * 6 + 8
        
        roll = int.from_bytes(s[data_index:data_index + 2], "big")
        pitch = int.from_bytes(s[data_index + 2:data_index + 4], "big")
        yaw = int.from_bytes(s[data_index + 4:data_index + 6], "big")
    
        print("yaw: %i, pitch: %i, roll: %i" % (roll, pitch, yaw))

        # write roll (horizon axis)
        r.seek(data_index)
        r.write(roll.to_bytes(2, byteorder='big'))

        # write pitch
        r.seek(data_index + 2)
        r.write(pitch.to_bytes(2, byteorder='big'))

        # write yaw
        r.seek(data_index + 4)
        r.write(yaw.to_bytes(2, byteorder='big'))
