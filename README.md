# Автоиграйка для тупайки Годвилль

Бот-самоиграйка для игры Годвилль. Возводим жанр Zero-player game до максимального состояния.

> [!WARNING]  
> Данный прокт предназначен только для образовательных целей. Его использование приведет к низкому качеству игры и блокировке аккаунта.

## Что он делает

Собирает кирпичи быстрым и недонатным способом. Но если игра нравится, то советую задонатить.

Стратегии:
- Плавка кирпичей, если скопилось >3000 золота
- Заполнение бинго, если у героя >50% инвентаря, и получение купона
- Копание в поле (при низком здоровье, чтобы не откопать босса)
- Разворот в город, где можно подешевле купить кирпич
- Открытие определенных активируемых предметов (классы предметов определяет Erinome Godville UI+)
- Поход на ZPG-арену
- Отмена побега с гильдии
- Воскрешение героя (рутинная операция)

Что не реализовано:
- Крафт вещей (кнопки появляются благодаря Erinome Godville UI+)
- Активация знаков
- Сброс счетчика разворотов при выполнении мини-квеста
- Быстрый парсинг. Сейчас достаются элементы не из выгруженный html файл, а прямо из страницы. Так сделать легче, так как не думаешь об актуальности html страницы, но так парсинг происходит гораздо медленней (30ms на один элемент через seleniumbase или 0.5ms парсинг html через BeautifulSoup).
- Возможности выше 12 уровня.

## Как это работает

Происходит управление браузером Chrome через фреймворк SeleniumBase со скрытым режимом. В коде описана логика обработки информации и принятия решений. То есть отдаются команды на взаимодействие со страницей (клики, заполнение текста).

## Пример работы

<details>
  <summary>Примеры логов</summary>

Активашки
```
2024-06-25 01:23:14,913 - INFO - I have алоэ веры, class: type-charge-box e_craft_impossible improved, Этот предмет добавляет заряд в прано-аккумулятор (требуется 50% праны), price: 50
2024-06-25 01:23:14,962 - INFO - Activated this item
2024-06-25 01:23:16,250 - INFO - Hero's response: Внезапно алоэ веры превратило в сияющий синий брикетик, который стремительно унёсся куда-то вверх. Великий тоже собирает кирпичи?
```

Копание
```
2024-06-24 23:52:49,488 - INFO - Возврат|money:508|prana:61|inv:16|bricks:33|hp:11|where:7,В пути|town:Подмостква|quest:11,заставить летать рождённого ползать
2024-06-24 23:53:04,951 - INFO - Godvoice command 'Копай клад!' executed. Hero RESPONDED.
2024-06-24 23:53:04,952 - INFO - Digging strategy executed.
2024-06-24 23:53:53,249 - INFO - Возврат|money:508|prana:56|inv:16|bricks:33|hp:11|where:6,В пути|town:Нижние Котлы|quest:11,заставить летать рождённого ползать
2024-06-24 23:54:16,078 - INFO - Godvoice command 'Копай клад!' executed. Hero RESPONDED.
2024-06-24 23:54:16,079 - INFO - Digging strategy executed.
```

ZPG-арена
```
2024-06-24 22:00:17,180 - INFO - Accepted first confirm for arena
2024-06-24 22:00:18,014 - INFO - Went to ZPG arena: Ближайшие 2 мин 43 с арена работает в режиме полного ZPG, не позволяя богам влиять на героев. Вы готовы положиться на волю случая?
2024-06-24 22:00:18,015 - INFO - ZPG arena strategy executed.
2024-06-24 22:01:07,630 - INFO - Авантюра|money:1140|prana:25|inv:75|bricks:32|hp:100|where:0,Годвилль|town:Годвилль|quest:10,набрать выпускной бал
```

Плавка
```
2024-06-24 08:56:36,828 - INFO - Influence was made with 3 strategy
2024-06-24 08:56:36,828 - INFO - Influence action 'PUNISH' executed successfully.
2024-06-24 08:56:36,828 - INFO - Melt bricks strategy executed.
```

Бинго
```
2024-06-24 01:11:50,087 - INFO - Осталось игр в бинго: 3
2024-06-24 01:11:50,744 - INFO - Trying to play bingo and get coupon
2024-06-24 01:11:52,204 - INFO - Bingo played: Трофеев в инвентаре: 7.
В бинго можно изъять: стройматериалы для песочного замка.
2024-06-24 01:11:55,477 - INFO - Bingo strategy executed.
```

Возврат
```
2024-06-23 21:42:43,579 - INFO - Godvoice command 'Домой' executed. Hero RESPONDED.
2024-06-23 21:42:43,715 - INFO - Return counter: 1
2024-06-23 21:42:43,715 - INFO - Returning strategy executed.
```

</details>

## Краткая статистика

## Это детектируется?

Не так просто как чистый Selenium, но есть зацепки. Источник - https://github.com/kaliiiiiiiiii/brotector
- Если использовать не на Linux, то детектируется Headless режим [следующим проектом](https://github.com/kaliiiiiiiiii/brotector). На Linux будет использоваться виртуальный дисплей, который не оставляет подобных артефакты для детекции.
- При взаимодействии с сайтом можно попробовать прочитать переменную `navigator.webdriver`. Во время работы стратегий (это около 2 секунд с перерывом в 10 секунд) данная переменная должна равняться `true`. Если оптимизировать взаимодействие, то все равно при клике на влияния или арену обнажается эта переменная, так как они не кликаются через JS, требуется именно помощь вебдрайвера.
- Открытие devtools тоже выглядит подозрительно и возможно задетектировать.
- Поведенческие индикаторы (быстрая реакция, скриптовая реакция на похожие условия).

## Как это запускать (по-прежнему не рекомендую это делать)

Для этого потребуется:

- `rye` (`rye sync`)
- `just` (доступный команды выведутся при выполнении `just`)
- Установленный Chrome
- логин и пароль в `.env` для работы автологина (либо вручную в хроме ввести)
- Внутри браузера надо установить расширение Erinome Godville UI+, указать нужные настройки крафта
- `just auto`

## Особенности

- При ошибках парсинга сохраняется исходный код и скриншот страницы. Выводится traceback питона.
- Легкое переключение между ручным, автоматическим с окном и автоматическим headless режимом (рецепты в `justfile`).
- Классы стараются выполнять только свою функцию, поэтому их немало, но так более понятно.
- Состояния (счетчик разворотов, бинго, время влияний и гласов) записываются в файл, чтобы при перезапуске корректно подгрузить прогресс.

## TODO:

- [x] Главный цикл с действиями, разобрать логику
- [x] test bingo+coupon strategy 100% auto
- [x] test gold melting strategy 100% auto
- [x] test zpg arena strategy 100% auto
- [x] test digging strategy 100% auto
- [x] Think about env vars like inventory (absolute or %), hp
- [x] Sleep logic and driver management (sleep, arena, random) (basic)
- [x] track godvoice responses, changes (basic)
- [x] ideabox parsing / analyzing / autoclick (won't do)
- [x] handling errors (screenshot + page_html + log)
- [x] parsing of response (basic text)
- [x] refactoring
- [x] decorators for tracking logic (saving, syncing)
- [x] benchmark parsing, what is faster (from html or seleniumbase)
- [x] can you detect seleniumbase (headless gets detected by HighEntropyValues)
- [x] test activatables opening 100% auto
- [ ] test returning strategy 100% auto
- [ ] crafting as a strategy (need manual testing first)
- [ ] unit tests
- [ ] speed up parsing by parsing from html or some sort of caching (think carefully)
- [ ] Saving progress to DB (with what purpose?)
- [ ] validation of elements in page, if something is wrong - notify (what is it?)


## small things
- timezone GMT+3 always
- is logging alright?
- How fast is parsing? Can we cache something to reduce time with ChromeEngine enabled?
- Is bot human enough?
- How to know if a player has finished a mini quest? What features can we use?
- some stale element reference error when scanning items. div_link in class of activatable means we can click on @ sign.
- after transfering to an arena some strategy might be in progress and it won't find element from environment and spam a couple of errors. I need to think about that.


## Заметки

- Мини-квесты не увеличивают порядковый номер, но содержат подстроку: (мини). Выполненные содержат: (выполнено), не увеличивают номер сразу. Отмененные: ?. Эпик: (эпик)? Гильдийские: ?.
- В разных кирпичных городах разная цена кирпича
- Я бы активировал только Инвайт (для коллекции), другие полезности можно открывать, но много ли будет пользы?
- Для контроля за ответом героя, можно смотреть на последнюю запись, но она может быть перекрыта предыдущей
- При смене дня, если герой в городе, то корректный город находится в панели, а не на карте, и герой переносится вместе с городом (сейчас не совсем корректно).
  - arena normal: Отправить героя на арену для дуэли с другим игроком?
  - arena zpg: like normal, then: Ближайшие 1 мин 41 с арена работает в режиме полного ZPG, не позволяя богам влиять на героев. Вы готовы положиться на волю случая?
  - if late: alert closes, some obscure error emerges
- zpg арена тоже перемещает в Годвилль и выдает 3 предмета, иногда вдобавок кирпич




