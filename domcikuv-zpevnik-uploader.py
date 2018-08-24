import docx2txt
import sys
import os
import sys
import requests
from PyPDF2 import PdfFileReader, PdfFileWriter

def pdf_splitter(path):
    fname = os.path.splitext(os.path.basename(path))[0]

    pdf = PdfFileReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))

        output_filename = 'document_page_{}.pdf'.format(page+1)

        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)

        #print('Created: {}'.format(output_filename))
    return pdf.getNumPages()

def pdf_splitter_cleanup(path,number_of_pages):
    for page in range(number_of_pages):
        os.remove('document_page_{}.pdf'.format(page+1))
    return 

class Song:
    def __init__(self, title, artist, language, date, file_path):
        self.title=title
        self.artist=artist
        self.language=language
        self.date=date
        self.file_path=file_path
    def __str__(self):
        return "{}: {} | Language: {} ({}), path: {}".format(self.title, self.artist, self.language, self.date, self.file_path)

def get_names_and_artists(text):
    text=text.replace("\t", "")
    lines=text.splitlines()
    return [line for line in lines if ": " in line and line[0:2]!="R:" and line[0]!='®']

def translate_lang(lang):
    return {
        "c": "CZECH",
        "e": "ENGLISH",
        "s": "SLOVAK",
        "sp": "SPANISH",
        "o": "OTHER"
    }.get(lang.lower(), "CZECH")

#parse cmd arguments
if len(sys.argv)<3:
    print("You need to pass two arguments: .docx file and .pdf file")
    quit()
if(sys.argv[1][-4:]=="docx"):
    docx_file_path=str(sys.argv[1])
    pdf_file_path = str(sys.argv[2])
else:
    docx_file_path=str(sys.argv[2])
    pdf_file_path = str(sys.argv[1])
    
number_of_pages=pdf_splitter(pdf_file_path)
fname=os.path.splitext(os.path.basename(pdf_file_path))[0]
date=fname[8:10]+fname[11:13]
text = docx2txt.process(docx_file_path)
#check with the user what are actual songs and find out the language
actual_songs = []
index=0
for possible_song in get_names_and_artists(text):
    read=input("Is this a song? {} (Y/n)  ".format(possible_song))
    if read == "" or read=="Y" or read=="y":
        lang=input("What's the language of this song? [C]zech, [E]nglish, [S]lovak, [Sp]anish, [O]ther  ")
        actual_songs.append(Song(possible_song.split(':')[1][1:], possible_song.split(':')[0], translate_lang(lang),date,
            'document_page_{}.pdf'.format(index+1)))
        index+=1
        print()
if number_of_pages!=len(actual_songs):
    print("Number of pages ({}) different to number of supposed songs ({}). Aborting...".format(number_of_pages, len(actual_songs)))
    quit()

#create a POST and send it
for song in actual_songs:
    url = 'http://appelt.cz/domcikuvzpevnik/upload.php'
    payload = {'access_password': 'domcik', 'inputTitle': song.title, 'inputArtist': song.artist, 'inputDate': str(song.date), 'inputLanguage': song.language}
    files = {'best': open(song.file_path, 'rb'), 'compressed': open(song.file_path, 'rb')}
    r = requests.post(url, data=payload, files=files)
    if "Píseň byla úspěšně zapsána do databáze. :)" not in r.text:
        print("Error with song " + str(song)+"\n"+r.text)
    print(song)

#clean up the files
pdf_splitter_cleanup(pdf_file_path,number_of_pages)