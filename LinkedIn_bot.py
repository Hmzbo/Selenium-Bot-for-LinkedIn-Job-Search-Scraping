from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

import time
import datetime
import logging
import random
import argparse
import pandas as pd
from tqdm import tqdm


class LinkedIn_bot:
    def __init__(self):
        log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_fmt)
        chromedriver_autoinstaller.install()
        logging.info("Starting driver")
        self.driver = webdriver.Chrome()
        logging.info("Initialization successful")
        logging.warning("This automated scraper uses few seconds of random waits throughout\
                         the whole process to mimic human behaviour!")


    def random_wait(self, a=4, b=6):
        '''Wait a randion amount of time'''
        if type(a)==int:
            delay = random.randint(a,b)
        else:
            delay = random.uniform(a,b)
        time.sleep(delay)

    def search_jobs(self, job_title='', location='United States'):
        '''Enter tags and search'''

        cleared = [False, False]
        clear_input = self.driver.find_elements(by=By.XPATH, value='//button[@data-tracking-control-name="homepage-jobseeker_dismissable-input-clear"]')
        try:
            clear_input[0].click()
            cleared[0]=True
        except:
            pass
        try:
            clear_input[1].click()
            cleared[1]=True
        except:
            pass

        search_job_name_input = self.driver.find_element(by=By.XPATH, value='//input[@id="job-search-bar-keywords"]')
        search_job_name_input.send_keys(Keys.CONTROL + "a")
        search_job_name_input.send_keys(Keys.DELETE)
        search_job_name_input.send_keys(job_title)

        search_job_location_input = self.driver.find_element(by=By.XPATH, value='//input[@id="job-search-bar-location"]')
        search_job_location_input.send_keys(Keys.CONTROL + "a")
        search_job_location_input.send_keys(Keys.DELETE)
        search_job_location_input.send_keys(location)

        search_job_location_input = self.driver.find_element(by=By.XPATH, value='//button[@data-tracking-control-name="public_jobs_jobs-search-bar_base-search-bar-search-submit"]')
        search_job_location_input.click()
        logging.info(f"Search for '{job_title}' in '{location}' successful")
    

    def load_all_results(self, max_page):
        '''Scroll through the whole page to load all the job search results'''

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        scroll = True
        scroll_page=1

        while scroll:
            height = self.driver.execute_script("return document.body.scrollHeight")
            current_cursor_height = self.driver.execute_script("return window.scrollY")
            page_length = height - current_cursor_height
            
            for i in tqdm(range(int(current_cursor_height), int(height), 5), desc=f"Scrolling page {scroll_page}"):
                if i < current_cursor_height+page_length*0.05 or i > current_cursor_height+page_length*0.80:
                    self.random_wait(a=0.02, b=0.2)
                self.driver.execute_script(f"window.scrollTo(0, {i});")

            
            self.random_wait()

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height==height:
                try:
                    load_more = self.driver.find_element(by=By.XPATH, value='//button[contains(., "See more jobs")]')
                    self.driver.execute_script("arguments[0].scrollIntoView();", load_more)
                    load_more.send_keys("\n")
                    self.random_wait()
                    logging.info("Loading More results button clicked!")
                except Exception as e:
                    logging.info(f"{e}")
                    pass
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            logging.info(f"{new_height}, {last_height}, {scroll_page}")
            if new_height == last_height or scroll_page==max_page:
                scroll = False

            scroll_page+=1
            last_height = new_height
            self.random_wait()
        logging.info("Successfully loaded all search results.")
    
    def time_ago_to_month_year(self, time_ago):
        '''Calculate the job posting month'''
        dic_to_days={'minute':0, 'hour':0, 'day':1, 'week':7, 'month': 30, 'year':365}
        p = list(time_ago.split('ago')[0].strip())
        if p[-1]=='s':
            p[-1]=''
        p = ''.join(p).split(' ')
        delta_days = int(p[0])*dic_to_days[p[1]]

        today = datetime.date.today()
        date = today - datetime.timedelta(days=delta_days)
        job_post_month = date.strftime("%B")
        job_post_year = date.strftime("%Y")
        return job_post_month, job_post_year
    
    def close_session(self):
        '''This function closes the current session'''
        logging.info("Closing session")
        self.driver.close()
    
    def run(self, job_title, location, max_pages=40):
        '''Running the bot to extract all the job search results data'''
        self.results_dic = {'Position':[], 'Company_Name':[], 'Location':[], 'Post_Month':[], 'Post_Year':[], 'Details':[]}
        website = 'https://www.linkedin.com/jobs/search?position=1&pageNum=0'
        self.driver.get(website)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1280, 720)

        self.search_jobs(job_title, location)
        self.load_all_results(max_pages)

        list_items = self.driver.find_element(by=By.CLASS_NAME, value="jobs-search__results-list")
        jobs_list = list_items.find_elements(by=By.TAG_NAME, value="li")
        nbr_jobs = len(jobs_list)
        logging.info(f"{nbr_jobs} jobs found")

        skipped = 0
        for job in tqdm(jobs_list, desc="Extracting Job Offers Details"):
            self.driver.execute_script("arguments[0].scrollIntoView();", job)
            job.click()
            self.random_wait()
            show_more = self.driver.find_element(by=By.CLASS_NAME, value="show-more-less-html__button")
            self.driver.implicitly_wait(2)
            try:
                show_more.click()
            except:
                continue
            self.random_wait()

            [position, position, company, location, *remaining] = job.text.split('\n')
            try:
                time_ago = time_ago = self.driver.find_element(by=By.XPATH, value="//span[@class='posted-time-ago__text topcard__flavor--metadata']").text
            except:
                try:
                    time_ago = remaining[-1]
                except:
                    time_ago = "10 years ago"
                    pass
                pass

            
            try:
                details = self.driver.find_element(by=By.XPATH, value="//div[@class='show-more-less-html__markup relative overflow-hidden']").text
            except:
                details = ''
                skipped += 1
                continue
            job_post_month, job_post_year = self.time_ago_to_month_year(time_ago)

            self.results_dic['Position'].append(position)
            self.results_dic['Company_Name'].append(company)
            self.results_dic['Location'].append(location)
            self.results_dic['Post_Month'].append(job_post_month)
            self.results_dic['Post_Year'].append(job_post_year)
            self.results_dic['Details'].append(details)
        
        logging.info("Done scraping.")
        self.close_session()

        return self.results_dic
    

def parse_args():
    parser = argparse.ArgumentParser(description='LinkedIn Bot job search')
    parser.add_argument('--job-title', metavar='Job_title', default='Data Analyst', type=str,
                        help='Enter a valid job title, e.g. Data Analyst.')
    parser.add_argument('--location', metavar='Location', default='Tunisia', type=str,
                        help='Enter the location "Country" or "City, Country" where to search for job offers.')
    parser.add_argument('--max-pages', metavar='Maximum_pages', default=40, type=int,
                        help='Enter the maximum number of pages to load.')
    args = parser.parse_args()
    return args

def generate_file_name(job_title, location, max_pages=40):
    today = datetime.date.today().strftime("%d/%m/%Y").replace('/','-')
    name=f'results_{job_title}_{location}_{max_pages}pages_{today}'
    return name

if __name__ == "__main__":
    args = parse_args()
    bot = LinkedIn_bot()
    results_dic = bot.run(**vars(args))
    results_df = pd.DataFrame(results_dic)
    file_name = generate_file_name(**vars(args))
    results_df.to_csv(f'./{file_name}.csv',index=False)