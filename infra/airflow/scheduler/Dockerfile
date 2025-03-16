FROM apache/airflow:2.10.4-python3.10

USER root

RUN apt update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;

ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/
RUN export JAVA_HOME

RUN mkdir -p /opt/airflow/spark/jars

RUN curl -o /opt/airflow/spark/jars/postgresql-42.2.18.jar https://jdbc.postgresql.org/download/postgresql-42.2.18.jar && \
    curl -o /opt/airflow/spark/jars/mongo-driver-sync_5.3.1.jar https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/5.3.1/mongodb-driver-sync-5.3.1.jar && \
    curl -o /opt/airflow/spark/jars/mongo-spark-connector.jar https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.13/10.4.0/mongo-spark-connector_2.13-10.4.0.jar

USER airflow
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow/scripts" 

# Entrypoint
CMD ["scheduler"]