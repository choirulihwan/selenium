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

# functions
def grab_data(driver, waittime, my_dict):
    # start grabdata
    # wait for load combo display
    wait = WebDriverWait(driver, waittime)
    wait.until(EC.presence_of_element_located((By.XPATH, "//select[@name='tbllelang_length']")))

    project_name = driver.find_element(By.XPATH, "//select[@name='tbllelang_length']")
    select = Select(project_name)

    select.select_by_value("100")
    sleep(5)

    # wait for load table
    wait = WebDriverWait(driver, waittime)
    wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='tbllelang']/tbody/tr")))

    tables = driver.find_elements(By.XPATH, "//table[@id='tbllelang']/tbody/tr")
    firstdata = driver.find_elements(By.XPATH, "//table[@id='tbllelang']/tbody/tr/td")

    # loop table content
    if firstdata[0].text != "Tidak ditemukan data yang sesuai":
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

        # search for next
        nextlink = idriver.find_element(By.XPATH, "//a[@data-dt-idx = 'next']")
        if nextlink:
            nextlink.click()
            WebDriverWait(idriver, waittime)
            idriver.execute_script("document.documentElement.scrollTop = 0;")
            grab_data(idriver, iwaittime, imydict)

    else:
        logging.warning("%s => Proyek belum ada", url)
        print("[{}] {} => Proyek belum ada".format(datetime.now(), url))

    return my_dict

# variabels
urls = []
with open('urls.txt') as f:
    for line in f:
        urls.append(line.strip())

logging.basicConfig(filename='app_lite.log', encoding='utf-8', filemode='w',
                    format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

version = '20240821.01'
logging.warning("LPSE versi " + version)
logging.warning("Mulai Proses")
print("[{}] Mulai Proses".format(datetime.now()))
iwaittime = 10

for url in urls:
    try:
        # sys.exit()
        # windows
        PATH = Service("chromedriver.exe")
        # linux
        # PATH = Service("./chromedriver")

        # initiate chrome selenium
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # windows
        idriver = webdriver.Chrome(service=PATH, options=options)

        path_url = urlparse(url)
        arr_query = path_url.query.split("&")
        kategori = arr_query[0].split("=")[1]
        tahun = arr_query[1].split("=")[1]

        idriver.get(url)
        idriver.maximize_window()
        # sleep(5)

        #start grabdata
        imydict = {'kode': [], 'nama': [], 'hps': [], 'tahun_anggaran': [], 'tahapan': [], 'lokasi': [],
                   'tgl_pengumuman_pemenang': [], 'link': []}
        result_dict = grab_data(idriver, iwaittime, imydict)
        # end grabdata

        # convert to excel
        # sys.exit()
        df = pd.DataFrame(result_dict)
        df.to_excel(r'lpse/{}_{}_{}.xlsx'.format(path_url.netloc, kategori, tahun), index=False)
        logging.warning("%s => Berhasil", url)
        print("[{}] {} => Berhasil".format(datetime.now(), url))
        #
        idriver.close()
        idriver.quit()
    except Exception as e:
        logging.warning("%s => Gagal", url)
        logging.warning("%s", e)
        print("[{}] {} => Gagal".format(datetime.now(), url))

logging.warning("Akhir Proses")
print("[{}] Akhir Proses".format(datetime.now(), url))