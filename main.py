# TODO: Apply TUI https://github.com/bczsalba/pytermgui
# TODO: sqlite 연동, 필드에 수정 여부 추가
# TODO: 엑셀 익스포트

import os
import sillookParser
import urllib3
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
        console.print('수정')
        input()
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

def exportPrompt() -> None:
    fullLocation = globals.getDbFile()
    basketName = fullLocation.split('/')[-1].split('.')[0]
    xlsx_default = "exports/" + basketName + ".xlsx"

    clear()
    console.print("\n\n====== 엑셀 내보내기 ======\n", style="bold yellow")
    console.print("아래에 내보낼 파일의 경로와 이름을 입력해주세요.\n")
    console.print(f"> 내보낼 파일의 경로 입력 <기본값: {xlsx_default}>: ", style="bold yellow")
    file = input()
    if file == "":
        file = xlsx_default

    try:
        export(file, basketName + " 바구니의 내보내기")
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
    clear()
    console.print("\n\n====== 바구니 바꾸기 ======\n", style="bold yellow")
    console.print("아래에 데이터베이스 파일의 이름을 입력해주세요.\n")
    console.print("db 폴더에 파일을 복사하고, 해당 파일의 이름을 입력하시면 됩니다. (확장자 .db는 제외)")
    console.print("그런 이름의 파일이 없으면 새로 만듭니다.\n")
    console.print("> 바구니 이름 입력 <기본값: default>: ", style="bold yellow")
    dbFile = input()
    if dbFile == "":
        dbFile = "default"
    fullLocation = "db/" + dbFile + '.db'
    changeBasket(fullLocation)

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
    table.add_column("DB ID", overflow="Fold")
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
        try:
            showDetailDataPanel(id + 1)
        except:
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
    
    if not article.isEmpty():
        articleInfoStrings.append('\n')
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
        
        if dbID != "None":
            articleInfoStrings.append('\n\n')
            articleInfoStrings.append("[blue][b]* 내 DB에서의 INDEX[/b][/blue]")
            articleInfoStrings.append(dbID)
    else:
        articleInfoStrings.append("[b]* 여기에는 어떠한 데이터도 없습니다.[/b]")
    
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