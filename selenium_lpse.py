import csv

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd

kategori = "2"
tahun = "2022"

url = "https://lpse.lkpp.go.id/eproc4/lelang?kategoriId="+kategori+"&tahun="+tahun

PATH = "D:\MINE\Git\selenium\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get(url)
driver.maximize_window()

# prepare for csv/dict
# writer = csv.writer(open('lpse/{}_{}.csv'.format(kategori, tahun), 'w', newline=''))
# header = ['KODE', 'NAMA', 'HPS', 'TAHUN ANGGARAN', 'TAHAPAN']
# writer.writerow(header)
my_dict = {}
my_dict['kode'] = []
my_dict['nama'] = []
my_dict['hps'] = []
my_dict['tahun_anggaran'] = []
my_dict['tahapan'] = []

# grab data
project_name = driver.find_element(By.XPATH, "//select[@name='tbllelang_length']/option[text()='Semua']")
project_name.click()
sleep(3)

tables =  driver.find_elements(By.XPATH, "//table[@id='tbllelang']/tbody/tr")
for i in range(1, len(tables)+1):
    kode = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) +"]/td[1])")
    nama = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[1]/a)")
    tahun_anggaran = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[2]/p[2])")
    tahapan = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[4]/a)")
    hps = driver.find_elements(By.XPATH, "(//table[@id='tbllelang']/tbody/tr[" + str(i) + "]/td[5])")

    # convert hps to float
    satuan = [hp.text for hp in hps][0].split()[1]
    angka = [hp.text for hp in hps][0].split()[0].replace(",", ".")

    if(satuan == 'Jt'):
        nom = float(angka) * 1000000
    elif(satuan == 'M'):
        nom = float(angka) * 1000000000
    else:
        nom = float(angka) * 1000000000000

    # print(i, nom)
    # writer = csv.writer(open('lpse/{}_{}.csv'.format(kategori, tahun), 'a', newline='', encoding='utf-8'))
    # data = [[kd.text for kd in kode][0], [nm.text for nm in nama][0], nom, [thn.text for thn in tahun_anggaran][0], [thp.text for thp in tahapan][0]]
    # writer.writerow(data)

    # for j in range(1, len(tables) + 1):
    my_dict['kode'].append([kd.text for kd in kode][0])
    my_dict['nama'].append([nm.text for nm in nama][0])
    my_dict['hps'].append(nom)
    my_dict['tahun_anggaran'].append([thn.text for thn in tahun_anggaran][0])
    my_dict['tahapan'].append([thp.text for thp in tahapan][0])


# print(my_dict)
# sleep(2)
# convert to excel
# data = pd.read_csv(r'lpse/{}_{}.csv'.format(kategori, tahun), encoding='utf-8')
df = pd.DataFrame(my_dict)
df.to_excel(r'lpse/{}_{}.xlsx'.format(kategori, tahun), index=False)
# print(df)


