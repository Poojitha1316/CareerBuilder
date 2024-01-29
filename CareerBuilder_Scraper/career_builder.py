# %%
import pandas as pd 
import numpy as np 
import warnings
warnings.filterwarnings('ignore')
from bs4 import BeautifulSoup
import time
import requests
from datetime import datetime, timedelta
from config import Config
import re
import random

# %%
user_agent_list = Config.user_agent_list
user_agent = random.choice(user_agent_list)
headers = {'User-Agent': user_agent,}
proxy = Config.PROXY
proxies = {"http": proxy, "https": proxy}

# %%

def categorize_work_type(title):
    if 'Onsite' in title:
        return 'On-site'
    elif 'Hybrid' in title:
        return 'Hybrid'
    elif 'Remote' in title:
        return 'Remote'
    else:
        return None  # or whatever default value you want

def convert_relative_dates(relative_date):
    try:
        if 'today' in relative_date or 'Today' in relative_date:
            return datetime.now().date()
        elif 'yesterday' in relative_date or '1 day ago' in relative_date:
            return (datetime.now() - timedelta(days=1)).date()
        elif 'days ago' in relative_date:
            days_ago = int(relative_date.split()[0])
            return (datetime.now() - timedelta(days=days_ago)).date()
        else:
            return None  # Handle other cases as needed
    except Exception as e:
        print(f"Error in convert_relative_dates: {e}")
        return None


def get_data(soup):
    try:
        a = soup.find_all('div', class_='collapsed-activated')
        all_inner_dfs = []

        for i in a:
            b = BeautifulSoup(str(i), 'html.parser')
            c = b.find_all('li', class_='data-results-content-parent relative bg-shadow')

            all_innermost_dfs = []

            for j in c:
                inner_job_listings = []
                d = BeautifulSoup(str(j), 'html.parser')
                job_data = {}
                
                try:
                    # Extracting data
                    job_data['publish_time'] = d.find('div', class_='data-results-publish-time').text.strip()
                    job_data['title'] = d.find('div', class_='data-results-title').text.strip()
                    job_data['company'] = d.find('div', class_='data-details').find('span').text.strip()
                    job_data['location'] = d.find('div', class_='data-details').find_all('span')[1].text.strip()
                    job_data['employment_type'] = d.find('div', class_='data-details').find_all('span')[2].text.strip()
                    job_url = j.find('a', class_='data-results-content')['href']
                    job_data['url'] = f"https://www.careerbuilder.com{job_url}"
                    result = d.select('div.block:not(.show-mobile)')
                    job_data['result'] = result[0].get_text(strip=True)
                    
                    inner_job_listings.append(job_data)
                    df = pd.DataFrame(inner_job_listings)
                    all_innermost_dfs.append(df)

                except Exception as e:
                    print(f"Error in inner loop: {e}")
                    continue  # Skip this iteration if there's an error

            try:
                df2 = pd.concat(all_innermost_dfs, ignore_index=True)
                all_inner_dfs.append(df2)
            except Exception as e:
                print(f"Error in outer loop: {e}")
                continue  # Skip this iteration if there's an error

        final_df = pd.concat(all_inner_dfs, ignore_index=True)
        final_df['Work Location'] = final_df['location'].apply(categorize_work_type)
        final_df['Date Posted'] = final_df['publish_time'].apply(convert_relative_dates)
        # Add a new column with today's date
        final_df['Current Date'] = datetime.now().date()
        columns_mapping = {
            'title': 'Title',
            'company': 'Company',
            'location': 'Location',
            'employment_type': 'Job_type',
            'url': 'Job_url',
            'result':'Salary'
        }
        final_df.rename(columns=columns_mapping, inplace=True)

        try:
            # Extract job IDs and create a new column
            final_df['Job_id'] = final_df['Job_url'].str.extract(r'/job/(.*)')
        except AttributeError:
            # Handle the case where the regular expression doesn't match (e.g., if 'Job_url' is not a string)
            final_df['Job_id'] = None

        final_df.drop(columns=['publish_time'], inplace=True)
        return final_df

    except Exception as e:
        print(f"Error in first try block: {e}")
        # Handle the first type of data here if there's an error

        # Additional except block for unexpected errors
        try:
            c = soup.find_all('li', class_='data-results-content-parent relative bg-shadow')

            all_innermost_dfs = []

            for j in c:
                inner_job_listings = []
                d = BeautifulSoup(str(j), 'html.parser')
                job_data = {}
                
                try:
                    # Extracting data
                    job_data['publish_time'] = d.find('div', class_='data-results-publish-time').text.strip()
                    job_data['title'] = d.find('div', class_='data-results-title').text.strip()
                    job_data['company'] = d.find('div', class_='data-details').find('span').text.strip()
                    job_data['location'] = d.find('div', class_='data-details').find_all('span')[1].text.strip()
                    job_data['employment_type'] = d.find('div', class_='data-details').find_all('span')[2].text.strip()
                    # 
                    result = d.select('div.block:not(.show-mobile)')
                    job_data['result'] = result[0].get_text(strip=True)
                    job_url = j.find('a', class_='data-results-content')['href']
                    job_data['url'] = f"https://www.careerbuilder.com{job_url}"
                    
                    inner_job_listings.append(job_data)
                    df = pd.DataFrame(inner_job_listings)
                    all_innermost_dfs.append(df)

                except Exception as e:
                    print(f"Error in inner loop: {e}")
                    continue  # Skip this iteration if there's an error

            try:
                df2 = pd.concat(all_innermost_dfs, ignore_index=True)
                final_df=df2
            except Exception as e:
                print(f"Error in outer loop: {e}")
                pass  # Skip this iteration if there's an error
            # final_df = pd.concat(all_inner_dfs, ignore_index=True)
            final_df['Work Location'] = final_df['location'].apply(categorize_work_type)
            final_df['Date Posted'] = final_df['publish_time'].apply(convert_relative_dates)
            # Add a new column with today's date
            final_df['Current Date'] = datetime.now().date()
            columns_mapping = {
                'title': 'Title',
                'company': 'Company',
                'location': 'Location',
                'employment_type': 'Job_type',
                'url': 'Job_url',
                'result':'Salary'
            }
            final_df.rename(columns=columns_mapping, inplace=True)

            try:
                # Extract job IDs and create a new column
                final_df['Job_id'] = final_df['Job_url'].str.extract(r'/job/(.*)')
            except AttributeError:
                # Handle the case where the regular expression doesn't match (e.g., if 'Job_url' is not a string)
                final_df['Job_id'] = None

            final_df.drop(columns=['publish_time'], inplace=True)
            return final_df

        except Exception as e:
            print(f"Error in second try block: {e}")
            return None


# %%
# output = Config.output_csv.format(keyword=Config.keyword)
config = Config()
proxy = config.PROXY
url_template = config.URL_TEMPLATE
output_filename_template = config.OUTPUT_FILENAME_TEMPLATE
keyword = config.KEYWORD
all_outer_dfs = []

# Use Config class attributes for proxy, url_template, and user_agent_list
for i in range(1, 10):
    url = url_template.format(keyword=keyword, page=i)
    user_agent = random.choice(Config.user_agent_list)
    proxy = Config.PROXY
    proxies = {"http": proxy, "https": proxy}
    headers = {'User-Agent': user_agent,}

    try:
        response = requests.get(url, headers=headers, proxies=proxies, verify=False)
        response.raise_for_status()
        print('Success!')

        soup = BeautifulSoup(response.content, 'html.parser')
        df1 = get_data(soup)

        if df1 is not None:
            all_outer_dfs.append(df1)
            print('Success for page: ' + str(i))
        else:
            print('Sorry, no data found. Either you entered the keyword wrong or connection aborted.')

    except requests.RequestException as e:
        print(f"Error: {e}")
        print(f"Sorry, the website blocked your connection or there was another error. Status Code: {response.status_code}")

# %%
final_df = pd.concat(all_outer_dfs, ignore_index=True)
final_df = final_df[final_df['Job Type'] != 'Full-time']
final_df.drop_duplicates(inplace=True)

# %%
final_df.to_csv(Config.OUTPUT_FILENAME_TEMPLATE, index=False)
