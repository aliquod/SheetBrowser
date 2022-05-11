# created on 5/9/22 at 13:59

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import json

path = '/Users/matthewan/Applications/chromedriver'
service = Service(path)
driver = webdriver.Chrome(service=service, options=webdriver.ChromeOptions())

years = ['Prelims', 'Part A', 'Part B', 'Part C']
terms = ['Michaelmas', 'Hilary', 'Trinity']

driver.get('https://courses.maths.ox.ac.uk/course/index.php?categoryid=9')
year_ids = []
year_names = []
for ele in driver.find_elements(by=By.TAG_NAME, value='option'):
    spele = ele.text.split(' / ')
    if not len(spele) == 3: continue
    if spele[0] == 'Undergraduate' and spele[1] in years and spele[2] in terms:
        year_ids.append(ele.get_attribute('value'))
        year_names.append(spele[1] + ' - ' + spele[2])
print(year_ids)

sheet_dict = {}
for id, year_id in enumerate(year_ids[2:3]):
    driver.get('https://courses.maths.ox.ac.uk/course/index.php?categoryid='+year_id)

    year_name = year_names[id]
    year_sheet_dict = {}

    course_links = [ele.get_attribute('href') for ele in driver.findGelements(by=By.CLASS_NAME, value='aalink')]
    sheet_id_regex = re.compile('(?<=sheet[ ])[0-9]', re.IGNORECASE)

    try:
        for course_link in course_links:
            driver.get(course_link)
            course_name = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, 'h1'))).text
            sheets_elements = driver.find_elements(by=By.CLASS_NAME, value='aalink')

            # build an id:sheet dictionary for each course
            sheets = {}
            for i in range(len(sheets_elements)):
                sheet_element = driver.find_elements(by=By.CLASS_NAME, value='aalink')[i]
                title = sheet_element.find_element(by=By.CLASS_NAME, value='instancename').text
                link = sheet_element.get_attribute('href')
                if not sheet_id_regex.search(title.lower()):
                    continue
                id = int(re.findall(sheet_id_regex, title.lower())[0])

                driver.get(link)

                # build dictionary of name:link of each file under a single sheet
                sheet_links = {}
                _ = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
                if '.pdf' in driver.current_url:
                    name = driver.current_url.split('/')[-1]
                    sheet_links[name] = driver.current_url
                else:
                    for file in driver.find_elements(by=By.CSS_SELECTOR, value='a[target=_blank]'):
                        link = file.get_attribute('href').split('?')[0]
                        name = file.text
                        if "https://courses.maths.ox.ac.uk" in link:
                            sheet_links[name] = link
                # sheet_links = [re.sub(sheet_forcedownload_regex,'0',ele.get_attribute('href')) for ele in driver.find_elements(by=By.CSS_SELECTOR, value='a[target=_blank]')]

                # add the dictionary of name:link to the id:sheet dict
                if not sheet_links == {}:
                    sheets[id] = sheet_links
                driver.back()
                _ = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'instancename')))
            year_sheet_dict[course_name] = sheets
    finally:
        pass
    sheet_dict[year_name] = year_sheet_dict
driver.quit()


print(json.dumps(sheet_dict, sort_keys=True, indent=4))
with open('/Users/matthewan/PycharmProjects/pystuffs/venv/sheet_links.json', 'w') as file:
    json.dump(sheet_dict, file)


## structure:
# [term=Prelims - Michaelmas]:
#   [class=1]:
#       [sheet id=1]:
#           [filename=a]: link
#           [filename=b]: link
#       [sheet id=2]:
#           [...]: ...
#   [class=2]:
#      [...]
# [term=...]:
#    [...]