import sys
import os
import send2trash
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTextEdit, QFileDialog, QStyle, QProgressBar)
from PyQt5.QtGui import QPixmap, QKeyEvent, QFont, QIcon
from PyQt5.QtCore import Qt, QSize

class FileSwiperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_folder = ""
        self.current_file_index = 0
        self.files = []
        self.deleted_files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Swiper')
        self.setGeometry(100, 100, 1400, 1000)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 16px;
            }
        """)

        layout = QVBoxLayout()

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        # File info and progress
        self.file_label = QLabel()
        self.file_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.file_label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Preview
        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignCenter)
        self.preview_widget.setMinimumSize(QSize(400, 400))
        layout.addWidget(self.preview_widget)

        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        layout.addWidget(self.text_preview)
        self.text_preview.hide()

        # Buttons
        button_layout = QHBoxLayout()
        self.keep_button = self.create_button('Keep', 'SP_ArrowForward')
        self.delete_button = self.create_button('Delete', 'SP_TrashIcon')
        self.undo_button = self.create_button('Undo Delete', 'SP_ArrowBack')
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.keep_button)
        button_layout.addWidget(self.undo_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.keep_button.clicked.connect(self.keep_file)
        self.delete_button.clicked.connect(self.delete_file)
        self.undo_button.clicked.connect(self.undo_delete)

        self.update_ui_state()

    def create_button(self, text, icon_name):
        button = QPushButton(text)
        icon = self.style().standardIcon(getattr(QStyle, icon_name, QStyle.SP_CustomBase))
        if not icon.isNull():
            button.setIcon(icon)
            button.setIconSize(QSize(24, 24))
        return button

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.folder_label.setText(f"Selected folder: {os.path.basename(folder)}")
            self.files = self.get_files()
            self.current_file_index = 0
            self.deleted_files = []
            self.show_current_file()

    def get_files(self):
        return [f for f in os.listdir(self.current_folder) if os.path.isfile(os.path.join(self.current_folder, f))]

    def show_current_file(self):
        if self.current_file_index < len(self.files):
            current_file = self.files[self.current_file_index]
            self.file_label.setText(f"File {self.current_file_index + 1} of {len(self.files)}: {current_file}")
            self.show_preview(current_file)
            self.progress_bar.setValue(int((self.current_file_index + 1) / len(self.files) * 100))
        else:
            self.file_label.setText("No more files")
            self.preview_widget.clear()
            self.text_preview.clear()
            self.progress_bar.setValue(100)

        self.update_ui_state()

    def show_preview(self, filename):
        file_path = os.path.join(self.current_folder, filename)
        
        self.preview_widget.clear()
        self.text_preview.clear()
        self.text_preview.hide()
        self.preview_widget.show()

        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            pixmap = QPixmap(file_path)
            self.preview_widget.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif filename.lower().endswith(('.txt', '.py', '.html', '.css', '.js')):
            self.preview_widget.hide()
            self.text_preview.show()
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read(1000)
                    self.text_preview.setText(content)
            except Exception as e:
                self.text_preview.setText(f"Error reading file: {str(e)}")
        else:
            self.preview_widget.setText(f"No preview available for {filename}")

    def keep_file(self):
        self.current_file_index += 1
        self.show_current_file()

    def delete_file(self):
        if self.current_file_index < len(self.files):
            file_to_delete = os.path.join(self.current_folder, self.files[self.current_file_index])
            try:
                send2trash.send2trash(file_to_delete)
                self.deleted_files.append(self.files[self.current_file_index])
                print(f"Moved to recycle bin: {file_to_delete}")
            except Exception as e:
                print(f"Error deleting {file_to_delete}: {e}")
        self.files = self.get_files()
        self.show_current_file()

    def undo_delete(self):
        if self.deleted_files:
            file_to_restore = self.deleted_files.pop()
            print(f"Restored: {file_to_restore}")
            self.files = self.get_files()
            self.current_file_index = self.files.index(file_to_restore) if file_to_restore in self.files else len(self.files) - 1
            self.show_current_file()

    def update_ui_state(self):
        has_files = bool(self.files)
        has_deleted = bool(self.deleted_files)
        self.keep_button.setEnabled(has_files)
        self.delete_button.setEnabled(has_files)
        self.undo_button.setEnabled(has_deleted)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Right:
            self.keep_file()
        elif event.key() == Qt.Key_Left:
            self.delete_file()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileSwiperApp()
    ex.show()
    sys.exit(app.exec_())