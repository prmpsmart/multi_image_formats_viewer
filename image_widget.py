import os
from commons import *


class ImageWidget(QFrame):
    def __init__(self, file: str):
        super().__init__()

        name = os.path.basename(file)

        lay = QVBoxLayout(self)

        s = 50

        pixmapLabel = QLabel()
        pixmapLabel.setFixedSize(s, s)
        lay.addWidget(pixmapLabel, 1, Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(file).scaledToWidth(s)
        pixmapLabel.setPixmap(pixmap)

        nameLabel = QLabel(name)
        lay.addWidget(nameLabel)


if __name__ == "__main__":
    os.system("python main.py")
