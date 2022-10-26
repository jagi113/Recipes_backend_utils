# -*- coding: utf-8 -*-
from psycopg_pool import ConnectionPool
import psycopg

from database_config.config import config
from scraping.getInstructions import getInstructions
from scraping.getIngredientsNutritionsTags import getIngredientsNutritionsTags
from scraping.getRecipes import getRecipes

params = psycopg.conninfo.make_conninfo(conninfo=config("database.ini"))
pool = ConnectionPool(params)


def startCycle():
    while True:
        choice = input("""
For scraping recipes write 'recipes', 
For scraping repice instructions write 'instructions', 
For scraping ingredients write 'ingredients', 
To exit write 'end'
your choice: 
>> """)
        if choice == 'recipes':
            getRecipes(pool)
        elif choice == 'instructions':
            getInstructions(pool)
        elif choice == 'ingredients':
            getIngredientsNutritionsTags(pool)
        elif choice == 'end':
            break


if __name__ == "__main__":
    startCycle()
