FROM python:3.12-alpine
ENV PYTHONPATH=/usr/src/app
WORKDIR /usr/src/app
COPY . .
RUN pip3 install --no-cache-dir -e .
EXPOSE 9876
CMD ["python3", "-m", "gistapi.gistapi"]