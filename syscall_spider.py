import requests
from bs4 import BeautifulSoup
import pickle


if __name__ == "__main__":
    html = requests.get(r'https://man7.org/linux/man-pages/dir_section_2.html').text
    soup = BeautifulSoup(html, 'lxml')

    func_list = []
    table = soup.find_all('table')[1]
    for td in table.find_all('td'):
        for a in td.find_all('a'):
            func_list.append(a.text.split('(')[0])
    
    with open(r'syscall_list', r'wb') as f:
        pickle.dump(func_list, f)
    f.close()