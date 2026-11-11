# Franko II / physical scan 100 — image-first first reading

- Printed label visible: **18**. Native image: `images/vol2/page-00100.jpg`, 1190×2003.
- Image SHA-256 **from pinned manifest (not independently rehashed in this run):** `2095de26447b9ce0d7ae5371a73424c4416326b35668931b02e63eb051586df2`.
- Asset commit: `e871f32537e81f81896f6ce9a6658aba667db9c5`.
- Reader: GPT-6, one conversation context, direct native-image inspection, first reading without original OCR; no second blind reader or third independent reviewer.
- Status: **agent_unverified / first image reading**. Intended to cover every visible printed line, including the page number, section headings, Church Slavonic source passages and Franko's editorial commentary. Inline forms with ambiguous titla are provisional. `⟦?⟧` means a still-undeciphered character or group; `⟦a/b?⟧` is an explicit alternate. Do not treat this file as image-verified gold, authoritative manuscript transcription, or finalized TEI.
- Literal physical line breaks are retained *within* each region. Different regions represent Franko's edition versus quoted historical sources, not extra scanned pages.

## Printed page number
```text
18
```

## Editorial continuation (12 printed lines)
```text
дитина“, хоча тут домішано дещо і з иньших жерел, а дещо ма-
буть треба покласти на карб поетичної творчости самого Т. Попо-
вича. Західно-европейський, латинський вплив видно в тім, що
з євангельських волхвів, що в „Слові Афродитияна“ являють ся
по просту слугами і висланцями перського царя, тут зроблено
трьох царів — ідея розвита широко в популярній, та на скрізь
фантастичній повісти Івана Гільдесгаймського (Johannes Hil-
desheimensis, Historia de translatione trium regum), що вмер
1375 р. Его книжечка була ще в XV віцї друкована по латинї і
то кілька разів, і по нїмецьки (перший друк вийшов 1480 р.)
і в наших часах передрукована Зімроком (K. Simrock, Die deut-
schen Volksbücher, Bd. IV, стор. 421—474).
```

## Section Е heading
```text
Е. Рукопис о. Яремецького Білахевича, стор. 392.
```

## Quoted Church Slavonic source: gifts of the Magi (10 printed lines)
```text
(О црѣхъ Перскихъ како прїйдоша со дары).
Волсви персиастїи прїйдоша поклонити ся Х⟦р҃/с҃?⟧у на рождество:
Івимельхъ принесе злато ꙗко црю, Іелисѳръ принесе ливанъ ꙗко
Б҃огу, а Єлнавъ принесе змирну ꙗко мертв҃цу. И поклониша ся
ему [н] рѣша: „Тебѣ твоя принесохом, нб҃ныхъ силъ Ісе, никто
же бо инъ исправилъ [бы] неисправленнаѧ, аще не бы ты пришелъ
и см⟦?⟧ксилъ долнѧѧ со вышними. Л⟦?⟧кто [sic! зам. л⟦?⟧кпо] твоей
всемремѫдростной хитрости сопротивника сице побѣдити и низ-
ложити“. І ин⟦?⟧к же пишетъ: пришедше волсви гл҃аху: „се єсть
перстъ бж҃їй“.
```

## Franko's comment (4 printed lines)
```text
Отся статейка зложена очевидно на підставі Слова Афроди-
тияна, хоча автор мав під рукою ще якесь иньше жерело, з якого
взяв останній цитат, а також назви волхвів відмінні від тих, які
подає звичайна церковна традиция (Каспар, Мельхіор і Валтасар).
```

## Section Ж heading (two printed lines)
```text
Ж. Рукопис віденської надв. бібліотеки ч. 88, XVII в.
стор. 44—48.
```

## Quoted Church Slavonic source: Sibyls (6 printed lines)
```text
(Сказаніє ѡ двѣнадесятихъ Сивиллахъ, сирѣчь
пророчицахъ, иже пророчествовахꙋ ѡ преч⟦?⟧тѣй Дв҃ѣ
Мр҃їи и ѡ воплощеніи Сн҃а Бж҃іа). Сїи пророчество-
вахꙋ в разныя времена до Хр҃тва рж҃тва. аще сꙋть и невѣрни,
но чистаго ради житїа ихъ ѿкрывахꙋ ся имъ; земныхъ ради
гл҃аша преди бꙋдꙋщаѧ.
```

## Open glyph-level questions / independent reviewer queue

1. All titla and superscripts in the ten-line Magi source and six-line Sibyl text need independent native-pixel comparison; the undeciphered spans are **not** silent substitutions. Source and edition typography differ substantially.
2. Check `Івимельхъ` / `Іелисѳръ` / `Єлнавъ` directly against enlarged source; these names are not to be normalized to Caspar/Melchior/Balthazar.
3. Audit the exact Church Slavonic forms in the sentence with editor's `[sic! зам. …]` and verify all printed editor's square brackets.
4. Check Ukrainian capitalization, hyphenation and `бібліотеки`/abbreviation in section Ж; maintain true image line breaks.
5. A word-level proofreading pass and two truly independent blind readings remain required; this is an **entire-page first attempt**, not completed verification.
