import requests
from bs4 import BeautifulSoup
import shutil

# download hero images from sota2 site
site = "https://www.dota2.com/heroes/"
result = requests.get(site)

# if successful parse the download into a BeautifulSoup object, which allows easy manipulation 
if result.status_code == 200:
    soup = BeautifulSoup(result.content, "html.parser")

    hero_images = soup.find_all('a', class_='heroPickerIconLink')

    for hero_image in hero_images:
        image = hero_image.findChildren("img", class_='heroHoverLarge')
        response = requests.get(image[0]['src'], stream=True)
        response.raw.decode_content = True

        file = open("C://Users//Jepoy//ActiveProjects//dota2_heroes//images//{}.jpg".format(image[0]['id'].replace('hover_', '')), 'wb')
        shutil.copyfileobj(response.raw, file)
        file.close()
