import random
import abc
import functools
from typing import Dict, List, Optional
from PySide6 import QtCore, QtWidgets, QtGui


def generate_image(size: QtCore.QSize, number: int):
    image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(image)
    gradient = QtGui.QLinearGradient(0, 0, size.width(), size.height())
    gradient.setColorAt(0, QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gradient.setColorAt(1, QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    painter.setBrush(QtGui.QBrush(gradient))
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
    def __init__(self):
        self._recycler: Optional["RecyclerView"] = None

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

    def get_bound_view(self, index: Index) -> Optional[QtWidgets.QWidget]:
        """Returns a view bound to the given index, or None if not bound."""
        return self._recycler.get_bound_view(index) if self._recycler else None


class RecyclerView(QtWidgets.QScrollArea):
    """A scrollable container used to efficiently show a large number of items."""

    _NUM_EXCESS_VIEWS = 3
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
        self.recycler.setParent(inner)
        self.recycler.move(0, 0)
        self.recycling_vbox = QtWidgets.QVBoxLayout(self.recycler)
        self.recycling_vbox.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.recycling_vbox.setContentsMargins(0, 0, 0, 0)
        self.recycling_vbox.setSpacing(0)

    def set_adapter(self, adapter: RecyclerViewAdapter):
        self._adapter = adapter
        self._adapter._recycler = self

        # TODO: move to other function
        item_height = self._get_item_size_hint().height()
        total_height = item_height * self._adapter.get_num_items()
        self.widget().setFixedHeight(total_height)

    def get_bound_view(self, index: Index) -> Optional[QtWidgets.QWidget]:
        """Returns a view bound to the given index, or None if not bound."""
        return self._bound_views.get(index)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)

        # TODO: move to update fn?
        self.recycler.setFixedWidth(self.widget().width())
        self._bind_and_show()

    def _bind_and_show(self):
        view_height = self.height()
        item_height = self._get_item_size_hint().height()
        view_top = self.verticalScrollBar().value()
        view_bottom = view_top + view_height
        total_num_items = self._adapter.get_num_items()
        total_items_height = total_num_items * item_height
        partially_exposed_top = view_top % item_height
        buffered_view_top = (
            view_top
            - partially_exposed_top
            - min(self._NUM_EXCESS_VIEWS, view_top // item_height) * item_height
        )
        buffered_view_bottom = min(
            total_items_height, view_bottom + item_height * self._NUM_EXCESS_VIEWS
        )

        def item_at(height: int):
            return height // item_height

        def view_indexes_needed():
            return list(map(item_at, range(buffered_view_top, buffered_view_bottom, item_height)))

        needed_indexes = view_indexes_needed()

        # recycle old views
        for index in list(self._bound_views.keys()):
            if index not in needed_indexes:
                view = self._bound_views.pop(index)
                self._unbound_views.append(view)
        # bind new views
        for index in needed_indexes:
            if index not in self._bound_views:
                view = self._take_fresh_view()
                self._adapter.bind_view(view, index)
                self._bound_views[index] = view
        # layout items
        for view in self._unbound_views + list(self._bound_views.values()):
            self.recycling_vbox.removeWidget(view)
            view.hide()
        for index in needed_indexes:
            view = self._bound_views[index]
            self.recycling_vbox.addWidget(view)
            view.show()
        self.recycler.move(0, buffered_view_top)

    def _get_fresh_view(self) -> QtWidgets.QWidget:
        """Get an unbound view, or create one if none available."""
        if not self._unbound_views:
            self._create_view()  # Ensure at least one exists.
        return self._unbound_views[0]

    def _take_fresh_view(self) -> QtWidgets.QWidget:
        """Get a fresh view to be bound immediately (not added to pool)."""
        view = self._get_fresh_view()  # This ensures it's in the pool.
        self._unbound_views.remove(view)  # Now remove it.
        return view

    def _create_view(self):
        """Create a new view and add it to the pool."""
        view = self._adapter.create_view()
        view.setParent(self.recycler)
        view.hide()  # is this needed?
        self._unbound_views.append(view)
        return view

    def _get_item_size_hint(self):
        return self._get_fresh_view().sizeHint()

    def scrollContentsBy(self, dx, dy):
        # Called when the scroll area is scrolled.
        super().scrollContentsBy(dx, dy)
        self._bind_and_show()


class MyListAdapter(RecyclerViewAdapter):
    def __init__(self, data):
        self.data = data
        self.images = {}

    def _load_image(self, index: int):
        image = QtGui.QPixmap.fromImage(generate_image(QtCore.QSize(240, 120), index))
        self.images[index] = image
        view = self.get_bound_view(index)
        if view:
            # item may have been scrolled out of view already
            self.bind_view(view, index)

    def create_view(self) -> QtWidgets.QWidget:
        label = QtWidgets.QLabel()
        label.setFixedSize(QtCore.QSize(240, 120))
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return label

    def bind_view(self, view: QtWidgets.QWidget, index: Index) -> None:
        label: QtWidgets.QLabel = view
        if index in self.images:
            # show already loaded image
            label.setPixmap(self.images[index])
            label.setText("")
        else:
            # load image (simulate loading delay)
            label.setPixmap(QtGui.QPixmap())
            label.setText("Loading...")
            QtCore.QTimer.singleShot(500, functools.partial(self._load_image, index))

    def get_num_items(self) -> int:
        return len(self.data)


class MyList(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        vbox1 = QtWidgets.QVBoxLayout(self)
        vbox1.setContentsMargins(0, 0, 0, 0)
        vbox1.setSpacing(0)

        recycler_view = RecyclerView()
        data = [f"{i}" for i in range(20_000)]
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
