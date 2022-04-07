# 百度新闻爬虫（正则实现）
import re
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
}


def baidu_news(keyword):
    url = "https://www.baidu.com/s?rtt=1&tn=news&word=" + keyword
    res = requests.get(url, headers=headers).text
    # print(res)
    pattern_date = '<span class="c-color-gray2 c-font-normal c-gap-right-xsmall".*?>(.*?)</span>'
    pattern_source = '<span class="c-color-gray".*?>(.*?)</span>'
    # pattern_title = 'class="news-title-font_1xS-F".*?>(.*?)</a>'
    pattern_title = '<a href=".*?" target="_blank" class="news-title-font_1xS-F".*?>(.*?)</a>'
    pattern_href = '<a href="(.*?)" target="_blank" class="news-title-font_1xS-F"'
    news_date = re.findall(pattern_date, res)
    news_source = re.findall(pattern_source, res)
    news_title = re.findall(pattern_title, res, re.S)
    news_href = re.findall(pattern_href, res)
    for i in range(len(news_title)):
        news_title[i] = re.sub('<.*?>', '', news_title[i])
        print(str(i + 1) + '.', news_title[i], news_source[i], news_date[i])


def save_baidu_news(keyword):
    url = "https://www.baidu.com/s?rtt=1&tn=news&word=" + keyword
    res = requests.get(url, headers=headers).text
    # print(res)
    pattern_date = '<span class="c-color-gray2 c-font-normal c-gap-right-xsmall".*?>(.*?)</span>'
    pattern_source = '<span class="c-color-gray".*?>(.*?)</span>'
    # pattern_title = 'class="news-title-font_1xS-F".*?>(.*?)</a>'
    pattern_title = '<a href=".*?" target="_blank" class="news-title-font_1xS-F".*?>(.*?)</a>'
    pattern_href = '<a href="(.*?)" target="_blank" class="news-title-font_1xS-F"'
    news_date = re.findall(pattern_date, res)
    news_source = re.findall(pattern_source, res)
    news_title = re.findall(pattern_title, res, re.S)
    news_href = re.findall(pattern_href, res)
    file = open('./baidu_news.txt', 'a', encoding='utf-8')
    file.write(keyword + '数据挖掘完毕！' + '\n\n')
    for i in range(len(news_title)):
        news_title[i] = re.sub('<.*?>', '', news_title[i])
        # print(str(i + 1) + '.', news_title[i], news_source[i], news_date[i], news_href)
        file.write(str(i + 1) + '.' + news_title[i] + '(' + news_date[i] + '-' + news_source[i] + ')\n')
        file.write(news_href[i] + '\n')
    file.write('——————————————————————————————————' + '\n\n')


if __name__ == '__main__':
    keywords = ['华能信托', '阿里巴巴', '百度集团']
    for keyword in keywords:
        # baidu_news(keyword)
        save_baidu_news(keyword)
