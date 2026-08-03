FROM python:3.13-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. 建立非 root 系統使用者 appuser
RUN adduser --disabled-password --gecos "" appuser

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./alembic /code/alembic
COPY ./alembic.ini /code/alembic.ini


# 🆕 複製開機腳本，去除 CRLF 換行並賦予執行權限
COPY ./start.sh /code/start.sh

# 2. 將 /code 目錄所有權交給 appuser，並賦予 start.sh 執行權限
RUN chmod +x /code/start.sh && chown -R appuser:appuser /code


RUN sed -i 's/\r$//' /code/start.sh && chmod +x /code/start.sh

EXPOSE 8000

# 3. 切換為非 root 使用者執行後續指令
USER appuser

# 🆕 使用符合官方建議的 JSON 格式（Exec Form）呼叫腳本
CMD ["/code/start.sh"]