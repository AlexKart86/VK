import lxml.html as html
import urllib.parse
import urllib.request
import urllib.error
import os
import re
import logging
import logging.config
import sys

folder_prefix = "k:\\feetspace\\"
base_url = "http://feetspace-forum.ru/"

logging.basicConfig( handlers=[logging.FileHandler("log.txt", 'w', 'utf-8')], level=logging.INFO)

# Регулярка для
file_name_patt = re.compile(r'^(.*)(/)(.*)$')
# Регулярки для разных сайтов-хостингов картинок
firepic = re.compile(r'^(http://)(.*)(\?v=)(\d)*?(\.)*?(\d+\-\d+)(\-)(\d+)(_)(.*)$')
jpegshare = re.compile(r'^(http://)(.*?)(/)(.*)(\.html)$')
ifotki = re.compile(r'^(http://)(.*)(/)(.*)(/)(.*)(\.html)$')


# Сперто из Django
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    # value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub('[^\w\s-]', '', value).strip().lower())
    # value = str(re.sub('[-\s]+', '-', value))
    return value

def log(msg):
    print(msg)
    logging.log(logging.INFO, msg)

def parse_firepic(url):
    url_fixed = firepic.sub(r'\1\4\5\2\4/images/\6/\8/\10', url)
    return url_fixed


def parse_vfl(url):
    opener = urllib.request.build_opener()
    opener.addheaders.append(('Cookie', 'vfl_ero=1'))
    page_vfl =  opener.open(url)
    doc_vfl = html.document_fromstring(page_vfl.read())
    doc_vfl.make_links_absolute(base_url='http://vfl.ru')
    photo_url = doc_vfl.cssselect('img[id="img_foto"]')
    if len(photo_url) == 0:
        photo_url = doc_vfl.cssselect('img')
    if len(photo_url) > 0:
        return photo_url[0].get("src")
    else:
        log("Error: "+url)
        return ""

def parse_postimorg(url):
    page_postim = urllib.request.urlopen(url)
    doc_postim = html.document_fromstring(page_postim.read())
    photo_url = doc_postim.cssselect('img')
    if len(photo_url) > 0:
        return photo_url[0].get("src")
    else:
        log("Error: "+url)
        return ""

def parse_imagetwist(url):
    page_imagetwist = urllib.request.urlopen(url)
    doc_imagetwist = html.document_fromstring(page_imagetwist.read())
    photo_url = doc_imagetwist.cssselect('img[class="pic"]')
    if len(photo_url) > 0:
        return photo_url[0].get("src")
    else:
        log("Error: "+url)
        return ""

def parse_ifotohost(url):
    page_ifotohost = urllib.request.urlopen(url)
    doc_ifotohost = html.document_fromstring(page_ifotohost.read())
    #doc_ifotohost.make_links_absolute(base_url='http://ifotohost.com/')
    photo_url = doc_ifotohost.cssselect('a[class="img"]')
    if len(photo_url) > 0:
        return 'http://ifotohost.com/'+photo_url[0].get("href")
    else:
        log("Error: "+url)
        return ""

def parse_imagevenue(url):
    page_imagevenue = urllib.request.urlopen(url)
    doc_imagevenuet = html.document_fromstring(page_imagevenue.read())
    parsed = urllib.parse.urlparse(url)
    #doc_imagevenuet.make_links_absolute(base_url=parsed.netloc)
    photo_url = doc_imagevenuet.cssselect('img[id="thepic"]')
    if len(photo_url) > 0:
        return "http://" +  parsed.netloc + "/" + photo_url[0].get("src")
    else:
        log("Error: "+url)
        return ""

def parse_jpegshare(url):
    return jpegshare.sub(r'\1\2\3images/\4', url)

def parse_ifotki(url):
    return ifotki.sub(r'\1f\4.\2/org/\6', url)


def parse_radikal(url):
    page_radikal = urllib.request.urlopen(url)
    doc_radikal = html.document_fromstring(page_radikal.read())
    photo_url = doc_radikal.cssselect('img[itemprop="contentUrl"]')
    if len(photo_url) > 0:
        return photo_url[0].get("src")
    else:
        log("Error: "+url)
        return ""

def parse_external_image(link, path):
    link_url = link[2]
    try:
        download_url = ""
        parsed = urllib.parse.urlparse(link_url)
        if parsed.netloc == 'firepic.org':
            download_url = parse_firepic(link_url)
        elif parsed.netloc == '4allforum.com':
            params = urllib.parse.parse_qs(parsed.query)
            if ('to' in params) and (len(params['to']) > 0) and \
                    ('firepic.org' in (params['to'][0])):
                download_url = parse_firepic(params['to'][0])
        elif parsed.netloc == 'vfl.ru':
            download_url = parse_vfl(link_url)
        elif parsed.netloc == 'jpegshare.net':
            download_url = parse_jpegshare(link_url)
        elif parsed.netloc == 'postimg.org':
            download_url = parse_postimorg(link_url)
        elif parsed.netloc == 'imagetwist.com':
            download_url = parse_imagetwist(link_url)
        elif "imagevenue.com" in parsed.netloc:
            download_url = parse_imagevenue(link_url)
        elif parsed.netloc == 'radikal.ru':
            download_url = parse_radikal(link_url)
        elif parsed.netloc == 'ifotki.info':
            download_url = parse_ifotki(link_url)
        elif parsed.netloc == 'i-fotki.info':
            download_url = parse_ifotki(link_url.replace('i-fotki', 'ifotki'))
        # Домены с которых ничего не распарсишь
        elif parsed.netloc in ['www.youtube.com', 'm.youtube.com', 'feetfetish.ucoz.com', 'feetspace-forum.ru',
                               'www.feetspace-forum.ru', 'picdump.ru', 'smayliki.ru']:
            pass
        #Ссылка непосредственно на картинку
        elif link_url.endswith(".jpg") or link_url.endswith(".png"):
            download_url = link_url
        else:
            log("Unknown link: " + link_url)
        if (download_url != ""):
            file_name = path + '\\' + file_name_patt.sub(r'\3', download_url)
            urllib.request.urlretrieve(download_url, file_name)
            # print(file_name + " downloaded")
    except urllib.error.HTTPError as err:
        log("Error! {}; {}".format(download_url, err))
    except:
        log("Unexpected error: {} \n download_url {}; link_url: {}".format(sys.exc_info()[0], download_url, link_url))



# Парсит одну страницу в теме
def parse_topic_page(doc, path):
    posts = doc.cssselect('table[id^="post"]')
    for post in posts:
        post_content = post.cssselect('div[id^="post_message"]')
        if len(post_content) > 0:
            # links = post_content[0].cssselect('a[href^="http"]')
            # for link in links:
            for link in html.iterlinks(post_content[0]):
                if ("http" in link[2]) and (link[1] == "href"):
                    parse_external_image(link, path)


# Парсит одну тему
def parse_topic(page_link, v_base_path):
    v_topic_name = page_link[0].text_content()
    log(v_topic_name + "---" + page_link[2])
    logging.log(logging.INFO, v_topic_name + "---" + page_link[2])
    v_full_path = v_base_path + "\\" + slugify(v_topic_name)
    v_url = page_link[2]
    # Создаем папку
    #if not os.path.exists(v_full_path):
    #    os.makedirs(v_full_path)
    #TODO Временно
    if True:
        # Ищем все посты
        page = urllib.request.urlopen(v_url)
        doc = html.document_fromstring(page.read())
        menu_controls = doc.cssselect('td[class="vbmenu_control"]')
        #TODO: Временно!
        #parse_topic_page(doc, v_full_path)
        for menu_control in menu_controls:
            v_page_text = menu_control.text_content()
            if re.match(r'Страница \d из \d', v_page_text):
                page_count = int(re.sub(r'(Страница \d из )(\d)', r'\2', v_page_text))
                for i in range(page_count-1):
                    #TODO: Временно!
                    if (i+2>=32):
                        url = "{}&page={}".format(page_link[2],i+2)
                        log(v_topic_name + "---" + url)
                        page = urllib.request.urlopen(url)
                        doc = html.document_fromstring(page.read())
                        parse_topic_page(doc, v_full_path)
                break
    else:
        log("{} already exists. Skipped".format(v_full_path))

def run_parse():
    page = urllib.request.urlopen(base_url)
    doc = html.document_fromstring(page.read())
    doc.make_links_absolute(base_url=base_url)
    for link in html.iterlinks(doc):
        if ("forumdisplay.php" in link[2]) and ("f=43" in link[2]):
            v_chapter_name = link[0].text_content()
            v_path = folder_prefix + v_chapter_name
            v_link = link[2]
            # Создаем папку
            if not os.path.exists(v_path):
                os.makedirs(v_path)
            page = urllib.request.urlopen(v_link)
            doc = html.document_fromstring(page.read())
            doc.make_links_absolute(base_url=base_url)
            for link_topics in html.iterlinks(doc):
                parsed_url = urllib.parse.urlparse(link_topics[2])
                # print(parsed_url)
                parsed_q = urllib.parse.parse_qs(parsed_url.query)
                # print(parsed_q)
                # Отыскиваем ссылку на первую страницу
                if (parsed_url.path == "/showthread.php") and ("t" in parsed_q) and not ("page" in parsed_q) and \
                        (link_topics[0].text_content() != "1")\
                        and (parsed_q["t"][0] == "1537" ):
                    parse_topic(link_topics, v_path)
                #print(parsed_q)