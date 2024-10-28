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
from bs4 import BeautifulSoup


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
    middle_url = "&regionId=all&isActiveLegalCase=null"
#    middle_url = "&isActiveLegalCase=null&regionId=" # Это для всех дел независимо от статуса
#    middle_url = "&isActiveLegalCase=true&regionId=" # Это для активных дел
#    middle_url = "&isActiveLegalCase=false&regionId=" # Это для завершенных дел

    end_url = "&limit=15&offset=0"
    encoding_prsnbankruptsId = start_url + prsnbankruptsId + middle_url + end_url
#    print(start_url + prsnbankruptsId + middle_url + end_url)
    return start_url + prsnbankruptsId + middle_url + end_url


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
        if len(debtor.split()) == 3:
            prslastname, prsfirstname, prsmiddlename = debtor.lower().split()
            print(f'Проверка {debtors.index(debtor) + 1} из {len(debtors)} - {(debtors.index(debtor) + 1) * 100 // len(debtors)}% завершено')
            if get_old_response(prslastname, prsfirstname, prsmiddlename) != None:
                prsn_name, prsn_inn, prsn_birthdate, prsn_birthplace, prsn_name_history = get_old_response(prslastname, prsfirstname, prsmiddlename)
                #print(prsn_name, type(prsn_name), prsn_inn, type(prsn_inn))
                get_response(prsn_name, prsn_inn, prsn_birthdate, prsn_birthplace, prsn_name_history)
            else:
                pass
        else:
            print(red_text + 'ПРОПУСК' + end_text)
            print(red_text + str(debtor.upper()) + end_text)
        asleep = random.randint(500, 1500) / 1000
        time.sleep(asleep)


def get_old_response(prslastname='', prsfirstname='', prsmiddlename='', regionid = '95'):
    prslastname, prsfirstname, prsmiddlename = quote(prslastname), quote(prsfirstname), quote(prsmiddlename)
    session = get_session()
    url = 'https://old.bankrot.fedresurs.ru/DebtorsSearch.aspx/'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'connection': 'keep-alive',
        'cookie': '_ym_uid=1700107103592041594; _ym_d=1728816354; ASP.NET_SessionId=sljw4ny104xlpbsk54vb3wqh; _ym_isad=2; bankrotcookie=fac94585d97b923e5b4447836196b410; _ym_visorc=w; debtorsearch=typeofsearch=Persons&orgname=&orgaddress=&orgregionid=&orgogrn=&orginn=&orgokpo=&OrgCategory=' + '&prslastname=' + prslastname + '&prsfirstname=' + prsfirstname + '&prsmiddlename=' + prsmiddlename + '&prsaddress=&prsregionid=' + regionid + '&prsinn=&prsogrn=&prssnils=&PrsCategory=&pagenumber=0; qrator_msid=1728820063.842.5fEIfvU8SkJAvMc1-lscmto11bij4aoseoijabb61qkui5pr5',
        'host': 'old.bankrot.fedresurs.ru',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    data = session.get(url, headers=headers)
    text = data.text
    soup = BeautifulSoup(text, 'html.parser')
    bank = soup.find('table', class_ = 'bank').find('tr').find_next_siblings('tr')
    for el in bank:
        prsn_data_list_dirty = str(el.get_text()).replace('\t', '').replace('Физическое лицо', '').split('\r\n')
        prsn_data_list = clean_prsn_data(prsn_data_list_dirty)
        person_old_link_end = get_person_old_link(soup)
        person_old_link = build_person_old_link(person_old_link_end)
        prsn_name, prsn_inn, prsn_snils, prsn_region, prsn_adress = parse_person_data(prsn_data_list)
        #print('NAME & INN', prsn_name, prsn_inn)
        #prsn_fio, prsn_inn = get_debtor_fio_inn(person_old_link)
        prsn_birthdate, prsn_birthplace, prsn_name_history = get_debtor_old_card(person_old_link)
#########        
        return prsn_name, prsn_inn, prsn_birthdate, prsn_birthplace, prsn_name_history


def get_debtor_old_card(person_old_link):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'connection': 'keep-alive',
        'cookie': '_ym_uid=1728029516311134247; _ym_d=1728029516; ASP.NET_SessionId=0bohgc1sylhu0kmbtchgkc11; debtorsearch=typeofsearch=Persons&orgname=&orgaddress=&orgregionid=&orgogrn=&orginn=1922547928&orgokpo=&OrgCategory=&prslastname=&prsfirstname=&prsmiddlename=&prsaddress=&prsregionid=&prsinn=&prsogrn=&prssnils=19225479288&PrsCategory=&pagenumber=0; _ym_isad=2; bankrotcookie=c98aae444770b29b2e0d2443407caf61; _ym_visorc=b; qrator_msid=1729866689.333.Ji8tvRKDjgadFiNb-ablknlgh28g2kh3rnbq6ifakmlou2kob',
        'host': 'old.bankrot.fedresurs.ru',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    response = requests.get(person_old_link, headers=headers)
    web_card = response.text
    #print(web_card)
    soup = BeautifulSoup(web_card, 'html.parser')
#    prsn_lastName = soup.find('span', id = 'ctl00_cphBody_lblLastName').text
#    print('prsn_lastName', prsn_lastName)
#    prsn_firstName = soup.find('span', id = 'ctl00_cphBody_lblFirstName').text
#    print('prsn_firstName', prsn_firstName)
#    prsn_middleName = soup.find('span', id = 'ctl00_cphBody_lblMiddleName').text
#    print('prsn_middleName', prsn_middleName)
    prsn_birthdate = soup.find('span', id = 'ctl00_cphBody_lblBirthdate').text
#    print('prsn_birthdate', prsn_birthdate)
    prsn_birthplace = soup.find('span', id = 'ctl00_cphBody_lblBirthplace').text
#    print('prsn_birthplace', prsn_birthplace)
#    prsn_caseRegion =  soup.find('span', id = 'ctl00_cphBody_lblRegion').text
#    print('prsn_caseRegion', prsn_caseRegion)
#    prsn_inn = soup.find('span', id = 'ctl00_cphBody_lblINN').text
#    print('prsn_inn', prsn_inn)
#    prsn_snils = soup.find('span', id = 'ctl00_cphBody_lblSNILS').text
#    print('prsn_snils', prsn_snils)
#    prsn_address = soup.find('span', id = 'ctl00_cphBody_lblAddress').text
#    print('prsn_address', prsn_address)
#    prsn_fio = get_fio(prsn_lastName, prsn_firstName, prsn_middleName)
#    print('fio', prsn_fio)
    prsn_name_history = soup.find('span', id = 'ctl00_cphBody_lblNameHistory').text
#    out_card = prsn_fio, person_old_link, prsn_inn, prsn_snils, prsn_address, prsn_birthdate, prsn_birthplace
#    print('prsn_birthdate', prsn_birthdate)
#    print('prsn_birthplace', prsn_birthplace)
#    print('prsn_name_history', prsn_name_history)
    return(prsn_birthdate, prsn_birthplace, prsn_name_history)


def fill_out_card(prsn_birthdate, prsn_birthplace, prsn_name_history):
    #print('FILL', prsn_birthdate, prsn_birthplace, prsn_name_history)
    data['birthdate'].append(prsn_birthdate)
    data['birthplace'].append(prsn_birthplace)
    data['name_history'].append(prsn_name_history)
    #print('fill', data)


def get_session():
    s = requests.Session()
    return s


def clean_prsn_data(prsn_data_list):
    clean_prsn_data_list = [i.strip() for i in prsn_data_list if i.strip()]
    return clean_prsn_data_list


def parse_person_data(prsn_data_list):
    prsn_name, prsn_inn, prsn_snils, prsn_region, prsn_adress = prsn_data_list
    return prsn_name, prsn_inn, prsn_snils, prsn_region, prsn_adress


def get_fio(prsn_lastName, prsn_firstName, prsn_middleName):
    fio = prsn_lastName + ' ' + prsn_firstName + ' ' + prsn_middleName
    return fio


def get_debtor_fio_inn(person_old_link):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'connection': 'keep-alive',
        'cookie': '_ym_uid=1728029516311134247; _ym_d=1728029516; ASP.NET_SessionId=0bohgc1sylhu0kmbtchgkc11; debtorsearch=typeofsearch=Persons&orgname=&orgaddress=&orgregionid=&orgogrn=&orginn=1922547928&orgokpo=&OrgCategory=&prslastname=&prsfirstname=&prsmiddlename=&prsaddress=&prsregionid=&prsinn=&prsogrn=&prssnils=19225479288&PrsCategory=&pagenumber=0; _ym_isad=2; bankrotcookie=c98aae444770b29b2e0d2443407caf61; _ym_visorc=b; qrator_msid=1729866689.333.Ji8tvRKDjgadFiNb-ablknlgh28g2kh3rnbq6ifakmlou2kob',
        'host': 'old.bankrot.fedresurs.ru',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    response = requests.get(person_old_link, headers=headers)
    web_card = response.text
    soup = BeautifulSoup(web_card, 'html.parser')
    prsn_lastName = soup.find('span', id = 'ctl00_cphBody_lblLastName').text
    prsn_firstName = soup.find('span', id = 'ctl00_cphBody_lblFirstName').text
    prsn_middleName = soup.find('span', id = 'ctl00_cphBody_lblMiddleName').text
    prsn_inn = soup.find('span', id = 'ctl00_cphBody_lblINN').text
    prsn_fio = get_fio(prsn_lastName, prsn_firstName, prsn_middleName)
    return(prsn_fio, prsn_inn)


def get_person_old_link(soup):
    link = soup.find('table', class_ = 'bank').find('a')
    person_link = link.get(('href'))
    return(person_link)


def build_person_old_link(person_old_link_end):
    person_old_link_start = 'https://old.bankrot.fedresurs.ru'
    person_old_link = person_old_link_start + person_old_link_end
    return person_old_link


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
        'address': [],
        'birthdate': [],
        'birthplace': [],
        'name_history': []}


def get_response(prsn_name, prsn_inn, prsn_birthdate, prsn_birthplace, prsn_name_history):
    url = build_url(prsn_inn)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Cookie": "_ym_uid=1728029516311134247; _ym_d=1728029516; _ym_isad=2; qrator_msid=1730009363.094.AsBwkpwu6WRUDT9z-mmi14i4b1deovhg89id1cq1bve2130e3; _ym_visorc=w",
        "Referer": "https://bankrot.fedresurs.ru/bankrupts?searchString=190308294089",
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
    #print('res_dict', res_dict) # Печатаем полученный словарь
    #print('total', res_dict['total'])
    if res_dict['total'] > 0:
        #print('ЗАШЁЛ')
        print(red_text + str(prsn_name) + end_text)
        for dict in res_dict['pageData']:
            #print('словарь из пэйдждата', dict)
            data['name'].append(prsn_name)
            if 'snils' in dict:
                #print('snils', dict['snils'])
                data['snils'].append(dict['snils'])
            else:
                #print('snils', '0')
                data['snils'].append('0')
            #print('inn', dict['inn'])
            data['inn'].append(dict['inn'])
            if 'lastLegalCase' in dict:
                if 'number' in dict['lastLegalCase']:
# правильно определить словарь для номера дела                
                    data['case'].append(dict['lastLegalCase']['number'])
            else:
                data['case'].append('н/д')
            if 'lastLegalCase' in dict:
                if 'description' in dict['lastLegalCase']['status']:
# Правильно определить словарь для процедуры
                    data['procedure'].append(dict['lastLegalCase']['status']['description'])
            else:
                data['procedure'].append('н/д')
            data['address'].append(dict['address'])
            data['link_fedresurs'].append('https://fedresurs.ru/persons/' + dict['guid'] + ' ')
            fill_out_card(prsn_birthdate, prsn_birthplace, prsn_name_history)
            #print('DATA', data)


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
    today_date = str(date_today())
    check_debtors(debtors)
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

Отрабатывать внесудебное банкротство: без номера дела, без процедуры, без АУ
"""