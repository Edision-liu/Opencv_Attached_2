import sys
from array import array

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from MainFromUI import Ui_Ui_MainWindow

import urllib.request
import urllib.error
import time
import numpy as np
import math
from scipy import misc, ndimage

http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
key = "daCr04BQtm-WwFGgbRLb_6Y1JIsVf_jq"
secret = "ARyKuHQ7ZxoUI4xJIeUa46sXKUqYz-K4"


class PyQtMainEntry(QMainWindow, Ui_Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.camera = cv2.VideoCapture(0)
        self.is_camera_opened = False  # 摄像头有没有打开标记

        # 定时器：30ms捕获一帧
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(30)

    def btnOpenCamera_Clicked(self):
        '''
        打开和关闭摄像头
        '''

        self.is_camera_opened = ~self.is_camera_opened
        if self.is_camera_opened:
            # capture = cv2.VideoCapture(0)
            # while 1:
            #     ret, frame = capture.read()
            #     cv2.imshow('frame', frame)
            #     if cv2.waitKey(1) == ord('q'):
            #         break
            self.btnOpenCamera.setText("关闭摄像头")
            self._timer.start()
        else:
            self.btnOpenCamera.setText("打开摄像头")
            self._timer.stop()

    def btnCapture_Clicked(self):
        """
        捕获图片
        """
        # 摄像头未打开，不执行任何操作
        if not self.is_camera_opened:
            print("摄像头未打开！")
            return
        # img = cv2.imread('u.png')
        # self.captured = img
        _, self.captured = self.camera.read()
        self.Rotate_image = self.captured
        print('保存摄像头采集图片...')
        cv2.imwrite("me.jpg", self.captured)
        print('已保存')

        # 后面这几行代码几乎都一样，可以尝试封装成一个函数
        rows, cols, channels = self.captured.shape
        bytesPerLine = channels * cols
        # Qt显示图片时，需要先转换成QImgage类型
        self.captured = cv2.cvtColor(self.captured, cv2.COLOR_BGR2RGB)
        QImg = QImage(self.captured.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
        self.labelCapture.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelCapture.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        print("尝试连接face++...")
        filepath = r"E:\AI\my______Python__my_BigData\python___CodeBlock\untitled\Opencv_Attached\User_Interface\me.jpg"
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        data.append('--%s' % boundary)
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
        data.append(key)

        data.append('--%s' % boundary)
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
        data.append(secret)

        data.append('--%s' % boundary)
        fr = open(filepath, 'rb')
        data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
        data.append('Content-Type: %s\r\n' % 'application/octet-stream')
        data.append(fr.read())
        fr.close()

        data.append('--%s' % boundary)
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
        data.append('1')

        data.append('--%s' % boundary)
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
        data.append(
            "gender,age,smiling,emotion,beauty")

        data.append('--%s--\r\n' % boundary)

        for i, d in enumerate(data):
            if isinstance(d, str):
                data[i] = d.encode('utf-8')

        http_body = b'\r\n'.join(data)

        # build http request
        req = urllib.request.Request(url=http_url, data=http_body)

        # header
        req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

        try:
            # post data to server
            resp = urllib.request.urlopen(req, timeout=15)
            # get response
            qrcont = resp.read()
            # if you want to load as json, you should decode first,
            # for example: json.loads(qrount.decode('utf-8'))
            print(qrcont.decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(e.read().decode('utf-8'))
        print("链接成功")
        mydict = eval(qrcont)
        self.faces = mydict["faces"]
        self.face_num = mydict['face_num']
    def btnReadImage_Clicked(self):
        """
        从本地读取图片 文件路径不能有中文
        """
        # 打开文件选取对话框
        filename, _ = QFileDialog.getOpenFileName(self, '打开图片')
        if filename:
            self.captured = cv2.imread(str(filename))
            # OpenCV图像以BGR通道存储，显示时需要从BGR转到RGB
            self.captured = cv2.cvtColor(self.captured, cv2.COLOR_BGR2RGB)

            rows, cols, channels = self.captured.shape
            bytesPerLine = channels * cols
            QImg = QImage(self.captured.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
            self.labelCapture.setPixmap(QPixmap.fromImage(QImg).scaled(
                self.labelCapture.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def btnGray_Clicked(self):
        """
        灰度化
        """
        # 如果没有捕获图片，则不执行操作
        if not hasattr(self, "captured"):
            return
        self.cpatured = cv2.cvtColor(self.captured, cv2.COLOR_RGB2GRAY)
        rows, columns = self.cpatured.shape
        bytesPerLine = columns
        # 灰度图是单通道，所以需要用Format_Indexed8
        QImg = QImage(self.cpatured.data, columns, rows, bytesPerLine, QImage.Format_Indexed8)
        self.labelResult.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelResult.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def btnThreshHold_Clicked(self):
        """
        Otsu自动阈值分割
        """
        if not hasattr(self, "captured"):
            return

        _, self.cpatured = cv2.threshold(
            self.cpatured, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        rows, columns = self.cpatured.shape
        bytesPerLine = columns
        # 阈值分割图也是单通道，也需要用Format_Indexed8
        QImg = QImage(self.cpatured.data, columns, rows, bytesPerLine, QImage.Format_Indexed8)
        self.labelResult.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelResult.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    @QtCore.pyqtSlot()
    def _queryFrame(self):
        """
        循环捕获图片
        """
        ret, self.frame = self.camera.read()
        img_rows, img_cols, channels = self.frame.shape
        bytesPerLine = channels * img_cols

        cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB, self.frame)
        QImg = QImage(self.frame.data, img_cols, img_rows, bytesPerLine, QImage.Format_RGB888)
        self.labelCamera.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelCamera.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def btnGetFace_Clicked(self):
        if not self.faces:
            self.label_sex.setText("no faces detected")
            self.label_age.setText("no faces detected")
            self.label_emotion.setText("no faces detected")
            return
        capture = self.captured
        Face1 = self.faces[0]["face_rectangle"]

        face1 = [[Face1["top"], Face1['left'], Face1['width'], Face1['height']]]
        print('数组1构成完毕')
        print(face1)
        face1 = np.array(face1)
        print(face1)
        for (y, x, w, h) in face1:
            cv2.rectangle(capture, (x, y), (x + w, y + h), (0, 255, 0), 2)
        print('保存图片...')
        capture = cv2.cvtColor(capture, cv2.COLOR_BGR2RGB)
        cv2.imwrite("./a.png", capture)

        rows, cols, channels = capture.shape
        bytesPerLine = channels * cols
        # Qt显示图片时，需要先转换成QImgage类型
        capture = cv2.cvtColor(capture, cv2.COLOR_BGR2RGB)  # self.captured 已经在capture时颜色转换过了,
                                                            # 但是上面保存图片的时候又转换了，在此还要转换
        QImg = QImage(capture.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
        self.labelCapture_Face.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelCapture_Face.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.label_faceCount.setText("检测到人脸个数：" + str(self.face_num))
    def btnGetAge_Clicked(self):
        if not self.faces:
            return
        print("Age")
        # faceNum = len(self.faces)
        # x = str(faceNum) + '\n'
        attributes = self.faces[0]['attributes']
        age = attributes['age']
        age = age['value']
        # print("age: " + age)   错误输出!!!要转成str()!!!
        self.label_age.setText(str(age))

    def btnGetSex_Clicked(self):
        if not self.faces:
            return
        print("Sex")
        attributes = self.faces[0]['attributes']
        gender = attributes["gender"]
        gender = gender["value"]
        self.label_sex.setText(gender)

    def btnGetEmotion_Clicked(self):
        if not self.faces:
            return
        print("Emotion")
        # faceNum = len(self.faces)
        # x = str(faceNum) + '\n'
        attributes = self.faces[0]['attributes']
        emotion = attributes['emotion']
        print(max(emotion.values()))
        for k, v in emotion.items():
            if v == max(emotion.values()):
                emotion_result = k
        self.label_emotion.setText(str(emotion_result))
        '''
        anger = emotion['anger']
        disgust = emotion['disgust']
        fear = emotion['fear']
        happiness = emotion['happiness']
        neutral = emotion['neutral']
        sadness = emotion['sadness']
        surprise = emotion['surprise']
        a = ([anger, disgust, fear, happiness, neutral, sadness, surprise])
        print(max(a))
        if max(a) == anger:
            self.label_emotion.setText("anger")
        if max(a) == disgust:
            self.label_emotion.setText("disgust")
        if max(a) == fear:
            self.label_emotion.setText("fear")
        if max(a) == happiness:
            self.label_emotion.setText("happiness")
        if max(a) == neutral:
            self.label_emotion.setText("neutral")
        if max(a) == sadness:
            self.label_emotion.setText("sadness")
        if max(a) == surprise:
            self.label_emotion.setText("surprise")
        '''
    def btnGetSmileValue_Clicked(self):
        if not self.faces:
            return
        smileValue = self.faces[0]['attributes']['smile']['value']
        self.label_smileValue.setText(str(smileValue))

    def btnRotate_Clicked(self):
        if not self.faces:
            return

        landmark = self.faces[0]["landmark"]
        left_eye_center = landmark["left_eye_center"]
        right_eye_center = landmark["right_eye_center"]
        print(left_eye_center, right_eye_center)
        t = float(right_eye_center["y"] - left_eye_center['y']) / (right_eye_center["x"] - left_eye_center["x"])
        print(t)
        rotate_angle = math.degrees(math.atan(t))
        if rotate_angle > 45:
            rotate_angle = -90 + rotate_angle
        elif rotate_angle < -45:
            rotate_angle = 90 + rotate_angle
        print("rotate_angle : " + str(rotate_angle))
        # frame[left_eye_center["x"]-10:left_eye_center["x"]+10, left_eye_center['y']-10:left_eye_center['y']+10, 2] = 0
        rotate_img = ndimage.rotate(self.Rotate_image, rotate_angle)
        # cv2.imshow("img", rotate_img)
        rows, cols, channels = rotate_img.shape
        bytesPerLine = channels * cols
        rotate_img = cv2.cvtColor(rotate_img, cv2.COLOR_BGR2RGB)
        # Qt显示图片时，需要先转换成QImgage类型
        QImg = QImage(rotate_img.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
        self.labelHough.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelHough.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PyQtMainEntry()

    # 还得重设对象名，才能显示背景图片？？问题未解决
    # 设置对象名称
    window.setObjectName("MainWindow")
    # #todo 1 设置窗口背景图片
    window.setStyleSheet("#MainWindow{border-image:url(E:/1.jpg);}")

    window.show()
    sys.exit(app.exec_())
