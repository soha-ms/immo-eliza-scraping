# immo-eliza-scraping

## 🏢 Description

This project is an asynchronous web scraper designed to extract property data from the **Immo-ELiza** real estate website [(`(https://www.immoweb.be/nl)`)](https://www.immoweb.be/nl). The goal is to scrape property listings and details like titles, prices, descriptions, and other relevant information, then store the data in a CSV file for further analysis or processing.

The project is built using Python with `aiohttp` for asynchronous HTTP requests, `pandas` for CSV file manipulation, and `BeautifulSoup` for parsing HTML.

## Features

- Efficient asynchronous web scraping with `aiohttp`.
- Customizable data extraction using `BeautifulSoup`.
- Supports scraping large numbers of URLs concurrently.
- Saves scraped data to CSV for easy data analysis.

## Prerequisites

Before running the project, make sure you have the following tools and libraries installed:

- Required Python packages:
  - `aiohttp`
  - `pandas`
  - `beautifulsoup4`
  - `requests`
  - `lxml`

## 📦 Repo structure

```
.
├── src/
├── data
    ├── filterd_urls.csv
    ├── final_properties.csv
├── scraper
├── xml_files
    ├── extracted_urls.csv
├── .gitignore
├── venv
├── main.py
├── requirements.txt
└── README.md
```
## 🛎️ Usage

1. Clone the repository to your local machine.

2 .To run the script, you can execute the `main.py` file from your command line:

    ```
    python main.py
    ```

3.The script reads XMls root data the filters  to get Appartments / Houses for sales save the filterd data in CSV file 
the use this file to scarp the filtered URL to get data from each URL such ( id , price , type of sale , living area ,...etc) using asynco and finally stores this data set in CSV file . 

```python
async def get_urls():
    # List of XML URLs to download
    urls = ["https://assets.immoweb.be/sitemap/classifieds-000.xml", ......]
by the of the function  save in  filtered_urls.to_csv('data/filterd_urls.csv', index=False)

def save_proprties(list_building_properties): #save the extracted data in csv file
            df.to_csv('data/final_properties.csv', index=False, encoding='utf-8-sig')

async def fetch(session, url): #Called from get_properties() to complete asyncio functionality
            async with session.get(url, headers = headers) as response:

async def main():
#create an AIOHTTP session
    async with aiohttp.ClientSession() as session:
        # initialize tasks list
        tasks = []
#group and Execute tasks concurrently
        for immo_url in df_slice['url']:
            # #get immo web pages properties by using BeautifulSoup
            tasks.append(get_properties(session, immo_url, sem)) 
save_proprties(building_properties) #save the extracted data in csv file


```
## ⏱️ Timeline

This project took 5 days for completion.

## 📌 Personal Situation
This project was done as part of the AI Boocamp at BeCode.org. 

Connect with me on [LinkedIn](https://www.linkedin.com/in/soha-mohamad-382b44219/).
