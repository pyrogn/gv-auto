# gv-auto

## TODO:

- [x] Главный цикл с действиями, разобрать логику
- [x] test bingo+coupon strategy 100% auto
- [x] test gold melting strategy 100% auto
- [ ] test zpg arena strategy 100% auto
- [ ] test returning strategy 100% auto
- [ ] test digging strategy 100% auto
- [x] Think about env vars like inventory (absolute or %), hp
- [ ] Saving progress to DB
- [x] track godvoice responses, changes (basic)
- [x] ideabox parsing / analyzing / autoclick
- [ ] handling errors (screenshot + log + notification)
- [ ] unit tests
- [ ] Sleep logic and driver management (sleep, arena, random)
- [ ] decorators for tracking logic (saving, waiting, comparing, syncing)
- [ ] test activatables opening 100% auto (invite only I think)
- [ ] crafting as a strategy
- [ ] validation of elements in page, if something is wrong - notify


## small things
- timezone GMT+3 always
- is logging alright?
- How fast is parsing? Can we cache something to reduce time with ChromeEngine enabled?
- Is bot human enough?
- How to know if a player has finished a mini quest? What features can we use?


## Заметки

- Мини-квесты не увеличивают порядковый номер, но содержат подстроку: (мини). Выполненные содержат: (выполнено), не увеличивают номер сразу. Отмененные: ?. Эпик: (эпик)? Гильдийские: ?.
- В разных кирпичных городах разная цена кирпича
- Я бы активировал только Инвайт (для коллекции), другие полезности можно открывать, но много ли будет пользы?
- Для контроля за ответом героя, можно смотреть на последнюю запись, но она может быть перекрыта предыдущей
- При смене дня, если герой в городе, то корректный город находится в панели, а не на карте, и герой переносится вместе с городом (сейчас не совсем корректно).
  - arena normal: Отправить героя на арену для дуэли с другим игроком?
  - arena zpg: like normal, then: Ближайшие 1 мин 41 с арена работает в режиме полного ZPG, не позволяя богам влиять на героев. Вы готовы положиться на волю случая?
  - if late: alert closes, some error emerges
- zpg арена тоже перемещает в Годвилль и выдает 3 предмета, иногда вдобавок кирпич
