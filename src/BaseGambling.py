import os
import datetime
import pandas as pd
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import Select
from time import sleep
from selenium import webdriver
import chromedriver_autoinstaller


class BaseGambling:
    def __init__(self, data_path, headless=True):
        self.data_dir = os.path.join(os.path.abspath('..'), data_path)
        self.driver = self.create_driver(headless=headless)

    def create_driver(self, headless=True):
        driver = chromedriver_autoinstaller.install(cwd=True)
        chrome_options = webdriver.ChromeOptions()     
        prefs = {'download.default_directory' : self.data_dir}
        chrome_options.add_experimental_option('prefs', prefs)
        if headless:
            chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(driver, 
                                 chrome_options = chrome_options)
        return driver

    def current_year(self):

        return str(datetime.datetime.now().year)

    def current_month(self):

        mydate = datetime.datetime.now()
        month = mydate.strftime("%B")
        

        return month

    def get_data_files(self):
        files = os.listdir(self.data_dir)
        return [file for file in files if not file.startswith('.')]

    def download_files(self, driver, start_date=None, end_date=None, vg=True):
    
        if start_date:
            start_date = pd.to_datetime(start_date)
        else:
            start_date = pd.to_datetime('09-01-2012')
                
        if end_date:
            end_date = pd.to_datetime(end_date)
            one_month_up = f'{end_date.month + 1 if end_date.month != 12 else 1}/{end_date.year + 1}'
            end_date = pd.to_datetime(one_month_up)
            
        else:
            end_date = pd.to_datetime(f'{self.current_month()} {self.current_year()}')

        self.start_date = start_date
        self.end_date = end_date
                                        
        if vg:
            radio_element = driver.find_element_by_id('ctl00_MainPlaceHolder_TypeEst')
            radio_element.click()
            select = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_SearchEstablishment'))
            options = select.options
            options[0].click()


        start_year = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_SearchStartYear'))
        years_objects = start_year.options
        years = sorted([object_.text for object_ in years_objects])

        files = set(self.get_data_files())
        file_count = len(self.get_data_files())
        for idx in range(len(years)):
            year = years[idx]
         
            if not int(year) >= start_date.year:
                continue
                
            start_years = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_SearchStartYear')).options
            end_years = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_SearchEndYear')).options
            start_year = [option for option in start_years if option.text == year][0].click()
            end_year = [option for option in end_years if option.text == year][0].click()
            start_months = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_SearchStartMonth')).options
            months = [start_month.text for start_month in start_months]

            for idx2 in range(len(months)):
                month = months[idx2]
                date = pd.to_datetime(f'{month} {year}')
                if date < start_date:
                    continue
                    
                if date > end_date:
                    break
                
                start_months = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_SearchStartMonth')).options
                end_months = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_SearchEndMonth')).options
                start_month = [option for option in start_months if option.text == month][0].click()
                end_month = [option for option in end_months if option.text == month][0].click()
                file_type = driver.find_element_by_id('ctl00_MainPlaceHolder_ViewCSV')
                
                file_type.click()
                submit = driver.find_element_by_id('ctl00_MainPlaceHolder_ButtonSearch')
                submit.click()
                sleep(3)

                file_names = self.get_data_files()
                for file in file_names:
                    if file not in files:
                        old_file = file
                        file = f'{month}_{year}' + file
                        files.add(file)
                        old_path = os.path.join(self.data_dir, old_file)
                        new_path = os.path.join(self.data_dir, file)
                        os.rename(old_path,new_path)
                        try:
                            edit_file = pd.read_csv(new_path, skiprows=3)
                            edit_file['date'] =  f'{month}-{year}'
                            edit_file.to_csv(new_path)
                            file_count +=1
                        except:
                            os.remove(new_path)