from threading import Thread
from commons import *

formats = [".svg", ".png", ".jpg"]


class Window(QWidget):
    imageSignal = Signal(str)
    onFinished = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi Image Format Viewer")
        self.setMinimumSize(800, 800)

        self.imagesWidgets: list[ImageWidget] = []

        lay = QVBoxLayout(self)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        browseButton = QPushButton(" Browse Image Folder ")
        browseButton.clicked.connect(self.browseFolder)
        hlay.addWidget(browseButton)

        self.lineEdit = QLineEdit()
        # self.lineEdit.setText(r"C:/Users/USER/Desktop/Icons/Featherly Icons")
        self.lineEdit.setReadOnly(True)
        hlay.addWidget(self.lineEdit)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        hlay.addWidget(QLabel("Image Format: "))

        self.formatComboBox = QComboBox()
        self.formatComboBox.addItems(formats)
        hlay.addWidget(self.formatComboBox)

        hlay.addStretch()

        self.allFormatCheckBox = QCheckBox("All formats")
        self.allFormatCheckBox.toggled.connect(self.formatComboBox.setDisabled)
        hlay.addWidget(self.allFormatCheckBox)

        hlay.addStretch()

        loadButton = QPushButton(" Load Images ")
        loadButton.clicked.connect(self.loadFolder)
        hlay.addWidget(loadButton)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        lay.addWidget(scroll)

        self.w = QWidget()
        scroll.setWidget(self.w)

        self.spinner = Spinner(self.w)

        self.wl = QFlowLayout(self.w)

        self.imageSignal.connect(self.onImage)
        self.onFinished.connect(self.onFinish)

        self.show()

    def onImage(self, path: str):
        iw = ImageWidget(path)

        self.wl.addWidget(iw)
        self.imagesWidgets.append(iw)

    def onFinish(self):
        self.spinner.stop()

        if not self.imagesWidgets:
            QMessageBox.warning(
                self,
                "No image",
                "No compactible image found.",
            )

    def browseFolder(self):
        _folder = self.lineEdit.text()
        if not os.path.isdir(_folder):
            _folder = (QDir.homePath(),)

        folder = QFileDialog.getExistingDirectory(self, "Select Image Folders", _folder)

        if folder:
            self.lineEdit.setText(folder)

    def _loadFolder(self, folder: str):
        allFormats = self.allFormatCheckBox.isChecked()
        format = self.formatComboBox.currentText().strip()
        _formats = formats if allFormats else [format]

        self.imagesWidgets.clear()

        for directory in os.listdir(folder):
            path = os.path.join(folder, directory)

            if (
                os.path.isfile(path)
                and os.path.splitext(directory)[-1].lower() in _formats
            ):
                self.imageSignal.emit(path)

        self.onFinished.emit()

    def loadFolder(self):
        folder = self.lineEdit.text()
        if os.path.isdir(folder):
            self.spinner.start()

            for iw in self.imagesWidgets:
                iw.hide()
                self.wl.removeWidget(iw)
                iw.deleteLater()

            Thread(
                target=self._loadFolder,
                args=(folder,),
            ).start()

        else:
            QMessageBox.warning(
                self,
                "Invalid Folder",
                "Select image folder first.",
            )

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        QApplication.instance().quit()


class App(QApplication):
    def __init__(self):
        super().__init__([])

        self.setStyleSheet(
            """
            ImageWidget {
                border: 1px solid black;
                border-radius: 10px;
                margin: 5px;
            }
            ImageWidget:hover {
                border: 1px solid blue;
                background: lightblue
            }
        """
        )

        self.window = Window()


app = App()
app.exec()
