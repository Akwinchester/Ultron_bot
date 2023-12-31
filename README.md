<div align="center">

# Telegram бот для ведения тренировочного дневника


</div>

Это telegram бот для ведения тренировочного дневника и мотивации с помощью рассылки уведомлений о достижениях выбранным пользователям.

Бот был разработан из-за потребности в повышении мотивации при занятиях спортом. Обычные тренировочные дневники перестали приносить желаемый результат. Для решения этой проблемы и была поставлена задача создания бота с игровыми элементами и возможностью настройки уведомлений.

Основная идея бота - добавление соревновательного аспекта путем привлечения друзей. Пользователь может пригласить других участников к своим активностям или присоединиться к чужим. После добавления новой записи уведомление получают только выбранные в настройках получатели, а не все друзья. Это стимулирует больше тренироваться и не отставать от других.

Также в боте присутствует возможность гибкой настройки уведомлений - изменения текста с использованием шаблонов и списка получателей. Это позволяет сделать рассылку максимально релевантной и полезной.

Интуитивный интерфейс бота и отсутствие необходимости устанавливать сторонние приложения делает процесс ведения дневника максимально простым и удобным.

<div align="center">

## **Возможности:**

</div>

- Создание своих активностей. Пользователь может заводить активности на любые темы - от спорта до изучения языков.

- Подключение друзей к своим активностям. Для каждой активности можно пригласить участников из числа друзей.

- Присоединение к чужим активностям. Можно подключиться к любой открытой активности друзей.

- Настройка текста уведомлений с использованием шаблонов. Это позволяет сделать сообщения персонализированными.

- Выбор получателей уведомлений из числа подключенных друзей.

- Возможность архивировать старые активности.

- Автоматическое удаление командных сообщений с ботом. В чате остаются только итоговые отчеты о добавленных записях.

<div align="center">

## **Используемые технологии:**

</div>

- <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotAPI</a> - SDK для создания телеграм ботов на python.

- <a href="https://www.sqlalchemy.org/">SQLAlchemy</a> - ORM для работы с БД из кода на python. Позволяет абстрагироваться от конкретной СУБД.

- <a href="https://alembic.sqlalchemy.org/en/latest/">Alembic</a> - инструмент для версионирования структуры БД, миграций.

<div align="center">

## **Структура БД:**

</div>


Данные хранятся в реляционной БД MySQL. Используются следующие основные таблицы:

<i>User</i> - хранит данные о зарегистрированных пользователях бота:


- id - уникальный идентификатор пользователя (primary key)

- name - имя пользователя в Телеграм  

- username - уникальное имя для входа на сайт

- password - хэш пароля для входа на сайт

- chat_id - уникальный идентификатор чата в Телеграм

- nick - опциональный никнейм пользователя



</br>
<i>Activity</i> - хранит данные о созданных пользователями активностях:



- id - уникальный идентификатор активности (primary key)

- name - название активности

- user_id - id создателя активности (внешний ключ к таблице User)

- notification_text - шаблон текста уведомлений

- status - признак активна ли активность или архивная



</br>
<i>Entry</i> - записи о выполнении активности конкретным пользователем:



- id - уникальный идентификатор записи (primary key)

- activity_id - id активности, к которой относится запись (внешний ключ к Activity)

- user_id - id пользователя, создавшего запись (внешний ключ к User)

- amount - количественное значение

- description - текстовое описание выполнения

- date - дата создания записи

</br>

</div>

Также используются дополнительные таблицы для связей "многие ко многим":

<i>user_activity</i> - хранит связи пользователей, подписанных на уведомления по конкретным активностям.

<i>user_friend</i> - хранит связи пользователей - кто чей друг. 

<i>activity_activity</i> - хранит связи активностей, позволяя подключаться к чужим активностям.

Такая структура позволяет гибко и эффективно хранить и связывать все данные о пользователях, их активностях, достижениях и отношениях между собой.

<div align="center">  

## Базовые сценарии использования

</div>

Пользователь может взаимодействовать с ботом по следующим основным сценариям:

**Добавление новой активности**

1. В главном меню выбрать "Добавить запись"
2. Выбрать "Создать новую активность" 
3. Ввести название активности в сообщении боту
4. Бот создаст активность и вернет в главное меню

**Присоединение к активности друга** 

1. В главном меню выбрать "Добавить запись"  
2. Выбрать имя друга в списке
3. Выбрать активность друга, к которой хотите присоединиться
4. Бот скопирует выбранную активность в ваш список

**Изменение статуса неактивной активности**

1. В главном меню выбрать "Добавить запись" 
2. Выбрать пункт "Мои активности"
3. Выбрать неактивную активность
4. Нажать кнопку изменения статуса активности
5. Бот сделает активность доступной для добавления записей  

**Добавление записи в активность**

1. В главном меню выбрать "Добавить запись"
2. Выбрать нужную активность
3. Указать количественное значение (или пропустить)
4. Добавить текстовое описание (или пропустить)
5. Бот сохранит запись и отправит уведомления подписчикам активности

**Настройка уведомлений для активности** 

1. В главном меню выбрать "Добавить запись"  
2. Выбрать активность, для которой настраиваются уведомления
3. Нажать кнопку "Уведомления"
4. Задать текст уведомления через шаблон  
5. Выбрать получателей уведомлений из подписанных пользователей

**Добавление друга**

1. При настройке уведомлений выбрать пункт "Добавить друга"
2. Ввести в сообщении боту никнейм друга  
3. Бот отправит запрос на добавление в друзья

<div align="center">

## Процесс добавления записи

</div>

Добавление новой записи о выполнении активности происходит в несколько этапов:

**1. Выбор активности**

Пользователь во взаимодействии с ботом выбирает активность из списка своих активностей.

**2. Указание количественного значения**

Пользователю предлагается указать количественное значение для записи (например, количество повторений упражнения). Этот шаг необязателен, можно пропустить указание значения.

**3. Добавление текстового описания** 

Пользователь может добавить текстовое описание к записи. Этот шаг также необязателен.

**4. Создание объекта записи**

На основе полученных от пользователя данных создается объект класса Row, описанный в модуле data_structares.py. Он содержит следующие поля:

- date_added - дата добавления записи
- activity_id - id выбранной активности
- amount - количественное значение
- description - текстовое описание

Объект заполняется данными с помощью класса RowFactory.

**5. Сохранение записи в БД**

Объект записи передается в модуль entry.py, где происходит сохранение в БД с помощью ORM.

**6. Формирование и отправка уведомлений**

На основе шаблона уведомлений для выбранной активности формируется текст уведомления с данными о новой записи. Отправляется подписчикам активности.

**7. Вывод информации пользователю**

Пользователю выводится сообщение с информацией о добавленной записи.

Такая структура позволяет гибко контролировать процесс создания записи на всех этапах.

<div align="center">

## Текущее состояние

</div>
В данный момент ведется разработка web интерфейса для удобного просмотра статистики и личных достижений пользователя, а также общего рейтинга.

В планах добавление новых способов взаимодействия с ботом - больше команд, настроек, возможностей.

