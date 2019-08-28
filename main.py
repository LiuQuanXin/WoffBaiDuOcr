# !/usr/bin/python
# coding: utf-8
# time: 2019/8/28

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import os
import random
import time
import json
import requests

from aip import AipOcr
from PIL import Image
from fontTools.pens.reportLabPen import ReportLabPen
from fontTools.ttLib import TTFont
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Group, Drawing, scale, Path

PATH = 'woff.woff'

URL = 'http://s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/bbe7f93e.woff'


def get_woff():
    resp = requests.get(URL)
    with open(PATH, 'wb+') as f:
        f.write(resp.content)


def img_save():
    img_path = PATH.rsplit('.', 1)[0]
    font = TTFont(PATH)  # it would work just as well with fontTools.t1Lib.T1Font
    glyf = font['glyf']
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    for glyphName in glyf.keys():
        gs = font.getGlyphSet()
        pen = ReportLabPen(gs, Path(fillColor=colors.black, strokeWidth=1))
        g = gs[glyphName]
        g.draw(pen)
        # 调整图片大小
        w, h = 800, 800
        g = Group(pen.path)
        g.translate(10, 200)
        g.scale(0.3, 0.3)

        d = Drawing(w, h)
        d.add(g)

        image = renderPM.drawToPIL(d)
        little_image = image.resize((180, 180))
        fromImage = Image.new('RGBA', (360, 360), color=(255, 255, 255))
        fromImage.paste(little_image, (0, 0))
        # fromImage.show()
        glyphName = glyphName.replace('uni', '&#x')
        imageFile = img_path + "/%s.png" % glyphName
        fromImage.save(imageFile)
        break


def client():
    '''百度api key'''
    l = []
    l.append(AipOcr('11567868', 'BkQY9zcNhAESQQEGb4eh1rhp', 'iLkBtC76EXTb2tBjweCaNgTmxhVqv2NV'))
    return random.choice(l)


def ocr(img, path):
    """ 带参数调用通用文字识别, 图片参数为本地图片 """
    image = get_file_content(path + '/' + img)
    for i in range(3):
        time.sleep(0.2)
        resp = client().basicAccurate(image)
        # '''高精度版本'''
        # resp = client().basicAccurate(image)
        if resp.get('words_result'):
            value = resp['words_result'][0]['words']
            return img.split('.')[0], value
        elif resp.get('error_code'):
            print resp
            continue
        else:
            print resp
            continue


def get_file_content(imgPath):
    with open(imgPath, 'rb') as fp:
        return fp.read()


def main():
    path = PATH.rsplit('.', 1)[0]
    l = os.listdir(path)
    tmp = {}
    for pt in l:
        # print pt
        if pt in ['x.png', 'glyph00000.png']:
            result = (pt.split('.')[0], ' ')
        elif pt == '&#xec2d.png':
            result = ['&#xec2d', '0']
        elif pt == '&#xf5de.png':
            result = ['&#xf5de', '丽']
        elif pt == '&#xec2d.png':
            result = ['&#xf009', '一']
        else:
            result = ocr(pt, path)
            if not result:
                result = ocr(pt, path)
        try:
            tmp[result[0]] = result[1]
        except:
            print path + '/' + pt + ' 识别失败'
            tmp[pt.split('.')[0]] = '失败'
    return tmp


if __name__ == '__main__':
    PATH = 'woff.woff'
    # get_woff()
    img_save()
    print json.dumps(main(), ensure_ascii=False)
