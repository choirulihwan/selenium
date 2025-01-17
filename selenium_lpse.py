from selenium import webdriver
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

logging.basicConfig(filename='app.log', encoding='utf-8', filemode='w',
                    format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

version = '20240821.01'
logging.warning("LPSE versi " + version)
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
        # tidak ada option semua
        select.select_by_value("100")
        sleep(5)

        # wait for load table
        wait = WebDriverWait(driver, waittime)
        wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='tbllelang']/tbody/tr")))

        tables = driver.find_elements(By.XPATH, "//table[@id='tbllelang']/tbody/tr")
        firstdata = driver.find_elements(By.XPATH, "//table[@id='tbllelang']/tbody/tr/td")

        # get original url
        window_handles_before = driver.window_handles

        # loop table content
        if firstdata[0].text != "Tidak ditemukan data yang sesuai":
            for i in range(1, len(tables) + 1):
                kode = driver.find_element(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[1])")
                nama = driver.find_element(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[1]/a)")
                tahun_anggaran = driver.find_element(By.XPATH,
                                                      "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[2])")
                tahapan = driver.find_element(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[4]/a)")
                hps = driver.find_element(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[5])")

                # convert hps to float
                arrhps = hps.text.split()
                satuan = arrhps[1]
                angka = arrhps[0].replace(",", ".")

                if satuan == 'Jt':
                    nom = float(angka) * 1000000
                elif satuan == 'M':
                    nom = float(angka) * 1000000000
                else:
                    nom = float(angka) * 1000000000000

                my_dict['kode'].append(kode.text)
                my_dict['nama'].append(nama.text)
                my_dict['hps'].append(nom)
                my_dict['tahun_anggaran'].append(tahun_anggaran.text)
                my_dict['tahapan'].append(tahapan.text)

                nama.click()
                wait = WebDriverWait(driver,waittime)
                wait.until(EC.number_of_windows_to_be(len(window_handles_before) + 1))
                window_handles_after = driver.window_handles

                new_window_handle = [wh for wh in window_handles_after if wh not in window_handles_before][0]
                driver.switch_to.window(new_window_handle)

                new_tab_url = driver.current_url
                # print(f"URL of detail: {new_tab_url}")

                try:
                    lokasi = driver.find_element(By.XPATH, "//table/tbody/tr[16]/td/ul/li").text
                except NoSuchElementException:
                    lokasi = ''

                # print(f"lokasi: {lokasi}")
                my_dict['lokasi'].append(lokasi)
                my_dict['link'].append(new_tab_url)

                # start window tahapan
                try:
                    linktahapan = driver.find_element(By.XPATH, "//table/tbody/tr[6]/td/a")
                    window_tahapan_before = driver.window_handles
                    linktahapan.click()
                    wait = WebDriverWait(driver, waittime)
                    wait.until(EC.number_of_windows_to_be(len(window_tahapan_before) + 1))
                    window_tahapan_after = driver.window_handles
                    new_window_tahapan = [wh for wh in window_tahapan_after if wh not in window_tahapan_before][0]
                    driver.switch_to.window(new_window_tahapan)
                    new_tab_tahapan = driver.current_url
                    # print(f"URL of the tahapan: {new_tab_tahapan}")

                    try:
                        tgl_tahapan = driver.find_element(By.XPATH, "//table/tbody/tr[10]/td[3]").text
                    except NoSuchElementException:
                        tgl_tahapan = ''

                    # print(f"tgl tahapan: {tgl_tahapan}")
                    my_dict['tgl_pengumuman_pemenang'].append(tgl_tahapan)
                    driver.close()
                except:
                    my_dict['tgl_pengumuman_pemenang'].append('')
                # end window tahapan

                driver.switch_to.window(new_window_handle)
                driver.close()

                driver.switch_to.window(window_handles_before[0])
                ActionChains(driver).scroll_by_amount(0, 200).perform()
        else:
            logging.warning("%s => Proyek belum ada", url)
            print("[{}] {} => Proyek belum ada".format(datetime.now(), url))

        # convert to excel
        # sys.exit()
        df = pd.DataFrame(my_dict)

        df.to_excel(r'lpse/{}_{}_{}.xlsx'.format(path_url.netloc, kategori, tahun), index=False)

        logging.warning("%s => Berhasil", url)
        print("[{}] {} => Berhasil".format(datetime.now(), url))

        driver.close()
        driver.quit()
    except Exception as e:
        logging.warning("%s => Gagal", url)
        logging.warning("%s", e)
        print("[{}] {} => Gagal".format(datetime.now(), url))


logging.warning("Akhir Proses")
print("[{}] Akhir Proses".format(datetime.now(), url))


