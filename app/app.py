"""App class for the logic of the app"""
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget,  QPushButton, QLineEdit, QLabel
from PyQt5.QtGui import QFont, QFontDatabase
import functools

# Color palette: https://colors.muz.li/palette/361d32/543c52/f55951/edd2cb/f1e8e6


class Font(QFont):
    def __init__(self, font_name: str, size: int, custom_font: bool = False, weight: int = None):
        font = font_name
        if custom_font:
            font_id = QFontDatabase.addApplicationFont(f"{font_name}.ttf")
            if font_id < 0:
                print("Error")
                raise Exception("Font not found")
            else:
                font = QFontDatabase.applicationFontFamilies(font_id)[0]
        super().__init__(font, size)
        if weight:
            self.setWeight(weight)


class QtStyleSheet:
    """Representation for a CSS Stylesheet"""
    @classmethod
    def to_string(cls, sheet_dictionary: dict) -> str: # TODO: CHANGE GIVEN PARAM TO BE A DICTIONARY
        """Return a string representation of the stylesheet.The parameter name
        must be a CSS property and the given value will be the value in the
        stylesheet"""
        sheet = ""
        # Unwrap the kwargs parameters
        for param, value in sheet_dictionary.items():
            # TODO: TRANSFORM PROPERTIES WITH HYPYHENS IN THEM (bg -> background-color)
            sheet += f"{param}: {value};"
        return sheet


class Label(QLabel):
    def __init__(self, content: str, stylesheet: str, font: Font, parent=None, pos_x=None, pos_y=None):
        """Initialize a QT Label"""
        super().__init__(content, parent)
        self.setFont(font)
        self.setStyleSheet(stylesheet)
        if pos_x and pos_y:
            self.position(pos_x, pos_y)
        # Adjust size of the label to the text
        self.adjustSize()

    def position(self, left, top):
        """Position the label relative to its parent"""
        self.move(left, top)

    def set_style(self, stylesheet: str):
        """Set the stylesheet of the label"""
        self.setStyleSheet(stylesheet)


class App(QMainWindow):
    def __init__(self):
        """"Initialize the app"""
        super().__init__()
        self.setWindowTitle("SafeKeys")
        self.resize(800, 700)

    def main_window(self):
        """Main window of the program. Set all
        the widgets to show the main window"""
        # Set the window's properties
        window_stylesheet = {
            "background-color": "#361d32",
        }
        self.setStyleSheet(QtStyleSheet.to_string(window_stylesheet))

        # Set the labels
        title_stylesheet = {
            "color": "#f55951",
        }
        title_stylesheet = QtStyleSheet.to_string(title_stylesheet)
        title_font = Font("Roboto-Regular", 20, True, 250)
        title = Label("SafeKeys", title_stylesheet, title_font, self, 25, 15)

        self.show()






