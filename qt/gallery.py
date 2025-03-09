from abc import abstractmethod
from collections import abc
from typing import Optional
from PySide6 import QtCore, QtWidgets, QtGui


def generate_image(size: QtCore.QSize, number: int):
    image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(image)
    painter.setBrush(QtGui.QBrush("#aaaaaa"))
    painter.drawRect(0, 0, size.width(), size.height())
    painter.setPen(QtGui.QPen("#000000"))
    painter.drawText(QtCore.QRect(QtCore.QPoint(), size), QtCore.Qt.AlignCenter, f"Image {number:04d}")
    return image


class RecyclerViewAdapter(metaclass=abc.ABCMeta):
    @abstractmethod
    def create_view(self) -> QtWidgets.QWidget:
        """Create a fresh, empty item.

        Its size hint will indicate how much space to allocate for the items.
        """
    
    @abstractmethod
    def bind_view(self, view: QtWidgets.QWidget, index: int) -> None:
        """Bind a widget, potentially one that is being recycled."""
    
    @abstractmethod
    def get_size(self) -> int:
        """Return the number of items in the dataset."""


class RecyclerView(QtWidgets.QScrollArea):
    """A scrollable container used to efficiently show a large number of items."""

    def __init__(self):
        super().__init__()
        self._adapter: Optional[RecyclerViewAdapter] = None

        # TODO is this needed?
        self.setWidgetResizable(True)

        inner = QtWidgets.QWidget()
        self.setWidget(inner)

        # TODO list only for now, later grid too
        vbox1 = QtWidgets.QVBoxLayout(inner)
        vbox1.setContentsMargins(0, 0, 0, 0)
        vbox1.setSpacing(0)

    def set_adapter(self, adapter: RecyclerViewAdapter):
        self._adapter = adapter

        view = self._adapter.create_view()
        total_height = view.sizeHint().height() * self._adapter.get_size()
        self.widget().setFixedHeight(total_height)

    def scrollContentsBy(self, dx, dy):
        # Called when the scroll area is scrolled.
        super().scrollContentsBy(dx, dy)


class MyListAdapter(RecyclerViewAdapter):
    def __init__(self, data):
        self.data = data

    def create_view(self) -> QtWidgets.QWidget:
        label = QtWidgets.QLabel()
        label.setFixedHeight(50)
        return label
    
    def bind_view(self, view: QtWidgets.QWidget, index: int) -> None:
        view.setText(f"Item {index}")
    
    def get_size(self) -> int:
        return len(self.data)

class MyList(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        vbox1 = QtWidgets.QVBoxLayout(self)
        vbox1.setContentsMargins(0, 0, 0, 0)
        vbox1.setSpacing(0)

        recycler_view = RecyclerView()
        data = [f"Item {i}" for i in range(100)]
        adapter = MyListAdapter(data)
        recycler_view.set_adapter(adapter)
        vbox1.addWidget(recycler_view)


class Gallery(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        NUM_COLS = 3
        NUM_IMAGES = 100


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

        # scroll_inner.setFixedHeight(1500)

        for i in range(NUM_IMAGES):
            image = generate_image(QtCore.QSize(240, 120), i)
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

    my_list = MyList()
    my_list.setMinimumSize(800, 600)
    my_list.show()

    # gallery = Gallery()
    # gallery.setMinimumSize(800, 600)
    # gallery.show()

    app.exec()


if __name__ == "__main__":
    main()
