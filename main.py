from window import *


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
