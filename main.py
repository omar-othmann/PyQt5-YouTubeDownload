# download mp3, mp4 from youtube using FFmpeg and pafy

# Wroted by: Omar Othman
# 2018/06/02, 9:12 PM


from pytube import YouTube
from PyQt5.uic import loadUiType
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import QApplication
import os
import sys
import urllib.request as ur
from ffmpeg_progress import ProgressFFmpeg
MAIN,_ = loadUiType(os.path.join(os.path.dirname(__file__), "main.ui"))
scriptDir = os.path.dirname(os.path.realpath(__file__))
class Threading(QThread):
    progress_dow = pyqtSignal(int, str)
    progress_cov = pyqtSignal(int, str)
    avatar_bytes = pyqtSignal(bytes, str)
    def __init__(self, parent=None, mp3=False, data=False, url=None):
        QThread.__init__(self, parent)
        self.mp3 = mp3
        self.data = data
        self.url = url
        self.save_file = os.path.dirname(os.path.realpath(__file__))+"/downloaded"
    def run(self):
        try: yt = YouTube(self.url)
        except:
            self.progress_dow.emit(0, "<html><body><center>Link error</center></body></html>")
            return
        yt.register_on_progress_callback(self.download_callback)
        yt.register_on_complete_callback(self.on_complete_callback)
        if self.data:
            if not yt.thumbnail_url:
                return
            b = ur.urlopen(yt.thumbnail_url).read()
            self.avatar_bytes.emit(b, yt.title)
            return
        if self.url:
            if self.mp3:
                yt.streams.filter(only_audio=True).first().download(self.save_file)
            else:
                yt.streams.filter(resolution="360p", subtype='mp4').first().download(self.save_file)
            return
    def download_callback(self, stream, chunk, file, byte):
        download = stream.filesize - byte
        total = stream.filesize
        i = self.get_result(download, total)
        form = "<html><body><center>{} bytes remaining out of {} bytes</center></body></html>".format(byte, stream.filesize)
        self.progress_dow.emit(i, form)
    def on_complete_callback(self, stream, file):
        if self.mp3:
            name = file.name
            name = os.path.basename(name)
            run = ProgressFFmpeg()
            run.set_callback(self.on_progress_FF)
            run.set_output(self.save_file + "/"+name.replace(".mp4", ".mp3"))
            run.set_input(self.save_file + "/"+name)
            run.run("ffmpeg -i")
    def on_progress_FF(self, i, current, total):
        form = "<html><body><center>Convert to mp3: {}%, {} from {}</center></body></html>".format(i, current, total)
        self.progress_cov.emit(i, form)
    def get_result(self, how, total):
        return int(how / total * 100)
class YouTubeWindow(QMainWindow, MAIN):
    def __init__(self, parent=None):
        super(YouTubeWindow, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        QApplication.clipboard().dataChanged.connect(self.on_clipboard)
        self.default()
        self.mp3 = False
        self.downloading = False
        
    def on_mp3_click(self):
        text = self.url.text()
        if not text:
            QMessageBox.information(self, "Copy or write", "Copy the link from the browser or place the link into filed")
        else:
            self.mp3 = True
            t = Threading(self, mp3=True, url=self.url.text())
            t.progress_dow.connect(self.on_progress_download)
            t.progress_cov.connect(self.on_prgoress_ffpmeg)
            t.start()
            self.dow_mp3.setEnabled(False)
            self.dow_mp4.setEnabled(False)
            self.url.setEnabled(False)
            self.download_msg.setText("<html><body><center>Connecting.. Please wait</center></body></html>")
    def on_mp4_click(self):
        text = self.url.text()
        if not text:
            QMessageBox.information(self, "Copy or write", "Copy the link from the browser or place the link into filed")
        else:
            self.mp3 = False
            t = Threading(self, url=self.url.text())
            t.progress_dow.connect(self.on_progress_download)
            t.start()
            self.dow_mp3.setEnabled(False)
            self.dow_mp4.setEnabled(False)
            self.url.setEnabled(False)
            self.download_msg.setText("<html><body><center>Connecting.. Please wait</center></body></html>")
    def on_load_info(self):
        if not self.is_youtube(self.url.text()):
            return
        t = Threading(self, data=True, url=self.url.text())
        t.avatar_bytes.connect(self.on_load_data)
        t.start()
        self.dow_mp3.setEnabled(False)
        self.dow_mp4.setEnabled(False)
        self.title.hide()
        self.download_msg.setText("<html><body><center>Check link...</center></body></html>")
    def on_text_change(self, text):
        self.on_load_info()
    def on_load_data(self, byte, title):
        if byte is None:
            self.on_load_info()
            return
        QApplication.processEvents()
        image = QImage()
        image.loadFromData(byte)
        bitmap = QPixmap(image)
        self.title.show()
        self.title.setText(title)
        self.avatar.setPixmap(bitmap)
        self.dow_mp3.setEnabled(True)
        self.dow_mp4.setEnabled(True)
        self.download_msg.setText("<html><body><center>Ready to download</center></body></html>")
    def default(self):
        self.url.setPlaceholderText("Copy the link from the browser or place the link here")
        self.dow_mp3.clicked.connect(self.on_mp3_click)
        self.dow_mp4.clicked.connect(self.on_mp4_click)
        self.url.textChanged.connect(self.on_text_change)
    def on_clipboard(self):
        text = QApplication.clipboard().text()
        if self.is_youtube(text):
            self.url.setText(text)
            self.on_load_info()
    def on_progress_download(self, i, speed):
        self.progressBar.setValue(i)
        self.download_msg.setText(speed)
        if i == 100:
            self.progressBar.setValue(0)
            if not self.mp3:
                self.download_msg.setText("<html><body><center>Downloaded!</center></body></html>")
                self.url.setEnabled(True)
                self.dow_mp3.setEnabled(True)
                self.dow_mp4.setEnabled(True)
            else:
                self.download_msg.setText("<html><body><center>Wait..</center></body></html>")
    def on_prgoress_ffpmeg(self, i, formating):
        self.progressBar.setValue(i)
        self.download_msg.setText(formating)
        if i == 100:
            self.download_msg.setText("<html><body><center>Done!</center></body></html>")
            self.progressBar.setValue(0)
            self.url.setEnabled(True)
            self.dow_mp3.setEnabled(True)
            self.dow_mp4.setEnabled(True)
    def is_youtube(self, text):
        return True if text.startswith("https://youtube.com/") or text.startswith("https://www.youtube.com") else False
    
def main():
    app=QApplication(sys.argv)
    window = YouTubeWindow()
    window.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'logo.png'))
    window.show()
    app.exec_()

if __name__ == "__main__": main()

