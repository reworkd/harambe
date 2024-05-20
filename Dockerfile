FROM mcr.microsoft.com/playwright:v1.44.0-jammy

RUN apt-get update && apt-get install -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libsqlite3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev wget

## Build python
WORKDIR /src/python
RUN wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz && \
    tar -xf Python-3.12.3.tgz && \
    rm Python-3.12.3.tgz && \
    cd Python-3.12.3 && \
    ./configure --enable-optimizations && \
    make install && \
    cd .. && \
    rm -rf Python-3.12.3

WORKDIR /src/reworkd/harambe

RUN chown pwuser:pwuser .

USER pwuser

ENV PATH="/home/pwuser/.local/bin:${PATH}"

ADD Prebuild.mk pyproject.toml poetry.lock ./

RUN make -f Prebuild.mk RESOLVE_DEPS

CMD ["make", "TEST"]
