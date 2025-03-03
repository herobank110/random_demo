import sys

'''
from PyQt5.QtWidgets import QMenuBar, QHBoxLayout, QPushButton, QApplication, QWidget, QMainWindow
from PyQt5.QtCore import Qt, pyqtSlot as Slot
from PyQt5.QtGui import QCursor
'''

from PySide2.QtWidgets import QMenuBar, QHBoxLayout, QPushButton, QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, QSizePolicy
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QCursor

import ctypes as ct
from ctypes import windll
from ctypes.wintypes import MSG, RECT


HTCAPTION = 2

WM_NCCALCSIZE = 131
WM_NCHITTEST = 132

HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17
HTMAXBUTTON = 9
HTMINBUTTON = 8
HTCLOSE = 20


class MARGINS(ct.Structure):
    _fields_ = [('cxLeftWidth', ct.c_int),
                ('cxRightWidth', ct.c_int),
                ('cyTopHeight', ct.c_int),
                ('cyBottomHeight', ct.c_int)]

    
class Example(QWidget):
    
    def __init__(self):
        super().__init__()

        self._bwidth = 8
        self._theight = 20
        
        # self.hbox = QHBoxLayout(self)
        top_bar = QWidget(styleSheet="background-color: rgba(220, 220, 70, 200);")
        top_bar.setFixedHeight(400)
        self.hbox = QHBoxLayout(top_bar)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(0)
        self.hbox.setAlignment(Qt.AlignTop)
        self.hbox.setSizeConstraint(QHBoxLayout.SetFixedSize)

        self.menuBar = QPushButton('Hello!')
        # menu = self.menuBar.addMenu('Hello!')
        # menu.addAction('World!')
        self.menuBar.setFixedHeight(40)
        # self.menuBar.setFixedWidth(400)
        # self.menuBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.hbox.addWidget(self.menuBar)

        # self.btnClose = QPushButton('X')
        # self.btnClose.clicked.connect(self.on_btnClose_clicked)
        # self.hbox.addWidget(self.btnClose)
        
        self.setGeometry(300, 300, 250, 150)

        self.hWnd = ct.c_int(self.winId())
        
        # self.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet('background-color: transparent;')
        # self.setStyleSheet('background-color: rgba(220, 220, 70, 100);')
        # self.setWindowOpacity(0.5)
        # self.setStyleSheet('background-color: rgba(220, 220, 70, 200);margin: 20px;padding:20px;')
        # self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_NoBackground)
        # self.setAttribute(Qt.WindowTransparentForInput)
        # self.setWindowFlags(Qt.WindowTransparentForInput)
        # self.setAttribute(Qt.BACKGROU)
        # self.setMouseTracking(False)

        vl = QVBoxLayout(self)
        # vl.setContentsMargins(0, 40, 0, 0)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)
        vl.addWidget(top_bar)
        vl.addWidget(QLabel("hi", styleSheet="background-color:red;"), stretch=1)

        # margins = MARGINS(1, 1, 1, 1)
        margins = MARGINS(-1, -1, -1, -1)
        # margins = MARGINS(-10, -10, -10, -10)
        windll.dwmapi.DwmExtendFrameIntoClientArea(self.hWnd, ct.byref(margins))

    @Slot()
    def on_btnClose_clicked(self):
        self.close()
        
    # def paintEvent(self, event):
    #     pass
        
    def nativeEvent(self, eventType, message):
        # return super().nativeEvent(eventType, message)
        try:
            # FIX: QTBUG-69074
            msg = MSG.from_address(int(message))

            if msg.message == WM_NCCALCSIZE:
                # ret_val = super().nativeEvent(eventType, message)
                # print("WM_NCCALCSIZE: ", ret_val)
                # return ret_val

                self.repaint()
                print('WM_NCCALCSIZE: True, 0')
                return True, 0
            elif msg.message == WM_NCHITTEST:
                # make the borders and title bar transparents so that they are
                # handled by the native parent window
                
                wr = RECT()
                windll.user32.GetWindowRect(msg.hWnd, ct.byref(wr))
                
                x = (msg.lParam & 0xFFFF)
                y = (msg.lParam >> 16)

                borderWidth = 8

                # check if we are on a side or corner (for resizing)
                if (wr.left <= x < wr.left + borderWidth and
                    wr.bottom > y >= wr.bottom - borderWidth):
                    print('WM_NCHITTEST: True, HTBOTTOMLEFT')
                    return True, HTBOTTOMLEFT
                elif (wr.right > x >= wr.right - borderWidth and
                      wr.bottom > y >= wr.bottom - borderWidth):
                    print('WM_NCHITTEST: True, HTBOTTOMRIGHT')
                    return True, HTBOTTOMRIGHT
                elif (wr.left <= x < wr.left + borderWidth and
                    wr.top <= y < wr.top + borderWidth):
                    print('WM_NCHITTEST: True, HTBOTTOMLEFT')
                    return True, HTTOPLEFT
                elif (wr.right > x >= wr.right - borderWidth and
                      wr.top <= y < wr.top + borderWidth):
                    print('WM_NCHITTEST: True, HTBOTTOMRIGHT')
                    return True, HTTOPRIGHT
                elif wr.left <= x < wr.left + borderWidth:
                    print('WM_NCHITTEST: True, HTLEFT')
                    return True, HTLEFT
                elif wr.right > x >= wr.right - borderWidth:
                    print('WM_NCHITTEST: True, HTRIGHT')
                    return True, HTRIGHT
                elif wr.bottom > y >= wr.bottom - borderWidth:
                    print('WM_NCHITTEST: True, HTBOTTOM')
                    return True, HTBOTTOM
                elif wr.top <= y < wr.top + borderWidth:
                    print('WM_NCHITTEST: True, HTTOP')
                    return True, HTTOP
                # elif QApplication.instance().widgetAt(QCursor.pos()) == self.menuBar:
                #     print('WM_NCHITTEST: True, HTCAPTION')
                #     return True, HTCAPTION
                # elif self.mapFromGlobal(QCursor.pos()).y() < 40 and self.mapFromGlobal(QCursor.pos()).x() < 60:
                #     print('WM_NCHITTEST: True, HTCAPTION', self.mapFromGlobal(QCursor.pos()).x())
                #     return True, HTCAPTION
                elif self.mapFromGlobal(QCursor.pos()).y() < 40:
                    
                    if self.mapFromGlobal(QCursor.pos()).x() < 60:
                        print('WM_NCHITTEST: True, HTCAPTION', self.mapFromGlobal(QCursor.pos()).x())
                        return True, HTCAPTION
                    else:
                        right = self.width() - self.mapFromGlobal(QCursor.pos()).x()
                        if right < 60:
                            self.update()
                            return True, HTCLOSE
                        if right < 120:
                            self.update()
                            return True, HTMAXBUTTON
                        if right < 180:
                            self.update()
                            return True, HTMINBUTTON
                        # print('WM_NCHITTEST: True, HTMAXBUTTON', self.mapFromGlobal(QCursor.pos()).x(), self.width())
                        # return True, HTMAXBUTTON
                # else:
                    # print("WM_NC_HITTEST: NATIVE")
                    # return super().nativeEvent(eventType, message)

        except Exception as e:
            print(str(e))

        return False, 0

app = QApplication(sys.argv)

ex = Example()
ex.show()

sys.exit(app.exec_())
