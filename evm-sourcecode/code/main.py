#..................................
#........Visualisierung 2..........
#..................................
#...Eulerian Video Magnification...
#..................................
#.. Author: Galya Pavlova..........
#..................................


import os
import sys
import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.uic import loadUi

import butterworth_filter
import ideal_filter


class App(QDialog):

    def __init__(self):
        '''
        Initializes and loads the GUI PyQt file
        '''
        super(App, self).__init__()
        self.vid = None
        self.name = None
        self.capture = None
        self.len = None
        self.l = 0
        loadUi('gui.ui', self)
        self.startButton.clicked.connect(self.on_start_clicked)
        self.lButton.clicked.connect(self.open_file)
        self.playButton.clicked.connect(self.play_video)


    def play_video(self):
        '''
        A function to play a given video
        '''
        self.capture = cv2.VideoCapture(self.videoOut)
        frame_rate = self.capture.get(cv2.CAP_PROP_FPS)
        self.len = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.dispayImage)
        self.timer.start(frame_rate)

    def dispayImage(self):
        '''
        Each video frame is read and loaded
        '''
        self.l += 1

        if self.l >= self.len:
            self.timer.stop()
            self.timer.deleteLater()
            self.l = 0

        ret, img = self.capture.read()
        qformat = QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], qformat)
        outImage = outImage.rgbSwapped()
        self.video.setPixmap(QPixmap.fromImage(outImage))

    def open_file(self):
        '''
        Opens Files
        '''
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Video File', '../', 'All Files(*)')
        if filename:
            self.vid = filename
            base = os.path.basename(filename)
            self.name = os.path.splitext(base)[0]
            self.nameLabel.setText(base)

    def on_start_clicked(self):
        '''
        Reads the input from the GUI and uses the parameters to start the program
        '''
        self.finished.clear()
        QApplication.instance().processEvents()

        alpha = float(self.alpha.text())
        cutoff = float(self.cutoff.text())
        low = float(self.low.text())
        high = float(self.high.text())
        chromAttenuation = float(self.chromAtt.text())
        linearAttenuation = self.linearAtt.isChecked()
        mode = self.comboBox.currentIndex()

        if mode == 0:
            butterworth_filter.start(self.vid, alpha, cutoff, low, high, linearAttenuation, chromAttenuation, self.name)
        else:
            if mode == 1:
                ideal_filter.start(self.vid, alpha, low, high, chromAttenuation, self.name)

        self.finished.setText('Done!')

        self.videoOut = self.name+"Out.avi"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.setWindowTitle('Eulerian Video Magnification')
    window.show()
    sys.exit(app.exec_())

