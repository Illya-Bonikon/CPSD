## Опис проєкту

Цей проєкт — це десктопний застосунок для імпорту історичних даних температури, навчання моделі LSTM (довготривалої короткочасної пам’яті) та прогнозування мінімальних і максимальних температур на обраний рік. 

## Вибір технологічного стеку

- **PySide6** так як я не люблю вигляд пітонівських додатків а ткінтері, а часу на те щоб роботи щось гарне та складне у мене не було. Наскільки я знаю це як QT для С++, а тому це гуі буде однаково добре працювати і на мобільних пристроях, що явно круто
    
- **Pandas** — база для обробки даних у Python, тут я використовую його для зручного імпорту CSV, маніпуляцій із датами та підготовки даних.
        
- **Mysql** — Найлегша для мене при взаємодії з csv, тому вибір пав на неї

- **QThread для навчання** — навчання моделі може займати тривалий час, тож я виніс його в окремий потік, щоб UI не зависав і користувач бачив прогрес.

- **LSTM (через власний клас TemperatureLSTM)** — вибір моделі обґрунтований характером задачі: прогнозування часових рядів із сезонністю. LSTM — один із найкращих варіантів для задач, де важливо врахувати послідовність і залежності у часі.
    
## Чому LSTM

Задача прогнозування температури — це часовий ряд із трендами і сезонними коливаннями. Більшість моделей не дуже добре підходять для такого типу даних, бо не враховують послідовності і довгострокові залежності. LSTM має спецефічний механізмами пам’яті, дозволяє моделі “пам’ятати” інформацію про попередні періоди.

## Можливі покращення в майбутньому

    
- **Покращення архітектури моделі**: впровадити двошарові LSTM, Attention-механізми або інші RNN-варіанти для підвищення точності.
    
- **Візуалізація результатів**. Додати графіки, які відображають тренди історичних даних та прогнозів, щоб користувач бачив динаміку температури.
    
- **Інтерпретованість**. Розробити механізми пояснення прогнозів, щоб можна було аналізувати, які фактори найбільше впливають на результат.
    
- **Оптимізація навчання**. Можна додати раннє зупинення, та автоматичний підбір гіперпараметрів.
    

## Висновки

Проєкт успішно демонструє машинне навчання з  десктопним інтерфейсом. Вибір LSTM був логічним для задачі часових рядів, а PySide6 забезпечив зручний інструмент для взаємодії з користувачем. Розробка врахувала типові виклики машинного навчання, а застосунок готовий до подальшого розвитку та масштабування.