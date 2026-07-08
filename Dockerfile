FROM python:3.10-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./alembic /code/alembic
COPY ./alembic.ini /code/alembic.ini
COPY ./.env /code/.env

# 🆕 複製開機腳本，並賦予執行權限
COPY ./start.sh /code/start.sh
RUN chmod +x /code/start.sh

EXPOSE 8000

# 🆕 使用符合官方建議的 JSON 格式（Exec Form）呼叫腳本
CMD ["/code/start.sh"]