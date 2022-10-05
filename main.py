# TODO: Apply TUI https://github.com/bczsalba/pytermgui
# TODO: sqlite 연동, 필드에 수정 여부 추가
# TODO: 엑셀 익스포트

import os
import platform
import sillokParser
import urllib3
from sillokArticleEntity import SillokArticleEntity
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

urllib3.disable_warnings()

if platform.system() == "Windows":
    IS_WINDOWS = True
else:
    IS_WINDOWS = False

DATA = []

MENU = [
    {
        "name": "뷰 전환",
        "key": "View",
        "desc": "데이터를 표로 보여주거나, 자세히 보여주도록 전환합니다."
    },
    {
        "name": "데이터 추가",
        "key": "Add",
        "desc": "새로운 항목을 추가합니다."
    },
    {
        "name": "데이터 수정",
        "key": "Modify",
        "desc": "기존 항목을 수정하거나 삭제합니다."
    },
    {
        "name": "내보내기",
        "key": "Export",
        "desc": "액셀 파일로 바구니 속 내용을 내보냅니다."
    },
    {
        "name": "바구니 변경",
        "key": "Basket",
        "desc": "현재 바구니를 바꿉니다."
    }
]

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
    if cmd == 'A' or cmd == 'a' or cmd == 'ㅁ' or cmd == 'Add':
        addDataPrompt()
    elif cmd == 'M' or cmd == 'm' or cmd == 'ㅡ' or cmd == 'Modify':
        console.print('수정')
        input()
    elif cmd == 'D' or cmd == 'd' or cmd == 'ㅇ' or cmd == 'Delete':
        console.print('삭제')
        input()
    elif cmd == 'B' or cmd == 'b' or cmd == 'ㅠ' or cmd == 'Basket':
        console.print('변경')
        input()
    elif cmd == 'X' or cmd == 'x' or cmd == 'ㅌ' or cmd == 'Exit':
        quit()
    elif cmd == '':
        pass
    else:
        console.print("!!! 잘못된 명령을 입력했습니다.\n아래와 같은 명령을 실행할 수 있습니다.\n", style="bold")
        printHelp()
        console.print("\n메인 메뉴로 돌아가려면 엔터를 입력하세요.", style="bold")
        input()

def addDataPrompt() -> None:
    clear()
    console.print("\n\n====== 새로운 기사 추가하기 ======", style="bold yellow")
    console.print("> 기사의 주소 혹은 아이디: ", style="bold yellow")
    src = input()

    try:
        item = sillokParser.parseAllAndGetEntity(src)

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

def addData(item: SillokArticleEntity) -> bool:
    DATA.append(item)

def sliceLetters(original: str, letters: int) -> str:
    if len(original) >= letters: # 50자 이상
        return original[0:letters] + "..."
    elif len(original) == 0: # 0자
        return ""
    else: # 0자 초과 50자 미만
        return original

def printAllData() -> int:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("DB ID", overflow="Fold")
    table.add_column("기사 ID", overflow="Fold")
    table.add_column("기사 제목", overflow="Fold")
    table.add_column("기사 위치", overflow="Fold")
    table.add_column("국문 내용", overflow="Fold")
    table.add_column("원문 내용", overflow="Fold")
    table.add_column("메타데이터")
    table.add_column("메모", overflow="Fold")

    if len(DATA) != 0:
        for index, item in enumerate(DATA):
            contentKorSummary = sliceLetters(item.getContentKor(), 50)
            contentHanSummary = sliceLetters(item.getContentHan(), 50)
            metadataSummary = sliceLetters(item.getMetadata(), 50)
            noteSummary = sliceLetters(item.getNote(), 50)
            table.add_row(
                str(index), item.getArticleId(), item.getTitle(), item.getLocation(), contentKorSummary, contentHanSummary, metadataSummary, noteSummary
            )
    else:
        table.add_row("0", "여기에는", " 아직 ", "저장된", "데이터가", "없습니다.")

    console.print(table)
    return len(DATA)

def printHelp() -> None:
    def makeMenuString(name, key, desc):
        return f"[yellow][b]{key[0]}[/b][/yellow]{key[1:]}\n[yellow]{name}[/yellow]\n{desc}"

    menu_renderables = [Panel(makeMenuString(item["name"], item["key"], item["desc"]), expand=True) for item in MENU]
    console.print(Columns(menu_renderables))

def printArticle(article: SillokArticleEntity, isShort=False, includeNote=True) -> None:
    articleInfoStrings = []

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
    else:
        articleInfoStrings.append("[red][b]* 여기에는 어떠한 데이터도 없습니다.[/b][/red]")

    console.print(Panel('  '.join(articleInfoStrings)))
def main() -> None:
    while True:
        clear()
        showMenu()

        count = printAllData()
        if count > 0:
            showMenu()

        enterMenu(input("> "))

    console.print("실록 기사 링크 혹은 기사 아이디 입력:")
    link = input() # ex> https://sillok.history.go.kr/id/kca_11004023_003

    try:
        test = sillokParser.parseAllAndGetEntity(link)
    except Exception as e:
        console.print("!!! 파싱 중 오류가 발생했습니다. 링크나 아이디가 잘못 되었을 수 있습니다.", e, style="bold red")
        test = SillokArticleEntity("", "", "", "", "", "")
    
    printAll(test)

main()