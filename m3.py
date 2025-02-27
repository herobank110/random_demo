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

        self.ripple_pos = None
        # Dynamic property for animation.
        self.setProperty("ripple_lerp", 0.0)

    def resizeEvent(self, event):
        self.refresh_view()
        return super().resizeEvent(event)

    def mousePressEvent(self, e):
        self.ripple_pos = e.pos()

        anim = QtCore.QPropertyAnimation()
        anim.setParent(self)
        anim.setTargetObject(self)
        anim.setPropertyName(b"ripple_lerp")
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(200)
        anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        # def on_finished():
        #     self.ripple_pos = None
        #     self.setProperty("ripple_lerp", 0)
        # anim.finished.connect(on_finished)
        anim.start()

        return super().mousePressEvent(e)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.ripple_pos:
            painter = QtGui.QPainter(self)
            clip_path = QtGui.QPainterPath()
            min_dimension = min(self.size().width(), self.size().height())
            clip_path.addRoundedRect(self.rect(), min_dimension // 2, min_dimension // 2)
            painter.setClipPath(clip_path)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 100)))
            painter.setPen(QtCore.Qt.NoPen)
            max_dimension = max(self.size().width(), self.size().height())
            lerp = lambda a, b, x: a + (b - a) * x
            size = lerp(20, max_dimension, self.property("ripple_lerp"))
            painter.drawEllipse(self.ripple_pos, size, size)

    def event(self, e):
        if e.type() == QtCore.QEvent.DynamicPropertyChange:
            print(e.propertyName())
            if e.propertyName().data().decode() == "ripple_lerp":
                self.update()
                return True
        return super().event(e)

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
