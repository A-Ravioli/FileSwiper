import sys
import os
import winshell
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTextEdit, QFileDialog, QStyle, QProgressBar, QMessageBox, QSlider)
from PyQt5.QtGui import QPixmap, QKeyEvent, QFont, QIcon
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from docx import Document
import pandas as pd

class FileSwiperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_folder = ""
        self.current_file_index = 0
        self.files = []
        self.deleted_files = []
        self.initUI()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.video_widget.hide()
        self.layout().addWidget(self.video_widget)
        
        self.audio_slider = QSlider(Qt.Horizontal)
        self.audio_slider.setRange(0, 100)
        self.audio_slider.setValue(0)
        self.audio_slider.sliderMoved.connect(self.set_position)
        self.audio_slider.hide()
        self.layout().addWidget(self.audio_slider)
        
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

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
        self.play_pause_button = self.create_button('Play/Pause', 'SP_MediaPlay')
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.keep_button)
        button_layout.addWidget(self.play_pause_button)
        self.play_pause_button.clicked.connect(self.play_pause_audio)
        self.play_pause_button.setEnabled(False)

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
        self.video_widget.hide()
        self.audio_slider.hide()
        self.play_pause_button.setEnabled(False)
        self.media_player.stop()

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
        elif filename.lower().endswith(('.pdf')):
            try:
                doc = fitz.open(file_path)
                page = doc.load_page(0)  # Load the first page
                pix = page.get_pixmap()
                image_path = os.path.join(self.current_folder, "preview.png")
                pix.save(image_path)
                pixmap = QPixmap(image_path)
                self.preview_widget.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                self.preview_widget.setText(f"Error previewing PDF: {str(e)}")
        elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            self.preview_widget.hide()
            self.video_widget.show()
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.play()
        elif filename.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a')):
            self.preview_widget.hide()
            self.audio_slider.show()
            self.play_pause_button.setEnabled(True)
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.media_player.play()
        elif filename.lower().endswith(('.docx')):
            try:
                doc = Document(file_path)
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)
                self.preview_widget.hide()
                self.text_preview.show()
                self.text_preview.setText('\n'.join(full_text))
            except Exception as e:
                self.text_preview.setText(f"Error previewing document: {str(e)}")
        elif filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            self.preview_widget.hide()
            self.text_preview.show()
            try:
                if filename.lower().endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                preview_text = df.head().to_string()
                self.text_preview.setText(preview_text)
            except Exception as e:
                self.text_preview.setText(f"Error previewing spreadsheet: {str(e)}")
        else:
            self.preview_widget.setText(f"No preview available for {filename}")


    def keep_file(self):
        self.current_file_index += 1
        self.show_current_file()

    def delete_file(self):
        if self.current_file_index < len(self.files):
            file_to_delete = os.path.join(self.current_folder, self.files[self.current_file_index])
            try:
                winshell.delete_file(file_to_delete, no_confirm=True, allow_undo=True)
                self.deleted_files.append(self.files[self.current_file_index])
                print(f"Moved to recycle bin: {file_to_delete}")
            except Exception as e:
                print(f"Error deleting {file_to_delete}: {e}")
                QMessageBox.warning(self, "Delete Error", f"Could not delete file: {self.files[self.current_file_index]}\n\nError: {str(e)}")
            finally:
                self.files = self.get_files()
                if self.current_file_index >= len(self.files):
                    self.current_file_index = max(0, len(self.files) - 1)
                self.show_current_file()

    def undo_delete(self):
        if self.deleted_files:
            file_to_restore = self.deleted_files.pop()
            print(f"Attempting to restore: {file_to_restore}")
            self.files = self.get_files()
            if file_to_restore in self.files:
                self.current_file_index = self.files.index(file_to_restore)
            else:
                self.current_file_index = min(self.current_file_index, len(self.files) - 1)
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

    def position_changed(self, position):
        self.audio_slider.setValue(position)

    def duration_changed(self, duration):
        self.audio_slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def play_pause_audio(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileSwiperApp()
    ex.show()
    sys.exit(app.exec_())
