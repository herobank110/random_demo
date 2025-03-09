from abc import abstractmethod
from collections import abc
from typing import Dict, List, Optional
from PySide6 import QtCore, QtWidgets, QtGui


def generate_image(size: QtCore.QSize, number: int):
    image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(image)
    painter.setBrush(QtGui.QBrush("#aaaaaa"))
    painter.drawRect(0, 0, size.width(), size.height())
    painter.setPen(QtGui.QPen("#000000"))
    painter.drawText(QtCore.QRect(QtCore.QPoint(), size), QtCore.Qt.AlignCenter, f"Image {number:04d}")
    return image



Index = int

class RecyclerViewAdapter(metaclass=abc.ABCMeta):
    @abstractmethod
    def create_view(self) -> QtWidgets.QWidget:
        """Create a fresh, empty item.

        Its size hint will indicate how much space to allocate for the items.
        """
    
    @abstractmethod
    def bind_view(self, view: QtWidgets.QWidget, index: Index) -> None:
        """Bind a widget, potentially one that is being recycled."""
    
    @abstractmethod
    def get_size(self) -> int:
        """Return the number of items in the dataset."""

class RecyclerView(QtWidgets.QScrollArea):
    """A scrollable container used to efficiently show a large number of items."""

    def __init__(self):
        super().__init__()
        self._NUM_EXCESS_VIEWS = 2
        """The number of views outside of the visible area to prepare for quick scrolling."""

        self._adapter: Optional[RecyclerViewAdapter] = None
        """The adapter aka delegate."""

        self._views_pool: List[QtWidgets.QWidget] = []
        """Views that have been created but aren't in use."""

        self._bound_views: Dict[Index, QtWidgets.QWidget] = {}
        """Views that are currently bound to an item in the dataset."""
        
        # TODO is this needed?
        self.setWidgetResizable(True)

        inner = QtWidgets.QWidget()
        self.setWidget(inner)

        # TODO list only for now, later grid too
        self.recycler = QtWidgets.QWidget()
        self.recycler.setParent(self)
        self.recycler.move(0, 0)
        self.recycler.show()
        self.recycling_vbox = QtWidgets.QVBoxLayout()
        self.recycling_vbox.setContentsMargins(0, 0, 0, 0)
        self.recycling_vbox.setSpacing(0)

        # for index in range(10):
        #     self.inner_layout.addWidget(QtWidgets.QLabel(f"Item {index}"))

    def set_adapter(self, adapter: RecyclerViewAdapter):
        self._adapter = adapter

        # TODO: move to other function
        item_height = self._get_item_size_hint().height()
        total_height = item_height * self._adapter.get_size()
        self.widget().setFixedHeight(total_height)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        self._ensure_enough_views_exist()
        self._bind_and_show()

    def _bind_and_show(self):
        for index in range(10):
            view = self._get_fresh_view()
            self._adapter.bind_view(view, index)
            self.recycling_vbox.addWidget(view)
            view.show()
            self._bound_views[index] = view

    def _ensure_enough_views_exist(self):
        """Ensure that there are enough views to fill the visible area."""

        item_height = self._get_item_size_hint().height()
        total_possible_bound_views = self.height() // item_height + self._NUM_EXCESS_VIEWS

        # Even if there are less items than views, create some empty
        # ones since RecyclerView is typically used for large datasets.
        while len(self._bound_views) + len(self._views_pool) < total_possible_bound_views:
            self._create_view()

    def _get_fresh_view(self) -> QtWidgets.QWidget:
        """Get an unbound view, or create one if none available."""
        if not self._views_pool:
            self._create_view()  # Ensure at least one exists.
        return self._views_pool[0]

    def _create_view(self):
        """Create a new view and add it to the pool."""
        view = self._adapter.create_view()
        self._views_pool.append(view)
        return view

    def _get_item_size_hint(self):
        return self._get_fresh_view().sizeHint()

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
    my_list.resize(400, 600)
    my_list.show()

    # gallery = Gallery()
    # gallery.setMinimumSize(800, 600)
    # gallery.show()

    app.exec()


if __name__ == "__main__":
    main()
