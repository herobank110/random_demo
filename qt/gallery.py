import itertools
import math
import random
import abc
import functools
from typing import Dict, List, Optional, Union
from collections import OrderedDict
from PySide6 import QtCore, QtWidgets, QtGui


def generate_image(size: QtCore.QSize, number: int):
    image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(image)
    gradient = QtGui.QLinearGradient(0, 0, size.width(), size.height())
    gradient.setColorAt(
        0, QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    )
    gradient.setColorAt(
        1, QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    )
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


RecyclerLayout = Union[QtWidgets.QVBoxLayout, QtWidgets.QGridLayout]
"""A layout that can be used with RecyclerView."""


class RecyclerView(QtWidgets.QScrollArea):
    """A scrollable container that efficiently shows a large number of items.

    Based on the RecyclerView from Android.
    """

    _NUM_EXCESS_VIEWS = 3
    """The number of views outside of the visible area to prepare for quick scrolling."""

    def __init__(self) -> None:
        super().__init__()

        self._adapter: Optional[RecyclerViewAdapter] = None
        """The adapter aka delegate."""

        self._unbound_views: List[QtWidgets.QWidget] = []
        """Views that have been created but aren't in use."""

        self._bound_views: Dict[Index, QtWidgets.QWidget] = {}
        """Views that are currently bound to an item in the dataset."""

        self.setWidgetResizable(True)

        self._inner = QtWidgets.QWidget()
        """Inner widget to fill out the total scrolling height."""
        self.setWidget(self._inner)

        self._recycler = QtWidgets.QWidget()
        """Holds the actual views."""
        self._recycler.setParent(self._inner)
        self._recycler.move(0, 0)

    def set_adapter(self, adapter: RecyclerViewAdapter) -> None:
        """Set the adapter for providing custom views."""
        self._adapter = adapter
        self._adapter._recycler = self
        self.update()

    def set_recycler_layout(self, layout: RecyclerLayout):
        """Set which layout to use for recycled views."""
        layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._recycler.setLayout(layout)
        self.update()

    def get_bound_view(self, index: Index) -> Optional[QtWidgets.QWidget]:
        """Returns a view bound to the given index, or None if not bound."""
        return self._bound_views.get(index)

    def update(self) -> None:
        super().update()
        if self._adapter is None or self._recycler.layout() is None:
            # not fully initialized yet
            return

        self._inner.setFixedHeight(self._get_total_items_height())
        self._recycler.setFixedWidth(self.widget().width())
        self._rebuild_views()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.update()

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        # Called when the scroll area is scrolled.
        super().scrollContentsBy(dx, dy)
        self.update()

    def _rebuild_views(self) -> None:
        needed_indices = self._get_needed_indices()
        # Recycle old views.
        recyclable_indices = set(self._bound_views.keys()).difference(needed_indices)
        for index in recyclable_indices:
            view = self._bound_views.pop(index)
            self._unbound_views.append(view)
        # Hide all for now. Needed ones will be shown next.
        all_created_views = self._unbound_views + list(self._bound_views.values())
        for view in all_created_views:
            self._recycler.layout().removeWidget(view)
            view.hide()
        # Bind and show new views.
        for index in needed_indices:
            view = self._get_or_bind_view(index)
            if self._is_grid:
                row = index // self._get_num_cols()
                col = index % self._get_num_cols()
                self._recycler.layout().addWidget(view, row, col)
            elif self._is_vbox:
                self._recycler.layout().addWidget(view)
            view.show()
        # Move layout to the false top position.
        buffered_view = self._get_buffered_view_rect()
        self._recycler.move(0, buffered_view.top())

    def _get_fresh_view(self) -> QtWidgets.QWidget:
        """Get an unbound view, or create one if none available."""
        if not self._unbound_views:
            self._create_view()  # Ensure at least one exists.
        return self._unbound_views[0]

    def _get_or_bind_view(self, index: Index) -> QtWidgets.QWidget:
        """Get a view bound to the given index, or bind a fresh one."""
        view = self._bound_views.get(index)
        if view is None:
            # Not already bound - bind a fresh one and move to bound pool.
            view = self._get_fresh_view()
            self._adapter.bind_view(view, index)
            self._unbound_views.remove(view)
            self._bound_views[index] = view
        return view

    def _create_view(self) -> QtWidgets.QWidget:
        """Create a new view and add it to the pool.

        They are always hidden when created.
        """
        view = self._adapter.create_view()
        view.setParent(self._recycler)
        view.hide()  # is this needed?
        self._unbound_views.append(view)
        return view
    
    @property
    def _is_grid(self) -> bool:
        return isinstance(self._recycler.layout(), QtWidgets.QGridLayout)

    @property
    def _is_vbox(self) -> bool:
        return isinstance(self._recycler.layout(), QtWidgets.QVBoxLayout)

    @property
    def _total_num_items(self) -> int:
        return self._adapter.get_num_items()

    def _get_num_cols(self) -> int:
        """Always think in columns. VBox just counts as 1 column."""
        return max(1, self.width() // self._get_item_size_hint().width()) if self._is_grid else 1

    def _get_item_height(self) -> int:
        return self._get_item_size_hint().height()

    def _get_total_items_height(self) -> int:
        return math.ceil(self._total_num_items / self._get_num_cols()) * self._get_item_height()

    def _get_item_size_hint(self) -> QtCore.QSize:
        return self._get_fresh_view().sizeHint()

    def _get_view_rect(self) -> QtCore.QRect:
        """Returns the bounding region of the scroll area that is currently visible."""
        ret_val = QtCore.QRect()
        ret_val.setTop(self.verticalScrollBar().value())
        ret_val.setBottom(self.verticalScrollBar().value() + self.height())
        ret_val.setWidth(self.width())
        return ret_val

    def _get_buffered_view_rect(self) -> QtCore.QRect:
        """Returns the bounding region of the views that should be shown."""
        ret_val = QtCore.QRect()
        view_rect = self._get_view_rect()
        item_height = self._get_item_height()
        partially_exposed_top = view_rect.top() % item_height
        ret_val.setTop(
            view_rect.top()
            - partially_exposed_top
            - min(self._NUM_EXCESS_VIEWS, view_rect.top() // item_height) * item_height
        )
        ret_val.setBottom(
            min(
                self._get_total_items_height(),
                view_rect.bottom() + item_height * self._NUM_EXCESS_VIEWS,
            )
        )
        ret_val.setWidth(view_rect.width())
        return ret_val

    def _get_needed_indices(self) -> List[Index]:
        def items_at(height: int):
            row_start_index = (height // self._get_item_height()) * self._get_num_cols()
            return (row_start_index + i for i in range(self._get_num_cols()))

        buffered_view = self._get_buffered_view_rect()
        rows = range(buffered_view.top(), buffered_view.bottom(), self._get_item_height())
        return list(itertools.chain.from_iterable(map(items_at, rows)))


class MyGalleryAdapter(RecyclerViewAdapter):
    def __init__(self, data):
        self.data = data
        self.images = OrderedDict()
        self._image_size = QtCore.QSize(480, 240)

    def _load_image(self, index: int):
        image = QtGui.QPixmap.fromImage(generate_image(self._image_size, index))
        self.images[index] = image
        if len(self.images) > 500:
            # remove oldest image to simulate memory limit
            self.images.popitem(last=False)

    def _load_image_and_apply(self, index: int):
        self._load_image(index)
        view = self.get_bound_view(index)
        if view:
            # item may have been scrolled out of view already
            self.bind_view(view, index)

    def create_view(self) -> QtWidgets.QWidget:
        label = QtWidgets.QLabel()
        label.setFixedSize(self._image_size)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return label

    def bind_view(self, view: QtWidgets.QWidget, index: Index) -> None:
        label: QtWidgets.QLabel = view

        # self._load_image(index)  # ensure always loaded

        if index in self.images:
            # show already loaded image
            label.setPixmap(self.images[index])
            label.setText("")
        else:
            # load image (simulate loading delay)
            label.setPixmap(QtGui.QPixmap())
            label.setText("Loading...")
            QtCore.QTimer.singleShot(500, functools.partial(self._load_image_and_apply, index))

    def get_num_items(self) -> int:
        return len(self.data)


class MyGallery(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        vbox1 = QtWidgets.QVBoxLayout(self)
        vbox1.setContentsMargins(0, 0, 0, 0)
        vbox1.setSpacing(0)

        recycler_view = RecyclerView()
        data = [f"{i}" for i in range(20_000)]
        adapter = MyGalleryAdapter(data)
        recycler_view.set_adapter(adapter)
        recycler_view.set_recycler_layout(QtWidgets.QGridLayout())
        vbox1.addWidget(recycler_view)


def main():
    app = QtWidgets.QApplication()

    my_gallery = MyGallery()
    my_gallery.resize(400, 250)
    my_gallery.show()

    app.exec()


if __name__ == "__main__":
    main()
