# gv-auto

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
- [ ] test returning strategy 100% auto
- [ ] test activatables opening 100% auto
- [ ] crafting as a strategy
- [ ] Saving progress to DB (with what purpose?)
- [ ] unit tests
- [ ] decorators for tracking logic (saving, waiting, comparing, syncing)
- [ ] parsing of response (what's changed after activating some item)
- [ ] validation of elements in page, if something is wrong - notify
- [ ] refactoring after tests


## small things
- timezone GMT+3 always
- is logging alright?
- How fast is parsing? Can we cache something to reduce time with ChromeEngine enabled?
- Is bot human enough?
- How to know if a player has finished a mini quest? What features can we use?
- some stale element reference error when scanning items. div_link in class of activatable means we can click on @ sign.


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




