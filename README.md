# File Swiper

File Swiper is a Python desktop application that allows users to quickly review and manage files in a selected folder. Users can swipe through files, preview their contents, and decide whether to keep or delete them.

## Features

- Select any folder to review files
- Preview images and text files
- Swipe through files using arrow keys or buttons
- Move unwanted files to the recycle bin
- Undo accidental deletions
- Progress tracking for the review process

## Requirements

- Python 3.6+
- PyQt5
- winshell

## Installation

1. Clone this repository or download the source code.
2. Install the required packages:

```
pip install PyQt5 winshell PyQt5-sip PyMuPDF python-docx
```

OR

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```
python file_swiper.py
```

2. Click "Select Folder" to choose the folder you want to review.
3. Use the arrow keys or buttons to navigate through files:
   - Right arrow or "Keep" button: Keep the file and move to the next one
   - Left arrow or "Delete" button: Move the file to the recycle bin and go to the next file
   - "Undo Delete" button: Restore the last deleted file
4. The preview pane will show image previews or the first 1000 characters of text files.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
