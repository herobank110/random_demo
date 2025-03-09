from PySide6 import QtCore, QtWidgets, QtGui


def generate_image(size: QtCore.QSize, number: int):
    image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(image)
    painter.setBrush(QtGui.QBrush("#aaaaaa"))
    painter.drawRect(0, 0, size.width(), size.height())
    painter.setPen(QtGui.QPen("#000000"))
    painter.drawText(QtCore.QRect(QtCore.QPoint(), size), QtCore.Qt.AlignCenter, f"Image {number:04d}")
    return image

class Gallery(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        NUM_COLS = 3
        NUM_IMAGES = 10_000

        vbox1 = QtWidgets.QVBoxLayout(self)
        vbox1.setContentsMargins(0, 0, 0, 0)
        vbox1.setSpacing(0)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        vbox1.addWidget(scroll_area)

        scroll_inner = QtWidgets.QWidget()
        scroll_area.setWidget(scroll_inner)

        grid1 = QtWidgets.QGridLayout(scroll_inner)
        grid1.setContentsMargins(0, 0, 0, 0)
        grid1.setSpacing(0)

        image = generate_image(QtCore.QSize(240, 120), 0)
        for i in range(NUM_IMAGES):
            label = QtWidgets.QLabel()
            label.setPixmap(QtGui.QPixmap.fromImage(image))
            grid1.addWidget(label, i // NUM_COLS, i % NUM_COLS)
        
        # grid1.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding), 2, 2, 3)

        # Spacers to fill the available area, so the images don't stretch.
        stretch_row_index = NUM_IMAGES // NUM_COLS + 1
        grid1.addWidget(QtWidgets.QLabel(styleSheet="background-color:red"), stretch_row_index, 0, 1, NUM_COLS)
        grid1.setRowStretch(stretch_row_index, 1)
        stretch_col_index = NUM_COLS + 1
        grid1.addWidget(QtWidgets.QLabel(styleSheet="background-color:red"), 0, stretch_col_index, NUM_COLS, 1)
        grid1.setColumnStretch(stretch_col_index, 1)


def main():
    app = QtWidgets.QApplication()
    # window = QtWidgets.QWidget()
    # window.show()

    gallery = Gallery()
    gallery.setMinimumSize(800, 600)
    gallery.show()

    app.exec()


if __name__ == "__main__":
    main()
