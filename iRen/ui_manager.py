import os
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, QItemSelectionModel
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow

from MainWindow import *
from image_list_manager import *
import breeze_resources


class AppWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # region Initialise global variables
        self.origin_folder = os.path.expanduser('~')
        self.destination_folder = None

        self.display_welcome_graphic()

        # Set the listview to know what model to emulate
        self.files_model = ImagefileModel(self.files_listview)
        self.files_listview.setModel(self.files_model)
        self.files_listview.selectionModel().selectionChanged.connect(self.on_list_item_selected)

        # We pass this pixmap around the app
        self.image_pixmap = QPixmap()

    @pyqtSlot()
    def on_origin_folder_button_clicked(self):
        """This method controls the QFileDialogBox"""
        options = QFileDialog.Options()
        # noinspection PyCallByClass,PyTypeChecker
        directory = QFileDialog.getExistingDirectory(self, "Select the images folder", directory=self.origin_folder,
                                                     options=options)
        if not directory:
            return

        self.origin_folder = directory
        self.origin_folder_label.setText(directory)

        if self.sync_folders_checkbox.isChecked():
            self.destination_folder = self.origin_folder
            self.destination_folder_label.setText(self.destination_folder)

        self.populate_listview()

    @pyqtSlot()
    def on_destination_folder_button_clicked(self):
        """Open a filedialog when the button is clicked"""
        if self.sync_folders_checkbox.isChecked():
            return

        options = QFileDialog.Options()
        # noinspection PyCallByClass,PyTypeChecker
        directory = QFileDialog.getExistingDirectory(self, "Select the images folder", directory=self.origin_folder,
                                                     options=options)

        if not directory:
            return

        self.destination_folder = directory
        self.destination_folder_label.setText(directory)

    def populate_listview(self):
        self.files_model.images = []
        self.files_model = get_filenames(self.origin_folder, self.files_model)
        self.files_listview.setModel(self.files_model)
        self.files_model.layoutChanged.emit()

    @pyqtSlot()
    def on_save_button_clicked(self):
        filename = self.filename_lineedit.text()
        if not filename.strip():
            return
        index = self.files_listview.selectedIndexes()
        if not index:
            return
        index = index[0]
        row = index.row()
        status, text = self.files_model.images[row]

        # Get the extension and set it to lower case
        extension = self.file_format_combobox.currentText().lower()
        save_filename = filename + extension

        # Save the file to th destination folder
        saved = self.image_pixmap.save(str(Path(self.destination_folder)/save_filename))
        print("%sly saved to: %s " % (saved, str(Path(self.destination_folder)/save_filename)))

        # If we are saving to the same folder
        self.files_model.layoutChanged.emit()

        # Decorate the file icon so we know it has been successfully saved
        self.files_model.images[row] = (saved, text)
        self.files_model.dataChanged.emit(index, index)
        return saved

    @pyqtSlot(int)
    def on_sync_folders_checkbox_stateChanged(self, state):
        self.destination_folder_group.setEnabled(not bool(state))

    def on_list_item_selected(self, current):
        """This takes care of parsing the selection when something in the listview
        is selected. The signal beings with it a QItemSelection which holds within it
        a list of selected values, i the form of QModelIndices. We then have to go into
        this list to get the value for the row the user selected. For now implementation is
        using the received row as a fererence in the main model, but it might be useful to
        get the filename with this signal as well in the future."""
        index = current.indexes()
        if index:
            row = index[0].row()
            _, filename = self.files_model.images[row]
        else:
            return

        self.image_pixmap = image_to_pixmap(str(Path(self.origin_folder)/filename))
        self.image_display_label.setPixmap(self.image_pixmap)
        self.image_display_label.setMask(self.image_pixmap.mask())
        # self.image_display_label.setScaledContents(True)
        self.image_display_label.show()
        self.filename_lineedit.setFocus(Qt.NoFocusReason)
        self.filename_lineedit.selectAll()

    @pyqtSlot()
    def on_filename_lineedit_returnPressed(self):
        saved = self.on_save_button_clicked()

        if not saved:
            return
        oldindex = self.files_listview.selectedIndexes()[0].row()

        # Compare the index to the row count - 1 cause fucking oython counts from 0
        if oldindex >= self.files_model.rowCount() - 1:
            return

        newindex = oldindex + 1

        # Clear selection first before we select the next one
        self.files_listview.clearSelection()

        newindexobject = self.files_model.createIndex(newindex, 0)
        self.files_listview.selectionModel().select(newindexobject, QItemSelectionModel.Select)

    def display_welcome_graphic(self):
        welcome = image_to_pixmap('Welcome.png')
        self.image_display_label.setPixmap(welcome)


def get_filenames(directory, model: ImagefileModel):
    """This method gets all the filenames is a particular directory. There is no recusion, so
       only top level files are considered. directory has to be a Pathlib Path. Return the
       filenames as QStandardItems in the model."""
    # Check if it is a pathlib path we've been fed. And convert it to a pathlib path
    directory = Path(directory)
    # Check if the directory exists before we go in and iterate through.
    if not directory.exists():
        return
    # Collect a list of the files in the directory
    filenames = [(False, f.name) for f in directory.iterdir() if f.name.endswith(('jpg', '.JPG', '.png', '.PNG'))]
    # Sadly we are not allowed to use list comprehension when we don't need a list
    # Append the data to the model
    for i in filenames:
        model.images.append(i)
    # Return the model
    return model


def image_to_pixmap(image_path):
    """To display an image in the label, we have to convert it to pixmap"""
    pixmap = QPixmap(image_path)
    return pixmap


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    # Set the stylesheet
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    window = AppWindow()
    window.show()
    window.raise_()
    sys.exit(app.exec())


