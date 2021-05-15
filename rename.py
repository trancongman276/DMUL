import os
import glob

path = "E:\\Video\\The Big Bang Theory Season 1-11 Complete 720p\\The Big Bang Theory Season 5"
baseName = "The Big Bang Theory S05E"
for i, file in enumerate(glob.glob(f"{path}\\*.srt")):
    if i+1 < 10:
        index = f"0{i+1}"
    else:
        index = i+1
    changedName = f"{path}\\{baseName}{index}.srt"
    os.rename(file, changedName)