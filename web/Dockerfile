FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN touch invalid_login_counter.txt
COPY . .
CMD ["python", "app.py"]