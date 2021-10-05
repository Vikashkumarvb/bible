import requests
import json
from bs4 import BeautifulSoup
import mysql.connector
import csv
import io
def ExportCSV():
    con= getConnection()
    cur= con.cursor()
    qur= 'SELECT * FROM books'
    cur.execute(qur)
    rows = cur.fetchall()
    headers = [col[0] for col in cur.description] # get headers
    rows.insert(0, tuple(headers))
    with io.open(r'C:\Users\Lenovo\Downloads\New folder\file.csv', "w", encoding="utf-8") as fp: 
        myFile = csv.writer(fp)
        myFile.writerows(rows)
    
    cur.close()
    con.close()

def getConnection():
    return mysql.connector.connect(host='localhost',database='bible',user='root',password='root')
    
def insertIntoTable(version,book,chapter,topic,verse):
    
    connection = getConnection()
    ot = ['Gen','Exod','Lev','Num','Deut','Josh','Judg','Ruth','1Sam','2Sam','1Kngs','2Kngs','1Chr','2Chr','Ezra','Neh','Esth','Job','Psalm','Prov','Eccl','Song','Isa','Jer','Lam','Ezek','Dan','Hos','Joel','Amos','Obad','Jonah','Mic','Nah','Hab','Zeph','Hag','Zech','Mal']
    nt = ['Matt','Mark','Luke','John','Acts','Rom','1Cor','2Cor','Gal','Eph','Phil','Col','1Thess','2Thess','1Tim','2Tim','Titus','Phlm','Heb','Jas','1Pet','2Pet','1John','2John','3John','Jude','Rev']
        
    if book in ot:
        testament= 'ot'
    else:
        testament= 'nt'
    print("inserting")
    success = False
    try:
        cursor = connection.cursor()
        query = 'INSERT INTO books (Version, Book,Testament, Topic, Verse,Chapeter) VALUES (%s,%s,%s,%s,%s,%s)'
        val =  [(version,book,testament,topic,verse,chapter)]
        cursor.executemany(query, val)
        connection.commit()
        success = True
        cursor.close()
    except Exception as e:
        print("ERROR", e)
    finally:
        connection.close()
    return success
def parsefun(book):
    
    response = requests.get(f"https://ap.api.stepbible.org/rest/search/masterSearch/reference={book}%7Cversion=ESV/NHVUG//////en?lang=en-US")

    if response.status_code==200:
        parse = json.loads(response.text)
        
        version=parse['searchTokens'][0]['token']
        
        shortName=parse['searchTokens'][1]['enhancedTokenInfo']['shortName']
        book,chapter = shortName.split()
        
        nextChapter=parse['nextChapter']['osisKeyId']
        islast=parse['nextChapter']['lastChapter']

        
        
        print(version)
        print(book)
        print(chapter)
        

        soup = BeautifulSoup(response.content,"html.parser")


        soup9 = soup.find_all('span',attrs={'class':'verse ltrDirection'})
        for i in soup9:
            link = i.find('a',attrs={'class':'verseLink'})
            topic= link.text
            sup = i.find('sup',attrs={'class':'note'})
            if link:
                link.decompose()
            if sup:
                sup.decompose()
            verse=' '.join(i.stripped_strings)
            print(insertIntoTable(version,book,chapter,topic,verse))
            
        #while(islast=='true'):
            #parsefun(nextChapter)
    else:
        print("ERROR")

def main():
       parsefun('Gen.1')

if __name__=='__main__':
   # main()
   ExportCSV()
