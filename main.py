#!/usr/bin/python
# -*- coding: utf-8 -*-

import http.client
from lxml import etree
from urllib import parse
import sys					# system by core
import re					# regular expression by core
import tdb 
import config
import time

def get_magnet_from_plaintext(pt):
    magnet = ""
    title = ""
    tree = etree.fromstring(pt, etree.HTMLParser())
    elements = tree.findall('.//div[@id="writeContents"]/fieldset/ul/li')
    count = 0
    for item in elements:
        if item.text.find('Hash') > 0:
            #magnet = "magnet:?xt=urn:btih:" + item.text.split()[-1]
            magnet = item.text.split()[-1]
        elif count == 0:
            title = item.text[item.text.find(' ')+1:]
            count = count + 1
    return title, magnet

def walker_apa(w_text):
    p = re.compile('[a-z]+|[A-Z]+')
    for i in range(len(w_text)):
        if p.match(w_text[i:]):
            return "/"+w_text[i:]
    return None

def get_urilist_from_plaintext(pt):
    tree = etree.fromstring(pt, etree.HTMLParser())
    elements =tree.findall('.//td/a')
    uri_list = []
    for element in elements:
        result = parse.urlparse(element.attrib['href'])
        uri_list.append(walker_apa(result.path)+result.query)
    return uri_list

def get_plaintext_from_uri(conn, uri):
    try:
        conn.request("GET", uri)
        r1 = conn.getresponse()

        if r1.status != 200:
            return ''
    except Exception as e:
        return ''
    return r1.read()

def main():
    c_ini = config.TwalConfig('./config.ini', debug=False)
    t_url = 'torrentwal.com'
    db_conn = tdb.connect_to_db(
            c_ini.DB.db_address, 
            c_ini.DB.db_port, 
            c_ini.DB.db_user_id, 
            c_ini.DB.db_user_pass, 
            c_ini.DB.db_name)
    if db_conn:
        print("DB connected")
    else:
        print("DB NOTTTTTTT connected")
    g_conn = http.client.HTTPSConnection(t_url)
    if not g_conn:
        print("Please check url %s" % t_url)
        return ''
    else:
        print("Connection Success")
    
    ul_1 = get_urilist_from_plaintext(get_plaintext_from_uri(g_conn, '/'))
    
    m_dic = {}
    tmp_dic = {}
    for item in ul_1:
        if not item.find('torrent') > 0 or item.find('torrent1.htm') > 0:
            continue
        title, magnet = get_magnet_from_plaintext(get_plaintext_from_uri(g_conn, item))
        m_dic[magnet] = {'title':title}

    ctp = tdb.candi_tbl()
    ctp.set_db_connection(db_conn)
    for key in m_dic.keys():
        ret, result =  ctp.torr_candi_search(key)
        if result:
            print("This magnet already exist in table. ({})".format(key))
        else:
            item = tdb.candi_tbl_t(key, m_dic[key]['title'], int(time.time()), 0, '', 'torrentwal.com')
            print("Add to CANDI_TBL ({})".format(item))
            if ctp.torr_candi_create(item) != 1:
                print("CANDI TBL insert ERROR!!")



if __name__ in ("__main__"):
    main()
