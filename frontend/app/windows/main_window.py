"""Main window implementation for the PyQt frontend."""

from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Placeholder main window to be wired with Qt Designer UI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Realtime Quality Inspection")
