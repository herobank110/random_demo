from PySide6 import QtWidgets, QtGui, QtCore


def main():
    app = QtWidgets.QApplication()
    window = QtWidgets.QWidget()
    window.setWindowTitle("Hello World")
    window.setGeometry(100, 100, 280, 80)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
