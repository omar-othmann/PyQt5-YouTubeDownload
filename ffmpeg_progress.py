# FFpmeg progress
# wroted by: Omar Othman
# 2018/06/02, 10:08 PM
import re
import subprocess
import math
import platform
from shutil import which
import os
import time
file_path = os.path.dirname(os.path.realpath(__file__))
class ProgressFFmpeg(object):
    def __init__(self):
        self.callback = None
        self.already_ex = "Output file is already exists, please delete it first. and try agian!"
        self.error_callback_msg = """
You need to set callback function example:
def function_callback(precent, current, total):
    # your code here
    

run = ProgressFFmpeg()
run.run("ffmpeg command", callback=function_callback, inputs=path_filename, outputs=path_filename)
or
run = ProgressFFmpeg()
run.set_callback(function_callback)
run.set_output(path_filename)
run.set_input(path_filename)
run.run("ffmpeg command")
"""
        self.percent = 0
        self.re_duration = re.compile('Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})[^\d]*', re.I)
        self.re_position = re.compile('time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})\d*', re.U | re.I)
        self.total = None
        self.time = None
        self.is_windows = False
        self.is_allow = False
        arch, name = self.get_info()
        if not name.count("Windows"):
            print("""
Warning: Your System is not Windows
You need to download ffmpeg:

Mac OS:

brew install ffmpeg

Linux:
If you're using Ubuntu 14.04 :
1- sudo add-apt-repository ppa:mc3man/trusty-media
2- sudo apt-get update
3- sudo apt-get install ffmpeg gstreamer0.10-ffmpeg
If you're using Ubuntu 15.04 :
1- sudo apt-get install ffmpeg

another System search on google:
how install ffmpeg in <Your System name>
""")
            self.is_windows = False
            self.is_allow = True if which("ffmpeg") else False
        else:
            self.is_windows = True
            self.is_allow = True
        self.arch = arch
        self.path = file_path + "/library/"+self.arch+"/"
        self.outputs = None
        self.inputs = None
    def run(self, cmd, outputs=None, inputs=None, callback=None):
        if not self.is_allow:
            raise Exception("You need to install ffmpeg first")
        self.callback = callback if callback else self.callback
        self.outputs = outputs if outputs else self.outputs
        self.inputs = inputs if inputs else self.inputs
        if not callable(self.callback) or not self.inputs or not self.outputs:
            raise Exception(self.error_callback_msg)
        try:
            os.remove(self.outputs)
            print("putput file is already exists. has been deleted!")
        except OSError:
            pass
        cmd += ' "'+self.inputs+'" "'+self.outputs+'"'
        if self.is_windows:
            cmd = self.path + cmd
        pipe = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines = True)
        while True:
            line = pipe.stdout.readline().strip()
            if line == '' and pipe.poll() is not None:
                break
            if self.total is None:
                self.total = self.get_duration(line)
            self.time = self.get_time(line)
            if self.time is None:
                continue
            percent, current, total = self.get_perecent(self.total, self.time)
            self.callback(percent, current, total)
        self.callback(100, 0, 0)
        pipe.kill()
        try: os.remove(self.inputs)
        except: pass
            
    def set_callback(self, callback):
        self.callback = callback

    def get_duration(self, string):
        if string.count("Duration"):
            result = self.re_duration.match(string)
            result = str(result.group(0)).split()
            result = result[1].replace(",", "")
            return result
        return None
    def get_time(self, string):
        if string.count("time="):
            result = self.re_position.search(string)
            result = str(result.group(0)).replace("time=", "")
            return result
        return None

    def get_perecent(self, a, b):
        a = a.split(":")
        b = b.split(":")
        a1, a2, a3 = self.get_int(a)
        b1, b2, b3 = self.get_int(b)
        a_total = a1 * 3600 + a2 * 60 + a3
        b_total = b1 * 3600 + b2 * 60 + b3
        res = self.get_result(b_total, a_total)
        return res, b_total, a_total
        
    def get_result(self, how, total):
        return int(how / total * 100)
    
    def get_int(self, _list: list):
        f = "("
        for x in _list:
            if len(x) <= 2:
                f += str(int(x))+","
            else:
                f += str(int(float(x)))+","
        f = f[:-1]
        f += ")"
        return eval(f)

    def get_info(self):
        return platform.architecture()

    def set_output(self, filename):
        self.outputs = filename

    def set_input(self, filename):
        self.inputs = filename

    
        

def progress(percent, current, total):
    print(str(percent)+"%", current, total)

"""inp = "F:\project\downloaded/Nassif Zeytoun - Sawt Rbaba (Audio)  ناصيف زيتون - صوت ربابة.mp4"
out = "F:\project\downloaded/Nassif Zeytoun - Sawt Rbaba (Audio)  ناصيف زيتون - صوت ربابة.mp3"
run = ProgressFFmpeg()
run.set_callback(progress)
run.set_output(out)
run.set_input(inp)
run.run("ffmpeg -i")"""

