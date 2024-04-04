import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
from urllib.parse import urlparse
import logging
from datetime import datetime

# variabels
urls = []
with open('urls.txt') as f:
    for line in f:
        urls.append(line.strip())

# sys.exit()
logging.basicConfig(filename='app.log', encoding='utf-8', filemode='w', format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.warning("Mulai Proses")
print("[{}] Mulai Proses".format(datetime.now()))

for url in urls:
    try:
        path_url = urlparse(url)
        arr_query = path_url.query.split("&")
        kategori = arr_query[0].split("=")[1]
        tahun = arr_query[1].split("=")[1]

        # sys.exit()
        # windows
        # PATH = Service("chromedriver.exe")
        # linux
        PATH = Service("./chromedriver")

        # initiate chrome selenium
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # windows
        driver = webdriver.Chrome(service=PATH, options=options)
        driver.get(url)
        driver.maximize_window()

        my_dict = {'kode': [], 'nama': [], 'hps': [], 'tahun_anggaran': [], 'tahapan': []}

        # check combo display data sudah terload atau belum
        sleep(3)

        # grab data
        project_name = driver.find_element(By.XPATH, "//select[@name='tbllelang_length']/option[text()='Semua']")
        sleep(7)

        tables = driver.find_elements(By.XPATH, "//table[@id='tbllelang']/tbody/tr")
        for i in range(1, len(tables) + 1):
            kode = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[1])")
            nama = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[1]/a)")
            tahun_anggaran = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[2])")
            tahapan = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[4]/a)")
            hps = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[5])")

            # convert hps to float
            satuan = [hp.text for hp in hps][0].split()[1]
            angka = [hp.text for hp in hps][0].split()[0].replace(",", ".")

            if satuan == 'Jt':
                nom = float(angka) * 1000000
            elif satuan == 'M':
                nom = float(angka) * 1000000000
            else:
                nom = float(angka) * 1000000000000

            my_dict['kode'].append([kd.text for kd in kode][0])
            my_dict['nama'].append([nm.text for nm in nama][0])
            my_dict['hps'].append(nom)
            my_dict['tahun_anggaran'].append([thn.text for thn in tahun_anggaran][0])
            my_dict['tahapan'].append([thp.text for thp in tahapan][0])

        # convert to excel
        df = pd.DataFrame(my_dict)

        df.to_excel(r'lpse/{}_{}_{}.xlsx'.format(path_url.netloc, kategori, tahun), index=False)

        logging.warning("%s Berhasil", url)
        print("[{}] {} Berhasil".format(datetime.now(), url))

        driver.close()
        driver.quit()
    except:
        logging.warning("%s Gagal", url)
        print("[{}] {} Gagal".format(datetime.now(), url))
        pass

logging.warning("Akhir Proses")
print("[{}] Akhir Proses".format(datetime.now(), url))
