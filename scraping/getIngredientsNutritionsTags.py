# Import libraries

from psycopg import Error
from modules.scrapeModules import scrapeRecipeIngredients, scrapeIngredientWebsite, scrapeIngredientNutritions, getTags
import time

import requests
from bs4 import BeautifulSoup

# Read database - PostgreSQL
from psycopg_pool import ConnectionPool
import psycopg
from database_config.config import config

params = psycopg.conninfo.make_conninfo(conninfo=config("database.ini"))
pool = ConnectionPool(params)


def writing_tag_query(conn, cur, values):
    try:
        cur.executemany("""
            INSERT INTO tags (recipe_id, tag) 
            VALUES (%s, %s) 
            ON CONFLICT DO NOTHING
            """, (values))
        conn.commit()
        print(f'Recipe tags for recipe {values[0]} successfully written')
        time.sleep(3)
    except Error as e:
        print(f"The error '{e}' occurred")


def writing_ingredients_query(conn, cur, values):
    try:
        cur.execute("""
            INSERT INTO recipe_ingredients (recipe_id, preparation_group, ingredient_id, amount, unit) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT DO NOTHING
            RETURNING id
            """, (values))
        id = cur.fetchone()
        conn.commit()
        if id:
            print(
                f'Ingredient {values[2]} for recipe {values[0]} successfully written.')
        else:
            print(
                f'!!!!!!!!!!!!!!!!!!!!!Ingredient {values[2]} for recipe {values[0]} WAS NOT written.!!!!!!!!!!!!!!!!!!!!!')
        time.sleep(7)
    except Error as e:
        print(f"The error '{e}' occurred")


def writing_nutritions_query(conn, cur, values):
    try:
        cur.execute("""
            INSERT INTO ingredient_nutritions (url, name, kcal, protein, protein_unit, carbohydrate, carbohydrate_unit, sugar, sugar_unit, fats, fats_unit, saturated_fatty_acids, saturated_fatty_acids_unit, transfatty_acids, transfatty_acids_unit, monounsaturated_fats, monounsaturated_fats_unit, polyunsaturated_fats, polyunsaturated_fats_unit, cholesterol, cholesterol_unit, fiber, fiber_unit, salt, salt_unit, water, water_unit, calcium, calcium_unit, PHE, PHE_unit) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT DO NOTHING
            RETURNING id;
            """, (values))
        id = cur.fetchone()
        conn.commit()
        print(f'Ingredient {values[1]} with nutritions successfully written.')
        time.sleep(3)
    except Error as e:
        print(f"The error '{e}' occurred")
    return id


def getIngredientsNutritionsTags(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # EXECUTE THE SQL QUERY
            cur.execute(
                'SELECT COUNT(*) FROM recipes WHERE id NOT IN (SELECT DISTINCT recipe_id FROM recipe_ingredients);')
            num_of_recipes = cur.fetchone()[0]
            for i in range(num_of_recipes):
                print(f'Need to fetch ingredients for {num_of_recipes - i}')
                reading_query = 'SELECT id, url FROM recipes WHERE id NOT IN (SELECT DISTINCT recipe_id FROM recipe_ingredients)'
                cur.execute(reading_query)
                recipe_id, recipe_url = cur.fetchone()
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.422.0 Safari/534.1', 'Upgrade-Insecure-Requests': '1',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'it-IT,', 'Cookie': 'CONSENT=YES+cb.20210418-17-p0.it+FX+917; '}
                try:
                    page = requests.get(recipe_url, headers=headers)
                    print(recipe_url)
                    recipe_soup = BeautifulSoup(page.content, "html.parser")
                    # getting and writing tags
                    tags = getTags(recipe_soup)
                    recipe_tags = []
                    for tag in tags:
                        recipe_tags.append([recipe_id, tag])
                    writing_tag_query(conn, cur, recipe_tags)

                    # getting ingredients
                    ingredients = scrapeRecipeIngredients(recipe_soup)
                    for ingredient in ingredients:
                        print(ingredient)

                        # getting website for ingredient nutritions
                        ingredient_url = scrapeIngredientWebsite(
                            ingredient["ingredient_name"])
                        print(ingredient_url)

                        # checking ingredient in kaloricke tabulky
                        if not ingredient_url:
                            words_in_name = ingredient["ingredient_name"].split(
                            )
                            for word in words_in_name:
                                ingredient_url = scrapeIngredientWebsite(word)
                                if ingredient_url:
                                    break
                        if not ingredient_url:
                            continue

                        # Checking url in ingredient_nutritions not to scrape it in vain
                        try:
                            cur.execute("""SELECT id 
                                FROM ingredient_nutritions 
                                WHERE url = %s;""", [ingredient_url], binary=True
                                        )
                            ingredient_id = int(cur.fetchone()[0])
                            print(
                                f'Ingredient {ingredient_id} found in database.')
                        except TypeError:
                            # if ingredient nutrition record does not recognize, scrape and save it, and return its id
                            ingredient_nutritions = list(
                                scrapeIngredientNutritions(ingredient_url).values())
                            print(
                                f'Ingredient nutrition from {ingredient_url} scraped and being saved.')
                            ingredient_id = int(
                                writing_nutritions_query(conn, cur, ingredient_nutritions)[0])
                        print(f'Ingredient id is: {ingredient_id}')
                        # Saving recipe ingredient with amount
                        recipe_ingredient = [recipe_id, ingredient["group"],
                                             ingredient_id, ingredient["amount"], ingredient["amount_unit"]]
                        writing_ingredients_query(conn, cur, recipe_ingredient)
                        print(
                            "-------------------------------------------------------")
                    print(
                        f"Ingredients for recipe {recipe_id} successfully scraped and written.")
                    print("//////////////////////////////////////////////////////")
                except Error as e:
                    print(e)
                    break
    conn.close()
