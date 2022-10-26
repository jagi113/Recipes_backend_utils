# Import libraries
from psycopg import Error
from modules.scrapeModules import getRecipe

import time


# Read database - PostgreSQL


def writing_query(values):
    try:
        cur = conn.cursor()
        cur.executemany("""
            INSERT INTO recipes (name, url, photo) 
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            """, (values))
        conn.commit()
    except Error as e:
        print(f"The error {e} occurred")


recipe_page_number = 1722


def getRecipes(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for i in range(recipe_page_number):
                recipes = []
                page_recipes = getRecipe(i)
                for recipe in page_recipes:
                    recipes.append(
                        [recipe["name"], recipe["url"], recipe["photo"]])
                writing_query(recipes)
                print(f"Page {i} scraped.")
                time.sleep(10)
    conn.close()
