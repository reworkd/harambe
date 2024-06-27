FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y \
  default-libmysqlclient-dev \
  gcc \
  pkg-config \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /src/reworkd/harambe

# Installing requirements
ADD Prebuild.mk pyproject.toml poetry.lock ./
RUN make -f Prebuild.mk RESOLVE_DEPS

CMD ["make", "TEST"]
