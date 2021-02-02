import os
import string
import pandas as pd
import numpy as np
from time import sleep
from tabula import read_pdf
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import Select
from selenium import webdriver
import chromedriver_autoinstaller
from .BaseGambling import BaseGambling

class CasinoGambling(BaseGambling):
    
    def get_months(self, start_date, end_date):
        end_date = pd.to_datetime(end_date)
        one_month_up = f'{end_date.month + 1 if end_date.month != 12 else 1}/{end_date.year + 1}'
        date_range = pd.date_range(start_date, one_month_up, freq='M')
        months = [date.strftime('%B') + ' ' + date.strftime('%Y') for date in date_range]
        return months


    def scrape(self, start_date=None, end_date=None):
        driver = self.driver
        driver.get('https://www.igb.illinois.gov/CasinoReports.aspx')

        # ================================================================================
        # Download the files from the web form
        self.download_files(driver, start_date='07-01-2020', end_date=end_date, vg=False)
        # ================================================================================
        # Format files to match tables that will be parsed from pdfs
        files = self.get_data_files()
        file_paths = [os.path.join(self.data_dir, file) for file in files]
        needed_columns = ['Casino', 'Total AGR', 'Square Feet', 'Admissions', 'State Share', 'Local Share']
        rename_columns = lambda df: df.rename({'Total AGR': 'agr', 'Square Feet': 'casino_square_feet'}, axis=1)
        def reformat_columns(df):
            df.columns = [column.lower().strip().replace(' ', '_') for column in df.columns]
            return df
        frames = [pd.read_csv(path) for path in file_paths]
        frames = [rename_columns(df) for df in frames]
        frames = [reformat_columns(df) for df in frames]
        columns = ['casino','agr','casino_square_feet','admissions','state_share','local_share', 'date']
        try:
            frames = [df[columns] for df in frames]
        except:
            print(frames[0].columns)
            return
        for idx in range(len(file_paths)):
            path = file_paths[idx]
            frame = frames[idx]
            frame.to_csv(path, index=False)
        # ================================================================================
        # Download and parse the archived pdfs
        self.download_pdfs(start_date=start_date, end_date=end_date)
        # ================================================================================
        # Merge datafiles
        self.merge_files()
        
    
    def download_pdfs(self, start_date=None, end_date=None):
        '''- Download Illinois Gaming Board Casino reports  within a given time frame
             into a designated directory
           - Translate the pdf file into a pandas dataframe
           - Clean the tables and merge the monthly reports into a single file.
           
           If not dates arguments are given, all reports are downloaded.
           If a start date is not given, the start day defaults to the January 2000
           If no end date is given, the end date defaults to the current month.'''
        
        # Collect months that fall within the required range
        now = f'{self.current_month()} {self.current_year()}'
        if start_date and end_date:
            date_range = self.get_months(start_date, end_date)
        elif start_date:
            date_range = self.get_months(start_date, now)
        elif end_date:
            date_range = self.get_months('January 2000', end_date)
        else:
            date_range = self.get_months('January 2000', now)
            
            
        # Nagivate driver to the casino monthly reports webpage
        driver = self.driver
        driver.get('https://www.igb.illinois.gov/CasinoReports.aspx')
        
        # Collect archived report dates
        options = Select(driver.find_element_by_id('ctl00_MainPlaceHolder_ArchiveRevenueReportPeriods')).options
        # Isolate dropdown options that fall within the required range
        file_matches = [file for file in options if file.text in date_range]

        
        # Count number of files in the data directory
        file_count = len(self.get_data_files())
        # Create empty list to append file names to
        files = self.get_data_files()
        # Loop over matching drop down options
        for file in file_matches:
            # Click option
            file.click()
            # Click submit
            button = driver.find_element_by_id('ctl00_MainPlaceHolder_ArchiveRevenueReportsButtonGo')
            button.click()
            # Wait for file to download into the data directory
            sleep(3)
            # Collect data files in in data directory
            found_files = self.get_data_files()
            # Isolate new files
            new_file = [file for file in found_files if file not in files]
            # An if check to ensure the list is not empty
            if new_file:
                # Isolate the new file name
                # There should never be more than one new file at a time
                file_name = new_file[0]
                
            # Create path to the file
            file_path = os.path.join(self.data_dir, file_name)
            # Parse the pdf file
            df = self.parse_pdf_table(file_path)
            # Add a column to the dataframe marking the date of the report
            df['date'] = file.text
            # Create date specific file name for the csv file
            csv_name = f'{file.text.replace(" ", "_").replace("/", "_")}.csv'
            # Create new path for csv file name
            new_path = os.path.join(self.data_dir, csv_name)
            # Remove old pdf file
            os.remove(file_path)
            # Before February 2013, the Illinois Gaming Board reported numbers
            # in the millions by dropping the zeros and indicating this change
            # in the header of the pdf. Because of this, the zeros must be added
            # back in to ensure the numeric data is accurate when converted from
            # string to float
            if pd.to_datetime(file.text) < pd.to_datetime('February 2013'):
                add_zeros = lambda x: x + ',000'
                df['agr'] = df.agr.apply(add_zeros)
                df['state_share'] = df.state_share.apply(add_zeros)
                df['local_share'] = df.local_share.apply(add_zeros)
            
            # Isolate the numeric columns, remove punctuation (other than periods)
            # and convert them to float.
            numeric = ['agr',
                     'casino_square_feet',
                     'admissions',
                     'state_share',
                     'local_share']
            for column in numeric:
                df[column] = df[column].apply(self.clean_string)
                df[column] = df[column].astype(float)
            # drop aggregate columns
            df.drop(['agr_per_square_foot',
                     'agr_per_admission',], axis = 1, inplace=True)
            # Save the cleaned data to the date specific csv file name!
            df.to_csv(new_path, index=False)
            # Add the name of the csv file to list of files
            files.append(csv_name)
            # Add one to the count of files in the data directory
            file_count += 1

            
            
            
    def parse_pdf_table(self, path):
        '''Takes in a file path to an Illinois Casino Report .pdf file, and returns a pandas dataframe
           of the page 1 table.'''
        
        # Read in the first page of the .pdf
        df = read_pdf(path, pages=1)
        
        # Some of the .pdf files are formatted somewhat differently. 
        # The code below checks the shape of the parsed files
        # And determines the proper way of merging all of the columns
        if len(df[0].columns) < 7:
            df = pd.concat([df[0], df[1],df[2].drop(0).reset_index()], axis = 1)
            df.drop('Unnamed: 0', axis = 1, inplace=True)
        else:
            df = df[0]
        
        # If merging multiple tables was requires, a column names 'index' will appear
        # This column in unecessary and is removed below
        if 'index' in list(df.columns):
            df.drop('index', axis = 1, inplace = True)
            
        # The .pdf reports use multi index headers. 
        # When translated into a dataframe, the placement of column names tends
        # to be pretty inconsistent. 
        # What is consistent is that the casino names are reliably
        # ordered alphabetically.
        # The most reliable way of isolated the desired data
        # is to locate the row that contains the first casino name
        # and remove all rows appearing before.
        start_index = df.fillna('Null')[df.fillna('Null').iloc[:,0].str.contains('alton', case=False)].index[0]
        df = df.iloc[start_index:]
        
        # Null values occasionally appear in columns that contain valuable data. 
        # The row containing the first casino name consistently marks
        # useless columns as null and useful columns with actual data.
        # For this reason, we isolate this row, and loop over the column observations.
        # If a null value is found, that column is dropped. 
        to_drop = []
        find_extra = df[df.iloc[:,0].str.contains('alton', case=False)]
        for idx in find_extra.iloc[0].index:
            try:
                if find_extra.iloc[0][idx] == np.nan:
                    to_drop.append(idx)
                elif find_extra.iloc[0][idx] == '$':
                    to_drop.append(idx)
            except:
                error =  find_extra.iloc[0][idx]
                print('Error')

        df.drop(to_drop, axis=1, inplace=True)
        
        # The pdf parser is occasionally successful at separating the 
        # state share and local share columns. 
        # Because of this, there are two table shapes that must be address.
        # If the two columns have not been seperated, we loop over the values
        # in that column, split the values, remove the merged column, and create two new columns
        if len(df.columns) == 7:

            df.columns = ['Casino','AGR','Casino Square Feet', 'Admissions','AGR Per Square Foot',
                         'AGR Per Admission','Tax Allocations']
            state = []
            local = []
            for val in df['Tax Allocations'].apply(lambda x: x.split('$')).values:
                if val[0] == '':
                    state.append(val[1])
                    local.append(val[2])
                    continue
                state.append(val[0])
                local.append(val[1])

            df = df.iloc[:,0:-1]

            df['state_share'] = state
            df['local_share'] = local
        
        # If the parser separated the columns, we set the column names with not edits
        elif len(df.columns) == 8:

            df.columns = ['Casino','AGR','Casino Square Feet', 'Admissions','AGR Per Square Foot',
                         'AGR Per Admission','State Share', 'Local Share']    
            
        # Edit the column names for easier manipulation
        df.columns = [column.lower().strip().replace(' ', '_') for column in df.columns]
        
        # The tables contain a row that totals the values for a given month.
        # This is not useful for a full monthly dataset so it is dropped
        total_index = df[df.casino.str.contains('total', case=False)].index
        if not total_index.empty:
            df.drop(total_index, inplace=True)
        
        return df
    
    def merge_files(self):
        files = self.get_data_files()
        path = lambda x: os.path.join(self.data_dir, x)
        dfs = [pd.read_csv(path(file)) for file in files]
        for file in files:
            os.remove(path(file))
        pd.concat(dfs).reset_index(drop=True).to_csv(path('casino_data.csv'), index=False)
        
    def clean_string(self, text):
        return text.translate(str.maketrans('','', string.punctuation.replace('.', '') + ' '))