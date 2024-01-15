# 数据库迁移命令

https://hellowac.github.io/technology/python/alembic/

```
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade head
```

# celery

```
 celery -A celery_app.app worker --loglevel=info
celery -A celery_app.app beat --loglevel=info
```

autoflake  --remove-all-unused-imports -i -r .