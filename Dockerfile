FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /src/reworkd/harambe

# Installing requirements
ADD Prebuild.mk pyproject.toml uv.lock ./
RUN make -f Prebuild.mk RESOLVE_DEPS

CMD ["make", "TEST"]
