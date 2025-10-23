"""PyQt application entry point."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from frontend.app.windows.main_window import MainWindow


def main() -> None:
    """Launch the PyQt application."""

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
