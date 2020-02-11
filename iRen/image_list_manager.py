import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QModelIndex, Qt

tick = QtGui.QImage('tick.png')


class ImagefileModel(QtCore.QAbstractListModel):
    """This class defines the structure of the data we are putting in the list view. We have to go this
    low level in order to use decorators with the list view."""
    def __init__(self, *args, images=None, **kwargs):
        super(ImagefileModel, self).__init__(*args, **kwargs)
        self.images = images or []

    def data(self, index, role=...) -> typing.Any:
        """We override the data structure of the item in the listview"""
        # If the role of this data at this row is display, give us the text
        if role == Qt.DisplayRole:
            _, text = self.images[index.row()]
            return text

        # If the role is decoration, give us the status which is a bool, which
        # lets us put ticks.
        if role == Qt.DecorationRole:
            status, _ = self.images[index.row()]
            if status:
                return tick

    def rowCount(self, parent=QModelIndex, *args, **kwargs):
        """Dont know why we are overriding the row count mathod from the
        base class. But whatever man."""
        return len(self.images)
