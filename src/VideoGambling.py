import os
import pandas as pd
from .BaseGambling import BaseGambling

class VideoGambling(BaseGambling):

        def scrape(self, start_date=None, end_date=None):
            driver = self.driver
            driver.get('https://www.igb.illinois.gov/VideoReports.aspx')
            self.download_files(driver, start_date=start_date, end_date=end_date)
            self.merge_files(start_date, end_date)
        
        
        def merge_files(self, start_date, end_date):
            
            files = self.get_data_files()
            frames = [pd.read_csv(os.path.join(self.data_dir, file)) for file in files]
            df = pd.concat(frames)
            columns = ['Establishment', 'License Number', 'Municipality',
            'VGT Count', 'Amount Played', 'Amount Won', 'Net Wager', 'Funds In',
            'Funds Out', 'Net Terminal Income', 'NTI Tax', 'State Share',
            'Municipality Share', 'date']
            df = df[columns]

            for file in files:
                os.remove(os.path.join(self.data_dir, file))
            date_range = f'{self.start_date.strftime("%x")}_{self.end_date.strftime("%x")}'.replace('/', '-')
            df.to_csv(os.path.join(self.data_dir, f'vg_gambling_{date_range}.csv'), index=False)
            print('Complete!')
      
    
