# Краткая справка по формату JSON

JSON это сокращение от JavaScript Object Notation, текстовый формат хранения
данных, изначально разработанный для JavaScript.

Благодаря тому, что этот формат текстовый, файлы этого формата можно
просматривать и редактировать любым текстовым редактором.

В JSON есть следующие типы данных:

- числа, например: 1
- строки, например: "а"
- последовательности, например: [1, 2, 3]
- записи, набор пар вида "ключ": "значение", например: {"key": "text"}
- ничего, записывается как null
- истина, записывается как true
- ложь, записывается как false

Это всё, что можно записать в JSON. Но содержимое можно комбинировать между
собой и вкладывать некоторые типы друг в друга, так что в итоге можно получать
очень сложные структуры.

### Стоит иметь в виду

- Пробелы не имеют значения (если только не внутри строк). В примерах я буду
  показывать красиво отформатированные записи, но в реальности это не имеет
  значения. Можете расставлять переносы строк как попало.
- Можно использовать только двойные кавычки. Одинарные можно применять только
  внутри строк, просто как вариант буквы.
- На верхнем уровне JSON должна быть либо последовательность [] либо запись {}.
- Нельзя допускать ошибки. Открытые скобки всегда должны закрываться, запятые
  не должны пропускаться. Висячие запятые в конце последовательностей не
  допускаются.
- Нет инструмента для многострочного текста. Если вам нужен перенос строки,
  вставьте \n в то место, где вам нужен разрыв текста.

### Примеры содержимого JSON

Минимально возможные варианты:

```json
[]
```

```json
{}
```

Маленькая последовательность или запись:

```json
[1, 2, 3]
```

```json
["a", "b"]
```

```json
{"name": "Vasya", "age": 20}
```

Можно делать вложенные структуры:

```json
[
    {
        "name": "Vasya",
        "age": 20,
        "is_student": true,
        "faculty": null,
        "grades": [
            4,
            5,
            3
        ]
    },
    {
        "name": "Georgy",
        "age": 40,
        "is_student": false,
        "faculty": "45-a1",
        "grades": null
    }
]
```