import sys

from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
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

logging.basicConfig(filename='app_lite.log', encoding='utf-8', filemode='w',
                    format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.warning("Mulai Proses")
print("[{}] Mulai Proses".format(datetime.now()))
waittime = 10

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

        my_dict = {'kode': [], 'nama': [], 'hps': [], 'tahun_anggaran': [], 'tahapan': [], 'lokasi': [],
                   'tgl_pengumuman_pemenang': [], 'link':[]}
        # sleep(5)

        # wait for load combo display
        wait = WebDriverWait(driver, waittime)
        wait.until(EC.presence_of_element_located((By.XPATH, "//select[@name='tbllelang_length']")))

        # grab data
        project_name = driver.find_element(By.XPATH, "//select[@name='tbllelang_length']")
        select = Select(project_name)
        select.select_by_value("-1")
        sleep(5)

        # wait for load table
        wait = WebDriverWait(driver, waittime)
        wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='tbllelang']/tbody/tr")))

        tables = driver.find_elements(By.XPATH, "//table[@id='tbllelang']/tbody/tr")

        # try:
        # loop table content
        for i in range(1, len(tables) + 1):
            kode = driver.find_element(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[1])").text
            nama = driver.find_element(By.XPATH,
                                       "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[1]/a)").text
            tahun_anggaran = driver.find_element(By.XPATH,
                                                  "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[2])").text
            tahapan = driver.find_element(By.XPATH,
                                          "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[4]/a)").text
            hps = driver.find_element(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[5])").text

            # convert hps to float
            arrhps = hps.split()
            satuan = arrhps[1]
            angka = arrhps[0].replace(",", ".")

            if satuan == 'Jt':
                nom = float(angka) * 1000000
            elif satuan == 'M':
                nom = float(angka) * 1000000000
            else:
                nom = float(angka) * 1000000000000

            my_dict['kode'].append(kode)
            my_dict['nama'].append(nama)
            my_dict['hps'].append(nom)
            my_dict['tahun_anggaran'].append(tahun_anggaran)
            my_dict['tahapan'].append(tahapan)
            my_dict['lokasi'].append(" ")
            my_dict['tgl_pengumuman_pemenang'].append(" ")
            my_dict['link'].append(" ")

            ActionChains(driver).scroll_by_amount(0, 200).perform()
        # except StaleElementReferenceException:
        #     pass
        # convert to excel
        # sys.exit()
        # print(my_dict)
        df = pd.DataFrame(my_dict)
        df.to_excel(r'lpse/{}_{}_{}.xlsx'.format(path_url.netloc, kategori, tahun), index=False)
        logging.warning("%s => Berhasil", url)
        print("[{}] {} => Berhasil".format(datetime.now(), url))
        #
        driver.close()
        driver.quit()
    except:
        logging.warning("%s => Gagal", url)
        print("[{}] {} => Gagal".format(datetime.now(), url))


logging.warning("Akhir Proses")
print("[{}] Akhir Proses".format(datetime.now(), url))