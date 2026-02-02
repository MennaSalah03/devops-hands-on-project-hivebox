FROM python:3.12-slim

# Create new non-root uesr
RUN useradd -m -u 1000 beekeeper

WORKDIR /home/beekeeper/app

COPY --chown=beekeeper:beekeeper src/ .

USER beekeeper

ENTRYPOINT [ "python", "src/print_version" ]