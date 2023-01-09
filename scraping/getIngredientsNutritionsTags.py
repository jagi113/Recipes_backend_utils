# Import libraries

from psycopg import Error
from modules.scrapeModules import scrapeRecipeIngredients, scrapeIngredientWebsite, scrapeIngredientNutritions, getTags
from modules.generalModules import currentTime, writeError
import time

import requests
from bs4 import BeautifulSoup

# Read database - PostgreSQL
from psycopg_pool import ConnectionPool
import psycopg
from database_config.config import config

error_file = "errorslog_ingredients.json"

def writing_tag_query(conn, cur, values):
    try:
        ids = []
        recipe_id = values[0][0]
        for value in values:
            cur.execute("""
            INSERT INTO tags (recipe_id, tag) 
            VALUES (%s, %s) 
            ON CONFLICT DO NOTHING
            """, (value))
        id = cur.fetchone()
        if id:
            ids.append(int(id[0]))
        conn.commit()
        if len(ids) == len(values):
            message = f'At {currentTime()} - {len(ids)} tags for recipe {recipe_id} were successfully written.'
            print(message)
        else:
            error_message = f'At {currentTime()} - tags for recipe {recipe_id} already in database.'
            writeError(error_file, {recipe_id: error_message})
        time.sleep(5)
    except Error as e:
        error_message = f'At {currentTime()} - the database error "{e}" occurred.'
        writeError(error_file, {recipe_id: error_message})


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
            message = f'Ingredient {values[2]} for recipe {values[0]} successfully written.'
            print(message)
        else:
            error_message =  f'At {currentTime()} - ingredient {values[2]} for recipe {values[0]} WAS NOT written.'
            writeError(error_file, {values[0]: error_message})
        time.sleep(15)
    except Error as e:
        error_message = f'At {currentTime()} - the database error "{e}" occurred.'
        writeError(error_file, {recipe_id: error_message})


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
        if id:
            message = f'Ingredient {values[1]} with nutritions successfully written.'
            print(message)
        else:
            error_message =  f'At {currentTime()} - ingredient {values[1]} WAS NOT written due to duplicate.'
            writeError(error_file, {values[1]: error_message})
        time.sleep(3)
    except Error as e:
        error_message = f'At {currentTime()} - the database error "{e}" occurred.'
        writeError(error_file, {recipe_id: error_message})
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
                try:
                    # getting and writing tags
                    tags = getTags(recipe_url, error_file, recipe_id)
                    print(f'Recipe {recipe_id} has tags: {", ".join(tags)}')
                    recipe_tags = [(recipe_id, tag) for tag in tags]
                    writing_tag_query(conn, cur, recipe_tags)

                    # getting ingredients
                    ingredients = scrapeRecipeIngredients(recipe_url, error_file, recipe_id)
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


if __name__ == "__main__":
    params = psycopg.conninfo.make_conninfo(conninfo=config())
    pool = ConnectionPool(params)
    getIngredientsNutritionsTags(pool)
