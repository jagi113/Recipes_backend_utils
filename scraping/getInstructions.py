# Import libraries
from psycopg import Error
from modules.scrapeModules import scrapeRecipeInstructions
from modules.generalModules import currentTime, writeError
import time

import requests

# Read database - PostgreSQL
from psycopg_pool import ConnectionPool
import psycopg
from database_config.config import config

error_file = "errorslog_instructions.json"


def writing_query(conn, cur, values):
    try:
        ids = []
        recipe_id = values[0][0]
        for value in values:
            cur.execute("""
                INSERT INTO instructions (recipe_slug, step, instruction, photo) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT DO NOTHING
                RETURNING recipe_slug
                """, (value))
            id = cur.fetchone()
            if id:
                ids.append(id[0])
            conn.commit()
        if len(ids) == len(values):
            message = f'At {currentTime()} - {len(ids)} instructions for recipe {recipe_id} were successfully written.'
            print(message)
        else:
            error_message = f'At {currentTime()} - Instructions for recipe {recipe_id} already in database.'
            writeError(error_file, error_message)
    except Error as e:
        error_message = f'At {currentTime()} - while saving instructions for {values[0][0]} the database error "{e}" occurred.'
        writeError(error_file, error_message)


def getInstructions(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            sesh = requests.Session()
            # Getting number of recipes which need to scrape instructions
            cur.execute(
                'SELECT COUNT(*) FROM recipes WHERE slug NOT IN (SELECT DISTINCT recipe_slug FROM instructions);')
            num_of_recipes = cur.fetchone()[0]
            for i in range(num_of_recipes//10 + 1):
                print(
                    f'There is still {num_of_recipes - i*10} recipes that need to get instructions')
                # Getting ids and urls of 10 recipes from database to scrape instructions
                reading_query = f'SELECT slug, url FROM recipes WHERE slug NOT IN (SELECT DISTINCT recipe_slug FROM instructions) LIMIT 10 OFFSET {10*i}'
                cur.execute(reading_query)
                recipes = cur.fetchall()
                for recipe in recipes:
                    recipe_slug, recipe_url = recipe
                    try:
                        instructions = scrapeRecipeInstructions(recipe_url, error_file, recipe_slug)
                        instruction_block = [
                            (recipe_slug,
                            int(instruction["step"]),
                            instruction["instruction"],
                            instruction["photo"])
                            for instruction in instructions
                            ]
                        message = f"{len(instructions)} instructions for recipe {recipe_slug} successfully scraped."
                        print(message)
                    except:
                        continue
                    writing_query(conn, cur, instruction_block)
                    time.sleep(10)
    conn.close()


if __name__ == "__main__":
    params = psycopg.conninfo.make_conninfo(conninfo=config())
    pool = ConnectionPool(params)
    getInstructions(pool)
