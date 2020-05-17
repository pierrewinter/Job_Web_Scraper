"""
This module is used to scrape job listing information from an online job portal (here we look at Indeed).
The data is parsed, aggregated, and saved to a .csv file.
"""

__author__ = "Pierre Winter"

import requests
from bs4 import BeautifulSoup as bs
import re

#-----------------------------------------INPUT PARAMETERS-------------------------------------------------------------
# We want to find up to 500 job listings on Indeed for full-time data scientist positions within 50 miles of a city.

job_name = 'data+scientist'  # Use plus sign instead of spaces here.
job_type = 'fulltime'
search_radius = 50  # Radius in miles to search jobs from.
city_name = 'Los+Angeles'  # Use plus sign instead of spaces here.
state_name = 'CA'  # State abbreviation.
default_jobs_per_page = 50  # I set this to the maximum allowable, which is 50 for Indeed. This minimizes the number of individual HTTP URL calls needed.
max_page_number = 100  # Maximum number of pages (jobs) you would want in the .csv file.
delim = ';'  # Used to delimit entries in the .csv file. I don't use a comma because some companies have commas in their name.
#----------------------------------------------------------------------------------------------------------------------

job_listings_website = 'https://www.indeed.com/jobs?q='+job_name+'&l='+city_name+'%2C+'+state_name+'&radius='+str(search_radius)+'&jt='+job_type+'&limit='+str(default_jobs_per_page)
output_filename = job_name+'_jobs_indeed_'+city_name+'.csv'
output_column_names = 'Job Title' + delim + 'Company Name' + delim + 'Job City' + delim + 'Job Rating' + delim + 'Job Post Date\n'
f = open(output_filename, 'w')
f.write(output_column_names)

# loop over website pages
page_number = 0
while page_number < max_page_number:
    page_url = job_listings_website+'&start='+str(page_number)
    website_request = requests.get(url=page_url)
    website_html = website_request.text
    soup_on_page = bs(website_html, 'html.parser')
    main_container = soup_on_page.find(name='table', attrs={'role':'main'})
    jobs = main_container.table.find_all(name='div', attrs={'data-tn-component':'organicJob'})
    assert len(jobs) <= default_jobs_per_page

    # loop over jobs on a given page
    for job in jobs:
        # get job title
        try:
            job_title = job.find(name='div', attrs={'class':'title'}).text.strip()
        except AttributeError:
            job_title = job.find(attrs={'class':'title'}).text.strip()

        # get company name
        company_name = job.find(name='span', attrs={'class':'company'}).text.strip()

        # get job location
        job_location = job.find(name='span', attrs={'class':re.compile('location')}).text.strip()

        # get job city
        job_city = job_location.split(',')[0]

        # get job post date
        job_post_date = job.find(name='span', attrs={'class':'date'}).text.split()[0]

        # get job rating
        try:
            job_rating = job.find(name='div', attrs={'class':'sjcl'}).div.find(name='span', attrs={'class':'ratingsContent'}).text.strip()
        except AttributeError:
            job_rating = str(None)
        f.write(job_title + delim + company_name + delim + job_city + delim + job_rating + delim + job_post_date + '\n')

    # This stops the code if the website has fewer than 'max_page_number' jobs
    if len(jobs) < default_jobs_per_page:
        break
    else:
        page_number += default_jobs_per_page

f.close()

#TODO: figure out how to get skill info (not in html, maybe need to get from dynamic java)
#TODO: combine tableau map with a map average cost of living and/or average housing prices
#TODO: create GUI and database for automatic pipeline of job search
