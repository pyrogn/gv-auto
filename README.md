# gv-auto

## TODO:

- [x] Главный цикл с действиями, разобрать логику
- [ ] test bingo+coupon strategy 100% auto
- [ ] test gold melting strategy 100% auto
- [ ] test zpg arena strategy 100% auto
- [x] Think about env vars like inventory (absolute or %), hp
- [ ] Saving progress to DB
- [ ] activatables (invite only I think)
- [ ] track godvoice responses
- [ ] ideabox parsing / analyzing / autoclick
- [ ] handling errors (screenshot + log)
- [ ] unit tests


## small things
- timezone GMT+3 always
- is logging alright?
- How fast is parsing? Can we cache something to reduce time with ChromeEngine enabled?


## Заметки

- Мини-квесты не увеличивают порядковый номер, но содержат подстроку: (мини). Выполненные содержат: (выполнено), не увеличивают номер сразу. Отмененные: ?. Эпик: (эпик)? Гильдийские: ?.
- В разных кирпичных городах разная цена кирпича
- Я бы активировал только Инвайт (для коллекции), другие полезности можно открывать, но много ли будет пользы?
- Для контроля за ответом героя, можно смотреть на последнюю запись, но она может быть перекрыта предыдущей
- При смене дня, если герой в городе, то корректный город находится в панели, а не на карте, и герой переносится вместе с городом (сейчас не совсем корректно).
