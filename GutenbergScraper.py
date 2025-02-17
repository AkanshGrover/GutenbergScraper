import requests, os, argparse
from bs4 import BeautifulSoup

def get_all_books(base_url, a_id):
    si = 1
    books_url = []
    while True:
        url = f"{base_url}/ebooks/author/{a_id}?start_index={si}"
        r = requests.get(url)

        if not r.ok:
            return([-1])

        bs = BeautifulSoup(r.content, 'html.parser')

        for link in bs.select("li.booklink a.link[href]"):
            id = link["href"]
            if "ebooks" in id:
                books_url.append(f"{base_url}{id}")

        if len(books_url) == 0:
            return([-2])

        next_exist = bs.find("a", string="Next")
        if next_exist:
            si += 25
        else:
            return(books_url)
        
def download_files(burl, urls, onefile, type):
    for url in urls:
        r = requests.get(url)
        if r.ok:
            if not os.path.isdir("downloaded_files"):
                os.mkdir("downloaded_files")
            bs = BeautifulSoup(r.content, 'html.parser')
            if type == "text":
                ext = ".txt.utf-8"
            elif type == "kindle":
                ext = ".kf8.images"
            elif type == "old_kindle":
                ext = ".kindle.images"
            elif type == "epub3":
                ext = ".epub3.images"
            elif type == "epub":
                ext = ".epub.images"
            elif type == "epub_noimages":
                ext = ".epub.noimages"
            elif type == "zip":
                ext = ".zip"
            elif type == "mp3":
                ext = ".mp3"
            elif type == "speex":
                ext = ".spx"
            elif type == "ogg":
                ext = ".ogg"
            elif type == "itunes":
                ext = ".mp4b"
            for f_url in bs.find_all("a", href =True):
                l = f_url["href"]
                if l.endswith(ext):
                    dl = f"{burl}{l}"
                    r = requests.get(dl)
                    if r.ok:
                        fname = os.path.join("downloaded_files", f"ebook-{l.split(".")[0].split("/")[-1]}.{ext}")
                        fmode = 'wb'
                        if (onefile):
                            fname = os.path.join("downloaded_files", "merged.txt")
                            fmode = 'ab'
                        with open(fname, fmode) as file :
                            file.write(r.content)
                    else:
                        print("download failed")
def main():
    parser = argparse.ArgumentParser(prog="GutenbergScraper.py",add_help=False)
    parser.add_argument("-a", "--author", type=int)
    parser.add_argument("-o", "--onefile", action="store_true")
    parser.add_argument("-f", "--file_type", type=str, default="text")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if not args.author and not args.help:
        parser.error("Author ID is required.")

    if args.onefile and args.file_type != "text":
        parser.error("The --onefile option only supports the 'text' file format.")

    if args.file_type not in ["text", "kindle", "old_kindle", "epub3", "epub", "epub_noimages", "zip", "mp3", "speex", "ogg", "itunes"]:
        parser.error("Chosen file type is not supported.")

    if args.help:
        print("""Usage: GutenbergScraper.py [-h] [-a AUTHOR_ID] [-o] [-f FILE_TYPE]              
Options:
  -h, --help                  Show this help message and exit
  -a AUTHOR_ID, --author AUTHOR_ID  Specify the author ID
  -o, --onefile               Enable onefile mode (only supports 'text' format)
  -f FILE_TYPE, --file_type FILE_TYPE  Specify the file type to download (default: text)

Supported formats:
  1) text           Default format
  2) kindle         For Kindle
  3) old_kindle     For older Kindles
  4) epub3          For e-readers
  5) epub           For older e-readers
  6) epub_noimages  For older e-readers (no images)
  7) zip            For HTML zip
  8) mp3            For MP3 audio
  9) speex          For Speex audio
 10) ogg            For Ogg Vorbis audio
 11) itunes         For Apple iTunes audiobooks""")

    base_url = 'https://www.gutenberg.org'
    r = requests.get(base_url)
    if not args.help and r.ok:
        book_urls = get_all_books(base_url, args.author)
        if (book_urls[0] == -1):
            print("error inital page not loaded")
        elif (book_urls[0] == -2):
            print("no books found")
        else:
            download_files(base_url, book_urls, args.onefile, args.file_type)

if __name__ == "__main__":
    main()