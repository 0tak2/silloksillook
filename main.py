# TODO: Apply TUI https://github.com/bczsalba/pytermgui
# TODO: sqlite 연동, 필드에 수정 여부 추가
# TODO: 엑셀 익스포트

import os
import subprocess
import sillookParser
import urllib3
from datetime import datetime
from sillookArticleEntity import SillookArticleEntity
from sillookGlobal import SillookGlobal
import sillookDatabase as db
import sillookPandas as sillokpd
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

urllib3.disable_warnings()

globals = SillookGlobal()
IS_WINDOWS = globals.getIsWindows()
MENU = globals.getMenuItems()

console = Console()


def clear() -> None:
    if IS_WINDOWS:
        os.system('cls')
    else:
        os.system('clear')

def showMenu() -> None:
    def makeMenuString(name, key):
        return f"[yellow][b]{key[0]}[/b][/yellow]{key[1:]}\n[yellow]{name}[/yellow]"

    menu_renderables = [Panel(makeMenuString(item["name"], item["key"]), expand=True) for item in MENU]
    console.print(Columns(menu_renderables))

def enterMenu(cmd: str) -> None:
    if cmd == 'V' or cmd == 'v' or cmd == 'ㅍ' or cmd == 'View':
        toggleViewMode()
    elif cmd == 'A' or cmd == 'a' or cmd == 'ㅁ' or cmd == 'Add':
        addDataPrompt()
    elif cmd == 'M' or cmd == 'm' or cmd == 'ㅡ' or cmd == 'Modify':
        modifyPrompt()
    elif cmd == 'E' or cmd == 'e' or cmd == 'ㄷ' or cmd == 'Export':
        exportPrompt()
    elif cmd == 'B' or cmd == 'b' or cmd == 'ㅠ' or cmd == 'Basket':
        changeBasketPrompt()
    elif cmd == 'X' or cmd == 'x' or cmd == 'ㅌ' or cmd == 'Exit':
        quit()
    elif cmd == '':
        if globals.getViewMode() == 1:
                globals.setCurrentId(globals.getCurrentId() + 1)
    elif cmd == ' ':
        if globals.getViewMode() == 1:
                globals.setCurrentId(globals.getCurrentId() - 1)
    else:
        console.print("!!! 잘못된 명령을 입력했습니다.\n아래와 같은 명령을 실행할 수 있습니다.\n", style="bold")
        printHelp()
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold")
        input()

def modifyPrompt() -> None:
    clear()
    console.print("\n\n====== 데이터 수정 / 삭제 ======\n", style="bold yellow")

    index = None

    if globals.getViewMode() == 0:
        count = showAllDataPanel()
        if count < 0:
            console.print("!!! 수정할 데이터가 없습니다.", style="bold yellow")

        console.print(f"> 수정할 데이터의 DB ID 입력 <기본값: 1>: ", style="bold yellow")
        index = input()
        if index == '':
            index = 1
            
    elif globals.getViewMode() == 1:
        index = globals.getCurrentId()

    showDetailDataPanel(index)
    console.print("\n! 아래에 수정할 컬럼을 입력해주세요. 데이터 전체를 삭제하려면 X를 입력해주세요.\n메모=M, 제목=T, 위치=L, 국문내용=K, 원문내용=H, 삭제=X", style="bold")

    while True:
        console.print(f"> 수정할 항목을 선택: ", style="bold yellow")
        col = input()
        if col == 'M' or col == 'm' or col == 'ㅡ':
            modify(index, 'note')
            break
        elif col == 'T' or col == 't' or col == 'ㅅ':
            console.print(f"> 원본 데이터로부터 내용을 수정하려고 하고 있습니다.\n 의도한 것인지 다시 한 번 확인해보십시오.", style="bold red")
            console.print(f"> 계속 수정하려면 엔터를 누르세요.", style="bold red")
            input()
            modify(index, 'title')
            break
        elif col == 'L' or col == 'l' or col == 'ㅣ':
            console.print(f"> 원본 데이터로부터 내용을 수정하려고 하고 있습니다.\n 의도한 것인지 다시 한 번 확인해보십시오.", style="bold red")
            console.print(f"> 계속 수정하려면 엔터를 누르세요.", style="bold red")
            input()
            modify(index, 'location')
            break
        elif col == 'K' or col == 'k' or col == 'ㅏ':
            console.print(f"> 원본 데이터로부터 내용을 수정하려고 하고 있습니다.\n 의도한 것인지 다시 한 번 확인해보십시오.", style="bold red")
            console.print(f"> 계속 수정하려면 엔터를 누르세요.", style="bold red")
            input()
            modify(index, 'content_kor')
            break
        elif col == 'H' or col == 'h' or col == 'ㅗ':
            console.print(f"> 원본 데이터로부터 내용을 수정하려고 하고 있습니다.\n 의도한 것인지 다시 한 번 확인해보십시오.", style="bold red")
            console.print(f"> 계속 수정하려면 엔터를 누르세요.", style="bold red")
            input()
            modify(index, 'content_han')
            break
        elif col == 'X' or col == 'x' or col == 'ㅌ':
            console.print(f"> 정말로 삭제하려면 '삭제'라고 입력하세요. 이 작업은 돌이킬 수 없습니다.", style="bold red")
            confirmInput = input()
            if confirmInput == "삭제" or confirmInput == "'삭제'":
                delete(index)
                break
        else:
            console.print("\n!!! 잘못된 명령을 입력했습니다.\n아래와 같이 입력해주세요.", style="bold")
            console.print("메모=M, 제목=T, 위치=L, 국문내용=K, 원문내용=H", style="bold")

def delete(index) -> None: 
    try:
        conn, cur = globals.getDB()
        db.deleteById(conn, cur, index)   
    except Exception as e:
        console.print("!!! 데이터 삭제 중 오류가 발생했습니다.", e, style="bold red")
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold red")
        input()

    console.print("* 데이터 삭제가 완료되었습니다.", style="bold blue")
    console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold blue")
    input()

def modify(index, col) -> None:
    conn, cur = globals.getDB()

    originalEntity = db.getOneById(cur, index) # 원본 데이터를 불러옴
    originalContent = ""
    if col == "title":
        originalContent = originalEntity.getTitle()
    elif col == "location":
        originalContent = originalEntity.getLocation()
    elif col == "content_kor":
        originalContent = originalEntity.getContentKor()
    elif col == "content_han":
        originalContent = originalEntity.getContentHan()
    elif col == "note":
        originalContent = originalEntity.getNote()

    tmpFileName = "tmp.txt" # 원본 데이터가 들어있는 텍스트 파일을 작성
    with open(tmpFileName, 'w') as f:
        f.write("# 데이터를 수정하고 저장한 후, 에디터를 닫으면 변경 내용이 반영됩니다.\n")
        f.write("# '#'으로 시작하는 줄은 변경 내용에 반영되지 않습니다.\n")
        f.write("# \n")
        f.write(originalContent)

    if IS_WINDOWS: # 에디터를 call
        subprocess.call(f"notepad.exe {tmpFileName}")
    else:
        subprocess.call(f"vim {tmpFileName}", shell=True)
    
    # 작성된 텍스트 파일의 내용을 불러옴
    newContent = ""
    with open(tmpFileName, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.strip()[0] == '#':
            continue
        else:
            newContent = newContent + line
    
    try:
        result = db.updateValue(conn, cur, index, col, newContent) # 에디터가 종료되면 UPDATE 문을 실행
    except Exception as e:
        console.print(e, style="bold red")
        result = -1
    finally:
        os.remove(tmpFileName)
    
    if result == 0:
        console.print("* 데이터 수정이 완료되었습니다.", style="bold blue")
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold blue")
        input()
    else:
        console.print("!!! 데이터 수정 중 오류가 발생했습니다.", style="bold red")
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold red")
        input()

def exportPrompt() -> None:
    fullLocation = globals.getDbFile()
    basketName = fullLocation.split('/')[-1].split('.')[0]

    dt = datetime.now()
    timestr = dt.strftime("%Y%m%d-%H%M%S.%f")
    timestr_for_sheet = dt.strftime("%Y%m%d")
    xlsx_default = f"exports/{basketName}_{timestr}.xlsx"

    clear()
    console.print("\n\n====== 엑셀 내보내기 ======\n", style="bold yellow")
    console.print("아래에 내보낼 파일의 경로와 이름을 입력해주세요.\n")
    console.print(f"> 내보낼 파일의 경로 입력 <기본값: {xlsx_default}>: ", style="bold yellow")
    file = input()
    if file == "":
        file = xlsx_default

    try:
        export(file, f"{basketName} ({timestr_for_sheet})")
        console.print("* 내보내기가 완료되었습니다. exports 디렉토리를 확인해보세요.", style="bold blue")
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold blue")
        input()
    except Exception as e:
        console.print("!!! 내보내기 중 오류가 발생했습니다.", e, style="bold red")
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold red")
        input()

def export(file, sheetName) -> None:
    conn, cur = globals.getDB()
    globals.setData(db.getAll(cur))

    TwoDList = sillokpd.entitiesTo2DList(globals.getData())
    df = sillokpd.makeDf(TwoDList)
    sillokpd.dfToExcel(df, file, sheetName)

def toggleViewMode() -> None:
    if globals.getViewMode() == 0:
        globals.setViewMode(1)
    elif globals.getViewMode() == 1:
        globals.setViewMode(0)

def addDataPrompt() -> None:
    clear()
    console.print("\n\n====== 새로운 기사 추가하기 ======", style="bold yellow")
    console.print("> 기사의 주소 혹은 아이디: ", style="bold yellow")
    src = input()

    try:
        item = sillookParser.parseAllAndGetEntity(src)

        console.print("\n* 다음과 같이 기사를 불러왔습니다.", style="bold yellow")
        printArticle(item, isShort=True, includeNote=False)

        console.print("\n> 이 기사에 대한 메모 (없으면 엔터): ", style="bold yellow")
        note = input()
        item.set(note=note)
        addData(item)
    except Exception as e:
        console.print("!!! 파싱 중 오류가 발생했습니다. 링크나 아이디가 잘못 되었을 수 있습니다.", e, style="bold red")
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold red")
        input()

def addData(item: SillookArticleEntity) -> bool:
    conn, cur = globals.getDB()
    newData = db.addArticle(conn, cur, item)
    globals.setData(newData)

def changeBasketPrompt() -> None:
    default = globals.getPreferences()['lastUsedDB']

    clear()
    console.print("\n\n====== 바구니 바꾸기 ======\n", style="bold yellow")
    console.print("아래에 데이터베이스 파일의 이름을 입력해주세요.\n")
    console.print("db 폴더에 파일을 복사하고, 해당 파일의 이름을 입력하시면 됩니다. (확장자 .db는 제외)")
    console.print("그런 이름의 파일이 없으면 새로 만듭니다.\n")
    console.print(f"> 바구니 이름 입력 <기본값: {default}>: ", style="bold yellow")

    dbFile = input()

    if dbFile == "":
        dbFile = default

    if ('/' in dbFile) or ('\\' in dbFile): # 전체 경로를 직접 입력했을 경우에는 입력값 자체를 쓴다
        fullLocation = dbFile
    else:
        fullLocation = "db/" + dbFile + '.db'
    changeBasket(fullLocation)

    globals.updatePreferences({
        "lastUsedDB": fullLocation
    })

def changeBasket(dbFile) -> None:
    globals.setDbFile(dbFile)
    globals.setConnection()

def sliceLetters(original: str, letters: int) -> str:
    if len(original) >= letters: # 50자 이상
        return original[0:letters] + "..."
    elif len(original) == 0: # 0자
        return ""
    else: # 0자 초과 50자 미만
        return original

def showAllDataPanel() -> int:
    conn, cur = globals.getDB()
    globals.setData(db.getAll(cur))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("순번", overflow="Fold")
    table.add_column("기사 ID", overflow="Fold")
    table.add_column("기사 제목", overflow="Fold")
    table.add_column("기사 위치", overflow="Fold")
    table.add_column("국문 내용", overflow="Fold")
    table.add_column("메모", overflow="Fold")

    if globals.getSizeOfData() != 0:
        for item in globals.getData():
            contentKorSummary = sliceLetters(item.getContentKor(), 15)
            noteSummary = sliceLetters(item.getNote(), 50)
            table.add_row(
                str(item.getId()), item.getArticleId(), item.getTitle(), item.getLocation(), contentKorSummary, noteSummary
            )
    else:
        table.add_row("1", "여기에는", " 아직 ", "저장된", "데이터가", "없습니다.")

    console.print(table)
    return globals.getSizeOfData()

def showDetailDataPanel(id) -> None:
    currentArticle = None

    conn, cur = globals.getDB()
    globals.setData(db.getAll(cur))

    for item in globals.getData():
        if item.getId() == id:
            currentArticle = item
            break
    
    if currentArticle != None:
        printArticle(currentArticle)
    else:
        currentArticle = SillookArticleEntity(id, "", "", "", "", "", "", "")
        printArticle(currentArticle)

def printHelp() -> None:
    def makeMenuString(name, key, desc):
        return f"[yellow][b]{key[0]}[/b][/yellow]{key[1:]}\n[yellow]{name}[/yellow]\n{desc}"

    menu_renderables = [Panel(makeMenuString(item["name"], item["key"], item["desc"]), expand=True) for item in MENU]
    console.print(Columns(menu_renderables))

def printArticle(article: SillookArticleEntity, isShort=False, includeNote=True) -> None:
    articleInfoStrings = []

    dbID = str(article.getId())
    articleId = article.getArticleId()
    title = article.getTitle()
    location = article.getLocation()
    content_kor = article.getContentKor()
    content_han = article.getContentHan()
    metadata = article.getMetadata()
    note = article.getNote()

    if isShort:
        articleId = sliceLetters(articleId, 200)
        title = sliceLetters(title, 200)
        location = sliceLetters(location, 200)
        content_kor = sliceLetters(content_kor, 200)
        content_han = sliceLetters(content_han, 200)
        metadata = sliceLetters(metadata, 200)
    
    if dbID != "None":
        articleInfoStrings.append('\n')
        articleInfoStrings.append("[blue][b]* 순번[/b][/blue]")
        articleInfoStrings.append(dbID)
        articleInfoStrings.append('\n\n')
    else:
        articleInfoStrings.append('\n')

    if not article.isEmpty():
        articleInfoStrings.append("[blue][b]* 기사 ID[/b][/blue]")
        articleInfoStrings.append(articleId)
        articleInfoStrings.append('\n\n')
        articleInfoStrings.append("[blue][b]* 기사 제목[/b][/blue]")
        articleInfoStrings.append(title)
        articleInfoStrings.append('\n\n')
        articleInfoStrings.append("[blue][b]* 기사 위치[/b][/blue]")
        articleInfoStrings.append(location)
        articleInfoStrings.append('\n\n')
        articleInfoStrings.append("[blue][b]* 국문 내용[/b][/blue]")
        articleInfoStrings.append(content_kor)
        articleInfoStrings.append('\n\n')
        articleInfoStrings.append("[blue][b]* 원문 내용[/b][/blue]")
        articleInfoStrings.append(content_han)
        articleInfoStrings.append('\n\n')
        articleInfoStrings.append("[blue][b]* 메타데이터[/b][/blue]")
        articleInfoStrings.append(metadata)

        if includeNote:
            articleInfoStrings.append('\n\n')
            articleInfoStrings.append("[blue][b]* 메모 사항[/b][/blue]")
            articleInfoStrings.append(note)
            articleInfoStrings.append('\n')
    else:
        articleInfoStrings.append("[b]* 불러올 수 있는 데이터가 없습니다.[/b]\n")
        if dbID != "None":
            articleInfoStrings.append(f"[b]아직 저장된 데이터가 없거나, {dbID}번 인덱스에 해당하는 데이터가 삭제되었을 수 있습니다.[/b]")
            articleInfoStrings.append('\n')
        else:
            articleInfoStrings.append(f"[b]아직 어떠한 데이터도 저장되지 않은 것일 수 있습니다.[/b]")
            articleInfoStrings.append('\n')

    
    console.print(Panel('  '.join(articleInfoStrings)))

def printCurrentBasket() -> None:
    fullLocation = globals.getDbFile()
    fileName = fullLocation.split('/')[-1].split('.')[0]
    console.print(f"\n[ 현재 바구니: {fileName} ({fullLocation}) ]\n", style="bold magenta")

def main() -> None:
    globals.setConnection()

    while True:
        clear()
        showMenu()

        printCurrentBasket()

        if globals.getViewMode() == 0:
            count = showAllDataPanel()
            if count > 0:
                showMenu()
        elif globals.getViewMode() == 1:
            showDetailDataPanel(globals.getCurrentId())
            console.print("\n! 다음 아이템을 보려면 엔터를 누르세요")
            console.print("! 이전 아이템을 보려면 스페이스바를 누르고, 엔터를 누르세요\n")
            showMenu()

        enterMenu(input("> "))

if __name__ == '__main__':
    main()