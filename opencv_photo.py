# coding: utf-8
import sys
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QLabel
from PyQt5.uic import loadUi
import cv2

# 默认使用0号的设备
video_capture = cv2.VideoCapture(0)
# mac 上面设置无效
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720.0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 720.0)

# 获取摄像头的宽度和高度
size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# 输出摄像头的长宽
print(size)

# 加载 opencv 自带的分类器
faceCascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')

app = QApplication(sys.argv) 

class MainWindow(QMainWindow):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        loadUi('mainwindow.ui', self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(1000 / 24)

    @pyqtSlot()
    def on_button_click(self):
        name = self.lineEdit.text()

        frame = self.get_image()
        print(frame)
        label = QLabel()
        label.setPixmap(QPixmap.fromImage(QImage(frame.data, 256, 256, QImage.Format_RGB888)));

        self.scrollArea.widget().layout().addWidget(label)
        self.lineEdit.clear()

    def get_image(self):
        ret, frame = video_capture.read()
        # TODO 假定高是 720 宽是 1280 需要后续处理
        # 截取图像中间的最大正方形
        dest = cv2.cvtColor(frame[:,280:1000], cv2.COLOR_BGR2RGB)
        # 变形为 256 x 256 的小正方形
        return cv2.resize(dest, (256,256), interpolation=cv2.INTER_CUBIC)

    def update_image(self):

        if not video_capture.isOpened():
            # 直接返回
            print('还未加载或者无法加载摄像头')
            return

        ret, frame = video_capture.read()

        # 转换成灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 使用OpenCV 自带的进行检测
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # 在人脸周围画个长方形，绿色
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # TODO 假定高是 720 宽是 1280 需要后续处理
        # 截取图像中间的最大正方形
        dest = cv2.cvtColor(frame[:,280:1000], cv2.COLOR_BGR2RGB)
        # 变形为 256 x 256 的小正方形
        destFrame = cv2.resize(dest, (256,256), interpolation=cv2.INTER_CUBIC)
        self.label.setPixmap(QPixmap.fromImage(QImage(destFrame.data, 256, 256, QImage.Format_RGB888)));

window = MainWindow()
window.show()
sys.exit(app.exec_())
