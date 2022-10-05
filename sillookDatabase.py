from re import X
import sqlite3
from sillookArticleEntity import SillookArticleEntity

def makeConnction(dbFile = "db/defalut.db"):
    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS articles \
        (id integer PRIMARY KEY AUTOINCREMENT, articleId text, title text, \
            location text, content_kor text, content_han text, \
            metadata text, note text)")
    conn.commit()

    return conn, cursor

def addArticle(conn, cursor, article: SillookArticleEntity):
    articleId = article.getArticleId()
    title = article.getTitle()
    location = article.getLocation()
    content_kor = article.getContentKor()
    content_han = article.getContentHan()
    metadata = article.getMetadata()
    note = article.getNote()

    newArticleTuple = (articleId, title, location, content_kor, content_han,
        metadata, note)
    
    cursor.execute("INSERT INTO articles (articleId, title, location, content_kor, \
        content_han, metadata, note) values (?, ?, ?, ?, ?, ?, ?)", newArticleTuple)
    
    conn.commit()

    return getAll(cursor)

def getAll(cursor):
    data = []

    cursor.execute("SELECT * FROM articles")
    rows = cursor.fetchall()

    for row in rows:
        key = row[0]
        articleId = row[1]
        title = row[2]
        location = row[3]
        content_kor = row[4]
        content_han = row[5]
        metadata = row[6]
        note = row[7]
        data.append(SillookArticleEntity(key, articleId, title, location,
            content_kor, content_han, metadata, note))
    
    return data