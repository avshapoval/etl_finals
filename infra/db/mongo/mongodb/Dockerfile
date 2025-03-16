FROM mongo:8.0.5

COPY init-mongo.js /docker-entrypoint-initdb.d/

CMD ["mongod", "--bind_ip_all"]