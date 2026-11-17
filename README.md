# Test_Bank — автотесты банковского API

Проект автотестов для учебного банковского API: пополнение счёта, перевод между счетами,
выдача кредита и погашение кредита. Тесты проверяют не только ответы API, но и последствия —
баланс, выписку по счёту, историю кредитов и записи в базе данных.

## Стек

| Компонент | Версия |
|---|---|
| Python | 3.15.1 |
| pytest | 9.2.0 |
| requests | 2.34.2 |
| Pydantic | 2.14.3 |
| SQLAlchemy | 2.1.8 |
| psycopg2-binary | 2.9.13 |
| allure-pytest | 2.16.2 |
| rstr | 3.2.2 |

## Структура проекта

```
Test_Bank/
├── conftest.py                 подключение фикстур
├── pytest.ini                  настройки pytest и маркеров
├── requirements.txt
├── resources/
│   └── urls.properties         адрес API и строка подключения к БД
└── src/main/
    ├── api/
    │   ├── classes/            ApiManager — точка входа в шаги
    │   ├── configs/            Config — чтение urls.properties
    │   ├── fixtures/           api_manager, created_obj, create_user_request, db_session
    │   ├── foundation/         транспорт и паспорта ручек
    │   │   ├── endpoint.py     9 ручек: Enum + dataclass
    │   │   ├── crud_endpoint.py Protocol для описания ручки
    │   │   ├── http_requester.py отправка запроса, шаги и вложения Allure
    │   │   └── requesters/     crud_requester и validate_crud_requester
    │   ├── generator/          CreationRule и RandomModelGenerator
    │   ├── models/             18 моделей Pydantic
    │   ├── specs/              спеки запроса и ответа
    │   ├── steps/              UserSteps (15), AdminSteps (2)
    │   └── tests/              4 файла тестов
    └── db/
        ├── base.py             Declarative Base
        ├── engine.py           engine и SessionLocal
        ├── models/             account, transaction, credit
        └── crud/               чтение по каждой таблице
```

## Слои

Запрос идёт по цепочке, каждый слой отвечает за одно:

```
tests → steps → requesters → http_requester → endpoint
                    ↑
        specs, models, fixtures, generator, db
```

| Слой | За что отвечает |
|---|---|
| `tests` | бизнес-логика проверки, без технических деталей |
| `steps` | одна ручка — один метод, имя говорит о действии |
| `requesters` | валидирующий возвращает модель, сырой — `Response` |
| `http_requester` | отправка, шаг Allure, вложения «Запрос» и «Ответ» |
| `endpoint` | паспорт ручки: URL, модель запроса, модель ответа |

## Установка

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Настройка

Все адреса лежат в `resources/urls.properties`:

```properties
backendUrl=http://localhost:4111/api
databaseUrl=postgresql+psycopg2://symfony:password@localhost:5432/symfony_db
```

Перед запуском должен быть поднят банк в Docker:

```powershell
docker start bank_api
```

Swagger доступен по адресу http://localhost:4111/api/swagger

## Запуск тестов

```powershell
# весь набор
.\.venv\Scripts\python.exe -m pytest src/main/api/tests -q

# один файл
.\.venv\Scripts\python.exe -m pytest src/main/api/tests/test_account_deposit_senior.py -q

# один тест
.\.venv\Scripts\python.exe -m pytest "src/main/api/tests/test_transfer_money_senior.py::TestMoneyTransferSenior::test_money_transfer" -q

# по маркеру
.\.venv\Scripts\python.exe -m pytest -m apis -q
```

## Отчёт Allure

```powershell
.\.venv\Scripts\python.exe -m pytest src/main/api/tests --alluredir=allure-results --clean-alluredir
npx --yes allure awesome allure-results --single-file --output allure-report
```

Готовый отчёт — `allure-report/index.html`, один файл, открывается в браузере.

## Что покрыто тестами

43 теста в четырёх файлах:

| Файл | Тестов | Что проверяет |
|---|---|---|
| `test_account_deposit_senior.py` | 9 | пополнение: границы 1000–9000, отказ вне лимита, запрос без токена |
| `test_transfer_money_senior.py` | 11 | перевод: границы 500–10000, нулевая сумма, балансы «до/после» |
| `test_credit_user_senior.py` | 16 | выдача кредита: границы 5000–15000, срок 1–60, отказ без роли |
| `test_credit_repay_senior.py` | 7 | погашение: полное, неполное, повторное, нехватка денег |

В каждом тесте проверяются три уровня:

1. **ответ API** — код, тело, поля модели;
2. **последствия через GET** — баланс счёта, выписка по счёту, история кредитов;
3. **записи в БД** — через SQLAlchemy, на тех же данных.

## Проверки выписки по счёту

Выписка (`GET /account/transactions`) показывает операции счёта:

| Операция | Тип в выписке | Знак суммы |
|---|---|---|
| Пополнение | `deposit` | положительный |
| Перевод у отправителя | `transfer_out` | отрицательный |
| Перевод у получателя | `transfer_in` | положительный |

Важно: в базе перевод хранится **одной строкой** с типом `transfer` и положительной суммой,
а API показывает её двумя видами — `transfer_out` у отправителя и `transfer_in` у получателя.
Поэтому выводы о содержимом БД делаются SQL-запросами, а не по ответам API.

## Слой базы данных

| Таблица | Модель | CRUD |
|---|---|---|
| `account` | `account_table.py` | `AccountCrudDb` |
| `transaction` | `transaction_table.py` | `TransactionCrudDb` |
| `credit` | `credit_table.py` | `CreditCrudDb` |

Фикстура `db_session` открывает соединение и откатывает транзакцию после теста,
поэтому тесты не оставляют за собой изменений.

## Найденные особенности стенда

| Что | Факт |
|---|---|
| Удаление пользователя | мягкое: ставится `user.deleted_at`, счета, транзакции и кредиты остаются в БД. Требованиям «удаляется вся связанная информация» не соответствует, тестом пока не покрыто |
| Код 422 по переводу | стенд отдаёт 400, поэтому в тестах используется 400 |
| Повторное погашение | 409 |
| Выдача второго кредита на счёт | по требованиям 404, тестом пока не покрыто |
