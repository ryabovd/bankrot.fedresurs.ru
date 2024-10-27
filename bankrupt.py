import requests
from datetime import date
from datetime import datetime
import csv
import ctypes
import pprint
import json
from urllib.parse import quote
import pandas as pd
import time
import random


kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

'''
Colors!
Write a module and import in future.
'''
red_text = '\033[31m'
green_text = '\033[32m'
yellow_text = '\033[33m'
blue_text = '\033[34m'
white_text_on_blue = '\033[37m\033[44m'
marked_text = '\033[43m'
end_text = '\033[0m'
numbers = white_text_on_blue



def build_url(prsnbankruptsId, regionId='95'):
    '''Build str url for parse'''
    start_url = "https://bankrot.fedresurs.ru/backend/prsnbankrupts?searchString="
    middle_url = "&isActiveLegalCase=null&regionId=" # Это для всех дел независимо от статуса
#    middle_url = "&isActiveLegalCase=true&regionId=" # Это для активных дел
#    middle_url = "&isActiveLegalCase=false&regionId=" # Это для завершенных дел

    end_url = "&limit=15&offset=0"
    encoding_prsnbankruptsId = quote(prsnbankruptsId)
    return start_url + encoding_prsnbankruptsId + middle_url + regionId + end_url


def get_prsnbankruptsId():
    '''Get Id return Id (str)'''
    prsnbankruptsId = input('Введите ФИО или ИНН или СНИЛС ').lower().strip()
    return prsnbankruptsId


def read_xls(filename='debtors.xls'):
    '''Не читаем первую строку, т.к. в ней нет данных'''
    table = pd.read_excel(filename, skiprows=1)
    return(table)


def get_column(table):
    column = table['Unnamed: 2']
    return column


def get_debtors():
#    print()
    table = read_xls()
    debtors = list(get_column(table))
    debtors = debtors[:-1]
#    print()
#    print(debtors)
    return debtors


def check_debtors(debtors):
    for debtor in debtors:
        id = debtor.strip().lower()
#        print('id', id)
        print(f'Проверка {debtors.index(debtor) + 1} из {len(debtors)} - {debtor.strip()} - {(debtors.index(debtor) + 1) * 100 // len(debtors)} % завершено')
        check_person(id)
        asleep = random.randint(2000, 6000) / 1000
#        print('sleep', asleep)
        time.sleep(asleep)
#        pass


def check_person(id):
    get_response(id)
    pass


data = {'name': [],
#        'debt': [],
        'procedure': [],
        'case': [],
        'link_fedresurs': [],
#        'link_kad': [],
        'inn': [],
        'snils': [],
        'address': []}


def get_response(id):
    url = build_url(id)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Cookie": "_ym_uid=1700107103592041594; _ym_d=1716266926; qrator_msid=1723728014.226.j2YTgLfBJOAmPXHf-0tqah7dmflbeihg9s4gcea2gn707dkbq; _ym_isad=2; _ym_visorc=w",
        "Referer": "https://bankrot.fedresurs.ru/bankrupts?searchString=^%^D0^%^BF^%^D0^%^B8^%^D1^%^81^%^D1^%^82^%^D1^%^83^%^D0^%^BD^%^D0^%^BE^%^D0^%^B2^%^D0^%^B8^%^D1^%^87^%^20^%^D1^%^81^%^D0^%^B5^%^D1^%^80^%^D0^%^B3^%^D0^%^B5^%^D0^%^B9&regionId=95&isActiveLegalCase=true&offset=0&limit=15^",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "sec-ch-ua": 'Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
        }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    string = response.text
    res_dict = json.loads(string)
#    print('res_dict', res_dict) # Печатаем полученный словарь
    if res_dict['total'] > 0:
        print(red_text + str(id) + end_text)
        for dict in res_dict['pageData']:
            if id == dict['fio'].lower():
                print('fio', dict['fio'])
                data['name'].append(dict['fio'])
                if 'snils' in dict:
                    print('snils', dict['snils'])
                    data['snils'].append(dict['snils'])
                else:
                    print('snils', '0')
                    data['snils'].append('0')
                print('inn', dict['inn'])
                data['inn'].append(dict['inn'])
                data['case'].append(dict['lastLegalCase']['number'])
                data['procedure'].append(dict['lastLegalCase']['status']['description'])
                data['address'].append(dict['address'])
                data['link_fedresurs'].append('https://fedresurs.ru/persons/' + dict['guid'] + ' ')
    else:
        pass


def start_time():
    start_time = datetime.now()
    return start_time


def process_time(start_time):
#    start_time = time.time()
    end_time = datetime.now()  # время окончания выполнения
    execution_time = end_time - start_time  # вычисляем время выполнения
    print(green_text + "Время выполнения программы: " + str(execution_time) + " секунд" + end_text + "\n")


def date_today():
    '''Func that returned today date'''
    today = date.today()
    return today


def main():
    start = start_time()
    debtors = get_debtors()
    check_debtors(debtors)
#    print(data)
    today_date = str(date_today())
    filename = 'bankrots_' + today_date + '.xlsx'
    if len(data['name']) > 0:
        print(red_text + 'Найдено ' + str(len(data['name'])) + ' записей' + end_text + "\n")
    else:
        print(green_text + 'Найдено ' + str(len(data['name'])) + ' записей' + end_text + "\n")
#    print(data)
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(red_text + "Файл данных ЗАПИСАН" + end_text + "\n")
    process_time(start)


if __name__ == "__main__":
    main()


def make_full_report(data): 
    '''Get data (? list) and return report (? list)'''
    
    
def make_main_report(data):
    '''get data (? list) and return (? list)'''
    pass

def read_file(file_name):
    pass

def write_file(file_name):
    pass


str_res_pist = '{"pageData":[{"snils":"10749272160","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"КРУГЛОВ ГЕОРГИЙ КОНСТАНТИНОВИЧ","address":"Республика Хакасия, Боградский район, с. Первомайское, ул. Кирова, д. 5, кв. 3","lastLegalCase":{"number":"А74-8815/2023","status":{"code":"CitizenAssetsDisposal","description":"Реализация имущества гражданина"}},"guid":"0677d445-f2e1-47a8-9230-302973cf3368","fio":"Пистунович Сергей Анатольевич","inn":"190111676789"}],"total":1}'
str_resp = '{"pageData":[{"snils":"10749272160","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"КРУГЛОВ ГЕОРГИЙ КОНСТАНТИНОВИЧ","address":"Республика Хакасия, Боградский район, с. Первомайское, ул. Кирова, д. 5, кв. 3","lastLegalCase":{"number":"А74-8815/2023","status":{"code":"CitizenAssetsDisposal","description":"Реализация имущества гражданина"}},"guid":"0677d445-f2e1-47a8-9230-302973cf3368","fio":"Пистунович Сергей Анатольевич","inn":"190111676789"}],"total":1}'
str_resp_7 = '{"pageData":[{"snils":"14397220165","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"Малюка Анна Алексеевна","address":"655602, Республика Хакасия, г. Саяногорск, мкр. Центральный, д. 34, кв. 11","lastLegalCase":{"number":"А74-3211/2024","status":{"code":"CitizenDebtRestructuring","description":"Реструктуризация долгов гражданина"}},"guid":"2a264a9a-1db2-11ef-a609-00620be2fa80","fio":"Горошко Светлана Андреевна","inn":"242000604230"},{"snils":"06414866972","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"Михайлова Наталья Александровна","address":"РХ, г. Саяногорск, рп. Майна, ул. Рабовича, д. 14Б","lastLegalCase":{"number":"А74-2672/2024","status":{"code":"CitizenAssetsDisposal","description":"Реализация имущества гражданина"}},"guid":"5d6a6e58-38fc-11ef-b2c8-00620be2fa80","fio":"Иванова Евгения Алексеевна","inn":"190200302922"},{"snils":"17416655279","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"Пискунова Ольга Александровна","address":"Республика Хакасия, г. Абакан, ул. Семнадцатая, д. 7","lastLegalCase":{"number":"А74-5511/2024","status":{"code":"CitizenAssetsDisposal","description":"Реализация имущества гражданина"}},"guid":"e8f9516a-545d-11ef-b1c1-00620be2fa80","fio":"Иванова Ксения Валерьевна","inn":"190119272940"},{"snils":"12497895514","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"Беспалова Светлана Николаевна","address":"Республика Хакасия, Усть-Абаканский район, аал Чарков, ул. Степная, д. 8, кв. 1","lastLegalCase":{"number":"А74-1252/2024","status":{"code":"CitizenDebtRestructuring","description":"Реструктуризация долгов гражданина"}},"guid":"d56d6548-01ea-11ef-986b-00620be2fa80","fio":"Иванова Мария Андреевна","inn":"245506290181"},{"snils":"17298472416","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"Часовской Николай Сергеевич","address":"655111, Республика Хакасия, г. Сорск, ул. Геологов, д.1, кв. 1","lastLegalCase":{"number":"А74-3690/2024","status":{"code":"CitizenAssetsDisposal","description":"Реализация имущества гражданина"}},"guid":"6e99662c-353f-11ef-8582-00620be2fa80","fio":"Иванова Надежда Александровна","inn":"190309950030"},{"snils":"13771787700","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"Новикова Вера Александровна","address":"Хакасия Респ, Черногорск г, Кирова 1-я линия ул, д. 15А","lastLegalCase":{"number":"А74-736/2024","status":{"code":"CitizenDebtRestructuring","description":"Реструктуризация долгов гражданина"}},"guid":"62fa1b06-e5e7-11ee-b5d7-00620be2fa80","fio":"Марьясова Ксения Александровна","inn":"170103764284"},{"snils":"10619085237","category":"Физическое лицо","region":"Республика Хакасия","arbitrManagerFio":"Тюриков Денис Юрьевич","address":"655603, Республика Хакасия, г. Саяногорск, мкр. Южный, д. 7, кв. 24","lastLegalCase":{"number":"А74-2152/2022","status":{"code":"CitizenAssetsDisposal","description":"Реализация имущества гражданина"}},"guid":"068230b4-c17a-4637-9832-55d61ff5b377","fio":"Трубникова Ольга Константиновна","inn":"190205855127"}],"total":7}'
str_resp_1 = '''{'pageData': [{'snils': '17808600286', 'category': 'Физическое лицо', 'region': 'Республика Хакасия', 'arbitrManagerFio': 'Новикова Вера Александровна', 'address': 'Хакасия 
Респ, Абаза г, Ленина ул, д. 5А, кв. 5', 'lastLegalCase': {'number': 'А74-156/2024', 'status': {'code': 'CitizenDebtRestructuring', 'description': 'Реструктуризация долгов гражданина'}}, 'guid': '4c4a8850-d9fd-11ee-80c9-00620be2fa80', 'fio': 'Козлов Игорь Сергеевич', 'inn': '190901763907'}], 'total': 1}'''

'''{"pageData": [{"snils": "14397220165", "category": "Физическое лицо", "region": "Республика Хакасия", "arbitrManagerFio": "Малюка Анна Алексеевна", "address": "655602, Республика Хакасия, г. Саяногорск, мкр. Центральный, д. 34, кв. 11", "lastLegalCase": {"number": "А74-3211/2024", "status": {"code": "CitizenDebtRestructuring", "description": "Реструктуризация долгов гражданина"}}, "guid": "2a264a9a-1db2-11ef-a609-00620be2fa80", "fio": "Горошко Светлана Андреевна", "inn": "242000604230"}, {"snils": "06414866972", "category": "Физическое лицо", "region": "Республика Хакасия", "arbitrManagerFio": "Михайлова Наталья Александровна", "address": "РХ, г. Саяногорск, рп. Майна, ул. Рабовича, д. 14Б", "lastLegalCase": {"number": "А74-2672/2024", "status": {"code": "CitizenAssetsDisposal", "description": "Реализация имущества гражданина"}}, "guid": "5d6a6e58-38fc-11ef-b2c8-00620be2fa80", "fio": "Иванова Евгения Алексеевна", "inn": "190200302922"}, {"snils": "17416655279", "category": "Физическое лицо", "region": "Республика Хакасия", "arbitrManagerFio": "Пискунова Ольга Александровна", "address": "Республика Хакасия, г. Абакан, ул. Семнадцатая, д. 7", "lastLegalCase": {"number": "А74-5511/2024", "status": {"code": "CitizenAssetsDisposal", "description": "Реализация имущества гражданина"}}, "guid": "e8f9516a-545d-11ef-b1c1-00620be2fa80", "fio": "Иванова Ксения Валерьевна", "inn": "190119272940"}, {"snils": "12497895514", "category": "Физическое лицо", "region": "Республика Хакасия", "arbitrManagerFio": "Беспалова Светлана Николаевна", "address": "Республика Хакасия, Усть-Абаканский район, аал Чарков, ул. Степная, д. 8, кв. 1", "lastLegalCase": {"number": "А74-1252/2024", "status": {"code": "CitizenDebtRestructuring", "description": "Реструктуризация долгов гражданина"}}, "guid": "d56d6548-01ea-11ef-986b-00620be2fa80", "fio": "Иванова Мария Андреевна", "inn": "245506290181"}, {"snils": "17298472416", "category": "Физическое лицо", "region": "Республика Хакасия", "arbitrManagerFio": "Часовской Николай Сергеевич", 
"address": "655111, Республика Хакасия, г. Сорск, ул. Геологов, д.1, кв. 1", "lastLegalCase": {"number": "А74-3690/2024", "status": {"code": "CitizenAssetsDisposal", "description": "Реализация имущества гражданина"}}, "guid": "6e99662c-353f-11ef-8582-00620be2fa80", "fio": "Иванова Надежда Александровна", "inn": "190309950030"}, {"snils": "13771787700", "category": "Физическое лицо", "region": "Республика Хакасия", "arbitrManagerFio": "Новикова Вера Александровна", "address": "Хакасия Респ, Черногорск г, Кирова 1-я линия ул, д. 15А", "lastLegalCase": {"number": "А74-736/2024", "status": {"code": "CitizenDebtRestructuring", "description": "Реструктуризация долгов гражданина"}}, "guid": "62fa1b06-e5e7-11ee-b5d7-00620be2fa80", "fio": 
"Марьясова Ксения Александровна", "inn": "170103764284"}, {"snils": "10619085237", "category": "Физическое лицо", "region": "Республика Хакасия", "arbitrManagerFio": "Тюриков Денис Юрьевич", "address": "655603, Республика Хакасия, г. Саяногорск, мкр. Южный, д. 7, кв. 24", "lastLegalCase": {"number": "А74-2152/2022", "status": {"code": "CitizenAssetsDisposal", "description": "Реализация имущества гражданина"}}, "guid": "068230b4-c17a-4637-9832-55d61ff5b377", "fio": "Трубникова Ольга Константиновна", "inn": "190205855127"}], "total": 7}'
'''


'''
Structure of response
{"pageData":
    [
0        {
            "snils":"10749272160",
            "category":"Физическое лицо",
            "region":"Республика Хакасия",
            "arbitrManagerFio":"КРУГЛОВ ГЕОРГИЙ КОНСТАНТИНОВИЧ",
            "address":"Республика Хакасия, Боградский район, с. Первомайское, ул. Кирова, д. 5, кв. 3",
            "lastLegalCase":
                {
                "number":"А74-8815/2023",
                "status":
                    {
                    "code":"CitizenAssetsDisposal",
                    "description":"Реализация имущества гражданина"
                    }
                },
            "guid":"0677d445-f2e1-47a8-9230-302973cf3368",
            "fio":"Пистунович Сергей Анатольевич",
            "inn":"190111676789"
        }
    ],
    "total":1
}

Dictionary dict_keys include keys:
    'pageData': value list from dictionaries (dictionaries) with data
    'total': value - total of dictionaries))

    
'''

'''
func for read data file(? csv)
func for clean data 
func for create data list for check
func for check person
func for make full report
func for make main report

'''
    


"""
Ссылки на страницу Федресурс должны быть активными.
Исправить.
Возможно, нужно добавить знак конца строки или перевода на другую строку - не работает, ищи другие варианты.

Исправить поиск.
Искать варианты с 'ё' вместо 'е'.
Потому что пропускает фамилиии с 'е' вместо 'ё'.

Увеличить ширину столбцов выходного файла эксел.

Собирать дату рождения и место рождения.

Сделать копирование данных в новую книгу эксел, 
в которой первый лист - это копия данных файла пользователя, 
а второй лист - это результат проверки данных из файла пользователя на сайте.

+Записать книгу эксел в файл с названием включающим год-месяц-дату проверки.

Удалить файл данных пользователя.

Перед проверкой спрашивать пользователя какой файл проверять.

После запуска находить файл с минимальной датой редактирования.
"""