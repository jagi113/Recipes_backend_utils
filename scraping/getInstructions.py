# Import libraries
from psycopg import Error
from modules.scrapeModules import scrapeRecipeInstructions
import time

import requests
from bs4 import BeautifulSoup

# Read database - PostgreSQL
from psycopg_pool import ConnectionPool
import psycopg
from database_config.config import config

params = psycopg.conninfo.make_conninfo(conninfo=config("database.ini"))
pool = ConnectionPool(params)


def writing_query(conn, cur, values):
    try:
        cur.executemany("""
            INSERT INTO instructions (recipe_id, step, instruction, photo) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT DO NOTHING
            """, (values))
        conn.commit()
        print("Instructions successfully written")
        time.sleep(10)
    except Error as e:
        print(f"The error '{e}' occurred")


def getInstructions(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # EXECUTE THE SQL QUERY
            cur.execute(
                'SELECT COUNT(*) FROM recipes WHERE id NOT IN (SELECT DISTINCT recipe_id FROM instructions);')
            num_of_recipes = cur.fetchone()[0]
            for i in range(num_of_recipes//10 + 1):
                print(
                    f'There is still {num_of_recipes - i} that need to get instructions')
                instruction_block = []
                reading_query = f'SELECT id, url FROM recipes WHERE id NOT IN (SELECT DISTINCT recipe_id FROM instructions) LIMIT 10 OFFSET {10*i}'
                cur.execute(reading_query)
                recipes = cur.fetchall()
                for recipe in recipes:
                    recipe_id, recipe_url = recipe
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.422.0 Safari/534.1', 'Upgrade-Insecure-Requests': '1',
                               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'it-IT,', 'Cookie': 'CONSENT=YES+cb.20210418-17-p0.it+FX+917; '}
                    try:
                        page = requests.get(recipe_url, headers=headers)
                        recipe_soup = BeautifulSoup(
                            page.content, "html.parser")
                        instructions = scrapeRecipeInstructions(recipe_soup)
                        for instruction in instructions:
                            instruction_block.append([recipe_id, int(
                                instruction["step"]), instruction["instruction"], instruction["photo"]])
                        print(
                            f"Instructions for recipe {recipe_id} successfully scraped.")
                        time.sleep(20)
                    except Error as e:
                        print(e)
                        break
                writing_query(conn, cur, instruction_block)
    conn.close()
