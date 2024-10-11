import requests
from bs4 import BeautifulSoup
import re

import pandas as pd
import os

import aiohttp
import asyncio
import time

async def get_urls():
    # List of XML URLs to download
    urls = [
        "https://assets.immoweb.be/sitemap/classifieds-000.xml",
        "https://assets.immoweb.be/sitemap/classifieds-001.xml",
        "https://assets.immoweb.be/sitemap/classifieds-002.xml",
        "https://assets.immoweb.be/sitemap/classifieds-003.xml",
        "https://assets.immoweb.be/sitemap/classifieds-004.xml",
        "https://assets.immoweb.be/sitemap/classifieds-005.xml",
        "https://assets.immoweb.be/sitemap/classifieds-006.xml",
        "https://assets.immoweb.be/sitemap/classifieds-007.xml",
        "https://assets.immoweb.be/sitemap/classifieds-008.xml",
        "https://assets.immoweb.be/sitemap/classifieds-009.xml",
        "https://assets.immoweb.be/sitemap/classifieds-010.xml",
        "https://assets.immoweb.be/sitemap/classifieds-011.xml",
        "https://assets.immoweb.be/sitemap/classifieds-012.xml",
        "https://assets.immoweb.be/sitemap/classifieds-013.xml",
        "https://assets.immoweb.be/sitemap/classifieds-014.xml",
        "https://assets.immoweb.be/sitemap/classifieds-015.xml",
        "https://assets.immoweb.be/sitemap/classifieds-016.xml",
        "https://assets.immoweb.be/sitemap/classifieds-017.xml",
        "https://assets.immoweb.be/sitemap/classifieds-018.xml",
        "https://assets.immoweb.be/sitemap/classifieds-019.xml",
        "https://assets.immoweb.be/sitemap/classifieds-020.xml",
        "https://assets.immoweb.be/sitemap/classifieds-021.xml",
        "https://assets.immoweb.be/sitemap/classifieds-022.xml",
        "https://assets.immoweb.be/sitemap/classifieds-023.xml",
        "https://assets.immoweb.be/sitemap/classifieds-024.xml",
        "https://assets.immoweb.be/sitemap/classifieds-025.xml",
        "https://assets.immoweb.be/sitemap/classifieds-026.xml",
        "https://assets.immoweb.be/sitemap/classifieds-027.xml",
        "https://assets.immoweb.be/sitemap/classifieds-028.xml",
        "https://assets.immoweb.be/sitemap/classifieds-029.xml",
        "https://assets.immoweb.be/sitemap/cms-000.xml",
        "https://assets.immoweb.be/sitemap/customers-000.xml",
        "https://assets.immoweb.be/sitemap/static-000.xml",
        "https://assets.immoweb.be/sitemap/static-001.xml",
        "https://assets.immoweb.be/sitemap/static-002.xml",
        "https://assets.immoweb.be/sitemap/static-003.xml",
        "https://assets.immoweb.be/sitemap/static-004.xml",
    ]

    # Directory to save XML files
    os.makedirs('xml_files', exist_ok=True)
    
    all_urls = []
 
    # Download and parse each XML file
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            file_path = os.path.join('xml_files', url.split('/')[-1])
    
            # Save the XML file
            with open(file_path, 'wb') as file:
                file.write(response.content)
    
            # Parse the XML file
            soup = BeautifulSoup(response.content, 'xml')
    
            # Extract URLs (adjust the tag name based on the XML structure)
            loc_tags = soup.find_all('loc')
            for loc in loc_tags:
                all_urls.append(loc.text)
    
        except Exception as e:
            print(f"Error downloading or parsing {url}: {e}")
    
    # Create a DataFrame and save to CSV
    df = pd.DataFrame(all_urls, columns=['url'])
    df.to_csv('xml_files/extracted_urls.csv', index=False)

    ###Filtered the extracted_urls.csv to extract only appartments and houses for sale using the URL"
    ## (You can choose your preference, for example to extract the english content.)
    
    # Read the CSV file
    df = pd.read_csv('xml_files/extracted_urls.csv')
    
    huis_pattern = 'https://www.immoweb.be/nl/zoekertje/huis/te-koop/'
    appartement_pattern = 'https://www.immoweb.be/nl/zoekertje/appartement/te-koop/'
    
    filtered_urls = df[df['url'].str.startswith(huis_pattern) | df['url'].str.startswith(appartement_pattern)]
    
    # Output the matching URLs
    print(filtered_urls)
    
    filtered_urls.to_csv('data/filterd_urls.csv', index=False)

async def get_properties(session,url,sem):
    
    async with sem:
        
             # block for a moment
            await asyncio.sleep(1)
            r = await fetch(session, url)
            if not r:
                return None
            soup = BeautifulSoup(r, 'html.parser')

            #execlude life
            try:
                is_life_annuity_sale = soup.find('th', string='Aantal lijfrentetrekkers').find_next_sibling('td').contents[0].strip()
                if int(is_life_annuity_sale )> 0:
                    return None
            except:
                is_life_annuity_sale = 0
            
            building_properties = {}
            building_properties['url'] = url

            #property_id
            try:
                for elem in soup.find_all("div", attrs={"class":"classified__header--immoweb-code"}):
                    property_id_info = elem.text.split(':')
                    property_id = property_id_info[1].strip()
                    break
            except:
                property_id = None
            building_properties["property_id"] = property_id
            
            #num_of_rooms
            try:
                num_of_rooms = soup.find('th', string='Slaapkamers').find_next_sibling('td').contents[0].strip()
            except:
                num_of_rooms = None
            building_properties["num_of_rooms"] = num_of_rooms
            
            #postal_code,Locality_name
            try:
                Locality_name =  url.split("/")[-3]
                postal_code =  url.split("/")[-2]       
            except:
                Locality_name =  None
                postal_code = None
            building_properties["Locality_name"] = Locality_name
            building_properties["postal_code"] = postal_code
        
            #price
            try:
                info = soup.find_all("div", {'class': 'grid__item desktop--9'})
                price = info[0].find("p", {'class': 'classified__price'}).find_all('span', {'class':'sr-only'})[0].text.strip()
            except:
                price = None
            if price == "€" : price = None 
            building_properties["price"] = price

            #property_type, sub_propert_type
            try:
                property_type_info = info[0].find("h1",{'class':'classified__title'}).text.strip().split(" ")
                if len(property_type_info) >= 4 : 
                    #real estate
                    property_type = property_type_info[0].strip() + " " + property_type_info[1].strip()    
                else: 
                    property_type = property_type_info[0].strip()

                #Check if building is sub type from appartement or huis lists and update sub type propert
                #Update these lists laterwith other sub types
                sub_type_house = ['Bungalow','Chalet','Uitzonderlijk vastgoed',
                                'Appartementsblok', 'Villa','Manoir']
                sub_type_appart = ['Studio','Triplex','Duplex', 'Benedenverdieping','Serviceflat']       
                if property_type.strip() in sub_type_house:        
                    sub_property_type = property_type
                    property_type = 'Huis'           
                elif property_type.strip() in sub_type_appart:
                    sub_property_type = property_type
                    property_type = 'Appartement'
                else:
                    sub_property_type = None
            except:
                property_type = None 
                sub_property_type = None
            building_properties["property_type"] = property_type
            building_properties["sub_property_type"] = sub_property_type
            
            #Type_sale
            try:
                biddit_link = soup.find('th', string='Plaats van de verkoop').find_next_sibling('td').contents[0].strip()
                type_sale = f'Public {biddit_link}'
            except AttributeError:
                type_sale = 'Non public'
            except:      
                type_sale = None
            building_properties['type_sale'] = type_sale
            

            #Living area
            abbreviation_span_meter =  'm²'
            try :
                living_area = soup.find('th',   string=re.compile(r'\sBewoonbare oppervlakte\s')).find_next_sibling('td').contents[0].strip() 
                living_area = f"{living_area} {abbreviation_span_meter}"
            except :
                living_area = None
            #print(f'living_area: {living_area}')
            building_properties["living_area"] = living_area
        
            #Kitchen type
            try :
                kitchen_type = soup.find('th', string='Type keuken').find_next_sibling('td').contents[0].strip()
            except:
                kitchen_type = None
            #print(f'Kitchen Type: {kitchen_type}')
            building_properties["kitchen_type"] = kitchen_type
            
            #Furnished
            try :
                furnished = soup.find('th', string='Gemeubeld').find_next_sibling('td').contents[0].strip()
                if furnished == 'Ja':
                    furnished = 1
                else :
                    furnished = 0
            except AttributeError :
                furnished = 0
            except:
                furnished = None
            building_properties["Furnished"] = furnished
        
            #open fire
            try:
                open_fire = soup.find('th', string='Aantal open haarden').find_next_sibling('td').contents[0].strip()
            except AttributeError :
                open_fire =0
            except:
                open_fire = None
            finally :
                #print(f'Open Fire: {open_fire}') 
                building_properties["Open_fire"] = open_fire

            #Terrace   
            try :
                terrace = soup.find('th', string=re.compile(r'.*\bterras\b$|^Terras$')).find_next_sibling('td').contents[0].strip()
                if terrace != 'Ja':
                    terrace = f"{terrace} {abbreviation_span_meter}"
            except :
                terrace = None
            finally :
                #print(f'terrace: {terrace}')    
                building_properties["Terrace"] = terrace
        
            #Garden
            try :
                garden = soup.find('th', string='Oppervlakte tuin').find_next_sibling('td').contents[0].strip()
                garden = f"{garden} {abbreviation_span_meter}"
            except :
                garden = None
            finally :
                #print(f'garden: {garden}') 
                building_properties["Garden"] = garden
            
            #Facades
            try :
                Number_of_faceds = soup.find('th', string=re.compile(r'\sAantal gevels\s')).find_next_sibling('td').contents[0].strip()
            except :
                Number_of_faceds = None
            finally :
                #print(f'Number of faceds: {Number_of_faceds}')
                building_properties["Number_of_faceds"] = Number_of_faceds
        
            #swimming pool
            try :
                Swimming_pool = soup.find('th', string=re.compile(r'\sZwembad\s')).find_next_sibling('td').contents[0].strip()
                if Swimming_pool== 'Ja':
                    Swimming_pool = 1
                else:
                    Swimming_pool = 0
            except :
                Swimming_pool = None
            finally :
                #print(f'Swimming pool: {Swimming_pool}')
                building_properties["Swimming_pool"] = Swimming_pool
            
            #State of building
            try :
                state_of_building = soup.find('th', string=re.compile(r'\sStaat van het gebouw\s')).find_next_sibling('td').contents[0].strip()
            except:
                state_of_building = None
            #print(f'State of building: {state_of_building}')
            building_properties["State_of_building"] = state_of_building
        
            return building_properties
      
def save_proprties(list_building_properties):
    # Create a DataFrame and save to CSV
    print(list_building_properties)
    df = pd.DataFrame(list_building_properties)
    df.to_csv('data/final_properties.csv', index=False, encoding='utf-8-sig')

async def fetch(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }
    try:
        async with session.get(url, headers = headers) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    
async def main():

    #This method is called once, to get urls from site maps
    #url saved to data/filterd_urls.csv'
    #await get_urls()

    # time Tracking: Start Time
    start_time = time.time()

    #Loop in url from filterd_urls.csv 
    df = pd.read_csv('data/filterd_urls.csv')
    df_slice = df.iloc[:12000]

    # create an AIOHTTP session
    async with aiohttp.ClientSession() as session:
        # initialize tasks list
        tasks = []  
        sem = asyncio.Semaphore(50)
        # group and Execute tasks concurrently 
        for immo_url in df_slice['url']:
            tasks.append(get_properties(session, immo_url, sem))
            print(immo_url)
        building_properties = await asyncio.gather(*tasks)
        building_properties = [p for p in building_properties if p is not None]
        save_proprties(building_properties)  
        """for properties in building_properties:
            if building_properties is not None : list_building_properties.append(properties)"""  

               
    # time Tracking: End Time
    end_time = time.time() 
    # calculating and printing the time taken
    print(f"Time taken: {(end_time - start_time)/60} minutes")
    
asyncio.run(main())  
