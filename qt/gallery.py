from PySide6 import QtCore, QtWidgets, QtGui


def generate_image(size: QtCore.QSize):
    image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(image)
    painter.setBrush(QtGui.QBrush("#aaaaaa"))
    painter.drawRect(0, 0, size.width(), size.height())
    painter.setPen(QtGui.QPen("#000000"))
    painter.drawText(QtCore.QRect(QtCore.QPoint(), size), QtCore.Qt.AlignCenter, "Image 0001")
    return image


def main():
    app = QtWidgets.QApplication()
    # window = QtWidgets.QWidget()
    # window.show()

    image = generate_image(QtCore.QSize(240, 180))
    label = QtWidgets.QLabel()
    label.setPixmap(QtGui.QPixmap.fromImage(image))
    label.show()

    app.exec()


if __name__ == "__main__":
    main()
