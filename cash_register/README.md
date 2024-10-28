# Касса

## Предварительно

Если не установлен cmake:
```
sudo apt update
sudo apt install cmake
```

## Запуск кассы

1. Переходим в соответствующую директорию: `cd cash_register`
2. Собираем проект: `make build`
3. Запускаем проект: `make run`

## Работа с сетью

Чтобы воспользоваться кассой, неободимо направить POST запрос по адресу `http://84.201.143.213:1234/purchase`. Если тело пустое и не содержит json, то необходимые данные (user_id и список продуктов) сгенерируются рандомно.

### Формат request json body

Пример:
```
{
    "user_id": 12345,
    "products": [
        {
            "name": "apple", 
            "price": "199.50"
        },
        {
            "name": "banana", 
            "price": "125.75"
        },
        {
            "name": "orange", 
            "price": "163.234"
        },
        {
            "name": "strawberry", 
            "price": "213.99"
        }
    ]
}
```

### Формат response json body

Пример:
```
{
    "total_cost": "572.101805",
    "user_id": 6944
}
```