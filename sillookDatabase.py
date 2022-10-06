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
    
    try:
        cursor.execute("INSERT INTO articles (articleId, title, location, content_kor, \
            content_han, metadata, note) values (?, ?, ?, ?, ?, ?, ?)", newArticleTuple)
        conn.commit()
    except Exception as e:
        raise Exception("INSERT 중 오류 발생 ", e)

    return getAll(cursor)

def getOneById(cursor, id):
    try:
        cursor.execute("SELECT * FROM articles WHERE id=?", (str(id)))
        rows = cursor.fetchall()
    except Exception as e:
        raise Exception("SELECT 중 오류 발생 ", e)

    if len(rows) > 1:
        raise Exception("SELECT 중 오류 발생: 특정 id로 조회한 값의 개수가 2개 이상")

    result_row = rows[0]

    key = result_row[0]
    articleId = result_row[1]
    title = result_row[2]
    location = result_row[3]
    content_kor = result_row[4]
    content_han = result_row[5]
    metadata = result_row[6]
    note = result_row[7]
    
    return SillookArticleEntity(key, articleId, title, location,
            content_kor, content_han, metadata, note)

def getAll(cursor):
    items = []

    try:
        cursor.execute("SELECT * FROM articles")
        rows = cursor.fetchall()
    except Exception as e:
        raise Exception("SELECT 중 오류 발생 ", e)

    for row in rows:
        key = row[0]
        articleId = row[1]
        title = row[2]
        location = row[3]
        content_kor = row[4]
        content_han = row[5]
        metadata = row[6]
        note = row[7]
        items.append(SillookArticleEntity(key, articleId, title, location,
            content_kor, content_han, metadata, note))
    
    return items

def updateValue(conn, cursor, id, column, newValue) -> int:
    verified = False
    for col in ["title", "location", "content_kor", "content_han", "note"]:
        if column == col:
            verified = True
            break
    
    if not verified:
        return -1
    
    try:
        sql = f"UPDATE articles SET {column} = '{newValue}' WHERE id={str(id)}"
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        raise Exception("UPDATE 중 오류 발생 ", e)

    return 0

def deleteById(conn, cursor, id):
    try:
        cursor.execute("DELETE FROM articles WHERE id = ?", (id))
        conn.commit()
    except Exception as e:
        raise Exception("DELETE 중 오류 발생 ", e)
