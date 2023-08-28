Settings = ⚙️ Настройки
Support = 🆘 Поддержка
My-Subscriptions = 🗂️ Мои подписки
Back = ↩️ Назад
Administrator = 👨‍💻 Администратор
Add = Добавить
Delete = Удалить
Change = Изменить
Title = Название
Months = Месяцы
Date = Дату
Set-lang = 🌍 <b>Выберите</b> язык, на котором <b>будет общаться</b> бот:

Catalog-add = <b>🗂️ Каталог добавленных подписок:</b>

               { $subs }

Catalog-change = Изменить

Catalog-remove = <b>🗂️ Каталог удаления подписок:</b>

                { $message }

Catalog-edit = <b>🗂️ Каталог изменения подписок:</b>

                { $message }

Are-you-sure = <b>Вы действительно</b> хотите <b>удалить</b> подписку?

Q-A = <b>❓ ЧаВо</b>

          <b>1. Для чего этот бот?</b>
          <i>— Бот создан, с целью напомнить пользователю, когда истечет его подписка в каком-либо сервисе.</i>

          <b>2. Какие сервисы можно добавлять?</b>
          <i>— Неважно где вы оформили подписку, можно добавлять любые сервисы.</i>

          <b>3. Как добавить сервис?</b>
          <i>— Перейдите в раздел Мои подписки и нажмите кнопку Добавить. Заполняйте данные, строго следуя инструкциям: сначала введите название, следующим шагом введите кол-во.бли месяцев (число), затем выберите на календаре, когда напомнить о списании. Подтвердите правильность, и подписка будет добавлена.</i>

Add-service-title = Как называется <b>сервис</b> на который Вы <b>подписались</b>?

                    <b>Пример:</b> <code>Tinkoff Premium</code>

Add-service-months = Сколько <b>месяцев</b> будет действовать подписка?

                    <b>Пример:</b> <code>12 (мес.)</code>

Add-calendar-date = В какую <b>дату</b> оповестить о <b>ближайшем списании</b>?

Check-form = 📩 Проверьте <b>правильность</b> введённых данных:

             <b>Сервис:</b> <code>{ $service }</code>
             <b>Длительность:</b> <code>{ $months } (мес.)</code>
             <b>Оповестить: </b> <code>{ $reminder }</code>

Start-menu = <b>Subscriptions Controller</b> — <b>лучший</b> способ <b>контролировать</b> свои подписки

            📣 <b>Обязательно</b> добавляйте свои подписки в <b>наш сервис</b>, чтобы получать <b>уведомления</b> о ближайшем списании

Nothing-delete = <b>🤷‍♂️ Кажется</b>, здесь <b>нечего удалять...</b>

Nothing-output = <b>🤷‍♂️ Кажется</b>, мы ничего <b>не нашли...</b>

Set-for-delete = <b>Выберите</b> подписку, которую <b>хотите удалить</b>:

Set-for-edit = <b>Выберите</b> подписку, которую <b>хотите изменить</b>:

Error-subs-limit = <b>🚫 Ошибка:</b> Достигнут лимит подписок

Error-len-limit = <b>🚫 Ошибка:</b> Достигнут лимит символов

Error-unsupported-char = <b>🚫 Ошибка:</b> Введены недопустимые символы

Error-range-reached = <b>🚫 Ошибка:</b> Достигнут диапазон значений

Approve-sub-add = <b>✅ Одобрено:</b> Данные успешно записаны

Error-sub-add = <b>❎ Отклонено:</b> Данные не записаны

Approve-sub-delete = <b>✅ Одобрено:</b> Подписка успешно удалена

Reject-sub-delete = <b>❎ Отклонено:</b> Подписка не удалена

Approve-sub-edit = <b>✅ Одобрено:</b> Подписка успешно изменена

Reject-sub-edit = <b>❎ Отклонено:</b> Подписка не изменена

Notification-message = <b>🔔 Уведомление</b>
                       <b>Напоминаем Вам</b>, что ваша подписка <code>{ $service }</code> скоро <b>закончится</b>!

Renew-subscription = Продлить подписку

Set-parameters = Выберите <b>параметр</b>, который <b>хотите изменить</b>:

Edit-form = Выберите <b>подписку</b>, которую <b>хотите изменить</b>:

Check-title-form = 📩 Проверьте <b>правильность</b> изменения данных:

                  <b>{ $service_old_title }</b> → <b>{ $service_new_title }</b>

Check-months-form = 📩 Проверьте <b>правильность</b> изменения данных:

                  <code>{ $service_old_months } (мес.)</code> → <code>{ $service_new_months } (мес.)</code>

Check-reminder-form = 📩 Проверьте <b>правильность</b> изменения данных:

                  <b>{ $service_old_reminder }</b> → <b>{ $service_new_reminder }</b>