#!/usr/bin/python
# -*- coding: utf-8 -*-

import http.client
from lxml import etree
from urllib import parse
import sys					# system by core
import re					# regular expression by core

def get_magnet_from_plaintext(pt):
	tree = etree.fromstring(pt, etree.HTMLParser())
	elements = tree.findall('.//div[@id="writeContents"]/fieldset/ul/li')
	for item in elements:
		if item.text.find('Hash') > 0:
			print("magnet:?xt=urn:btih:" + item.text.split()[-1])
		else:
			print(item.text)

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
	t_url = 'torrentwal.com'
	g_conn = http.client.HTTPSConnection(t_url)
	if not g_conn:
		print("Please check url %s" % t_url)
		return ''
	else:
		print("Connection Success")
	
	ul_1 = get_urilist_from_plaintext(get_plaintext_from_uri(g_conn, '/'))

	for item in ul_1:
		if not item.find('torrent') > 0 or item.find('torrent1.htm') > 0:
			continue
		get_magnet_from_plaintext(get_plaintext_from_uri(g_conn, item))
		print('')

if __name__ in ("__main__"):
	main()
