FROM python:3.11

# 
WORKDIR /src

# 
COPY ./requirements.txt /src/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install fastapi uvicorn


# 
COPY ./app /src/app

ENV PYTHONPATH=/src/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
