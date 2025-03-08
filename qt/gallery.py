import abc
from typing import Dict, List, Optional
from PySide6 import QtCore, QtWidgets, QtGui


def generate_image(size: QtCore.QSize, number: int):
    image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(image)
    painter.setBrush(QtGui.QBrush("#aaaaaa"))
    painter.drawRect(0, 0, size.width(), size.height())
    painter.setPen(QtGui.QPen("#000000"))
    painter.drawText(
        QtCore.QRect(QtCore.QPoint(), size),
        QtCore.Qt.AlignCenter,
        f"Image {number:04d}",
    )
    return image


Index = int


class RecyclerViewAdapter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_view(self) -> QtWidgets.QWidget:
        """Create a fresh, empty item.

        Its size hint will indicate how much space to allocate for the
        items, and is assumed to be constant for all items.
        """

    @abc.abstractmethod
    def bind_view(self, view: QtWidgets.QWidget, index: Index) -> None:
        """Bind a widget, potentially one that is being recycled."""

    @abc.abstractmethod
    def get_num_items(self) -> int:
        """Return the number of items in the dataset."""


class RecyclerView(QtWidgets.QScrollArea):
    """A scrollable container used to efficiently show a large number of items."""

    _NUM_EXCESS_VIEWS = 2
    """The number of views outside of the visible area to prepare for quick scrolling."""

    def __init__(self):
        super().__init__()

        self._adapter: Optional[RecyclerViewAdapter] = None
        """The adapter aka delegate."""

        self._unbound_views: List[QtWidgets.QWidget] = []
        """Views that have been created but aren't in use."""

        self._bound_views: Dict[Index, QtWidgets.QWidget] = {}
        """Views that are currently bound to an item in the dataset."""

        self.setWidgetResizable(True)

        inner = QtWidgets.QWidget()
        self.setWidget(inner)

        # TODO list only for now, later grid too
        self.recycler = QtWidgets.QWidget()
        self.recycler.setParent(self)
        self.recycler.move(0, 0)
        self.recycling_vbox = QtWidgets.QVBoxLayout(self.recycler)
        self.recycling_vbox.setContentsMargins(0, 0, 0, 0)
        self.recycling_vbox.setSpacing(0)

        # for index in range(10):
        #     self.recycling_vbox.addWidget(QtWidgets.QLabel(f"Item {index}"))

    def set_adapter(self, adapter: RecyclerViewAdapter):
        self._adapter = adapter

        # TODO: move to other function
        item_height = self._get_item_size_hint().height()
        total_height = item_height * self._adapter.get_num_items()
        self.widget().setFixedHeight(total_height)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)

        self.recycler.setFixedWidth(self.widget().width())
        # self.recycler.adjustSize()
        # self.recycler.update()

        self._ensure_enough_views_exist()
        self._bind_and_show()

    def _bind_and_show(self):
        print(
            f"{self.height():03d} {self.verticalScrollBar().value():03d} {self.verticalScrollBar().value() / self.verticalScrollBar().maximum():3.3f} {self._get_item_size_hint().height():03d}\r",
            end="",
        )
        return
        for index in range(len(self._adapter.data)):
            view = self._get_fresh_view()
            self._adapter.bind_view(view, index)
            self._bound_views[index] = view
            self._unbound_views.remove(view)
            self.recycling_vbox.addWidget(view)

            # view.show()
            # self.recycler.adjustSize()
            # # self.recycling_vbox.update()

    def _ensure_enough_views_exist(self):
        """Ensure that there are enough views to fill the visible area."""

        item_height = self._get_item_size_hint().height()
        total_possible_bound_views = self.height() // item_height + self._NUM_EXCESS_VIEWS

        # Even if there are less items than views, create some empty
        # ones since RecyclerView is typically used for large datasets.
        while len(self._bound_views) + len(self._unbound_views) < total_possible_bound_views:
            self._create_view()

    def _get_fresh_view(self) -> QtWidgets.QWidget:
        """Get an unbound view, or create one if none available."""
        if not self._unbound_views:
            print("created")
            self._create_view()  # Ensure at least one exists.
        return self._unbound_views[0]

    def _create_view(self):
        """Create a new view and add it to the pool."""
        view = self._adapter.create_view()

        view.setParent(self.recycler)  # prevent GC?
        view.hide()  # is this needed?

        self._unbound_views.append(view)
        return view

    def _get_item_size_hint(self):
        return self._get_fresh_view().sizeHint()

    def scrollContentsBy(self, dx, dy):
        # Called when the scroll area is scrolled.
        super().scrollContentsBy(dx, dy)
        self._bind_and_show()
        self.recycler.move(0, -self.verticalScrollBar().value())


class MyListAdapter(RecyclerViewAdapter):
    def __init__(self, data):
        self.data = data

    def create_view(self) -> QtWidgets.QWidget:
        label = QtWidgets.QLabel()
        label.setFixedHeight(100)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return label

    def bind_view(self, view: QtWidgets.QWidget, index: Index) -> None:
        view.setText(self.data[index])
        view.setStyleSheet(f"background-color: {'#888888' if index % 2 == 0 else '#666666'}")

    def get_num_items(self) -> int:
        return len(self.data)


class MyList(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        vbox1 = QtWidgets.QVBoxLayout(self)
        vbox1.setContentsMargins(0, 0, 0, 0)
        vbox1.setSpacing(0)

        recycler_view = RecyclerView()
        data = [f"Item {i + 1:04d}" for i in range(5)]
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
        grid1.addWidget(
            QtWidgets.QLabel(styleSheet="background-color:red"),
            stretch_row_index,
            0,
            1,
            NUM_COLS,
        )
        grid1.setRowStretch(stretch_row_index, 1)
        stretch_col_index = NUM_COLS + 1
        grid1.addWidget(
            QtWidgets.QLabel(styleSheet="background-color:red"),
            0,
            stretch_col_index,
            NUM_COLS,
            1,
        )
        grid1.setColumnStretch(stretch_col_index, 1)


def main():
    app = QtWidgets.QApplication()
    # window = QtWidgets.QWidget()
    # window.show()

    my_list = MyList()
    my_list.resize(400, 250)
    my_list.show()

    # gallery = Gallery()
    # gallery.setMinimumSize(800, 600)
    # gallery.show()

    app.exec()


if __name__ == "__main__":
    main()
