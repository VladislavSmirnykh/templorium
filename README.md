# Templorium

Форк **Odoo 20** с отличиями от upstream: **UUID** как идентификаторы записей, **`NULL` / `null`** для пустых скаляров и типы **`big_integer` / `decimal`** в ORM и веб-клиенте. Сборка урезана до бэкенда, Discuss (`mail`) и Live Chat (`im_livechat`).

## Модули

| Модуль | Назначение |
|--------|------------|
| `base` | Ядро ORM и системные модели |
| `web`, `bus`, `html_editor`, `web_tour`, `base_setup`, `rpc`, `iap` | Веб-клиент и редактор HTML |
| `mail` | Discuss, chatter |
| `im_livechat` | Live Chat на сайте |
| `portal`, `auth_signup`, `http_routing`, `base_address_extended`, `digest`, `resource`, `utm`, `phone_validation` | Зависимости чата |
| `templorium_demo` | Демо: все типы полей, form/list/kanban, compute, onchange, constraints; post-install тесты метаданных и поведения полей |

Остальные аддоны полного Odoo 20 из репозитория убраны.

**Расположение в репозитории:** upstream-модули (включая `base`, `web`, `mail`, …) — в **`odoo/addons/`**; кастомный **`templorium_demo`** — в **`addons/`**. В `odoo.conf`: `addons_path = odoo/addons,addons`.

## Брендинг и URL

В интерфейсе — **Templorium** (правки в `web`, `mail`, `portal`, `auth_signup`, `im_livechat`). Бэкенд-клиент доступен только по **`/web`** (и вложенным путям вида `/web/action-…`). Техническое имя пакета Python, `odoo-bin`, глобал `window.odoo` и префикс `@odoo-module` **не** переименовываются — это совместимость с экосистемой Odoo.

---

## UUID: идентификаторы записей

### Сервер (ORM)

- У моделей с `_auto=True` поле **`id` обязательно** и имеет тип **UUID** (PostgreSQL, по умолчанию `gen_random_uuid()`). Отключить нельзя; исключение — модели без автоматической таблицы (`_auto=False`).
- **Many2one**, **Many2oneReference**, ссылки в доменах и RPC принимают UUID-строки вида `550e8400-e29b-41d4-a716-446655440000`.
- **`SUPERUSER_ID`** — UUID технического пользователя `base.user_root` (login `__system__`). Задаётся в **`odoo.conf`** параметром **`superuser_id`** (или env **`ODOO_SUPERUSER_ID`**). Значение по умолчанию: `00000000-0000-0000-0000-000000000001`. При каждой загрузке registry id в БД приводится к конфигу (обновляются FK на `res_users`).
- Отдельное поле **`fields.Uuid()`** — дополнительный UUID на записи (не замена `id`).

### Клиент (JavaScript)

- Персистентный id записи — только **UUID-строка** (проверка `isPersistedRecordId()` в `record_id.js`). Числовые id в JS не поддерживаются.
- ORM-клиент, props компонентов и URL (`/web/image/<model>/<uuid>/...`) передают id **как строку**, без `parseInt`.
- Виртуальные id новых строк (до сохранения) по-прежнему **не** UUID — это временные идентификаторы клиентской модели.

### Миграция с integer `id`

**Обновить существующую базу Odoo с integer PK на Templorium нельзя.** Нужны новая БД и установка модулей с нуля (`createdb`, `-i base,...`).

---

## Big integer и Decimal

Дополнительные скалярные типы поверх стандартных `integer` и `float`:

| Python (ORM) | Тип поля | PostgreSQL | Назначение |
|--------------|----------|------------|------------|
| `fields.BigInteger()` | `big_integer` | `int8` | 64‑битное целое (диапазон шире, чем у `integer` / `int4`) |
| `fields.Decimal()` | `decimal` | `numeric` | точная десятичная арифметика без IEEE float в ORM и RPC |

Объявление — `BigInteger` / `Decimal` из `odoo.fields` (`odoo/orm/fields_numeric.py`). Пустое значение — **`None` / `NULL`**, не `0`.

### `big_integer`

- В кэше и в Python на записи — **`int`**; в `/web` значения вне `Number.MAX_SAFE_INTEGER` уходят **строкой**, чтобы JSON не округлял id‑подобные числа.
- Виджет — тот же, что у `integer` (`integer_field` в `odoo/addons/web`).

### `Decimal` (отдельно от `Float` и `Monetary`)

**Зачем отдельный тип:** стандартный `fields.Float()` и `fields.Monetary()` хранят и обрабатывают суммы как **`float`** (колонки `float8` или `numeric` с округлением в кэше). Для литералов вроде `2.2222222222222221` нужен путь без round-trip через IEEE.

| Слой | `Decimal` | `Float` / `Monetary` |
|------|-----------|----------------------|
| PostgreSQL | `numeric` | `float8` или `numeric` (если задан `digits`) |
| Чтение из БД | `sql_db.undecimalize` → **`decimal.Decimal`**, в кэше **`Decimal`** | тот же адапter PG, затем **`convert_to_cache` → `float`** |
| На записи (Python) | `rec.field` → **`Decimal`** | **`float`** |
| `read` / `web_read` / RPC | **строка** (нормализованный литерал) | число (`float`) |
| Запись с формы | клиент шлёт **строку**, не JSON‑number | как у float |

- **Драйвер:** для OID PostgreSQL `numeric` Templorium декодирует значение в **`Decimal`**, а не в `float` (`odoo/sql_db.py`). Поля `Float` (с колонкой `numeric`) и `Monetary` при загрузке строки по-прежнему приводят значение к **`float`** в `_insert_cache`.
- **Точность в БД:** колонка создаётся как **`numeric`** без `(p,s)`, если не задан параметр **`digits`** — тогда лимиты PostgreSQL (до ~131 072 цифр до запятой и ~16 383 после). С **`digits=(всего, дробных)`** или **`digits='Product Price'`** действует то же округление при записи в кэш, что у `Float`.
- **Демо:** `templorium_demo` — поля **`scalar_decimal`** (exact) и **`scalar_float`** (классический float8) для сравнения.

### Веб-клиент

- Тип **`decimal`** зарегистрирован рядом с **`float`** (`float_field`, `parseDecimal` в `odoo/addons/web`): пустой ввод → **`null`**; значение в RPC — **строка**, чтобы `JSON.stringify` не портил дробь.
- **`big_integer`** и **`decimal`** на форме/списке выглядят как integer/float, но с другой семантикой парсинга и read.

---

## NULL: пустые скалярные значения

Цель — однозначно отделить «не задано» от нуля, пустой строки и явного `False` у boolean.

### Сервер (Python / PostgreSQL)

| Смысл | Python | PostgreSQL |
|--------|--------|------------|
| Не задано | `None` | `NULL` |
| Число ноль | `0` | `0` |
| Булево «нет» | `False` | `false` |
| Булево «не задано» | `None` | `NULL` (только если поле **не** `required=True`) |
| Непустая строка | `'…'` | `'…'` |

Затронуты конвертеры полей в `odoo/orm/` (`Integer`, `BigInteger`, `Float`, `Decimal`, `Monetary`, `Boolean`, `Char`, `Text`, `Html`, `Json`, `Selection` и общие `convert_to_record` / `convert_to_read`). Пустой char/text/html на чтении не подменяется на `""`, если в БД `NULL`.

### Клиент (JavaScript)

- В relational model пустой скаляр — **`null`** (`isUnsetScalar()` в `scalar_value.js`).
- При **записи** на сервер уходит **`null`**, а не `false` (кроме boolean: не задано — `null`, явное «нет» — `false`; см. `isUnsetBoolean()`). Для **`required=True`** boolean допустимы только `true` и `false`; `null`/`None` запрещены (NOT NULL в БД и проверка формы).
- Парсеры полей: пустой ввод integer/float/big_integer/decimal → `null`, не `0`.
- RPC: пустой скаляр — только **`null`**; `false` для не-boolean полей не поддерживается.

### Особые случаи

- **Boolean:** `null` означает «значение не выбирали»; `false` — явное «нет». На форме незаданное поле показывается indeterminate. Поле с `required=True` должно быть явно `true` или `false`.
- **Html:** в модели поле может быть `null`; редактор (`html_editor`) трактует `null` как пустой HTML (WYSIWYG), а не принудительный code view.
- **Many2one / Reference:** «пусто» — `false` или отсутствие значения в UI; это не скаляр NULL, а отсутствие связи.
- **Binary / Image:** пустое поле — **`null`** / `None` (нет вложения или пустая колонка); данные — объект `{ content, filename?, size? }` в RPC. Очистка файла на форме пишет **`null`**, не `false`.

### Практика для разработчиков

- **Дублирование записей в UI:** по умолчанию выключено (атрибут arch `duplicate` трактуется как `false`). Чтобы показать «Duplicate» на форме, списке или kanban, явно задайте `duplicate="1"` / `duplicate="true"` на корневом теге представления (при включённом `create`).
- В доменах и Python: «не задано» — только **`None`** (`('field', '=', None)` или `'in'` с `None`). **`False`** в домене — только смысл булева «нет», не подстановка NULL.
- В JS: не сравнивайте пустое число с `0`; проверяйте `value == null` или `isUnsetScalar(value)`.
- Новые виджеты и RPC: id и foreign key — **UUID string**, не `number`.

---

## HEIC / HEIF (изображения)

Поддержка фото с iPhone и других камер в формате **HEIC/HEIF** — на сервере и в веб-клиенте.

### Зависимости и сервер

- В **`requirements.txt`** — пакет **`pillow-heif`** (версия зависит от Python). После обновления репозитория переустановите зависимости: `.venv/bin/pip install -r requirements.txt`.
- **`odoo/tools/image.py`** регистрирует HEIF opener для Pillow; **`image_process`** и поле **`fields.Image`** могут декодировать HEIC при сохранении (ресайз, JPEG/PNG на выходе).
- **`odoo/tools/mimetypes.py`** — сигнатура ISO BMFF (`ftyp`) и MIME **`image/heic`** / **`image/heif`**.
- Загрузка в **html_editor** (медиа-диалог, вложения) и просмотр в **file viewer** — расширения `.heic` / `.heif` и соответствующие MIME.

### Веб-клиент (виджет Image)

Chrome и большинство браузеров **не отображают** сырой HEIC в `<img>` и в `data:`-URL. Поэтому:

- При выборе HEIC/HEIF виджет **`image`** вызывает RPC **`ir.attachment.web_image_data_preview`**: сервер конвертирует байты в **JPEG** для превью до сохранения записи.
- После сохранения картинка отдаётся через **`/web/image/<model>/<uuid>/...`** (уже обработанное вложение); виджет сбрасывает состояние ошибки превью при смене **`checksum`**, чтобы не требовать полную перезагрузку страницы.

---

## Требования

- Python 3.12+ (`requirements.txt`), включая **`pillow-heif`** для HEIC
- PostgreSQL

## Установка и запуск

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

createdb templorium_test   # при необходимости

.venv/bin/python odoo-bin -c odoo.conf -d templorium_test \
  -i base,mail,im_livechat
```

Дальнейшие запуски без `-i`:

```bash
.venv/bin/python odoo-bin -c odoo.conf -d templorium_test
```

Рекомендуется открывать UI по **`http://127.0.0.1:8069`**, чтобы совпадали `web.base.url` и кэш ассетов. После правок в `static/src` — жёсткое обновление страницы (Cmd+Shift+R) или сброс вложений `/web/assets/...` в БД.

Логин после установки: `admin` / `admin` (смените пароль).

### Тесты `templorium_demo`

```bash
.venv/bin/python odoo-bin -c odoo.conf -d templorium_test --test-enable --stop-after-init \
  -u templorium_demo --test-tags=templorium_demo
```

Покрытие: атрибуты полей в registry и `ir.model.fields` (`field_specs.py`), NULL/roundtrip, Selection, relational, compute, onchange (`Form`), constraints, Properties, binary/json.

## Лицензия

Код Odoo — LGPL-3 (`LICENSE`). Дополнительные модули из upstream 20.0 — под тем же лицензированием Odoo.
