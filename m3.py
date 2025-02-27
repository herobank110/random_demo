from PySide6 import QtWidgets, QtGui, QtCore
import re


def to_style_sheet(style_dict):
    return "".join(f"{k}:{v};" for k, v in style_dict.items())


class ThemeAwareStyle:
    """
    https://mui.com/system/getting-started/the-sx-prop/#spacing
    """
    def __init__(self):
        self._sx = {}

    sx_changed = QtCore.Signal()

    @QtCore.Property(dict)
    def sx(self):
        return self._sx

    @sx.setter
    def sx(self, value):
        self._sx = value
        self.sx_changed.emit()


class Button(QtWidgets.QPushButton, ThemeAwareStyle):
    def __init__(self):
        super().__init__()
        self._style = {
            "background-color": "white",
            "color": "black",
            "border-radius": "4px",
            "padding": "0.5em 2em",
            "font-size": "14pt",
        }
        self.setStyleSheet(to_style_sheet(self._style))
        # self.sx_changed.connect(lambda: print("hihh"))
        # self.sx = {"color": "red"}

    def resizeEvent(self, event):
        self.refresh_view()
        return super().resizeEvent(event)

    def mousePressEvent(self, e):
        pos = e.pos()
        ripple = QtWidgets.QWidget(parent=self, styleSheet="background-color: red;border-radius: 5px;")
        ripple.resize(40, 40)
        ripple.show()
        ripple.move(pos - QtCore.QPoint(20, 20))

        return super().mousePressEvent(e)

    def event(self, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            print("Button pressed")
        return super().event(event)

    def refresh_view(self):
        min_dimension = min(self.size().width(), self.size().height())
        self._style["border-radius"] = f"{min_dimension // 2}px"
        self.setStyleSheet(to_style_sheet(self._style))



def main():
    app = QtWidgets.QApplication()

    window = QtWidgets.QWidget()
    window.setWindowTitle("Hello World")
    window.setGeometry(100, 100, 280, 80)

    button = Button()
    button.setText("hi")
    button.setParent(window)
    button.move(100, 20)

    window.show()
    app.exec()


if __name__ == "__main__":
    main()
