import re
import requests
from collections import Counter
import jieba
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import numpy as np
from imageio import imread

headers = {
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Upgrade-Insecure-Requests": "1",
    "cookie": "SINAGLOBAL=5939359704574.88.1610760684686; UOR=www.google.com,s.weibo.com,www.google.com.hk; _s_tentry=weibo.com; Apache=3300064153432.1274.1648983857273; ULV=1648983857312:11:1:1:3300064153432.1274.1648983857273:1646005290536; SCF=AkZKy6esK5soTKKQN5aCLbq4y8PfXMoTSY1rZkoxgFOrlKbOtl9WTf7vtqTTW3OggiU7pN42KoDByzZC8pY3U7Y.; SUB=_2AkMVEh1YdcPxrAFQmfocy2zgb45H-jymx3SuAn7uJhMyAxh77n8uqSVutBF-XM4nbN2DO_5RFcJ3rSq9uKb_iHFu; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9W57O._.ysOmylNY6JGyJ1pP5JpV2K2EeoB71h-R1Kx5MP2Vqcv_"
}


def weibo(keyword):
    url = 'https://s.weibo.com/weibo?q=' + keyword
    res = requests.get(url, headers=headers, timeout=10).text
    # print(res)
    pattern_nickname = '<p class="txt" node-type="feed_list_content" nick-name="(.*?)">'
    pattern_content = '<p class="txt" node-type="feed_list_content" nick-name=".*?">(.*?)</p>'
    nickname = re.findall(pattern_nickname, res)
    content = re.findall(pattern_content, res, re.S)
    # 数据清洗和打印输出
    content_all = ''
    for i in range(len(content)):
        content[i] = content[i].strip()
        content[i] = re.sub('<.*?>', '', content[i])
        content_all = content_all + content[i]
        print(str(i + 1) + '.', content[i], nickname[i])
    # 分词
    words = jieba.cut(content_all)
    report_words = []
    for word in words:
        if len(word) >= 2:
            report_words.append(word)
    print(report_words)

    # 获取词频最高的50个词
    result = Counter(report_words).most_common(50)
    print(result)
    # 按特定形状和特定颜色绘制词云图
    # (1)获取词云图蒙版
    background_pic = 'weibo.jpeg'
    images = Image.open(background_pic)
    maskImages = np.array(images)
    # (2)按照形状蒙版绘制词云图
    content = ' '.join(report_words)
    wc = WordCloud(font_path='SimHei.ttf',
                   background_color='white',
                   width=1000,
                   height=600,
                   mask=maskImages).generate(content)
    # (3)修改词云图的颜色
    back_color = imread(background_pic)
    image_colors = ImageColorGenerator(back_color)
    wc.recolor(color_func=image_colors)
    wc.to_file('weibo_result.png')


if __name__ == '__main__':
    weibo("阿里巴巴")
