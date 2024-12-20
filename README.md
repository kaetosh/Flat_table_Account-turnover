# Flat account turnover

## Программа-генератор сводной таблицы из оборотов счетов 1С
Эта программа предназначена для экономистов, аналитиков, бухгалтеров и других специалистов, которые занимаются составлением сводной финансовой и управленческой отчетности по группе компаний.
Программа позволяет объединить выгрузки из 1С оборотов счета в одну сводную плоскую таблицу, что значительно упрощает дальнейший анализ и подготовку сводных отчетов.

## Создание нового файла Excel
После запуска программы в папке с исходными файлами для обработки создается новый файл Excel с двумя листами: сводная таблица и таблица с отклонениями по оборотам до и после обработки. Второй лист служит для проверки правильности интеграции необходимых строк из оборотов счетов в итоговый файл.

## Тестирование на различных версиях 1С
Программа была протестирована на оборотах счета из 1С:Предприятие 8.3 (Конфигурация "Бухгалтерия предприятия", Конфигурация "Управление производственным предприятием", Конфигурация "1С:ERP Агропромышленный комплекс", Конфигурация "1С:ERP Управление предприятием 2"). Она поддерживает обороты счета с детализацией по субсчетам и субконто любого уровня вложенности.
Внедрена поддержка указания количества.

## Этапы обработки
Под «капотом» скрипта файлы проходят следующие этапы обработки:
1.	после запуска программы пользователю будет предложено выбрать папку с исходными файлами с оборотами счетов в формате .xls/.xlsx;
2.	все обнаруженные в папке файлы пересохраняются в актуальный формат .xlsx текущей версией Excel, установленной на компьютере пользователя (некоторые версии 1С выгружают файлы в устаревшей версии Excel, из-за чего Python не может их корректно обработать);
3.	далее в цикле каждый файл проходит предварительную обработку с помощью библиотеки openpyxl, которая работает непосредственно с excel-файлами, а именно снимается объединение ячеек, удаляются пустые столбцы и строки, устанавливается один дополнительный столбец. В нем будут указаны номера группировок (по уровням иерархии, в соответствии с «+» и «-» слева на полях рабочего листа excel файла). По этим номерам скрипт далее разнесет данные в «плоский» вид. На этом этапе непосредственная работа с excel-файлами заканчивается, данные из этих предобработанных файлов загружаются в библиотеку pandas, предназначенную для работы с большими табличными данными;
4.	также в цикле в каждой таблице скрипт ищет значение «Счет» или «Субконто» и строку, содержащую искомое значение, определяет эту строку как шапку таблицы. Удаляет строки выше шапки таблицы, добавляет столбец с названием файла. В название файла стоит включать идентификатор компании, чтобы в сводном файле разграничивать данные разных компаний;
5.	далее в каждой таблице в столбце с аналитикой скрипт по определенным критериям определяет не заполненные значения (пропущенные субконто или вид субконто), заменяя их значениями «не_заполнено»;
6.	на следующем этапе в строки с самым глубоким уровнем иерархии добавляются значения вышестоящих уровней иерархии, тем самым мы обеспечиваем «плоский» вид таблицы. Строки вышестоящих уровней иерархии будут удалены на следующем этапе как строки с дублирующими оборотами;
7.	на завершающем этапе из таблицы удаляются строки с дубль-оборотами (итоговые обороты, обороты по родительским счетам и по счетам, которые расшифрованы по субконто т. д.);
8.	все обработанные таблицы конкатенируются одна под одной с общей шапкой, происходит выравнивание столбцов, чтобы счета располагались в одном столбце (разные счета имеют субсчета разной глубины);
9.	алгоритмом предусмотрена сверка итоговой суммы по оборотам до обработки таблиц и после для контроля правильности разнесения оборотов в «плоский» вид. Сверка сохраняется на отдельном листе итогового файла.
10.	общая таблица вместе с таблицей сверки выгружается в excel-файл.

## Рекомендации по работе с программой
При работе с программой рекомендуется включать в название файлов идентификатор компании, так как в результирующем файле будет столбец с названием файла, по которому можно идентифицировать каждую компанию в группе.
Допускается в настройках при выгрузке оборотов указывать опцию "Периодичность", однако сверка итогового сальдо до и после обработки покажет ошибку из-за суммирования переходящих остатков между периодами.  

## Уровни иерархии и прочие требования к выгрузкам оборотов счета
Важно отметить, что выгруженные в файлы Excel обороты счетов должны содержать уровни иерархии (группировки строк, которые скрываются/отображаются с помощью кнопок + и – слева в полях). По этим уровням программа будет разворачивать вложенные данные в плоский вид таблицы. Поэтому обороты счетов следует выгружать через меню "Сохранить как" в 1С.
Также следует выгружать обороты счета по его субсчетам.

## Запуск программы
Перед запуском программы убедитесь, что нет открытых файлов Excel.

## Ошибки и улучшения
Обратите внимание, что алгоритм скрипта не может учесть все особенности различных вариаций выгрузок оборотов счетов из 1С, что может привести к ошибкам в работе программы. Если вы столкнулись с какими-либо ошибками или хотите предложить улучшения, пожалуйста, отправьте информацию об ошибках (вместе с образцами выгрузок из 1С, которые не были корректно обработаны программой) или предложения по улучшению по контакту в телеграм @kaetosh.

## Создание .exe файла
Для создания .exe файла с помощью pyinstaller используйте команду:
```bash
pyinstaller --onefile --collect-all pyfiglet --icon=icon.ico main.py
