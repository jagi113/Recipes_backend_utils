# Import libraries
from psycopg import Error
from modules.scrapeModules import getRecipe

import time


# Read database - PostgreSQL
from psycopg_pool import ConnectionPool
import psycopg
from database_config.config import config

params = psycopg.conninfo.make_conninfo(conninfo=config("database.ini"))
pool = ConnectionPool(params)


def writing_query(conn, cur, values):
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
                writing_query(conn, cur, recipes)
                print(f"Page {i} scraped.")
                time.sleep(10)
    conn.close()
