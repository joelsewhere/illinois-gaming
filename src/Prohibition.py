from .BaseGambling import BaseGambling

class Prohibition(BaseGambling):
    
    def collect_data(self):
        self.driver.get('https://www.igb.illinois.gov/VideoProhibit.aspx')
        self.driver.find_element_by_link_text('Export to CSV').click()
        print('Complete!')
