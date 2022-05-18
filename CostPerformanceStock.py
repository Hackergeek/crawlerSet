import akshare as ak
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
import time
# 使用akshare需要安装msgpack orjson yaml tomlkit ujson这些模块
# 股票代码、股票名称、所属行业、当前股价、市盈率、市净率、审计机构、净资产（股东权益）、总市值、股息率、过去十年市净率、过去十年净利润、过去十年现金分红金额。
'''
第一步：将所有股票用“市净率”指标按照由低到高的次序排序，然后删除所有市净率高于1.5倍的公司。
第二步：删除所有“过去十年市净率”从来不曾超过1倍的公司。这样的公司在A股市场截至2017年1月一家也没有，但在其他市场却有不少。
这里要提醒大家的一点是：作为保守的投资者，我们不仅要关注一笔投资的商业逻辑，也要关注其历史规律。
一家公司的估值始终保持在一个非常低的水平，对于我们是不利的，因为我们的很大一部分投资收益都来源于“投资体系第二层级”所介绍的“动态再平衡”。
第三步：删除所有“审计机构”不是“全球四大会计师事务所”（简称“四大”）的公司。由“四大”进行审计的公司，其财务造假的可能性会降低很多。
全球四大会计师事务所分别为：普华永道（PwC）、安永（E&Y）、毕马威（KPMG）和德勤（DTT）。
第四步：删除所有“股息率”为0的公司。有现金分红的公司，其财务造假的可能性会进一步降低。
第五步：删除所有“净资产（股东权益）”低于100亿元的公司。平均而言，规模越大、资产越雄厚的公司，存活能力越强。
第六步：将所有股票用“市净率”指标按照由低到高的次序排序。排名第一得1分，排名第二得2分，排名第一百得100分，以此类推。得分越低越好。
第七步：将所有股票用“市盈率”指标按照由低到高的次序排序。排名第一得1分，排名第二得2分，排名第一百得100分，以此类推。得分越低越好。亏损的公司市盈率为负，统一计为所有公司中得分最高的分值。比如共有300家公司参与排序，其中100家亏损，则亏损公司的分值统一计为200分。[插图]
第八步：将所有股票用“股息率”指标按照由高到低的次序排序。排名第一得1分，排名第二得2分，排名第一百得100分，以此类推。得分越低越好。
第九步：将每一家公司的“市净率”“市盈率”“股息率”三项数据的分值相加，然后按照由低到高的次序排序，等比例买入排名前三十的公司。经过九个步骤的筛选，我们现在得到了一个优质的投资组合。
'''


# 获取所有A股的市盈率、市净率,并保存到output_path
def valuation_analysis(output_path):
    chrome_options = webdriver.ChromeOptions()
    # 无界面浏览模式
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path='/Users/skyward/Downloads/chromedriver', options=chrome_options)
    browser.get("https://data.eastmoney.com/gzfx/list.html")
    result_table = pd.DataFrame()
    for i in range(0, 94):
        table = pd.read_html(browser.page_source)
        result_table = result_table.append(table)
        print(result_table)
        try:
            browser.find_element(by=By.LINK_TEXT, value='下一页').click()
        except:
            result_table.to_csv('./valuation_analysis.csv')
            return None
        time.sleep(2)
    # 最后一页的数据
    table = pd.read_html(browser.page_source)
    result_table = result_table.append(table)
    result_table.to_csv(output_path)


# 数据清洗，减少股票数量，以减少后续的股息率查询次数
def filter(input_path, output_path):
    table = pd.read_csv(input_path)
    # 股票代码用0补足六位
    table['股票代码']  = table['股票代码'].apply(lambda x:str(x).zfill(6))
    # table['股票代码'] = table['股票代码'].apply(lambda x: '{:0>6d}'.format(x))
    # 删除未命名的列
    table = table.drop(columns='Unnamed: 0')
    # 删除序号列
    table = table.drop(columns='序号')
    # 删除相关列
    table = table.drop(columns='相关')
    table = table.drop(table[(table['PE(TTM)'] == '-') | (table['PE(静)'] == '-')].index)
    # 字符串类型转为数字类型
    table['PE(TTM)'] = pd.to_numeric(table['PE(TTM)'], errors='coerce')
    table['PE(静)'] = pd.to_numeric(table['PE(静)'], errors='coerce')
    table['市净率'] = pd.to_numeric(table['市净率'], errors='coerce')
    # 删除PE为负，PB为负，PB大于1.5，股价小于1元
    table = table.drop(table[(table['PE(TTM)'] < 0.0)
                             | (table['PE(静)'] < 0.0)
                             | (table['市净率'] < 0.0)
                             | (table['市净率'] > 1.5)
                             | (table['最新价'] < 1.0)].index)
    # 删除股票简称包含ST、退市的股票
    table = table[~ table['股票简称'].str.contains('ST')]
    # 删除科创板和创业板的股票
    table = table[~ table['股票代码'].str.startswith('30')]
    table = table[~ table['股票代码'].str.startswith('688')]
    # 把股票代码设置为索引
    table.set_index('股票代码', inplace=True)
    # 删除PB为负的行
    table.to_csv(output_path)


# 获取股票的股息率、市值，并保存到output
def dividend_rate(input_path, output_path):
    table = pd.read_csv(input_path)
    table['市值'] = 0
    table['股息率'] = 0
    table['日期'] = '2022-05-18'
    for i in table.index:
        stock_code = str(table.iloc[i]['股票代码']).zfill(6)
        print(stock_code)
        # if stock_code.startswith('60'):
        #     stock_code = 'sh' + stock_code
        # else:
        #     stock_code = 'sz' + stock_code
        # data = ak.stock_hk_eniu_indicator(indicator='市值', symbol=stock_code)
        # print(data)
        data = ak.stock_a_lg_indicator(symbol=stock_code)
        table.loc[i, '市值'] = data.iloc[0]['total_mv']
        table.loc[i, '股息率'] = data.iloc[0]['dv_ratio']
        table.loc[i, '日期'] = data.iloc[0]['trade_date']
    table.to_csv(output_path)


def filter_final(input_path, output_path):
    table = pd.read_csv(input_path)
    # 删除股息率为空，0的结果
    table = table.drop(table[(table['股息率'] <= 0.0)
                             ].index)
    # 刪除任意列為 NaN 值的行
    table = table.dropna()
    # 删除市值小于100亿的结果
    table = table.drop(table[(table['市值'] < 1000000)
                       ].index)
    # 删除未命名的列
    table = table.drop(columns='Unnamed: 0')
    # print(table)
    table.to_csv(output_path)


if __name__ == '__main__':
    # 获取所有A股的市盈率、市净率,并保存到valuation_analysis.csv文件中
    valuation_analysis('valuation_analysis.csv')
    # 数据清洗，减少股票数量，以减少后续的股息率查询次数
    filter('valuation_analysis.csv', 'format.csv')
    # 获取股票的股息率、市值，并保存到dividend_rate.csv文件中
    dividend_rate('format.csv', 'dividend_rate.csv')
    # 最终清洗
    filter_final('dividend_rate.csv', 'final_result.csv')

