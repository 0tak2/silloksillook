class SillookArticleEntity:
    def __init__(self, id, articleId: str, title: str, location: str, content_kor: str, content_han: str, metadata: str, note: str):
        self.id = id
        self.articleId = articleId
        self.title = title
        self.location = location
        self.content_kor = content_kor
        self.content_han = content_han
        self.metadata = metadata
        self.note = note

    def set(self, articleId = None, title = None, location = None, content_kor = None, content_han = None, metadata = None, note = None):
        if articleId != None:
            self.articleId = articleId

        if title != None:
            self.title = title
        
        if location != None:
            self.location = location

        if content_kor != None:
            self.content_kor = content_kor

        if content_han != None:
            self.content_han = content_han
        
        if metadata != None:
            self.metadata = metadata

        if note != None:
            self.note = note

    def isEmpty(self) -> bool:
        if self.articleId != "":
            return False
        elif self.title != "":
            return False
        elif self.location != "":
            return False
        elif self.content_kor != "":
            return False
        elif self.content_han != "":
            return False
        elif self.metadata != "":
            return False
        else:
            return True

    def getId(self) -> str:
        return self.id

    def getArticleId(self) -> str:
        return self.articleId

    def getTitle(self) -> str:
        return self.title

    def getLocation(self) -> str:
        return self.location

    def getContentKor(self) -> str:
        return self.content_kor

    def getContentHan(self) -> str:
        return self.content_han

    def getMetadata(self) -> str:
        return self.metadata

    def getNote(self) -> str:
        return self.note

    def getAll(self):
        return {
            "href": self.href,
            "title": self.title,
            "location": self.location,
            "content_kor": self.content_kor,
            "content_han": self.content_han,
            "metadata": self.metadata,
        }
