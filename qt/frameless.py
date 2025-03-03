from PySide6 import QtCore, QtWidgets, QtGui, Extra


def main():
    app = QtWidgets.QApplication()
    window = QtWidgets.QWidget()
    window.setWindowFlags(QtCore.Qt.FramelessWindowHint)# | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
    # window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    window.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
