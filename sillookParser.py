import re
import requests
from bs4 import BeautifulSoup as bs
from sillookArticleEntity import SillookArticleEntity

BASE_URL = "https://sillok.history.go.kr/id/"

def toPureText(rawHtml) -> str:
    pureText = re.sub('<.+?>', '', str(rawHtml), 0).strip()
    pureText = pureText.replace("[", "").replace("]", "").replace("\n", "").replace("\t", "")
    return pureText

def map_collectOnlyParagraph(el) -> str:
    if (el.name == "p") and ("paragraph" in el['class']) :
        return toPureText(el) + "\n"
    else:
        return ""

def map_collectOnlyMetadata(el) -> str:
    if el.name == "ul":
        return toPureText(el) + "\n"
    else:
        return ""

def parseContent(rawContent) -> str:
    return ''.join(list(map(map_collectOnlyParagraph, rawContent)))

def parseMetadataFromContent(rawContent) -> str:
    return ''.join(list(map(map_collectOnlyMetadata, rawContent)))

def parseAllAndGetEntity(source) -> SillookArticleEntity:
    link = None
    articleId = None
    if source.split("/")[0] == "https:":
        # The "source" is a https link.
        link = source
        articleId = source.split("/")[-1]
    else:
        # The "source" is an id of the article.
        link = BASE_URL + source
        articleId = source


    try:
        rawPage = requests.get(link, verify=False)
        soup = bs(rawPage.text, "html.parser")

        title = soup.select('.ins_view_tit')
        title_parsed = toPureText(title)

        location = soup.select('span.tit_loc')
        location_parsed = toPureText(location).replace("기사", "기사 ")

        content_raw = soup.select('div.ins_view_pd')
        content_kor = content_raw[0]
        content_han = content_raw[1]
        content_kor_parsed = parseContent(content_kor)
        content_han_parsed = parseContent(content_han)
        metadata_parsed = parseMetadataFromContent(content_kor)

        return SillookArticleEntity(None, articleId, title_parsed, location_parsed, content_kor_parsed, content_han_parsed, metadata_parsed, "")

    except Exception as e:
        raise Exception("파싱 중 에러가 발생했습니다.", e)