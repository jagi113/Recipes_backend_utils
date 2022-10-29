Scraping recipe and ingredient module.

Run run.py file which will ask you to choose 1 of three options.

This module consists from 3 separate cycle.

1. cycle - getRecipes - getRecipe function in scrapeModules scrapes basic information from slovak recipe website
            - it scrapes name, url and image url of the recipe
            - cycle then stores data in postgres database

2. cycle - getInstructions - reads recipe urls from database and scrapes instructions steps and provided 
                    step-image-urls from each of them
            - for scraping instruction_step, instruction, step_image_url is used scrapeModule 
                    function scrapeRecipeInstructions
            - data are stored to database after 10 scraped recipes

3. cycle - getIngredients -  reads recipe url from database
            - stores ingredient, its amount and measure_unit using scrapeRecipeIngredients function in scrapeModules
            - looks for ingredient in slovak website that stores info about various ingredients nutritions through 
                    google search using scrapeIngredientWebsite function in scrapeModules
            - when found (the same or similar), searches for this url in own database, if not found, scrapes ingredient 
                    nutrition info website and the ingredient nutritions into database using scrapeIngredientNutritions 
                    function in scrapeModules
            - finally cycle stores recipe ingredient id, needed amount and unit into database

For scraping is used requests and BeautifulSoup library and scraping is limited for mentioned websites only.
Connection to the database is provided through psycopg and psycopg-pool libraries.
To avoid 429 error for too many requests, there are only 6 requests per minute using time library.