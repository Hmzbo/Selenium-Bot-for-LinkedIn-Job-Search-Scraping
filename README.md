# Selenium-Bot-for-LinkedIn-Job-Search-Scraping

A selenium bot to scrape LinkedIn for job search results.\
The bot uses chrome driver to perform the scraping process, other web browsers will be added in upcoming versions.

This bot does not require logins credintials, it performs job search on the url: `https://www.linkedin.com/jobs`, and that's to avoid breaking the terms of service of LinkedIn which does not allow automatic collect data from the platform.

## Usage
First, you need to install the required python dependencies. You can use the following command line:\
`pip install -r requirements.txt`

To use the bot, you simply need to specify the `job_title`, the `location`, and `max_pages`(optional). For example:\
`python LinkedIn_bot.py --job-title "Machine Learning" --location "Tunisia" --max-pages 40`
