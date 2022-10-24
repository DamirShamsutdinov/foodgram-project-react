## Foodgram – продуктовый помошник
![Foodgram workflow](https://github.com/DamirShamsutdinov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Cайт временно доступен по ссылке: http://158.160.6.225/
```
Суперюзер
Логин: admin@bk.ru
Пароль: Industrial
```
Документация к API по ссылке: http://158.160.6.225/api/docs/

## О проекте
На этом сервисе пользователи смогут:
- публиковать рецепты
- подписываться на публикации других авторов
- добавлять понравившиеся рецепты в список «Избранное»
- скачивать сводный список продуктов для покупок

## Стек технологий

![python version](https://img.shields.io/badge/Python-3.7-yellowgreen)
![python version](https://img.shields.io/badge/Django-3.2.15-yellowgreen)
![python version](https://img.shields.io/badge/djangorestframework-3.13.1-yellowgreen)
![python version](https://img.shields.io/badge/djoser-2.1.0-yellowgreen)
![python version](https://img.shields.io/badge/gunicorn-20.1.0-yellowgreen)
![python version](https://img.shields.io/badge/psycopg2--binary-2.9.2-yellowgreen)

## Запуск проекта

Клонировать репозиторий и перейти в него в командной строке

```
https://github.com/DamirShamsutdinov/foodgram-project-react.git
cd foodgram-project-react
```

Перейти в папку "infra" <br>
```
cd infra
```
Заполнить файл ".env" собственными настройками БД <br>
Запустить контейнеры

```
docker-compose up -d --build
```

В скрипте автоматически выполнятся задачи миграции, подключения статики и наполнение базы демонстрациооными данными

Запустить в браузере

```
http://localhost/
```
