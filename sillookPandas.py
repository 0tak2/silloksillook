import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
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
    df = pd.DataFrame(TwoDList, columns =['순번', '기사ID', '기사제목', '기사위치', '국문내용', '원문내용', '메타데이터', '메모'])
    return df

def dfToExcel(df, fileName, sheet_name):
    df.to_excel(fileName, sheet_name=sheet_name, index=False)

    # 스타일링을 위해 다시 파일을 연다
    wb = load_workbook(fileName)
    ws = wb.active

    # 각 열에 최적의 너비를 설정한다
    ws.column_dimensions["A"].width = 2.10 * 4
    ws.column_dimensions["B"].width = 4.38 * 4
    ws.column_dimensions["C"].width = 7.00 * 4
    ws.column_dimensions["D"].width = 9.15 * 4
    ws.column_dimensions["E"].width = 10.00 * 4
    ws.column_dimensions["F"].width = 10.00 * 4
    ws.column_dimensions["G"].width = 9.15 * 4
    ws.column_dimensions["H"].width = 10.00 * 4

    # 모든 셀에 자동 줄바꿈을 설정한다
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True)
    
    ws['C2'].alignment = Alignment(wrap_text=True)

    wb.save(fileName)
