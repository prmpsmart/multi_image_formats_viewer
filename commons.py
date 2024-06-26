from enum import Enum
import math, os


try:
    # if PySide6 if what you have installed
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except:  # if PyQt6 is what you have installed
    from PyQt6.QtCore import *  # type: ignore
    from PyQt6.QtGui import *  # type: ignore
    from PyQt6.QtWidgets import *  # type: ignore


class SvgCompositions(Enum):
    Overlay = QPainter.CompositionMode_Overlay
    SourceIn = QPainter.CompositionMode_SourceIn
    SourceOut = QPainter.CompositionMode_SourceOut
    SourceAtop = QPainter.CompositionMode_SourceAtop


def QSvgPixmap(
    pixmap: QPixmap = None,
    color: QColor = Qt.black,
    composition: SvgCompositions = SvgCompositions.SourceIn,
) -> QPixmap:
    assert composition in SvgCompositions
    o = pixmap
    if not isinstance(pixmap, QPixmap):
        pixmap = QPixmap(pixmap)

    if pixmap.isNull():
        print(o)

    painter = QPainter(pixmap)
    painter.setCompositionMode(composition.value)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return pixmap


def QSvgIcon(
    icon: str = "",
    size: QSize = None,
    color: QColor = Qt.black,
    composition: SvgCompositions = SvgCompositions.SourceIn,
) -> QIcon:
    if isinstance(icon, QIcon):
        icon = icon.pixmap(size)

    pixmap = QSvgPixmap(pixmap=icon, color=color, composition=composition)
    return QIcon(pixmap)


class QFlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self._items = []
        self.__pending_positions = {}

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, a0: QLayoutItem) -> None:
        try:
            position = self.__pending_positions[a0.widget()]
            self._items.insert(position, a0)
            del self.__pending_positions[a0.widget()]
        except KeyError:
            self._items.append(a0)

    def addWidget(self, w: QWidget, position: int = None) -> None:
        if position:
            self.__pending_positions[w] = position
        super().addWidget(w)

    def count(self):
        return len(self._items)

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def itemAt(self, index: int) -> QLayoutItem:
        if 0 <= index < len(self._items):
            return self._items[index]

        return None

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._doLayout(QRect(0, 0, width, 0), True)
        return height

    def minimumSize(self):
        size = QSize()

        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def removeItem(self, a0: QLayoutItem) -> None:
        a0.widget().deleteLater()

    def removeWidget(self, w: QWidget) -> None:
        w.deleteLater()

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def takeAt(self, index: int) -> QLayoutItem:
        if 0 <= index < len(self._items):
            return self._items.pop(index)

        return None

    def _doLayout(self, rect, testOnly):
        """This does the layout. Dont ask me how. Source: https://github.com/baoboa/pyqt5/blob/master/examples/layouts/flowlayout.py"""
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self._items:
            wid = item.widget()
            space_x = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.PushButton,
                QSizePolicy.PushButton,
                Qt.Horizontal,
            )
            space_y = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.PushButton,
                QSizePolicy.PushButton,
                Qt.Vertical,
            )
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


class Spinner(QWidget):
    def __init__(
        self,
        parent,
        centerOnParent: bool = True,
        disableParentWhenSpinning: bool = True,
        modality: Qt.WindowModality = Qt.WindowModality.NonModal,
    ):
        super().__init__(parent)

        self._centerOnParent = centerOnParent
        self._disableParentWhenSpinning = disableParentWhenSpinning

        # WAS IN initialize()
        self._color = QColor(Qt.black)
        self._roundness = 100.0
        self._minimumTrailOpacity = 3.14159265358979323846
        self._trailFadePercentage = 80.0
        self._revolutionsPerSecond = 1.57079632679489661923
        self._numberOfLines = 20
        self._lineLength = 10
        self._lineWidth = 2
        self._innerRadius = 10
        self._currentCounter = 0
        self._isSpinning = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()
        # END initialize()

        self.setWindowModality(modality)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, _):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        painter.setPen(Qt.NoPen)
        for i in range(0, self._numberOfLines):
            painter.save()
            painter.translate(
                self._innerRadius + self._lineLength,
                self._innerRadius + self._lineLength,
            )
            rotateAngle = float(360 * i) / float(self._numberOfLines)
            painter.rotate(rotateAngle)
            painter.translate(self._innerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(
                i, self._currentCounter, self._numberOfLines
            )
            color = self.currentLineColor(
                distance,
                self._numberOfLines,
                self._trailFadePercentage,
                self._minimumTrailOpacity,
                self._color,
            )
            painter.setBrush(color)
            rect = QRect(
                0,
                int(-self._lineWidth / 2),
                int(self._lineLength),
                int(self._lineWidth),
            )
            painter.drawRoundedRect(
                rect, self._roundness, self._roundness, Qt.RelativeSize
            )
            painter.restore()

    def start(self):
        self.updatePosition()
        self._isSpinning = True
        self.show()

        if self.parentWidget and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self._timer.isActive():
            self._timer.start()
            self._currentCounter = 0

    def stop(self):
        self._isSpinning = False
        self.hide()

        if self.parentWidget() and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._currentCounter = 0

    def setNumberOfLines(self, lines):
        self._numberOfLines = lines
        self._currentCounter = 0
        self.updateTimer()

    def setLineLength(self, length):
        self._lineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self._lineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self._innerRadius = radius
        self.updateSize()

    def color(self):
        return self._color

    def roundness(self):
        return self._roundness

    def minimumTrailOpacity(self):
        return self._minimumTrailOpacity

    def trailFadePercentage(self):
        return self._trailFadePercentage

    def revolutionsPersSecond(self):
        return self._revolutionsPerSecond

    def numberOfLines(self):
        return self._numberOfLines

    def lineLength(self):
        return self._lineLength

    def lineWidth(self):
        return self._lineWidth

    def innerRadius(self):
        return self._innerRadius

    def isSpinning(self):
        return self._isSpinning

    def setRoundness(self, roundness):
        self._roundness = max(0.0, min(100.0, roundness))

    def setColor(self, color=Qt.black):
        self._color = QColor(color)

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self._revolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self._trailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self._minimumTrailOpacity = minimumTrailOpacity

    def rotate(self):
        self._currentCounter += 1
        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0
        self.update()

    def updateSize(self):
        size = int((self._innerRadius + self._lineLength) * 2)
        self.setFixedSize(size, size)

    def updateTimer(self):
        self._timer.setInterval(
            int(1000 / (self._numberOfLines * self._revolutionsPerSecond))
        )

    def updatePosition(self):
        if self.parentWidget() and self._centerOnParent:
            self.move(
                int(self.parentWidget().width() / 2 - self.width() / 2),
                int(self.parentWidget().height() / 2 - self.height() / 2),
            )

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(
        self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, colorinput
    ):
        color = QColor(colorinput)
        if countDistance == 0:
            return color
        minAlphaF = minOpacity / 100.0
        distanceThreshold = int(math.ceil((totalNrOfLines - 1) * trailFadePerc / 100.0))
        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)
        else:
            alphaDiff = color.alphaF() - minAlphaF
            gradient = alphaDiff / float(distanceThreshold + 1)
            resultAlpha = color.alphaF() - gradient * countDistance
            # If alpha is out of bounds, clip it.
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color


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
