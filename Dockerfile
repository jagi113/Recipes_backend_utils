FROM python:3.10.6

WORKDIR /Server/Programs/Recipes_backend_utils

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./run.py" ]
