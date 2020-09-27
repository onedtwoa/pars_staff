import requests
from bs4 import BeautifulSoup
import xlsxwriter

URL = 'https://www.italska8.cz/byty'
NAMES = ['jednotka', 'dispozice', 'podlaží', 'typ', 'plocha', 'stav', 'cena']


def get_html(url):
    DOC = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'accept': '*/*'}
    r = requests.get(url, headers=DOC, timeout=15)
    return r


# для получения дополнительной информации 'other'
def get_second_content(html):
    global NAMES
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.find('strong')
    res = []
    for i in list(filter(bool, item.text.replace(' ', '').split('\n'))):
        summ = 0
        for j in NAMES:
            summ += i.lower().count(j)
        if summ == 0:
            res.append(i.replace('\xa0', ' '))
    return res


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('tr', class_='clickable-row')
    obj = []
    objs = []
    for i in items:
        for j in i.find_all('td'):
            obj.append(j.get_text())

        a = get_second_content(get_html(i.get('data-href')).text)
        objs.append(obj)
        obj.append(a)
        obj = []

    return objs


def parse(url):
    html = get_html(url)
    return get_content(html.text)


def res_excel(arr):
    fields = ['id', 'floor_plan', 'floor', 'area', 'status', 'price', 'type', 'other']
    workbook = xlsxwriter.Workbook('pars.xlsx')
    worksheet = workbook.add_worksheet()

    for i in range(len(fields)):
        worksheet.write(0, i, fields[i])

    # 'id', 'floor_plan', 'floor'
    for i in range(len(arr)):
        for j in range(0, 3):
            worksheet.write(i + 1, j, arr[i][j])

    # 'area'
    for i in range(len(arr)):
        if arr[i][4].split(' ')[0].replace(' ', '') != '':
            worksheet.write(i + 1, 3, float(arr[i][4].split(' ')[0].replace(',', '.')))
        else:
            worksheet.write(i + 1, 3, 0)

    # 'status'
    for i in range(len(arr)):
        if arr[i][5] == 'rezervováno':
            worksheet.write(i + 1, 4, 'reserved')
        elif arr[i][5] == 'volný':
            worksheet.write(i + 1, 4, 'available')
        else:
            worksheet.write(i + 1, 4, 'sold')

    # 'price'
    for i in range(len(arr)):
        if arr[i][6].replace(' ', '') != '':
            worksheet.write(i + 1, 5, float(arr[i][6].replace(' ', '')))
        else:
            worksheet.write(i + 1, 5, 0)

    # 'type'
    for i in range(len(arr)):
        worksheet.write(i + 1, 6, arr[i][3])

    # 'other'
    for i in range(len(arr)):
        if arr[i][7] != []:
            worksheet.write(i + 1, 7, arr[i][7][0])
        else:
            worksheet.write(i + 1, 7, '')

    workbook.close()


arr = parse(URL)
res_excel(arr)
