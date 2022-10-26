import requests
from bs4 import BeautifulSoup


def getRecipe(page_num):
    URL = f'https://varecha.pravda.sk/recepty/{page_num}'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    recepty = soup.find_all("a", {"class": "card-a"})
    page_recepty = []
    for recept in recepty:
        name = recept["title"]
        try:
            if name.split()[-1] == "(fotorecept)" or name.split()[-1] == "(videorecept)":
                name = " ".join(recept["title"].split()[0: -1])
        except:
            name = recept["title"].strip()
        url = "https://varecha.pravda.sk"+recept["href"]
        photo = "https://varecha.pravda.sk"+recept["data-src"]
        page_recepty.append({"name": name, "url": url, "photo": photo})
    return page_recepty


def scrapeRecipeIngredients(recipe_soup):
    suroviny_col = recipe_soup.find(
        "div", {"class": "col suroviny col-12 col-xs-12 col-sm-4 pl-0 pr-0 pr-sm-3"})
    ingredient_group = "main"
    ingredients = []
    for tr in suroviny_col.find_all("tr"):
        if (tr.attrs["class"][0] == 'recipe-ingredients__row'):
            surovina_info = tr.find(
                "td", {"class": "recipe-ingredients__amount"}).text.replace("\xa0", " ").split()
            if len(surovina_info) >= 2:
                try:
                    surovina_amount = float(surovina_info[0])
                except:
                    if "-" in surovina_info[0]:
                        surovina_amount = (surovina_info[0].split("-"))[0]
                    else:
                        surovina_amount = None
                if surovina_info[1].lower() in ["g", "mg", "kg", "ks", "l", "ml", "dl", "pl", "čl", "bal", "bal."]:
                    surovina_unit = surovina_info[1].lower().replace(".", "")
            else:
                surovina_amount = None
                surovina_unit = None
            surovina = tr.find(
                "td", {"class": "recipe-ingredients__ingredient"}).text.strip()
            ingredients.append({"group": ingredient_group, "ingredient_name": surovina,
                               "amount": surovina_amount, "amount_unit": surovina_unit})
        elif tr.attrs["class"][0] == 'ingredients__group':
            ingredient_group = tr.find(
                "td", {"class": "recipe-ingredients__group"}).text.strip()
    return ingredients


def scrapeIngredientWebsite(ingredient):
    # passing cookie confirmation site
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.422.0 Safari/534.1', 'Upgrade-Insecure-Requests': '1',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'it-IT,', 'Cookie': 'CONSENT=YES+cb.20210418-17-p0.it+FX+917; '}
    googleurl = f'https://www.google.com/search?q={ingredient.replace(" ","+")}+kaloricke+tabulky'
    googlepage = requests.get(googleurl, headers=headers)
    googlesoup = BeautifulSoup(googlepage.text, "html.parser")
    ingredient_url = ""
    for url in googlesoup.find_all("a"):
        if "/url?q=https://www.kaloricketabulky.sk/potraviny/" in url.get('href'):
            ingredient_url = url.get('href')[7:]
            if "&sa=" in ingredient_url:
                ingredient_url = ingredient_url[:ingredient_url.index("&sa=")]
            break
    return ingredient_url


def scrapeIngredientNutritions(ingredientURL):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.422.0 Safari/534.1', 'Upgrade-Insecure-Requests': '1',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'it-IT,', 'Cookie': 'CONSENT=YES+cb.20210418-17-p0.it+FX+917; '}
    page = requests.get(ingredientURL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    ingredient_name = soup.find(
        "h1", {"class": "header2-font-lg"}).text.strip()
    ingredient_kcal = soup.find(
        "span", text=lambda t: t and "kcal" in t).string.split(" ")[0]
    ingredient_nutritions = {"ingredient_url": ingredientURL,
                             "ingredient_name": ingredient_name, "ingredient_kcal": float(ingredient_kcal)}
    nutritions = soup.find("tbody")
    for tr in nutritions.find_all("tr"):
        column, value = tr.find_all("td")
        column_name = column.get_text().strip()
        if column_name.lower() == "stav" or column_name == "GI Glykemický indexhelp":
            continue
        columns = ['Bielkoviny', 'Sacharidy', 'Cukry', 'Tuky', 'Nasýtené mastné kyseliny', 'Transmastné kyseliny',
                   'Mononenasýtené', 'Polonenasýtené', 'Cholesterol', 'Vláknina', 'Soľ', 'Voda', 'Vápnik', 'PHE']
        if column_name not in columns:
            continue
        value_cleared = value.get_text().strip()
        try:
            amount_str, unit = value_cleared.split(" ")
            amount = float(amount_str.replace(",", "."))
        except:
            amount = None
            unit = None
        ingredient_nutritions[f"{column_name}_value"] = amount
        ingredient_nutritions[f"{column_name}_unit"] = unit
        # check for all values
        keys = ['ingredient_url', 'ingredient_name', 'ingredient_kcal', 'Bielkoviny_value', 'Bielkoviny_unit', 'Sacharidy_value', 'Sacharidy_unit', 'Cukry_value', 'Cukry_unit', 'Tuky_value', 'Tuky_unit', 'Nasýtené mastné kyseliny_value', 'Nasýtené mastné kyseliny_unit', 'Transmastné kyseliny_value',
                'Transmastné kyseliny_unit', 'Mononenasýtené_value', 'Mononenasýtené_unit', 'Polonenasýtené_value', 'Polonenasýtené_unit', 'Cholesterol_value', 'Cholesterol_unit', 'Vláknina_value', 'Vláknina_unit', 'Soľ_value', 'Soľ_unit', 'Voda_value', 'Voda_unit', 'Vápnik_value', 'Vápnik_unit', 'PHE_value', 'PHE_unit']
        for key in keys:
            if key in ingredient_nutritions.keys():
                continue
            else:
                pos = keys.index(key)
                items = list(ingredient_nutritions.items())
                items.insert(pos, (key, None))
                ingredient_nutritions = dict(items)
    return ingredient_nutritions


def scrapeRecipeInstructions(recipe_soup):
    postup = recipe_soup.find("ol", {"class": "recipe-instructions"})
    instructions = []
    for step in postup.find_all("li", {"class": "recipe-instruction clearfix"}):
        step_num = step.find(
            "span", {"class": "recipe-instruction__number handwritten"}).text.strip()
        instruction = step.find("div", {
                                "class": "recipe-instruction__main"}).find("p").text.strip().replace('\r\n', ' ')
        try:
            image_url = f"https://varecha.pravda.sk{step.find('div', {'class':'recipe-instruction__main'}).find('img').get('data-src')}"
        except:
            image_url = None
        instructions.append(
            {"step": step_num, "instruction": instruction, "photo": image_url})
    return instructions


def getTags(recipe_soup):
    tag_col = recipe_soup.find("div", {"class": "recipe-in-tags"})
    tags = []
    for tag in tag_col.find_all("a", {"class": "color-varechalink"}):
        tags.append(tag.text)
    return tags


"""
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.422.0 Safari/534.1', 'Upgrade-Insecure-Requests': '1',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'it-IT,', 'Cookie': 'CONSENT=YES+cb.20210418-17-p0.it+FX+917; '}
recipe_url = "https://varecha.pravda.sk/recepty/mliecne-rozky-plnene-tvarohom-fotorecept/80749-recept.html"
page = requests.get(recipe_url, headers=headers)
recipe_soup = BeautifulSoup(page.content, "html.parser")
print(scrapeRecipeIngredients(recipe_soup))

instructions = scrapeRecipeInstructions(recipe_soup)
print(instructions)

print(scrapeIngredientNutritions(
    "https://www.kaloricketabulky.sk/potraviny/maslo"))

print(scrapeIngredientWebsite("šalát lollo rosso"))
"""
