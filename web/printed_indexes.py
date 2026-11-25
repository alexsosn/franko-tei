"""Provisional navigation projection of Franko's printed indexes.

Explicit reviewed-in-draft line partitions; no OCR, no guessed page offsets.
"""
from collections import defaultdict
import hashlib
import json
import re

# Inclusive physical scan ranges; end-line ordinals apply only to the frozen
# first-page reading in each section. The source line arrays remain literal.
SECTIONS = (
    ("names", 416, 430, "gpt62-i416-first-image-20261125",
     {"index-left": [1,2,3,4,5,6,7,10,11,12,14,15,16,17,18,29],
      "index-right": [1,2,3,4,5,6,7,8,9,10,11,12,13,20,21,22,23,24,26,27,28,30,31]}),
    ("works", 431, 436, "gpt62-i431-first-image-20261125",
     {"left-a": [3,4,5,6,7,8,10,12,13,14,15,17,18,21,23],
      "left-b": [3], "right-b": [1,3,4,5,8,9,11,12],
      "right-v": [1,2,3,4,6,8,10,13,15]}),
    ("motifs", 437, 458, "gpt62-i437-first-image-20261125",
     {"motifs": [2,3,6,8,9,10,11,13,14,16,18,20,22,24,26,28,30]}),
    ("glossary", 459, 462, "gpt62-i459-first-image-20261125",
     {"left": [2,3,6,7,9,12,14,20,22],
      "right": [2,4,6,8,10,13,15,17,19,20,22]}),
)
SOURCE_BLOBS = {416: "4dc041eecb418dc4f16654feb3f4dd98ed592452",
                431: "e664c2826055e20af0f7696e8e3c4e5f54e2a379",
                437: "df3dba2453e10ee5ee44b9bfc12edb5304cc409f",
                459: "70c19e15133c47d635d4b50c5f80a1af06af040e"}
# Additional explicitly segmented pages in the glossary. None has an
# entry crossing the recorded scan/column boundaries in these drafts.
EXTRA_PAGES = {
    "names": (
        (417, "gpt62-i417-first-image-20261125", {
            "index-left": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49],
            "index-right": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,22,23,24,25,26,27,28,29,30,31,32,33,35,36,37,38,39,41,42,43,44,45,47,48,49]}),
        (418, "gpt62-i418-first-image-20261125", {
            "index-a": [1,2,3,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23],
            "index-b": [1,2,3,4,5,6,7],
            "index-v-left": [1,4,5,6,7,8,10,12,13,14],
            "index-v-right": [2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,24,25,26,27,28,29,30,32,33,34,35,36,37,38,39,40,41,42,43,44,45],
            "index-g": [1,2]}),
        (419, "gpt62-i419-first-image-20261125", {
            "left": [1,2,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49],
            "right-g": [1,2,3],
            "right-d": [4,5,6,7,8,9,10,13,14,18,19,21,22,23,24,25,26,27,28,29,30,32,33,34,35,36,37,38,39,40,41,42,43]}),
        (420, "gpt62-i420-first-image-20261125", {
            "left": [3,4,5,6,7,8,9,10,11,12,13,14,24,25,26,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47],
            "right": [1,2,3,5,6,7,8,9,10,11,12,13,18,19,20,21,22,23,24,26,27,28,29,30,31,32,33,39,40,41,42,43,44,45,46,47,48,49]}),
        (421, "gpt62-i421-first-image-20261125", {
            "left-e": [1,2,3,4,5,6,7,8,9,10],
            "left-zh": [4,5,6],
            "left-z": [1,2,4,5,7,9,10,11,13,14,15,16,17,18,19,20,21],
            "left-i": [1,2],
            "right": [1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,28,29,30,31,32,44,45,46,47,49]}),
        (422, "gpt62-i422-first-image-20261125", {
            "left": [1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,26,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,44,45,46,49],
            "right": [11,12,13,14,15,16,17,18,19,20,21,22,23,25,27,33,34,35,36,37,38,39,40,41,42,43,44,45,48,49]}),
        (423, "gpt62-i423-first-image-20261125", {
            "left-i": [1,2,3,4,12,13,14,15,16,17],
            "left-k": [1,2,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24,25,26,27,28],
            "right-k": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25],
            "right-l": [1,2,3,4,5,6,7,9,10,14,15,16,17,18,19]}),
        (424, "gpt62-i424-first-image-20261125", {
            "left-l": [1,2,6,7,8,9,10,11,12,13,14,15,16],
            "left-m": [1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30],
            "right": [1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24,25,26,28,29,30,31,32,33,34,35,36,37,38,39,41,42,43,44,45,46,48]}),
        (425, "gpt62-i425-first-image-20261125", {
            "left-m": [2,3,4,5,6,7,8,9,10,17,18,19,20,21,23,25,26,27,28,29,31,32],
            "left-n": [1,2,3,6,7,8,9,10,11,12,13],
            "right-n": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,29],
            "right-o": [1,2,3,4,5,6,7,8,9,10,11,12,13,14]}),
        (426, "gpt62-i426-first-image-20261125", {
            "left-p": [2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
            "left-r": [1,2,4,5,6,7,11],
            "right-r": [1,3,4,5,6,7,8,9,10,11,12,17,18,19,20,21,22],
            "right-s": [1,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,20,21,22,23]}),
        (427, "gpt62-i427-first-image-20261125", {
            "left": [1,2,3,4,6,8,9,10,11,12,13,14,15,16,17,19,20,21,22,23,24,25,26,27,28,30,34,35,36,37,38,39,40,41,43,44,45,46,47,48,49],
            "right": [1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,31,32,33,34,35,36,37,38,39,40,41,42,43,48,49]}),
        (428, "gpt62-i428-first-image-20261125", {
            "left-s": [1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],
            "left-t": [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18],
            "left-u": [1,2,3,4,5,6,7],
            "right-u": [1,2,3,4],
            "right-f": [1,2,3,4,5,6,7,8,9,11,19,20,21,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41]}),
        (429, "gpt62-i429-first-image-20261125", {
            "left-f": [1,2,3,4],
            "left-x": [1,2,3,4,5,6,7,9,10,11,12,13,14,15,17,18,20,21,22,23,24,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42],
            "right-x": [1,2,3,4,5,6,7,8,17,18,19,20,21],
            "right-theta": [1,2,3,4],
            "right-ts": [1,2,3,4],
            "right-ch": [2,3,4,5],
            "right-ya": [1,2]}),
        (430, "gpt62-i430-first-image-20261125", {
            "left": [14],
            "right-ya": [4,5,6],
            "right-yu": [1],
            "right-shch": [1]}),
    ),
    "works": (
        (432, "gpt62-i432-first-image-20261125", {
            "left-v": [3,5,7,8,11,12,15,16,17],
            "left-g": [1,2,5,6,7,9,10,11,13,17,20,22,23],
            "left-d": [1,3],
            "right-d": [2,3,4,6,8,9,10,11,14],
            "right-e": [1,2,3,4,5,7,8,10,12,15,17,18,23,24],
            "right-zh": [1,2,3]}),
        (433, "gpt62-i433-first-image-20261125", {
            "left-zh": [2,4],
            "left-z": [2,3,4,5,6,7],
            "left-i": [2,3,4,5,6,7,8,9,10,11,13,14,15],
            "left-k": [2,5,6,7,10,12],
            "right-k": [1,2,3,4,5,6,9,10,11,12,13],
            "right-l": [1,2,3,4,5,6,7,9,10],
            "right-m": [1,2,3,7,8,9,10,12,14,15,16,17,18]}),
        (434, "gpt62-i434-first-image-20261125", {
            "left-m": [1,2,4],
            "left-n": [2,3,4,5,6],
            "left-o": [1,3,4,6,7,9],
            "left-p": [1,2,3,6,7,10,16,19],
            "right-p": [8,9,11,13,14,17,21,25,26,28,29,30,31,32,33,34,35,36,37,38,39,40,41,43,44,47,49]}),
        (435, "gpt62-i435-first-image-20261125", {
            "left-p": [3,6,8,9,12,13,15,17,22,33,35,36,37,38,39,40,41,42,43],
            "left-r": [1,2],
            "right-r": [1,2,5,7,8,10,11,13,17,24,26,27,32,33],
            "right-s": [1,3,6,7,8,9,10,11,12]}),
        (436, "gpt62-i436-first-image-20261125", {
            "left-s": [1,2,6,9,10,11,12,13],
            "left-t": [1,2,11,13,15,16],
            "left-u": [1],
            "left-f": [2,5,6,7],
            "right-x": [2,4,6,8,9,11,12],
            "right-theta": [1],
            "right-ts": [1,4,5,7],
            "right-ch": [1,2,4],
            "right-sh": [2],
            "right-ya": [2,3,5,8]}),
    ),
    "glossary": (
        (460, "gpt62-i460-first-image-20261125", {
            "left": [2,3,4,6,8,10,11,13,15,18,20,22,24,25,26,28,30,32,35,37,38,40,41,43,44,45,49],
            "right": [1,2,3,4,6,8,10,13,15,17,20,22,24,26,27,28,30,31,33,35,36,37,39,40,41,42,44,45,47,48,49]}),
        (461, "gpt62-i461-first-image-20261125", {
            "left": [2,3,6,7,10,11,14,16,17,18,20,21,22,24,26,28,29,31,33,34,36,37,38,40,42,43,44,46,47,48,49],
            "right": [3,7,9,11,13,17,21,22,24,25,26,28,33,35,37,38,40,43,45,46,47,48,49]}),
        (462, "gpt62-i462-first-image-20261125", {
            "left": [1,2,4,9,10,12,14,16,17,19,21,22,24,26,28,30,31,33,35,38,41,42,43,44,46,47],
            "right": [2,3,4,7,8,10,11,13,14,15,17,19,22,24,25,26,27,29,30,31,33,34,35,37,39,40,41,42,44,46,48]}),
    ),
}
# Editorial context is separate from the printed ditto glyphs.
ENTRY_CONTEXTS = {
    (431, "left-a", 5): "апокріф",
    (431, "left-a", 6): "Адамів; апокріф",
    (431, "right-v", 3): "Варнавино; апокр.",
    (431, "right-v", 14): "Веселовскій А. Н.",
    (432, "left-v", 4): "Веселовскій А. Н.",
    (432, "left-v", 6): "Веселовскій А. Н.",
    (432, "left-v", 13): "Вопросы Іоанна Богослова",
    (432, "left-v", 17): "книга",
    (432, "left-g", 21): "Grünbaum M.",
    (432, "left-d", 2): "Давид",
    (432, "right-d", 3): "Данїіл",
    (432, "right-e", 11): "Епіфанїй Кипрський",
    (432, "right-e", 13): "Епіфанїй Кипрський",
    (432, "right-e", 16): "Епіфанїй Кипрський",
    (432, "right-e", 24): "Єфрем Сирин",
    (433, "left-z", 7): "книга",
    (433, "left-i", 9): "апокр.",
    (433, "right-k", 2): "Клїментово; апокр.",
    (433, "right-k", 4): "Книга",
    (433, "right-k", 5): "Книга",
    (433, "right-l", 3): "книга",
    (433, "right-l", 4): "книга",
    (433, "right-m", 10): "Минея",
    (434, "left-m", 2): "Молитви",
    (434, "left-n", 4): "апокр.",
    (434, "left-p", 2): "Павла апостола",
    (434, "left-p", 7): "Палея",
    (434, "left-p", 8): "Палея",
    (434, "left-p", 11): "Палея",
    (434, "left-p", 17): "Палея",
    (434, "right-p", 9): "Палея",
    (434, "right-p", 10): "Палея",
    (434, "right-p", 12): "Палея",
    (434, "right-p", 14): "Палея",
    (434, "right-p", 15): "Палея",
    (434, "right-p", 18): "Палея",
    (434, "right-p", 22): "Палея",
    (434, "right-p", 26): "Палея",
    (434, "right-p", 33): "Паралїпомена",
    (434, "right-p", 35): "Патерик",
    (434, "right-p", 36): "Патерик",
    (434, "right-p", 37): "Патерик",
    (434, "right-p", 38): "Патерик",
    (434, "right-p", 39): "Патерик",
    (435, "left-p", 7): "Пыпинъ А. Н.",
    (435, "left-p", 16): "Поповъ А. Н.",
    (435, "left-p", 23): "Порфирьевъ И. Я.",
    (435, "right-r", 3): "Рукописи",
    (435, "right-r", 6): "Рукописи",
    (435, "right-r", 8): "Рукописи",
    (435, "right-r", 9): "Рукописи",
    (435, "right-r", 11): "Рукописи",
    (435, "right-r", 12): "Рукописи",
    (435, "right-r", 14): "Рукописи",
    (435, "right-r", 18): "Рукописи",
    (435, "right-r", 25): "Рукописи",
    (435, "right-r", 27): "Рукописи",
    (435, "right-r", 28): "Рукописи",
    (435, "right-s", 4): "Сборникъ",
    (435, "right-s", 7): "Сборникъ",
    (436, "left-s", 11): "книга",
    (436, "left-s", 12): "книга",
    (436, "left-t", 12): "Тихонравовъ",
    (436, "left-f", 3): "Fabricius",
    (436, "right-x", 3): "Хожденіє",
    (436, "right-x", 7): "Хожденіє",
    (436, "right-ya", 3): "Jagić V.",
    (436, "right-ya", 4): "Jagić V.",
    (436, "right-ya", 6): "Jagić V.",
    (422, "left", 10): "Індийські",
    (422, "left", 12): "Індия",
    (422, "left", 13): "ефіопська",
    (422, "left", 19): "Іоав",
    (422, "left", 24): "Іоан",
    (422, "left", 25): "Іоан",
    (422, "left", 26): "Іоан",
    (422, "left", 27): "Іоан",
    (422, "left", 36): "пророк",
    (422, "left", 37): "пророк",
    (422, "left", 46): "Іосиф",
    (422, "right", 35): "Ісахар",
    (422, "right", 42): "Ісус",
    (422, "right", 43): "Ісус",
    (422, "right", 44): "Ісус",
    (422, "right", 45): "Ісус",
    (422, "right", 46): "Ісус",
    (423, "left-i", 5): "Іюда",
    (423, "left-k", 2): "син Левії",
    (423, "left-k", 7): "Каінан син",
    (423, "left-k", 10): "мати трьох отроків",
    (423, "left-k", 20): "син Ізмаїла",
    (423, "right-k", 2): "Кирил",
    (423, "right-k", 3): "Кирил",
    (423, "right-k", 7): "негниюче дерево",
    (423, "right-k", 10): "Козма",
    (423, "right-k", 11): "Козма",
    (423, "right-k", 15): "Константин",
    (423, "right-k", 20): "Крон",
    (423, "right-l", 6): "цар вавилонський",
    (423, "right-l", 7): "цар вавилонський",
    (424, "left-l", 14): "Лювійські",
    (424, "left-m", 12): "Макарий",
    (424, "left-m", 14): "Максим",
    (424, "left-m", 18): "Малелеіл",
    (424, "right", 6): "сестра Мойсеєва",
    (424, "right", 12): "син Ізмаїлів",
    (424, "right", 14): "Матѳей",
    (424, "right", 16): "син Енохів",
    (424, "right", 17): "син Енохів",
    (424, "right", 31): "син Левіїв",
    (424, "right", 37): "син Енохів",
    (425, "left-m", 4): "пророк",
    (425, "left-m", 9): "Моавля",
    (425, "left-m", 20): "син Ноїв",
    (425, "left-m", 30): "Мунт",
    (425, "left-n", 10): "пророк",
    (425, "left-n", 12): "син Ізмаїла",
    (425, "right-n", 7): "гл. Неврод",
    (425, "right-n", 18): "Ніл",
    (425, "right-n", 19): "Ніл",
    (425, "right-n", 21): "Нікон",
    (426, "left-p", 4): "Павло",
    (426, "left-p", 16): "Персида",
    (426, "left-p", 29): "цар ізмаїльський",
    (426, "left-r", 2): "ангел",
    (426, "left-r", 3): "Рагуїл",
    (426, "left-r", 7): "город",
    (427, "left", 14): "архангел",
    (427, "left", 15): "архангел",
    (427, "left", 29): "Семеон",
    (427, "left", 37): "Семфора",
    (427, "right", 15): "Симеон",
    (427, "right", 16): "Симеон",
    (428, "left-t", 7): "Теодор",
    (428, "left-t", 8): "Теодор",
    (428, "left-t", 14): "ріка",
    (428, "left-u", 3): "Угорська",
    (428, "right-u", 3): "Урия",
    (428, "right-f", 25): "Фелоной",
    (428, "right-f", 28): "ріка",
    (428, "right-f", 34): "Филип",
    (428, "right-f", 38): "Филон",
    (429, "left-f", 3): "цар",
    (429, "left-x", 14): "Хамово",
    (429, "left-x", 16): "земля",
    (429, "left-x", 25): "Хеврон",
    (429, "left-x", 30): "племя",
    (429, "left-x", 39): "цар",
    (429, "right-x", 2): "цар",
    (429, "right-x", 6): "цар",
    (429, "right-x", 7): "цар",
    (429, "right-x", 8): "цар",
    (429, "right-x", 19): "цар",
    (429, "right-x", 21): "Хус",
    (429, "right-ts", 4): "жінка Мойсеєва",
    (429, "right-ya", 2): "Яков",
    (417, "index-left", 2): "Академія Наук",
    (417, "index-left", 3): "Академія Наук",
    (417, "index-left", 40): "Анна",
    (417, "index-left", 41): "Анна",
    (418, "index-a", 15): "камінь",
    (418, "index-v-left", 6): "Вавилонський",
    (418, "index-v-left", 7): "Вавилонський",
    (418, "index-v-right", 14): "Василий",
    (418, "index-v-right", 15): "Василий",
    (418, "index-v-right", 16): "Василий",
    (419, "left", 10): "Гаїдад",
    (419, "left", 19): "Геннадій",
    (419, "left", 22): "Георгій",
    (419, "left", 23): "Георгій",
    (419, "left", 25): "син Левіїв",
    (419, "left", 41): "Григорій",
    (419, "left", 42): "Григорій",
    (419, "left", 43): "Григорій",
    (419, "left", 44): "Григорій",
    (419, "left", 45): "Григорій",
    (419, "left", 46): "Григорій",
    (419, "left", 47): "Григорій",
    (419, "left", 48): "Григорій",
    (419, "left", 49): "Григорій",
    (420, "right", 12): "Енос",
    (420, "right", 13): "Енос",
    (420, "right", 44): "Єтривська",
    (421, "left-z", 2): "син Яковів",
    (421, "right", 3): "імя Бога",
    (421, "right", 4): "імя Бога",
    (421, "right", 5): "імя Бога",
    (421, "right", 21): "цар",
}
SOURCE_BLOBS.update({
    432: "28bc37a0cacf67dab695ebbece95c5ffe9abfcb3",
    433: "0568936619eeec3611cc51a452eaec081aa1b60f",
    434: "8796bddbeb7e691f8c10fc95c7dc34628a4ec950",
    435: "ced95ae19de5eef9dcaa6f51a72b1b8f6164a8b2",
    436: "58992b023ca6428e2030dff97185fa93f823f400",
    422: "f7ec80af0be6a32a8e3ae7a43805145d78437c72",
    423: "0df835d131f7038572d2ac42ee29a033dd97df94",
    424: "3d068c94633b40d8284f0803420f1806e4c7f3fd",
    425: "090ead89b042709501a7bd8f06feadb13884f309",
    426: "1c2c04fae740ec649a8226103b96f3bb2bebadf7",
    427: "9236f4ee9ae5790f4b8470c76c68b67d0e45f620",
    428: "682bbce13b4aeaa80b05c9f77e497e52a72aa336",
    429: "5c326d0934f04f74bc00879ce8e3f49d7a5bef77",
    430: "dea6a4aff18edadc3a71fc44f20919092e967459",
    417: "d2e707ec31b1757619e7cc293d69de50f562d2fc",
    418: "2f9210d9d0f69d99f61c585cbb923361019861a1",
    419: "300c03db9adbeab783be0dc51f753525f03b4f9f",
    420: "06ddfea746b776b7227d95d7445ba77bfe9c551b",
    421: "a3ff6bfec252e48cb942d0577657017b9fb9dfc8",
    460: "600c616fe03fe0531c7e6d730d4192d88bc43f67",
    461: "d4d6497923b6d002dd66a69f79066cd4bed93e13",
    462: "f54a224cb68cd485fe90b5ff1ddca922d2deaf88",
})
# The following first partitions continue the immediately preceding article.
# Pairs are atomic: do not expose a truncated article or orphan if either
# scan's pinned reading is absent or changed.
CONTINUATIONS = {(422, "right", 1), (425, "left-m", 1),
                 (430, "left", 1), (430, "right-ya", 1),
                 (433, "left-zh", 1), (434, "right-p", 1), (435, "left-p", 1)}
ATOMIC_PAIRS = ((424, 425), (429, 430), (432, 433), (434, 435))
# Running continuation heading is literal evidence, not part of the numeric tail.
CONTINUATION_PREFIXES = {(434, "right-p", 1): "Палея Крех. "}
# Explicit source line break with no printed separator; do not guess missing commas.
# The source remains literal; the parse uses the joined numeric tail only.

NUMBER = r"[1-9][0-9]{0,2}"
TOKEN = NUMBER + r"(?:[—–-]" + NUMBER + r")?"
TAIL = re.compile(r"\s+(" + TOKEN + r"(?:\s*,\s*" + TOKEN + r")*)\s*,?$")


def folio_targets(observations):
    """Only unique explicit Arabic folio observations, never arithmetic."""
    candidates = defaultdict(set)
    for scan, printed in observations:
        if isinstance(printed, str) and re.fullmatch(NUMBER, printed):
            page = int(printed)
            if 1 <= page <= 340:
                candidates[page].add(scan)
    return {p: next(iter(scans)) for p, scans in candidates.items() if len(scans) == 1}


def make_ref(literal, targets, role="citation"):
    numbers = [int(n) for n in re.split(r"[—–-]", literal)]
    start, end = numbers[0], numbers[-1]
    if not 1 <= start <= end <= 340:
        return None
    pages = range(start, end + 1)
    return dict(literal=literal, volume="1", role=role,
                targets=[dict(page=p, scan=targets[p]) for p in pages if p in targets],
                missing=[p for p in pages if p not in targets])


def parse_entry(kind, lines, targets):
    """Derive display label/refs; the underlying lines never change.

    Do not treat arbitrary digits in a motif or glossary gloss as citations.
    Unsupported or suspicious numeric tails stay in the literal label.
    """
    joined = " ".join(lines)
    if kind == "glossary":
        # Two explicitly named forms in one gloss, each with its own page:
        # Попава 199, попавица 241; Ꙗза 12, яза 148.
        paired = re.match(r"^([^\d]+?) (" + NUMBER + r"), ([^\d]+?) (" + NUMBER + r") (.+)$", joined)
        if paired:
            first, p1, second, p2, detail = paired.groups()
            refs = [make_ref(p1, targets), make_ref(p2, targets)]
            if all(refs):
                refs[0]["form"], refs[1]["form"] = first, second
                return f"{first} {p1}, {second} {p2}", detail, refs
        m = re.match(r"^(.+?) (" + TOKEN + r") (.+)$", joined)
        if not m:
            return joined, "", []
        label, literal, detail = m.groups()
        ref = make_ref(literal, targets)
        if ref is None:
            return joined, "", []
        refs = [ref]
        # Explicitly labelled variant references, not every numeral in a gloss.
        for found in re.finditer(r"\bстор\.\s+(" + TOKEN + r")(?=\s|$|[.,;])", detail):
            other = make_ref(found[1], targets, "variant")
            if other:
                refs.append(other)
        return label, detail, refs
    if kind in ("names", "works"):
        # Some source rows use full stops as separators, or lack punctuation.
        # Split only explicit comma/period boundaries. A damaged token such as
        # "2 9" is not two page references or a guessed 29/209.
        m = re.fullmatch(r"(.+?)\s+([0-9][0-9\s,.—–-]*)", joined)
        if m:
            label, tail = m.groups()
            tokens = [token.strip() for token in re.split(r"[,.]", tail) if token.strip()]
            refs = []
            for token in tokens:
                ref = make_ref(token, targets) if re.fullmatch(TOKEN, token) else None
                refs.append(ref or dict(literal=token, volume="1", role="unresolved",
                                        targets=[], missing=[]))
            if any(ref["role"] != "unresolved" for ref in refs):
                return label, "", refs
            return joined, "", []
    m = TAIL.search(joined)
    if not m:
        return joined, "", []
    refs = [make_ref(token.strip(), targets) for token in m[1].split(",")]
    if not all(refs):
        return joined, "", []
    label = joined[:m.start()].rstrip()
    if kind == "motifs":
        label = re.sub(r"(?:\s+\.)+\s*$", "", label)
    if not label:
        return joined, "", []
    return label, "", refs


def read_draft(path):
    raw = path.read_bytes()
    data = json.loads(raw)
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    return data, blob


def build_printed_indexes(pilot, ref):
    files = {}
    for path in sorted(pilot.glob("vol1_scan*_single_reading.json")):
        data, blob = read_draft(path)
        if data["volume"] != "1":
            raise ValueError(f"wrong volume: {path}")
        scan = data["scan_page"]
        if path.name != f"vol1_scan{scan:05d}_single_reading.json" or scan in files:
            raise ValueError(f"duplicate or mismatched scan: {path}")
        files[scan] = (path, data, blob)
    targets = folio_targets((scan, d["printed_page_observed"])
                            for scan, (_, d, _) in files.items() if 76 <= scan <= 415)
    sections = []
    for kind, start, end, reader, partitions in SECTIONS:
        draft_scans = [n for n in range(start, end + 1) if n in files]
        section = dict(volume="1", kind=kind, scans=list(range(start, end + 1)),
                       draft_scans=draft_scans, structured_scans=[], entries=[])
        sections.append(section)
        page_specs = ((start, reader, partitions), *EXTRA_PAGES.get(kind, ()))
        eligible = {scan for scan, reader, _ in page_specs
                    if scan in files and files[scan][1]["reading"]["reader_id"] == reader
                    and files[scan][2] == SOURCE_BLOBS[scan]}
        if kind in ("names", "works"):
            for pair in ATOMIC_PAIRS:
                if not set(pair) <= eligible:
                    eligible.difference_update(pair)
        for scan, reader, partitions in page_specs:
            # A changed/missing reading must not publish stale partitions or block
            # unrelated reader deployments. Re-segment explicitly against new bytes.
            if scan not in eligible:
                continue
            path, draft, blob = files[scan]
            reading = draft["reading"]
            if reading["reader_id"] != reader or blob != SOURCE_BLOBS[scan]:
                continue
            source = dict(volume="1", scan=scan, path="pilot/" + path.name,
                          blob=blob, reader_id=reader, asset_commit=draft["asset_commit"])
            entries = []
            seen_regions = set()
            for region in reading["regions"]:
                region_id = region["id"]
                if region_id not in partitions:
                    if region["kind"] == "body" and region_id != "intro":
                        raise ValueError(f"unpartitioned body region: {path}: {region_id}")
                    continue
                seen_regions.add(region_id)
                lines = region["lines"]
                ends = partitions[region_id]
                if sorted(set(ends)) != ends or ends[0] < 1 or ends[-1] != len(lines):
                    raise ValueError(f"index line partition no longer fits: {path}: {region_id}")
                previous = 0
                for stop in ends:
                    part = [{"id": l["id"], "text": l["text"]} for l in lines[previous:stop]]
                    if (scan, region_id, previous + 1) in CONTINUATIONS:
                        # A region/page boundary never manufactures a new entry.
                        prior = entries[-1] if entries else section["entries"][-1]
                        segments = prior.setdefault("segments", [
                            dict(source=prior["source"], region_id=prior["region_id"],
                                 lines=prior["lines"][:])])
                        segments.append(dict(source=source, region_id=region_id, lines=part))
                        prior["lines"].extend(part)
                        parse_lines = []
                        for segment in segments:
                            texts = [l["text"] for l in segment["lines"]]
                            # Explicit printed running heading; preserve in source.
                            if (segment["source"]["scan"], segment["region_id"], 1) in CONTINUATION_PREFIXES:
                                prefix = CONTINUATION_PREFIXES[(segment["source"]["scan"], segment["region_id"], 1)]
                                if not texts[0].startswith(prefix):
                                    raise ValueError("changed running continuation heading")
                                texts[0] = texts[0][len(prefix):]
                            parse_lines.extend(texts)
                        prior["label"], prior["detail"], prior["refs"] = parse_entry(
                            kind, parse_lines, targets)
                        previous = stop
                        continue
                    label, detail, refs = parse_entry(kind, [l["text"] for l in part], targets)
                    # Only the explicit Abraham block on the pilot motif page.
                    context = ("Авраам" if kind == "motifs" and label.startswith("„")
                               else ENTRY_CONTEXTS.get((scan, region_id, previous + 1), "") if kind in ("names", "works") else "")
                    entries.append(dict(id=f"v1-{scan}-{part[0]['id']}", source=source,
                                        region_id=region_id, lines=part, label=label,
                                        detail=detail, context=context, refs=refs))
                    previous = stop
            if seen_regions != set(partitions):
                raise ValueError(f"missing index regions: {path}")
            section["structured_scans"].append(scan)
            section["entries"].extend(entries)
    return dict(schema_version=1, ref=ref, status="agent_unverified", sections=sections)
