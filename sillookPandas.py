import pandas as pd
from sillookArticleEntity import SillookArticleEntity

def entitiyToList(item: SillookArticleEntity):
    dbID = str(item.getId())
    articleId = item.getArticleId()
    title = item.getTitle()
    location = item.getLocation()
    content_kor = item.getContentKor()
    content_han = item.getContentHan()
    metadata = item.getMetadata()
    note = item.getNote()

    return [dbID, articleId, title, location, content_kor,
        content_han, metadata, note]

def entitiesTo2DList(entitiesList):
    result = list(map(entitiyToList, entitiesList))
    return result

def makeDf(TwoDList):
    df = pd.DataFrame(TwoDList, columns =['내 DB ID', '기사ID', '기사제목', '기사위치', '국문내용', '원문내용', '메타데이터', '메모'])
    return df

def dfToExcel(df, fileName, sheet_name):
    df.to_excel(fileName, sheet_name=sheet_name, index=False)