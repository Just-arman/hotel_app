FROM python:3.9-slim

WORKDIR /hotels

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN find docker -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;
RUN chmod +x ./docker/*.sh

CMD ["./docker/app.sh"]