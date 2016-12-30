# -*- coding: utf-8 -*-
import httplib, urllib, base64
from argparse import ArgumentParser
import json
import traceback

json_headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '26d51ac57037430ca49b641fd4880df7',
}

binary_headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '26d51ac57037430ca49b641fd4880df7',
}

params = urllib.urlencode({
    # Request parameters
    'language': 'unk',
    'detectOrientation ': 'true',
})

def ocr_with_content(content):
    try:
	conn = httplib.HTTPSConnection('api.projectoxford.ai')
	conn.request("POST", "/vision/v1.0/ocr?%s" % params, content, binary_headers)
	response = conn.getresponse()
        print response
	data = response.read()
	conn.close()
	text = get_ocr_string(data)
        print 'str',text
        return text

    except Exception as e:
	traceback.print_exc()
	print "error",e

def ocr(url):
    print url
    try:
	conn = httplib.HTTPSConnection('api.projectoxford.ai')
	conn.request("POST", "/vision/v1.0/ocr?%s" % params, "{'url':'%s'}" % url, json_headers)
	response = conn.getresponse()
	data = response.read()
	conn.close()
	return data
    except Exception as e:
	traceback.print_exc()

def get_ocr_string(jsonstring):
    print jsonstring
    data = json.loads(jsonstring)
    output = ""
    for r in data['regions']:
        for l in r['lines']:
            for w in l['words']:
                output += w['text'] + " "
            output += "\n"
        output += "\n"
    return output

if __name__ == "__main__":
    arg_parser = ArgumentParser( usage='Usage: python ' + __file__ + ' [--url <url>] [--help]')
    arg_parser.add_argument('-u', '--url', help='url')
    options = arg_parser.parse_args()

    data = ocr(options.url)
    print get_ocr_string(data)
