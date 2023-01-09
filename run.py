# -*- coding: utf-8 -*-
from psycopg_pool import ConnectionPool
import psycopg
from database_config.config import config

from scraping.getInstructions import getInstructions
from scraping.getIngredientsNutritionsTags import getIngredientsNutritionsTags
from scraping.getRecipes import getRecipes

choice_dict = {
    "recipes": getRecipes,
    "instructions": getInstructions,
    "ingredients": getIngredientsNutritionsTags
}


def startCycle():
    while True:
        choice = input("""
For scraping recipes write 'recipes', 
For scraping repice instructions write 'instructions', 
For scraping ingredients write 'ingredients', 
To exit write 'end'
your choice: 
>> """)
        if choice == 'end':
            break
        elif choice in choice_dict:
            params = psycopg.conninfo.make_conninfo(
                conninfo=config()
            )
            pool = ConnectionPool(params)
            choice_dict[choice](pool)


if __name__ == "__main__":
    startCycle()
