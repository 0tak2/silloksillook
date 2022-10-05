import platform
from sillookArticleEntity import SillookArticleEntity
import sillookDatabase as db

class SillookGlobal:
    def __init__(self):
        if platform.system() == "Windows":
            self.IS_WINDOWS = True
        else:
            self.IS_WINDOWS = False
        
        self.DB_FILE = "db/default.db"

        self.DB_CONN = None
        self.DB_CURSOR = None

        self.LOADED_DATA = []

        self.MENU = [
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

        self.VIEW_MODE = 0 # 0 = table, 1 = detail

        self.CURRENT_ID = 1
    
    def getData(self):
        return self.LOADED_DATA
    
    def getSizeOfData(self):
        return len(self.LOADED_DATA)
    
    def setData(self, newDataList: list):
        self.LOADED_DATA = newDataList
        return self.LOADED_DATA # 데이터 치환 및 리턴

    def addData(self, element: SillookArticleEntity):
        newList = [element]
        self.LOADED_DATA = self.LOADED_DATA + newList
    
    def getIsWindows(self):
        return self.IS_WINDOWS
    
    def getMenuItems(self):
        return self.MENU

    def getDbFile(self):
        return self.DB_FILE

    def setDbFile(self, dbFileLoaction):
        self.DB_FILE = dbFileLoaction

    def setDB(self, conn, cursor):
        self.DB_CONN = conn
        self.DB_CURSOR = cursor
    
    def getDB(self):
        return (self.DB_CONN, self.DB_CURSOR)
    
    def setConnection(self):
        conn, cursor = db.makeConnction(self.getDbFile())
        self.setDB(conn, cursor)
    
    def getViewMode(self):
        return self.VIEW_MODE
    
    def setViewMode(self, mode): # 0 = table, 1 = detail
        self.VIEW_MODE = mode

    def getCurrentId(self):
        return self.CURRENT_ID
    
    def setCurrentId(self, id):
        if id > self.getSizeOfData() + 1:
            self.CURRENT_ID = 1
        elif id < 1:
            self.CURRENT_ID = self.getSizeOfData() + 1
        else:
            self.CURRENT_ID = id