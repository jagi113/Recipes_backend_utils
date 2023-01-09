import json
import datetime

# getting formatted current time


def currentTime():
    return datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")


# creating and saving error logs
def writeError(filename, error):
    print(error)
    try:
        with open(filename, "a+") as file:
            json.dump({error}, file)
    except IOError:
        with open(filename, "w+") as file:
            json.dump({error}, file)

    

