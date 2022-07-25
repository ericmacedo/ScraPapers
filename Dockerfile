# syntax=docker/dockerfile:1
FROM python:3.10.5-slim-buster

WORKDIR /app
ARG requirements=requirements.txt
COPY ${requirements}* .
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.10 && \
	[ -f "${requirements}" ] && pip install --no-cache-dir -r ${requirements} || \
	echo "Missing ${requirements} file!"

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD sh entrypoint.sh
