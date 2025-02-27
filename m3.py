from PySide6 import QtWidgets, QtGui, QtCore
import re


def to_style_sheet(style_dict):
    return "".join(f"{k}:{v};" for k, v in style_dict.items())


class Button(QtWidgets.QPushButton):
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

    def resizeEvent(self, event):
        return super().resizeEvent(event)

    def event(self, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            print("Button pressed")
        return super().event(event)


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
    app.exec_()


if __name__ == "__main__":
    main()
