# Read database - PostgreSQL
from psycopg_pool import ConnectionPool
import psycopg
from psycopg import Error
import time

from database_config import config
from modules.scrapeModules import getRecipe
from modules.generalModules import currentTime, writeError

error_file = "errorslog_recipes.json"


def writing_query(conn, cur, values):
    try:
        for value in values:
            cur.execute("""
                INSERT INTO recipes (name, url, photo, slug) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT DO NOTHING
                RETURNING slug
                """, (value))
            id = cur.fetchone()
            conn.commit()
            if id:
                message = f'At {currentTime()} - Recipe "{id[0]}" was successfully written.'
                print(message)
            else:
                error_message = f'At {currentTime()} - Recipe "{value[3]}" is already in database.'
                writeError(error_file, error_message)
    except Error as e:
        error_message = f'At {currentTime()} - saving {values[0][3]}-{values[-1][3]} - the database error "{e}" occurred.'
        writeError(
            error_file, error_message)


recipe_page_number = 1722


def getRecipes(pool):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for i in range(recipe_page_number):
                try:
                    page_recipes = getRecipe(i, error_file)
                    recipes = [[recipe["name"], recipe["url"], recipe["photo"], recipe["slug"]]
                               for recipe in page_recipes]
                    writing_query(conn, cur, recipes)
                    time.sleep(10)
                except Error:
                    continue
    conn.close()


if __name__ == "__main__":
    params = psycopg.conninfo.make_conninfo(conninfo=config())
    pool = ConnectionPool(params)
    getRecipes(pool)
