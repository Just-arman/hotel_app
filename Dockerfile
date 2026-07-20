FROM python:3.9

WORKDIR /hotels

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /hotels/docker/*.sh

CMD ["/hotels/docker/celery.sh"]
