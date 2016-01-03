import lxml.html as html
import urllib.parse
import urllib.request
import urllib.error
import csv

log_file_name = "log.txt"
result_file = "res.csv"

log = open(log_file_name, 'a')


def parse_one_page(url):
    pg = urllib.request.urlopen(url)
    page = html.document_fromstring(pg.read())
    title = page.find_class("title-description")

    if len(title) > 0:
      print(title[0].text_content())
    #tbls = page.find_class("tablesaw tablesaw-stack")
    tbls = page.cssselect("table")
    #print(len(tbls))
    for tbl in tbls:
        if not(tbl.attrib.get("id") is None) and  tbl.attrib["id"].isdigit():
            for row in tbl.cssselect("tr"):
                columns = row.cssselect("td")
                if len(columns) >= 6:
                    print(columns[1].get_text())





def process_education_form(form_name):
    try:
        t =  doc.get_element_by_id(form_name )
        for i in t.iterlinks():
            k = urllib.parse.urlsplit(i[2])
            process_url = 'http://'+k[1]+k[2]
            print(process_url)
            parse_one_page(process_url)
            log.flush()
            return True
    except KeyError:
        log.write("Error: {} form {} doesn't exists".format(full_url, form_name))
        log.flush()
        return False





#Проходимся по всем страничкам вузов
for i in range(5, 6, 1):
    base_url = "http://vstup.info/2015/"
    full_url = (base_url + "i2015i{}.html").format(i)
    try:
        page = urllib.request.urlopen(full_url)
        doc = html.document_fromstring(page.read())
        doc.make_links_absolute(base_url=base_url)
        print(full_url)
        if process_education_form("denna1"):
           log.write("Success: {} \n".format(full_url))


    except urllib.error.HTTPError as err:
        log.write("Error: " +full_url + err.msg + "\n")
        log.flush()
log.close()

"""
    t =  doc.get_element_by_id("denna1")
    for i in t.iterlinks():
        k = urllib.parse.urlsplit(i[2])
        process_url = 'http://'+k[1]+k[2]
        print(process_url)
"""