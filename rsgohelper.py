from shutil import copyfile
from tkinter import *
from tkinter import filedialog, messagebox

outputfile = ""


def selectfile():
    global outputfile
    inputfile = filedialog.askopenfilename(title="Select a video to patch",
                                           filetypes=(("GoPro MP4 Files", "*.mp4"),))
    outputfile = inputfile[:-4] + "_patched.MP4"
    copyfile(inputfile, outputfile)


def patch():
    try:
        r = open(outputfile, "r+b")
    except FileNotFoundError:
        messagebox.showerror(title="Error", message="No input file specified")
    else:
        s = r.read()
        accl = [m.start() for m in re.finditer(b'\x41\x43\x43\x4c', s)]

        samples = 0
        for i in accl:
            sample_count = int.from_bytes(s[i + 6:i + 8], "big")
            for l in range(sample_count):
                data_index = i + l * 6 + 8
                y = int.from_bytes(s[data_index:data_index + 2], byteorder='big', signed=True)
                x = int.from_bytes(s[data_index + 2:data_index + 4], byteorder='big', signed=True)
                z = int.from_bytes(s[data_index + 4:data_index + 6], byteorder='big', signed=True)
                samples += 1
                print("sample %i - y: %i, x: %i, z: %i" % (samples, y, x, z))

                # write y (front/back)
                if yAxis.get() == "front/back":
                    value = y
                elif yAxis.get() == "right/left":
                    value = x
                elif yAxis.get() == "up/down":
                    value = z

                if yInv.get() == 1:
                    value = -value
                r.seek(data_index)
                r.write(value.to_bytes(2, byteorder='big', signed=True))

                # write x (right/left)
                if xAxis.get() == "front/back":
                    value = y
                elif xAxis.get() == "right/left":
                    value = x
                elif xAxis.get() == "up/down":
                    value = z

                if xInv.get() == 1:
                    value = -value
                r.seek(data_index + 2)
                r.write(value.to_bytes(2, byteorder='big', signed=True))

                # write z (up/down)
                if zAxis.get() == "front/back":
                    value = y
                elif zAxis.get() == "right/left":
                    value = x
                elif zAxis.get() == "up/down":
                    value = z

                if zInv.get() == 1:
                    value = -value
                r.seek(data_index + 4)
                r.write(value.to_bytes(2, byteorder='big', signed=True))

        r.close()
        messagebox.showinfo(title="Done", message="Successfully patched %i accelerometer samples" % samples)


root = Tk()
root.title("RSGOHelper by jaromeyer")

mainframe = Frame(root)
mainframe.pack()

yAxis = StringVar(root)
xAxis = StringVar(root)
zAxis = StringVar(root)

axes = {'front/back', 'right/left', 'up/down'}

yAxis.set('front/back')
xAxis.set('right/left')
zAxis.set('up/down')

yInv = IntVar()
xInv = IntVar()
zInv = IntVar()

Button(mainframe, text="Select File", command=selectfile).grid(row=1, column=1)
Button(mainframe, text="Patch Accl Data", command=patch).grid(row=1, column=2)

Label(mainframe, text="Sensor Orientation:").grid(row=2, column=1)
Label(mainframe, text="Mainboard Orientation:").grid(row=2, column=2)

Label(mainframe, text="front/back").grid(row=3, column=1)
OptionMenu(mainframe, yAxis, *axes).grid(row=3, column=2)
Checkbutton(mainframe, text="invert", variable=yInv).grid(row=3, column=3)

Label(mainframe, text="right/left").grid(row=4, column=1)
OptionMenu(mainframe, xAxis, *axes).grid(row=4, column=2)
Checkbutton(mainframe, text="invert", variable=xInv).grid(row=4, column=3)

Label(mainframe, text="up/down").grid(row=5, column=1)
OptionMenu(mainframe, zAxis, *axes).grid(row=5, column=2)
Checkbutton(mainframe, text="invert", variable=zInv).grid(row=5, column=3)

root.mainloop()
