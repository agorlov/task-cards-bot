# Запуск DEV

docker-compose up

# Импорт схемы:

Схема импортируется автоматически при создании нового
контейнера postgres из папки db-init


# Деплой в продакшен

0. Сделаем бэкап

Зайти в контейнер lxc:

Базы:

```sh
sudo lxc-attach karma-yoga-bot
pg_dump -U admin -d admin -h localhost > backup.sql
```

Файлов: скопировать папку ``/app`` в ``/home/alexandr/backup/``


1. Обновление файлов
```sh
rsync -avz --exclude-from=rsync-exclude.txt --dry-run --delete ./ alexandr@92.53.120.211:/home/alexandr/karma-yoga-bot/
rsync -avz --exclude-from=rsync-exclude.txt --backup --backup-dir=backup/ --delete ./ alexandr@92.53.120.211:/home/alexandr/karma-yoga-bot/
```

2. Применим миграции БД:
```sh
psql -U admin -d admin -h localhost -a -f 1.sql
```

3. Docker:

запуск всех
```sh
docker-compose build # пересборка образов (если поменялся Dokcerfile или cronjob)
docker-compose -f docker-compose.prod.yml up
```

перезапуск контейнера karma_bot:
```sh
docker-compose -f ./docker-compose.prod.yaml restart karma_bot
```


## Отладка

```
$ docker ps

# Запуск hello.py в контейнере
$ docker exec -it karma_cron python /app/hello.py
$ docker-compose exec karma_cron python /app/hello.py

```


## Всякое разное

На проде, чтобы временно открыть порт для доступа к БД:

```
iptables -t nat -A PREROUTING -p tcp --dport 5432 -j DNAT --to-destination 10.0.3.134:5432
iptables -A FORWARD -p tcp -d 10.0.3.134 --dport 5432 -j ACCEPT
```

Так можно загрузить какой-нибудь дамп:
```sh
psql -U admin -d admin -h localhost -a -f app.sql
```

### Экспорт/импорт докер-образа

Экспорт:
docker save myimage:latest > myimage_latest.tar

docker save karma-yoga-bot_karma_bot:latest > karma-yoga-bot_karma_bot.tar

Перенос в прод:
scp myimage_latest.tar user@prod-server:/path/to/location

Импорт:
docker load < myimage_latest.tar
