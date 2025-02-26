# GutenbergScraper
GutenbergScraper is a simple command-line tool for scraping books from [Project Gutenberg](https://www.gutenberg.org/). It allows users to download books in various formats by specifying the author's ID or by specifying the subject/genre.

## Installation
1. Clone this repository:
      ```sh
   git clone https://github.com/AkanshGrover/GutenbergScraper
   cd GutenbergScraper
   ```
2. Install dependencies:
      ```sh
   pip install -r requirements.txt
   ```

## Usage
Run the script using Python:
```sh
python  GutenbergScraper.py [-h] [-a AUTHOR_ID] [-o] [-f FILE_TYPE] [-u] [-l] [-s SUBJECT] [-n NUMBER]
```

### Arguments:
-  `-h` : Show help message and exit.
-  `-a AUTHOR_ID` : Author ID from the Gutenberg website.
-  `-o` : Downloads all ebooks from the author and saves them in a single file (only for text format).
-  `-f FILE_TYPE` : Specify the file format.
-  `-u, --update` : Updates the list of search topics
-  `-l, --list`   : Lists all the subjects
-  `-s SUBJECT, --search SUBJECT` : Search different subjects
-  `-n NUMBER, --number NUMBER` : Specify the number of ebooks to download

### Supported File Types:
1.  `text` - Default plain text format
2.  `kindle` - Kindle format
3.  `old_kindle` - Older Kindle format
4.  `epub3` - EPUB for modern e-readers
5.  `epub` - EPUB for older e-readers
6.  `epub_noimages` - EPUB without images
7.  `zip` - HTML in a ZIP archive
8.  `mp3` - MP3 audiobook
9.  `speex` - Speex audio format
10.  `ogg` - Ogg Vorbis audio format
11.  `itunes` - Apple iTunes audiobook