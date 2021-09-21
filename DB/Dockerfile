FROM postgres
ENV POSTGRES_PASSWORD 123
ENV POSTGRES_DB ImageDescribePipeDB
COPY dumped.sql /docker-entrypoint-initdb.d/
