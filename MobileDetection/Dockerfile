FROM python:3.7
WORKDIR /app
COPY requirements_app.txt ./requirements_app.txt
RUN pip3 install -r requirements_app.txt
COPY . .
CMD streamlit run app.py
