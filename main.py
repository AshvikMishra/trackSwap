import sys
import threading
import queue
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QInputDialog,
)
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer

import scrapper
import cleaner
import script
import builtins
import io

class QTextEditLogger(io.StringIO):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def write(self, msg):
        self.text_edit.moveCursor(QTextCursor.End)
        self.text_edit.insertPlainText(msg)
        self.text_edit.moveCursor(QTextCursor.End)
        self.text_edit.ensureCursorVisible()

    def flush(self):
        pass

class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrackSwap")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.showMaximized()  # Maximize window

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

        # Start Button (80%)
        self.start_button = QPushButton("Start Conversion")
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
        self.start_button.setMinimumWidth(0)
        self.start_button.clicked.connect(self.start_conversion)
        button_row.addWidget(self.start_button, 9)

        # Exit Button (20%)
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

        # Add buttons row to main layout
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)

        # Redirect print to GUI
        sys.stdout = QTextEditLogger(self.text_edit)

        # Setup input redirection
        self.input_queue = queue.Queue()
        builtins.input = self.get_input

        # Periodic check for input prompts from background thread
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_input_requests)
        self.timer.start(200)
        

    def get_input(self, prompt=""):
        response_queue = queue.Queue()
        self.input_queue.put((prompt, response_queue))
        return response_queue.get()

    def process_input_requests(self):
        if not self.input_queue.empty():
            prompt, response_queue = self.input_queue.get()
            user_input, ok = QInputDialog.getText(self, "Input Required", prompt)
            if ok:
                response_queue.put(user_input)
            else:
                QApplication.quit()

    def start_conversion(self):
        self.text_edit.append("🚀 Starting Amazon Music to Spotify Conversion...\n")
        threading.Thread(target=self.run_pipeline, daemon=True).start()

    def run_pipeline(self):
        try:
            print("\n📥 Running scraper...")
            scrapper.main()

            print("\n🧹 Running cleaner...")
            cleaner.main()

            print("\n🎧 Running Spotify uploader...")
            script.main()

            print("\n✅ Playlist successfully transferred to Spotify!")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec_())