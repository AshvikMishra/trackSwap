import sys
import threading
import queue
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit
)
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

from components import scrapper
from components import cleaner
from components import script

import builtins
import io
import os

class QTextEditLogger(QObject):
    new_text = pyqtSignal(str)

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.new_text.connect(self._append_text)

    def write(self, msg):
        self.new_text.emit(str(msg))

    def flush(self):
        pass

    def _append_text(self, msg):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.insertPlainText(msg)
        self.text_edit.moveCursor(QTextCursor.End)
        self.text_edit.ensureCursorVisible()

class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrackSwap-Sync-Mode")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.showMaximized()

        # Layouts
        main_layout = QVBoxLayout()
        button_row = QHBoxLayout()

        # Output Text Area
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 11))
        self.text_edit.setStyleSheet("""
            background-color: #2e2e2e;
            color: #e0e0ff;
            border: 1px solid #555;
            padding: 10px;
        """)
        main_layout.addWidget(self.text_edit)

        # Start Button
        self.start_button = QPushButton("Start Sync")
        self.start_button.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #6a1b9a;
                color: white;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #7b1fa2;
            }
            QPushButton:pressed {
                background-color: #4a148c;
            }
        """)
        self.start_button.clicked.connect(self.start_conversion)
        button_row.addWidget(self.start_button, 9)

        # Exit Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFont(QFont("Segoe UI", 13))
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #b71c1c;
                color: white;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c62828;
            }
            QPushButton:pressed {
                background-color: #8e0000;
            }
        """)
        self.exit_button.clicked.connect(self.close)
        button_row.addWidget(self.exit_button, 1)

        main_layout.addLayout(button_row)
        self.setLayout(main_layout)

        self.logger = QTextEditLogger(self.text_edit)
        sys.stdout = self.logger
        sys.stderr = self.logger

        builtins.input = self.auto_input

    def auto_input(self, prompt=""):
        if "y/n" in prompt.lower():
            return "y"
        return ""

    def start_conversion(self):
        self.text_edit.append("🚀 Starting Amazon Music to Spotify Sync...\n")
        threading.Thread(target=self.run_all_playlists, daemon=True).start()

    def run_all_playlists(self):
        playlists_file = os.path.join(os.path.dirname(__file__), "playlists.txt")
        if not os.path.exists(playlists_file):
            print("❌ playlists.txt file not found in the current directory.[if not made, create this file in the same directory and paste your playlists in each line]")
            return

        with open(playlists_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        if not urls:
            print("❌ No playlist URLs found in playlists.txt.")
            return

        for idx, url in enumerate(urls, start=1):
            print(f"\n⏳ Processing playlist {idx}/{len(urls)}: {url}")
            try:
                scrapper.main(url)

                print("\n🧹 Running cleaner...")
                cleaner.main()

                print("\n🎧 Running Spotify uploader...")
                script.main()

                print(f"\n✅ Playlist {idx} successfully transferred to Spotify!")
            except Exception as e:
                print(f"\n❌ Error with playlist {idx}: {e}")

        print("\n🎯 All playlists processed!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec_())