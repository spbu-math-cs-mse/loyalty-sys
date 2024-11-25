# API Backend для аналитики покупок

## Создание нового пользователя

POST /user - Создание нового пользователя

- Параметры:
  - chat_id (обязательный): идентификатор телеграм чата пользователя с ботом.
- Тело запроса:

```json
{
  "chat_id": "1234567890"
}
```

- Пример ответа:

```json
{
  "message": "User created",
  "user_id": "234567890abcdef1234567890abcdef12345678"
}
```

## Запись о покупке пользователя

POST /user/[user_id]/purchase

- Параметры:
  - user_id: идентификатор пользователя.
- Тело запроса:

```json
{
  "date": "2023-12",
  "purchases": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}
```

- Пример ответа:

```json
{
  "message": "Purchases recorded",
  "purchase_id": 1
}
```

## Получение данных для графика статистики по продуктам

GET /data/values

- Параметры:
  - product_id (обязательный): идентификатор продукта.
  - start_date (необязательный): начальная дата в формате "YYYY-MM".
  - end_date (необязательный): конечная дата в формате "YYYY-MM".
- Пример запроса:

```
    GET /data/values?product_id=1&start_date=2023-10&end_date=2023-12
```

- Пример ответа:

```json
{
  "label": "Milk",
  "values": [5, 6, 7]
}
```

## Сумма покупок в период времени

GET /data/total_purchases

- Параметры:
  - start_date (необязательный): начальная дата в формате "YYYY-MM".
  - end_date (необязательный): конечная дата в формате "YYYY-MM".
- Пример запроса:

```
    GET /data/total_purchases?start_date=2023-10&end_date=2023-12
```

- Пример ответа:

```json
{
  "total_purchases": 190300.0
}
```

## Средний чек в период времени

GET /data/average_check

- Параметры:
  - start_date (необязательный): начальная дата в формате "YYYY-MM".
  - end_date (необязательный): конечная дата в формате "YYYY-MM".
- Пример запроса:

```
    GET /data/average_check?start_date=2023-10&end_date=2023-12
```

- Пример ответа (в копейках):

```json
{
  "average_check": 250000.0
}
```

## Количество посетителей в период времени

GET /data/visitor_count

- Параметры:
  - start_date (необязательный): начальная дата в формате "YYYY-MM".
  - end_date (необязательный): конечная дата в формате "YYYY-MM".
- Пример запроса:

```
    GET /data/visitor_count?start_date=2023-10&end_date=2023-12
```

- Пример ответа:

```json
{
  "visitor_count": 100
}
```

## Список продуктов и их id

GET /data/products

- Пример ответа:

```json
[
  {
    "id": 1,
    "label": "Milk",
    "price_copeck": 1203
  },
  {
    "id": 2,
    "label": "Bread",
    "price_copeck": 13
  }
]
```
