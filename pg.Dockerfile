FROM postgres:latest

# Install dependencies and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    postgresql-server-dev-all

# Clone and build pgvector
RUN git clone https://github.com/ankane/pgvector.git \
    && cd pgvector \
    && make \
    && make install

# Clean up
RUN apt-get remove -y build-essential git postgresql-server-dev-all \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the entrypoint to load the pgvector extension
COPY ./init-db.sh /docker-entrypoint-initdb.d/
