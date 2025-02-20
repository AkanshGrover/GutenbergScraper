import requests, os, argparse, csv
from bs4 import BeautifulSoup
from thefuzz import process

def get_all_books(howmany, what, base_url, a_id=None, subject=None):
    si = 1
    books_url = []
    if howmany == -1:
        howmany = float("inf")
    cn = 1
    if what == "a":
        url = f"{base_url}/ebooks/author/{a_id}"
    elif what == "s":
        url = subject
    while True:
        f_url = f"{url}?start_index={si}"
        r = requests.get(f_url)

        if not r.ok:
            return([-1])

        bs = BeautifulSoup(r.content, 'html.parser')

        for link in bs.select("li.booklink a.link[href]"):
            if cn <= howmany:
                id = link["href"]
                if "ebooks" in id:
                    books_url.append(f"{base_url}{id}")
                    cn+=1
            else:
                break

        if len(books_url) == 0:
            return([-2])
        elif len(books_url) == howmany:
            return(books_url)

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
                        fname = os.path.join("downloaded_files", f"ebook-{l.split(".")[0].split("/")[-1]}{ext}")
                        fmode = 'wb'
                        if (onefile):
                            fname = os.path.join("downloaded_files", "merged.txt")
                            fmode = 'ab'
                        with open(fname, fmode) as file :
                            file.write(r.content)
                    else:
                        print("download failed")

def update_search_subjects():
    si = 1
    subject_dict = {}
    while True:
        url = f"https://www.gutenberg.org/ebooks/subjects/search/?start_index={si}"
        r = requests.get(url)
        if not r.ok:
            return([-1])
        
        bs = BeautifulSoup(r.content, 'html.parser')
    
        for subjects in bs.select("li.navlink:not(.grayed) a.link[href]"):
            s_id = "https://www.gutenberg.org" + subjects.get("href")
            title = subjects.find_next("span", class_="title").text.strip()
            if s_id:
                subject_dict[title] = s_id
    
        if len(subject_dict) == 0:
            return([-2])
    
        next_exist = bs.find("a", string="Next")
        if next_exist:
            si += 25
        else:
            break

    with open("subjects.csv", "w", newline="") as file:
            writer = csv.writer(file)
            for title, s_id in subject_dict.items():
                writer.writerow([title, s_id])
    return subject_dict

def subject_loader():
    subject_dic = {}
    with open("subjects.csv", "r", newline="") as file:
        csvFile = csv.reader(file)
        for row in csvFile:
            title, s_id = row
            subject_dic[title] = s_id
    return subject_dic

def search_subject(user_ip, subject_dic, limit=5, threshold=60):
    matches = process.extract(user_ip, subject_dic.keys(), limit=limit)
    results = []
    for match, score in matches:
        if score >= threshold:
            results.append((match, subject_dic[match]))
    sno = 1
    print("Choose subject which matches your input the most:")
    for i in results:
        print(sno, i[0])
        sno+=1
    no_ip = int(input("Enter S.No.: "))
    final_subject = results[no_ip-1]
    print(f"Downloading ebooks from the topic {final_subject[0]}.")
    return final_subject

def downloader(base_url, what, onefile=False, number="-1", author=None, subject=None, file_type="text"):
    book_urls = get_all_books(number, what, base_url, a_id=author, subject=subject)
    if (book_urls[0] == -1):
        print("error inital page not loaded")
    elif (book_urls[0] == -2):
        print("no books found")
    else:
        download_files(base_url, book_urls, onefile, file_type)

def main():
    parser = argparse.ArgumentParser(prog="GutenbergScraper.py",add_help=False)
    parser.add_argument("-a", "--author", type=int)
    parser.add_argument("-o", "--onefile", action="store_true")
    parser.add_argument("-f", "--file_type", type=str, default="text")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-u", "--update", action="store_true")
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-n", "--number", type=int, default="-1")

    args = parser.parse_args()

    if not args.author and not args.help and not args.update and not args.list and not args.search:
        parser.error("Author ID is required.")

    if args.onefile and args.file_type != "text":
        parser.error("The --onefile option only supports the 'text' file format.")

    if args.file_type not in ["text", "kindle", "old_kindle", "epub3", "epub", "epub_noimages", "zip", "mp3", "speex", "ogg", "itunes"]:
        parser.error("Chosen file type is not supported.")

    if args.help:
        print("""Usage: GutenbergScraper.py [-h] [-a AUTHOR_ID] [-o] [-f FILE_TYPE] [-u] [-l] [-s SUBJECT] [-n NUMBER]              
Options:
  -h, --help                  Show this help message and exit
  -a AUTHOR_ID, --author AUTHOR_ID  Specify the author ID
  -o, --onefile               Enable onefile mode (only supports 'text' format)
  -f FILE_TYPE, --file_type FILE_TYPE  Specify the file type to download (default: text)
  -u, --update                Updates the list of search topics
  -l, --list                  Lists all the subjects
  -s SUBJECT, --search SUBJECT      Search different subjects
  -n NUMBER, --number NUMBER  Specify the number of ebooks to download

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

    if not os.path.isfile("subjects.csv"):
        update_search_subjects()

    loaded_subject = subject_loader()

    base_url = 'https://www.gutenberg.org'
    r = requests.get(base_url)
    if not args.help and r.ok and not args.update and not args.list and not args.search:
        downloader(what="a", onefile=args.onefile, number=args.number, base_url=base_url, author=args.author, file_type=args.file_type)
    elif args.update:
        update_search_subjects()
        loaded_subject = subject_loader()
    elif args.list:
        for x in loaded_subject.keys():
            print(x)
    elif args.search:
        s = search_subject(args.search, loaded_subject)[1]
        downloader(what="s", onefile=args.onefile, number=args.number, base_url=base_url, subject=s, file_type=args.file_type)

if __name__ == "__main__":
    main()