import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from email.mime.text import MIMEText
import smtplib
import dont_share as ds
numList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


class Digimart:
    def __init__(self):
        self.mark = []
        self.alter = []
        self.send = 0

    @staticmethod
    def get_online_data():
        data = pd.DataFrame = pd.read_csv('digimart.csv', names=['guitar', 'num'], header=0)
        return data

    @staticmethod
    def search_goods(url, name):
        url = 'https://www.digimart.net/search?keywordAnd='+name+'&productTypes=USED'

        ### 填自己的代理地址
        proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

        response = requests.get(url=url, proxies=proxies)
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        info = str(soup.select('.resultsOfNumber'))
        info = re.findall("\\d+", info)
        if len(info) == 0:
            num = int(0)
        else:
            num = int(info[0])
        return num

    def update(self):
        data = Digimart.get_online_data()
        for index in range(data.shape[0]):
            url = 'https://www.digimart.net/search?keywordAnd=' + data.guitar[index] + '&productTypes=USED'
            num_searched = Digimart.search_goods(url, data.guitar[index])
            if data.num[index] < num_searched:
                self.alter.append(int(num_searched - data.num[index]))
                self.mark.append(1)
                # print(str(num_searched-data.num[index])+' '+str(data.guitar[index])+' new goods on digimart')
                data.loc[index, 'num'] = num_searched

            elif data.num[index] > num_searched:
                self.alter.append(int(data.num[index] - num_searched))
                self.mark.append(-1)
                # print(str(data.num[index] - num_searched) + ' '+str(data.guitar[index]) + ' has ' + ' sold on digimart')
                data.loc[index, 'num'] = num_searched

            else:
                # print(str(data.guitar[index])+' has nothing changed')
                self.mark.append(0)
                self.alter.append(int(0))
        data.to_csv('digimart.csv')

    def write_email(self):
        data = Digimart.get_online_data()
        flag = 0
        for index in range(data.shape[0]):
            if self.mark[index] != 0:
                flag = 1

        if flag == 1:
            text = 'found some new goods for you : )\n'
            for index in range(data.shape[0]):
                if self.mark[index] == 1:
                    text += (str(self.alter[index])+' '+str(data.guitar[index])+' new goods on digimart\n')
                elif self.mark[index] == -1:
                    text += (str(self.alter[index])+' '+str(data.guitar[index])+' goods sold on digimart\n')
        else:
            text = 'There is nothing happened.'

        print(text)
        return text, flag

    def send_email(self):
        text, flag = Digimart.write_email(self)
        if flag == 1:
            msg = MIMEText(text, 'plain', 'utf-8')
            from_address = ds.from_address
            password = ds.password
            to_address = ds.to_address
            server = smtplib.SMTP_SSL('smtp.gmail.com')
            server.connect('smtp.gmail.com', 465)
            server.login(from_address, password)
            server.sendmail(from_address, to_address, msg.as_string())
            server.quit()
            print('Gmail sended')
        else:
            print('Nothing changed, do not send email')


digimart = Digimart()
digimart.update()
digimart.send_email()





