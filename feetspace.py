import lxml.html as html
import urllib.parse
import urllib.request
import urllib.error
import os
import re


folder_prefix = "k:\\feetspace\\"
base_url = "http://feetspace-forum.ru/"

#Регулярка для
file_name_patt = re.compile(r'^(.*)(/)(.*)$')
#Регулярки для разных сайтов-хостингов картинок
firepic = re.compile(r'^(http://)(.*)(\?v=)(\d)*?(\.)*?(\d+\-\d+)(\-)(\d+)(_)(.*)$')



#Сперто из Django
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub('[^\w\s-]', '', value).strip().lower())
    #value = str(re.sub('[-\s]+', '-', value))
    return value


def parse_firepic(url):
    url_fixed = firepic.sub(r'\1\4\5\2\4/images/\6/\8/\10', url)
    return url_fixed

def parse_vfl(url):
    page_vfl = urllib.request.urlopen(url)
    doc_vfl = html.document_fromstring(page_vfl.read())
    photo_url = doc_vfl.cssselect('img[id="img_foto"]')
    if len(photo_url)>0:
        return photo_url[0].get("src")
    else:
        print("Error: url")

def parse_external_image(link, path):
    link_url = link[2]
    parsed = urllib.parse.urlparse(link_url)
    download_url = ""
    if parsed.netloc == 'firepic.org':
        #download_url = parse_firepic(link_url)
        pass
    elif parsed.netloc == '4allforum.com':
        params = urllib.parse.parse_qs(parsed.query)
        if ('to' in params) and (len(params['to'])>0) and \
                ('firepic.org' in (params['to'][0])) :
            #download_url = parse_firepic(params['to'][0])
            pass
    elif parsed.netloc == 'vfl.ru':
        download_url =  parse_vfl(link_url)
    #Домены с которых ничего не распарсишь
    elif parsed.netloc in ['www.youtube.com']:
        pass
    else:
        print(link_url)
    if (download_url != ""):
        print(download_url)
        try:
            file_name = path + '\\' + file_name_patt.sub('\3')
            urllib.request.urlretrieve(download_url, file_name)
            print(file_name + " downloaded")
        except urllib.error.HTTPError as err:
            print("Error! {}; {}".format(download_url, err))


def parse_page(page_link):
     v_topic_name =  page_link[0].text_content()
     print(v_topic_name+"---"+page_link[2])
     v_full_path = v_path+"\\"+slugify(v_topic_name)
     v_url = page_link[2]
     #Создаем папку
     if not os.path.exists(v_full_path):
        os.makedirs(v_full_path)
     #Ищем все посты
     page = urllib.request.urlopen(v_url)
     doc = html.document_fromstring(page.read())
     posts = doc.cssselect('table[id^="post"]')
     for post in posts:
         post_content = post.cssselect('div[id^="post_message"]')
         if len(post_content) > 0:
             #links = post_content[0].cssselect('a[href^="http"]')
             #for link in links:
             for link in html.iterlinks(post_content[0]):
                 if ("http" in link[2]) and (link[1] == "href"):
                     parse_external_image(link, v_full_path)


page = urllib.request.urlopen(base_url)
doc = html.document_fromstring(page.read())
doc.make_links_absolute(base_url=base_url)
for link in html.iterlinks(doc):
    if ("forumdisplay.php" in  link[2]) and ("f=43" in link[2]) :
      v_chapter_name = link[0].text_content()
      v_path = folder_prefix+v_chapter_name
      v_link =  link[2]
      #Создаем папку
      if not os.path.exists(v_path):
        os.makedirs(v_path)
      page = urllib.request.urlopen(v_link)
      doc = html.document_fromstring(page.read())
      doc.make_links_absolute(base_url=base_url)
      for link_topics in html.iterlinks(doc):
          parsed_url = urllib.parse.urlparse(link_topics[2])
          #print(parsed_url)
          parsed_q = urllib.parse.parse_qs(parsed_url.query)
          #print(parsed_q)
          #Отыскиваем ссылку на первую страницу
          if (parsed_url.path == "/showthread.php") and  ("t" in parsed_q) and not ("page" in  parsed_q) and \
                  (link_topics[0].text_content() != "1"):
              parse_page(link_topics)

          #if ("showthread.php" in link_topics[2]) and ("t=" in link_topics[2]):
          #    print(urllib.parse.urlparse(link_topics[2]))


