FROM python:3.10-slim

WORKDIR /app

# 依存関係のインストール
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# アプリケーションコードのコピー
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# 環境変数の設定
ENV PYTHONPATH=/app

# コンテナ起動時のコマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


