FROM python:3.7-alpine
COPY . /app
WORKDIR /app
RUN pip install .
RUN miasi create-db
RUN miasi populate-db
RUN miasi add-user -u admin -p admin
EXPOSE 5000
CMD ["miasi", "run"]
