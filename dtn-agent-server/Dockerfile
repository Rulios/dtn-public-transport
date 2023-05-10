FROM python

ADD requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

ADD main.py /

CMD [ "python", "./main.py" ]