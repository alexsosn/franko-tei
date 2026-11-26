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
    "motifs": (
        (438, "gpt62-i438-first-image-20261125", {
            "motifs": [2,3,4,5,6,8,10,12,14,16,18,21,23,25,26,28,29,30,32,35,36,37,39,40,42,43,44,46,47,49]}),
        (439, "gpt62-i439-first-image-20261125", {
            "motifs": [1,3,5,9,10,13,15,17,19,21,24,26,29,35,37,40,42,46,48]}),
        (440, "gpt62-i440-first-image-20261125", {
            "motifs": [2,4,6,7,9,12,14,16,19,21,23,24,29,33,34,36,38,40,43,49]}),
        (441, "gpt62-i441-first-image-20261125", {
            "motifs-a": [3,5,11,14],
            "motifs-b": [2,3,5,6,8,10,11],
            "motifs-v": [1,3,7,9,11,13,14,16]}),
        (442, "gpt62-i442-first-image-20261125", {
            "motifs-v": [5,10,11,12,16,20,21,22,23],
            "motifs-g": [3,5,7,10,12,13,15,17,18,20]}),

        (443, "gpt62-i443-first-image-20261125", {
            "motifs": [3,6,9,11,12,14,15,17,19,20,22,24,25,27,31,36,39,41,42,44,45,46,47]}),
        (444, "gpt62-i444-first-image-20261125", {
            "motifs-d": [1,4,6,7,9,10,12,14,15,18,20,22,24,27,31,34,35,38],
            "motifs-e": [2,4,6,7]}),
        (445, "gpt62-i445-first-image-20261125", {
            "motifs": [1,3,4,7,10,12,13,17,19,21,24,26,27,29,31,33,36,38,40,42,44,46,47,49]}),
        (446, "gpt62-i446-first-image-20261125", {
            "motifs-e": [2,4,7],
            "motifs-zh": [2,7,8,10,12,13],
            "motifs-z": [5,6,9,12,14,15,16,17,18,20]}),
        (447, "gpt62-i447-first-image-20261125", {
            "motifs": [2,5,8,9,12,14,15,17,18,22,23,24,25,29,33,36,39,44,47]}),
        (448, "gpt62-i448-first-image-20261125", {
            "motifs": [2,6,8,10,12,14,16,19,20,23,27,32,34,38,40,42,43,45,46,48,49]}),

        (449, "gpt62-i449-first-image-20261125", {
            "motifs-i": [3,4,5,7,8,9,11,13,15,16],
            "motifs-k": [1,4,5,7,10,12,14,16,18,20,22,24,26,29]}),
        (450, "gpt62-i450-first-image-20261125", {
            "motifs-k": [2,4,6,7,8,9,10],
            "motifs-l": [4,5,6,9,10,11,12,14,15,17,19,21,24,25,27,28,30,31,32,34]}),
        (451, "gpt62-i451-first-image-20261125", {
            "motifs": [2,4,6,9,13,16,18,19,21,23,24,25,26,28,30,31,32,34,37,39,42,45,47]}),
        (452, "gpt62-i452-first-image-20261125", {
            "motifs-m": [2,4,7,13,15,17,19,20,23,25,28,29,32,33,35,37],
            "motifs-n": [1,3,5,7,8]}),
        (453, "gpt62-i453-first-image-20261125", {
            "motifs-n": [3,11,12,14,18,20,23,25,27,30],
            "motifs-o": [2,3,6,8,9],
            "motifs-p": [2]}),
        (454, "gpt62-i454-first-image-20261125", {
            "motifs-p": [5,7,11,13,16],
            "motifs-r": [3,5,6,8,10,11,15,16,18,19],
            "motifs-s": [2,3,5,6]}),
        (455, "gpt62-i455-first-image-20261125", {
            "motifs": [2,5,7,9,10,12,13,17,18,20,23,25,27,28,29,31,32,33,34,36,38,41,43,45,47,49]}),
        (456, "gpt62-i456-first-image-20261125", {
            "motifs-s": [2,5,9,12,15,16,17,19,21,24,26,28,30,31,33,34,35,36,37,40,41,43],
            "motifs-t": [1,3]}),
        (457, "gpt62-i457-first-image-20261125", {
            "motifs-t": [2,4,7,8,11,14],
            "motifs-f": [4,6,11,13,15,17],
            "motifs-x": [2,6,8],
            "motifs-ts": [2]}),
        (458, "gpt62-i458-first-image-20261125", {
            "motifs": [1,2,3,5,8,9,11,12,14,16,19]}),
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
    (449, "motifs-i", 6): "Іюда",
    (449, "motifs-i", 8): "Іюда",
    (449, "motifs-i", 9): "Іюда",
    (449, "motifs-i", 10): "Іюда",
    (449, "motifs-i", 12): "Іюда",
    (449, "motifs-i", 14): "Іюда",
    (449, "motifs-i", 16): "Іюда",
    (449, "motifs-k", 2): "Каін",
    (449, "motifs-k", 5): "Каін",
    (449, "motifs-k", 6): "Каін",
    (449, "motifs-k", 13): "Китоврас",
    (449, "motifs-k", 15): "Китоврас",
    (449, "motifs-k", 17): "Китоврас",
    (449, "motifs-k", 19): "Китоврас",
    (449, "motifs-k", 21): "Китоврас",
    (449, "motifs-k", 23): "Китоврас",
    (449, "motifs-k", 25): "Китоврас",
    (449, "motifs-k", 27): "Китоврас",
    (450, "motifs-k", 8): "Кровосумішка",
    (450, "motifs-k", 9): "Кровосумішка",
    (450, "motifs-k", 10): "Кровосумішка",
    (450, "motifs-l", 6): "Лев",
    (450, "motifs-l", 10): "Левгій",
    (450, "motifs-l", 11): "Левгій",
    (450, "motifs-l", 12): "Левгій",
    (450, "motifs-l", 13): "Левгій",
    (450, "motifs-l", 22): "Лот",
    (450, "motifs-l", 25): "Лот",
    (450, "motifs-l", 28): "Лотові дочки",
    (450, "motifs-l", 31): "Люципер",
    (450, "motifs-l", 32): "Люципер",
    (451, "motifs", 7): "Мелхіседек",
    (451, "motifs", 10): "Мелхіседек",
    (451, "motifs", 14): "Мелхіседек",
    (451, "motifs", 17): "Мелхіседек",
    (451, "motifs", 19): "Мелхіседек",
    (451, "motifs", 20): "Мелхіседек",
    (451, "motifs", 24): "Михаїл",
    (451, "motifs", 25): "Михаїл",
    (451, "motifs", 26): "Михаїл",
    (451, "motifs", 27): "Михаїл",
    (451, "motifs", 29): "Михаїл",
    (451, "motifs", 33): "Мойсей",
    (451, "motifs", 35): "Мойсей",
    (451, "motifs", 38): "Мойсей",
    (451, "motifs", 40): "Мойсей",
    (451, "motifs", 43): "Мойсей",
    (451, "motifs", 46): "Мойсей",
    (452, "motifs-m", 3): "Мойсей",
    (452, "motifs-m", 5): "Мойсей",
    (452, "motifs-m", 8): "Мойсей",
    (452, "motifs-m", 14): "Мойсей",
    (452, "motifs-m", 16): "Мойсей",
    (452, "motifs-m", 18): "Мойсей",
    (452, "motifs-m", 20): "Мойсей",
    (452, "motifs-m", 21): "Мойсей",
    (452, "motifs-m", 24): "Мойсей",
    (452, "motifs-m", 26): "Мойсей",
    (452, "motifs-m", 29): "Мойсей",
    (452, "motifs-m", 30): "Мойсей",
    (452, "motifs-n", 2): "Навуходоносор",
    (452, "motifs-n", 4): "Навуходоносор",
    (452, "motifs-n", 6): "Навуходоносор",
    (453, "motifs-n", 13): "Нефталим",
    (453, "motifs-n", 15): "Нефталим",
    (453, "motifs-n", 24): "Ной",
    (453, "motifs-n", 26): "Ной",
    (453, "motifs-o", 3): "Огонь",
    (454, "motifs-r", 4): "Рахиль",
    (454, "motifs-r", 6): "Рахиль",
    (454, "motifs-r", 9): "Рахмани",
    (454, "motifs-r", 16): "Рувим",
    (454, "motifs-r", 17): "Рувим",
    (454, "motifs-r", 19): "Рувим",
    (454, "motifs-s", 3): "Самсон",
    (455, "motifs", 8): "Сатанаіл",
    (455, "motifs", 10): "Сатанаіл",
    (455, "motifs", 11): "Сатанаіл",
    (455, "motifs", 13): "Сатанаіл",
    (455, "motifs", 18): "Семеон",
    (455, "motifs", 19): "Семеон",
    (455, "motifs", 26): "Сивидла",
    (455, "motifs", 28): "Сивидла",
    (455, "motifs", 30): "Сиф",
    (455, "motifs", 32): "Сиф",
    (455, "motifs", 33): "Сиф",
    (455, "motifs", 34): "Сиф",
    (455, "motifs", 35): "Сиф",
    (455, "motifs", 44): "Соломон",
    (455, "motifs", 46): "Соломон",
    (455, "motifs", 48): "Соломон",
    (456, "motifs-s", 1): "Соломон",
    (456, "motifs-s", 3): "Соломон",
    (456, "motifs-s", 6): "Соломон",
    (456, "motifs-s", 10): "Соломон",
    (456, "motifs-s", 13): "Соломон",
    (456, "motifs-s", 16): "Соломон",
    (456, "motifs-s", 17): "Соломон",
    (456, "motifs-s", 18): "Соломон",
    (456, "motifs-s", 20): "Соломон",
    (456, "motifs-s", 22): "Соломон",
    (456, "motifs-s", 25): "Соломон",
    (456, "motifs-s", 27): "Соломон",
    (456, "motifs-s", 29): "Соломон",
    (456, "motifs-s", 31): "Соломон",
    (456, "motifs-s", 35): "Сонце",
    (456, "motifs-s", 36): "Сонце",
    (456, "motifs-s", 37): "Сонце",
    (456, "motifs-s", 41): "Сотона",
    (457, "motifs-t", 3): "Три отроки",
    (457, "motifs-t", 5): "Три отроки",
    (457, "motifs-t", 8): "Три отроки",
    (457, "motifs-t", 9): "Три отроки",
    (457, "motifs-t", 12): "Три отроки",
    (457, "motifs-f", 5): "Фараон",
    (457, "motifs-f", 7): "Фараон",
    (457, "motifs-f", 12): "Фараон",
    (457, "motifs-f", 14): "Фараон",
    (457, "motifs-f", 16): "Фараон",
    (457, "motifs-x", 7): "Хрестове дерево",
    (458, "motifs", 2): "Яков",
    (458, "motifs", 3): "Яков",
    (458, "motifs", 4): "Яков",
    (458, "motifs", 6): "Яков",
    (458, "motifs", 9): "Яков",
    (458, "motifs", 10): "Яков",
    (458, "motifs", 12): "Яков",
    (458, "motifs", 13): "Яков",
    (458, "motifs", 15): "Яков",
    (458, "motifs", 17): "Яков",
    (443, "motifs", 4): "Давид",
    (443, "motifs", 7): "Давид",
    (443, "motifs", 12): "Дан",
    (443, "motifs", 13): "Дан",
    (443, "motifs", 16): "Даниїл",
    (443, "motifs", 18): "Даниїл",
    (443, "motifs", 20): "Даниїл",
    (443, "motifs", 21): "Даниїл",
    (443, "motifs", 23): "Даниїл",
    (443, "motifs", 25): "Даниїл",
    (443, "motifs", 26): "Даниїл",
    (443, "motifs", 32): "Дарий",
    (443, "motifs", 40): "Демони",
    (443, "motifs", 42): "Демони",
    (443, "motifs", 43): "Демони",
    (443, "motifs", 45): "Демони",
    (443, "motifs", 46): "Демони",
    (443, "motifs", 47): "Демони",
    (444, "motifs-d", 2): "Демони",
    (444, "motifs-d", 5): "Демони",
    (444, "motifs-d", 7): "Демони",
    (444, "motifs-d", 8): "Демони",
    (444, "motifs-d", 10): "Демони",
    (444, "motifs-d", 11): "Демони",
    (444, "motifs-d", 13): "Демони",
    (444, "motifs-d", 15): "Демони",
    (444, "motifs-d", 21): "Диявол",
    (444, "motifs-d", 23): "Диявол",
    (444, "motifs-d", 25): "Диявол",
    (444, "motifs-d", 28): "Диявол",
    (444, "motifs-d", 32): "Диявол",
    (444, "motifs-e", 3): "Ева",
    (444, "motifs-e", 5): "Ева",
    (444, "motifs-e", 7): "Ева",
    (445, "motifs", 2): "Ева",
    (445, "motifs", 4): "Ева",
    (445, "motifs", 8): "Єгиптяне",
    (445, "motifs", 11): "Єгиптяне",
    (445, "motifs", 13): "Єгиптяне",
    (445, "motifs", 14): "Єгиптяне",
    (445, "motifs", 22): "Єлисей",
    (445, "motifs", 25): "Єлисей",
    (445, "motifs", 27): "Єлисей",
    (445, "motifs", 30): "Енох",
    (445, "motifs", 32): "Енох",
    (445, "motifs", 34): "Енох",
    (445, "motifs", 37): "Енох",
    (445, "motifs", 39): "Енох",
    (445, "motifs", 41): "Енох",
    (445, "motifs", 43): "Енох",
    (445, "motifs", 45): "Енох",
    (445, "motifs", 47): "Енох",
    (445, "motifs", 48): "Енох",
    (446, "motifs-e", 3): "Єремія",
    (446, "motifs-zh", 3): "Жаби",
    (446, "motifs-zh", 13): "Жінка",
    (446, "motifs-z", 7): "Заулон",
    (446, "motifs-z", 10): "Заулон",
    (446, "motifs-z", 16): "Земля",
    (446, "motifs-z", 18): "Змія",
    (447, "motifs", 3): "Ізмаїл",
    (447, "motifs", 6): "Ізмаїл",
    (447, "motifs", 13): "Ілия",
    (447, "motifs", 15): "Ілия",
    (447, "motifs", 16): "Ілия",
    (447, "motifs", 18): "Ілия",
    (447, "motifs", 19): "Ілия",
    (447, "motifs", 23): "Ілия",
    (447, "motifs", 24): "Ілия",
    (447, "motifs", 25): "Ілия",
    (447, "motifs", 34): "Йосиф",
    (447, "motifs", 37): "Йосиф",
    (447, "motifs", 40): "Йосиф",
    (447, "motifs", 45): "Йосиф",
    (448, "motifs", 3): "Йосиф",
    (448, "motifs", 7): "Йосиф",
    (448, "motifs", 9): "Йосиф",
    (448, "motifs", 11): "Йосиф",
    (448, "motifs", 13): "Йосиф",
    (448, "motifs", 15): "Йосиф",
    (448, "motifs", 17): "Йосиф",
    (448, "motifs", 20): "Йосиф",
    (448, "motifs", 21): "Йосиф",
    (448, "motifs", 24): "Йосиф",
    (448, "motifs", 28): "Йосиф",
    (448, "motifs", 33): "Йосиф",
    (448, "motifs", 35): "Йосиф",
    (448, "motifs", 43): "Ісаак",
    (448, "motifs", 46): "Ісав і Яков",
    (448, "motifs", 49): "Ісав",
    (438, "motifs", 4): "Адам",
    (438, "motifs", 5): "Адам",
    (438, "motifs", 6): "Адам",
    (438, "motifs", 7): "Адам",
    (438, "motifs", 9): "Адам",
    (438, "motifs", 11): "Адам",
    (438, "motifs", 13): "Адам",
    (438, "motifs", 15): "Адам",
    (438, "motifs", 17): "Адам",
    (438, "motifs", 19): "Адам",
    (438, "motifs", 22): "Адам",
    (438, "motifs", 24): "Адам",
    (438, "motifs", 26): "Адам",
    (438, "motifs", 27): "Адам",
    (438, "motifs", 29): "Адам",
    (438, "motifs", 30): "Адам",
    (438, "motifs", 31): "Адам",
    (438, "motifs", 33): "Адам",
    (438, "motifs", 36): "Адам",
    (438, "motifs", 37): "Адам",
    (438, "motifs", 38): "Адам",
    (438, "motifs", 40): "Адам",
    (438, "motifs", 41): "Адам",
    (438, "motifs", 43): "Адам",
    (438, "motifs", 44): "Адам",
    (438, "motifs", 45): "Адам",
    (438, "motifs", 47): "Адам",
    (438, "motifs", 48): "Адам",
    (439, "motifs", 4): "Адама",
    (440, "motifs", 5): "Ангел",
    (440, "motifs", 7): "Ангел",
    (440, "motifs", 8): "Ангел",
    (440, "motifs", 10): "Ангел",
    (440, "motifs", 13): "Ангел",
    (440, "motifs", 15): "Ангел",
    (440, "motifs", 17): "Ангел",
    (440, "motifs", 20): "Ангел",
    (441, "motifs-a", 4): "Асирийцї",
    (441, "motifs-b", 4): "Бог",
    (441, "motifs-b", 6): "Бог",
    (441, "motifs-b", 7): "Бог",
    (441, "motifs-v", 4): "Валаам",
    (441, "motifs-v", 8): "Валаам",
    (441, "motifs-v", 10): "Валаам",
    (441, "motifs-v", 12): "Валаам",
    (441, "motifs-v", 14): "Валаам",
    (441, "motifs-v", 15): "Валаам",
    (442, "motifs-v", 12): "Вино",
    (442, "motifs-g", 8): "Гедеон",
    (442, "motifs-g", 11): "Гедеон",
    (442, "motifs-g", 13): "Гедеон",
    (439, "motifs", 14): "Амемфрия",
    (439, "motifs", 16): "Амемфрия",
    (439, "motifs", 18): "Амемфрия",
    (439, "motifs", 20): "Амемфрия",
    (439, "motifs", 22): "Амемфрия",
    (439, "motifs", 25): "Амемфрия",
    (439, "motifs", 27): "Амемфрия",
    (439, "motifs", 30): "Амемфрия",
    (439, "motifs", 36): "Амемфрия",
    (439, "motifs", 38): "Амемфрия",
    (439, "motifs", 41): "Амемфрия",
    (439, "motifs", 43): "Амемфрия",
    (440, "motifs", 24): "Ангели",
    (440, "motifs", 25): "Ангели",
    (440, "motifs", 34): "Антихрист",
    (440, "motifs", 39): "Арон",
    (440, "motifs", 41): "Арон",
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
    449: "f3bec1abe99f059d7af5d7906274bf48dc76e2e3",
    450: "5fcc6710f90cb569ab52c85ce4fa2418b2c3ad6e",
    451: "6d8dfb85565ff051054755c614a5a8743b6f7c28",
    452: "882b0bd52a26e8c2b1bc59a94f04ca2cf93609de",
    453: "dc3564ddc9a7d88bdd92f5b15ad6ef3616da5c1e",
    454: "c5951c7eac6ca0ea8a8dab8535437c5f4bd6a509",
    455: "c1dbad57365486867e41f34e649875f5d1faeef2",
    456: "90bd14a54099d53e7e90f1221bf926a0f4d3aa98",
    457: "3f4a2f6c33eae9489eb0bd61105531279e5abe64",
    458: "cbd27abd2c5ee361a96f70779dbbfd798521084c",
    443: "ee98bf07de67afe7a54f811ee5525372fb0259a4",
    444: "5aa350401906e658af4414ef092a45f3b81afc0a",
    445: "92ac1209f2403226e7eca952243e5e58556ba71f",
    446: "c87dce1d07212e812a3eb9f241ecaa41a37e1498",
    447: "7c6bb7da27062451db2947fca797c0d7e130c4d0",
    448: "8616a6185c04afece72044e60670490fb17ab81e",
    438: "bbdf5472ce6638754bd4729e46d43ba94da0a468",
    439: "6a24cebe457567c7953a30481566d70c471f30a1",
    440: "7194df7663ca8b387ac0ac2fdc6cf2afe90c6a31",
    441: "d0bab02fb1cd0ec6ed31d9b5ac2702bfe291cc69",
    442: "7413ed6ba3f96c366ecb5acf808130832c219be3",
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
                 (433, "left-zh", 1), (434, "right-p", 1), (435, "left-p", 1), (440, "motifs", 1), (444, "motifs-d", 1), (445, "motifs", 1), (448, "motifs", 1), (452, "motifs-m", 1), (453, "motifs-n", 1)}
ATOMIC_PAIRS = ((424, 425), (429, 430), (432, 433), (434, 435), (439, 440), (443, 444), (444, 445), (447, 448), (451, 452), (452, 453))
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


def complete_folio_targets(observations):
    """Recover only bounded missing folios; never override a conflicting number."""
    observations = list(observations)
    targets = folio_targets(observations)
    estimated = set()
    by_scan = dict(observations)
    observed_pages = {int(p) for _, p in observations if isinstance(p, str) and re.fullmatch(NUMBER, p)}
    anchors = sorted((scan, page) for page, scan in targets.items())
    for (left, first), (right, last) in zip(anchors, anchors[1:]):
        if right - left != last - first or right - left < 2:
            continue
        if not all(scan in by_scan and by_scan[scan] is None for scan in range(left + 1, right)):
            continue
        for scan in range(left + 1, right):
            page = first + scan - left
            if page not in targets and page not in observed_pages:
                targets[page] = scan
                estimated.add(page)
    return targets, estimated


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
                if ref:
                    refs.append(ref)
                    continue
                # A space-separated series of legal page numbers whose joined
                # digits exceed the volume cannot be a single page. Keep the
                # source token, and mark the recovered separator explicitly.
                parts = token.split()
                if (len(parts) > 1 and all(re.fullmatch(NUMBER, p) and int(p) <= 340 for p in parts)
                        and int("".join(parts)) > 340):
                    for p in parts:
                        item = make_ref(p, targets, "separator_recovered")
                        item["printed_literal"] = token
                        refs.append(item)
                else:
                    refs.append(dict(literal=token, volume="1", role="unresolved",
                                     targets=[], missing=[]))
            return label, "", refs
    # I453 Heaven is one article with two separately printed citation groups.
    if kind == "motifs" and joined.startswith("Небо зложене з 10 поверхів:") and len(lines) == 8:
        first, _, a = parse_entry(kind, lines[:5], targets)
        second, _, b = parse_entry(kind, lines[5:], targets)
        if [r["literal"] for r in a+b] == ["40—44", "44—46"]:
            return first + " " + second, "", a+b
    # The source on I442 has two complete adjacent page ranges, with no comma.
    if kind == "motifs" and joined.endswith("258—259 261—262"):
        label = re.sub(r"(?:\s+\.)+\s*$", "", joined[:-len("258—259 261—262")].rstrip())
        refs = [make_ref(token, targets, "separator_recovered") for token in ("258—259", "261—262")]
        for ref in refs:
            ref["printed_literal"] = "258—259 261—262"
        return label, "", refs
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


# Explicit source-entry links, not fuzzy matches on modernized names.
CROSSREFS = {
    "v1-416-index-right-l013": ["v1-416-index-right-l027"],
    "v1-418-index-b-l002": ["v1-418-index-v-right-l021"],
    "v1-421-left-z-l017": ["v1-418-index-v-right-l031"],
    "v1-421-right-l032": ["v1-421-right-l048"],
    "v1-423-right-l-l001": ["v1-423-right-l-l002"],
    "v1-424-left-m-l021": ["v1-424-left-m-l019"],
    "v1-424-left-m-l022": ["v1-424-left-m-l019"],
    "v1-424-right-l019": ["v1-424-right-l033"],
    "v1-425-right-n-l006": ["v1-425-right-n-l005"],
    "v1-425-right-n-l007": ["v1-425-right-n-l005"],
    "v1-428-right-f-l024": ["v1-425-right-n-l027"],
    "v1-432-left-g-l006": ["v1-431-left-a-l009"],
    "v1-433-left-z-l004": ["v1-435-right-r-l006"],
    "v1-433-left-i-l010": ["v1-435-right-r-l008"],
    "v1-434-left-o-l002": ["v1-432-right-e-l011"],
    "v1-435-left-p-l007": ["v1-434-right-p-l048"],
    "v1-435-left-p-l013": ["v1-435-right-r-l009"],
    "v1-435-right-s-l009": ["v1-432-right-e-l019", "v1-432-right-e-l024"],
    "v1-460-right-l009": ["v1-460-right-l001"],
}


def link_audit(data):
    """Separate article coverage, unresolved citations and unanchored mentions."""
    report = []
    for section in data["sections"]:
        missing, unresolved, no_refs = [], [], []
        pages, estimated, anchored = 0, 0, 0
        mention_counts = defaultdict(int)
        mention_exceptions = []
        for entry in section["entries"]:
            ident = dict(id=entry["id"], label=entry["label"])
            if not entry["refs"] and not entry.get("crossrefs"):
                no_refs.append(ident)
            for ref in entry["refs"]:
                pages += len(ref["targets"])
                estimated += sum(bool(t.get("estimated")) for t in ref["targets"])
                anchored += sum(bool(t.get("anchor")) for t in ref["targets"])
                for target in ref["targets"]:
                    review = target.get("mention_review")
                    if review:
                        mention_counts[review["status"]] += 1
                        if review["status"] != "attested":
                            mention_exceptions.append(dict(**ident, page=target["page"], status=review["status"], note=review["note"]))
                if ref["missing"]:
                    missing.append(dict(**ident, literal=ref["literal"], pages=ref["missing"]))
                if ref["role"] == "unresolved":
                    unresolved.append(dict(**ident, literal=ref["literal"]))
        report.append(dict(kind=section["kind"], entries=len(section["entries"]),
                           linked_pages=pages, estimated_pages=estimated,
                           line_anchors=anchored, mention_review=dict(mention_counts), mention_exceptions=mention_exceptions,
                           missing=missing, unresolved=unresolved,
                           no_refs=no_refs, crossrefs=sum(len(e.get("crossrefs", [])) for e in section["entries"])))
    return report


def read_draft(path):
    raw = path.read_bytes()
    data = json.loads(raw)
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    return data, blob


def reconcile_achatis_reference(pilot, files, targets, entry):
    """Distinguish the photographed numeral from the attested destination.

    Only this exact reviewed entry qualifies. Never guess a page from an
    ambiguous digit, or expose a stale reference after the source changes.
    """
    if (entry["source"]["scan"] != 418 or entry["source"]["blob"] != SOURCE_BLOBS[418]
            or entry["label"] != "Ахатис камінь" or entry["refs"][0]["literal"] != "215"
            or entry["supplementary_reading"][0]["line_id"] != "index-a-l014"
            or entry["supplementary_reading"][0]["text"] != "Ахатис камінь 215"):
        return
    unresolved = dict(literal="215", volume="1", role="unresolved", targets=[], missing=[])
    entry["refs"] = [unresolved]
    path = pilot / "reviews/vol1_scan00418_unstamped_facs_20261126.json"
    if not path.is_file() or 320 not in files or targets.get(245) != 320:
        return
    evidence = json.loads(path.read_text(encoding="utf-8")).get("citation_crosscheck", {})
    target_path, target, blob = files[320]
    if (evidence.get("line_id"), evidence.get("photo_literal"),
            evidence.get("target_page"), evidence.get("target_scan"),
            evidence.get("target_path"), evidence.get("target_blob"),
            evidence.get("target_line_id")) != (
            "index-a-l014", "215", 245, 320, "pilot/vol1_scan00320_single_reading.json",
            "e8b772faa8d2ac06d1596639a3142d84f5076865", "moses-apparatus-l021"):
        return
    if (target_path.name != "vol1_scan00320_single_reading.json" or blob != evidence["target_blob"]
            or target["printed_page_observed"] != "245"
            or target["source_image_sha256"] != evidence.get("target_image_sha256")):
        return
    lines = [line["text"] for region in target["reading"]["regions"]
             for line in region["lines"] if line["id"] == evidence["target_line_id"]]
    if lines != [evidence.get("target_text")] or lines[0].count("ахатисъ") != 2:
        return
    ref = make_ref("245", targets, "editorial_citation")
    ref["printed_literal"] = "215"
    ref["evidence"] = dict(path=evidence["target_path"], blob=blob,
                           line_id=evidence["target_line_id"], text=lines[0])
    ref["targets"][0]["anchor"] = dict(suffix="single_reading", reader_id=target["reading"]["reader_id"], line_id=evidence["target_line_id"], text=lines[0], region_kind="note")
    entry["refs"] = [ref]


def reconcile_ishmael_reference(files, targets, entry):
    # The draft reads "2 9"; page 269 contains the exact variant Измаилтяне
    # in the apparatus. Do not silently overwrite the uncertain source token.
    if entry["id"] != "v1-421-right-l027" or 344 not in files or targets.get(269) != 344:
        return
    path, draft, blob = files[344]
    if blob != "2d27b4ceb62a722d43191f18d54c54cbf58ba7c6" or draft["printed_page_observed"] != "269":
        return
    hits = [(region, line) for region in draft["reading"]["regions"] for line in region["lines"]
            if line["id"] == "gideon-apparatus-l020" and "Измаилтяне" in line["text"]]
    if len(hits) != 1:
        return
    region, line = hits[0]
    for i, ref in enumerate(entry["refs"]):
        if ref["role"] == "unresolved" and ref["literal"] == "2 9":
            corrected = make_ref("269", targets, "editorial_citation")
            corrected["printed_literal"] = "2 9"
            corrected["evidence"] = dict(path="pilot/" + path.name, blob=blob, line_id=line["id"], text=line["text"])
            corrected["targets"][0]["anchor"] = dict(suffix="single_reading", reader_id=draft["reading"]["reader_id"],
                                                       line_id=line["id"], text=line["text"], region_kind=region["kind"])
            entry["refs"][i] = corrected


def reconcile_darius_reference(files, targets, entry):
    # The source text spans pp.321–322; the parallel motif on I442 gives
    # 320–321, and I443 has no numeral. Preserve both source readings.
    printed = {"v1-442-motifs-v-l006": "320—321", "v1-443-motifs-l028": ""}
    if entry["id"] not in printed:
        return
    literal = printed[entry["id"]]
    if ([r["literal"] for r in entry["refs"]] != ([literal] if literal else [])
            or targets.get(321) != 396 or targets.get(322) != 397):
        return
    evidence = [(396, "dc158de3ca4c7583e4ca2892414244a64b648ecd", "belshazzar-body-l005"),
                (397, "27882c2c25acdcb4c07616a52e2835df284e7113", "belshazzar-body-l001")]
    anchors = []
    for scan, blob, line_id in evidence:
        if scan not in files or files[scan][2] != blob:
            return
        path, draft, _ = files[scan]
        hits = [(r, l) for r in draft["reading"]["regions"] for l in r["lines"]
                if r["id"] == "belshazzar-body" and l["id"] == line_id]
        if len(hits) != 1:
            return
        region, line = hits[0]
        anchors.append(dict(suffix="single_reading", reader_id=draft["reading"]["reader_id"],
                            line_id=line_id, text=line["text"], region_kind=region["kind"]))
    ref = make_ref("321—322", targets, "editorial_citation")
    ref["printed_literal"] = literal
    ref["evidence"] = [dict(path="pilot/" + files[scan][0].name, blob=blob, line_id=line_id)
                       for scan, blob, line_id in evidence]
    for target, anchor in zip(ref["targets"], anchors):
        target["anchor"] = anchor
    entry["refs"] = [ref]


# Four explicit index numerals contradict the actual attested text.
MOTIF_EDITORIAL = {
    "v1-456-motifs-s-l025": ("235", 285, 360, "598615576266d8ac04638e6a380e7dfbf3b2e0e4", "solomon-inheritance-l001"),
    "v1-456-motifs-t-l002": ("351", 331, 406, "846e8d740b5fa3e4db792c6e73175928cff661ec", "abraham-body-l024"),
    "v1-457-motifs-f-l005": ("222", 225, 300, "2c17b484068c5fe7253afca57af0190ed74d3fed", "pharaoh-dream-l013"),
    # I/184 footnote-link and language-marker update; motif anchor, text, folio and geometry unchanged.
    "v1-458-motifs-l001": ("199", 109, 184, "291c547dd7eb3bc1ff73b5decc108e906ae29941", "jacob-ladder-continuation-l004"),
}


def reconcile_motif_reference(files, targets, entry):
    if entry["id"] not in MOTIF_EDITORIAL:
        return
    literal, page, scan, blob, line_id = MOTIF_EDITORIAL[entry["id"]]
    if targets.get(page) != scan or scan not in files or files[scan][2] != blob:
        return
    if literal == "351":
        if entry["refs"] or not entry["label"].endswith(" 351"):
            return
        entry["label"] = re.sub(r"(?:\s+\.)+\s*$", "", entry["label"][:-4].rstrip())
    elif [r["literal"] for r in entry["refs"]] != [literal]:
        return
    path, draft, _ = files[scan]
    hits = [(r, l) for r in draft["reading"]["regions"] for l in r["lines"] if l["id"] == line_id]
    if len(hits) != 1:
        return
    region, line = hits[0]
    ref = make_ref(str(page), targets, "editorial_citation")
    ref["printed_literal"] = literal
    ref["evidence"] = dict(path="pilot/" + path.name, blob=blob, line_id=line_id, text=line["text"])
    ref["targets"][0]["anchor"] = dict(suffix="single_reading", reader_id=draft["reading"]["reader_id"],
                                       line_id=line_id, text=line["text"], region_kind=region["kind"])
    entry["refs"] = [ref]


# Manual mention-level review of glossary articles. The source entry
# itself is already pinned by SOURCE_BLOBS; each destination is separately
# pinned. Keep negative/conflicting observations separate from attestations.
GLOSSARY_MENTION_REVIEWS = {
    ("v1-462-right-l001", "204"): (204, "5c75b798a27b4431aa2d019dca1db628030c1bd2", "not_found", [], "No Сраща form on cited page; adjacent pp203/205 screened."),
    ("v1-462-right-l003", "55"): (55, "38c3fb40eaa869564da66320803629a9fd94be63", "attested", ["enoch-face-l011"], "ставила, in the weighing passage"),
    ("v1-462-right-l004", "230"): (230, "9279c63602505baa96dc7145852afa0c6c634db6", "attested", ["moses-storks-l004","moses-storks-l005","moses-storks-l006","moses-storks-l007","moses-storks-l010","moses-storks-l012"], "стєрковы (including split стєр-/ковы), стєрковѣ, стєркъ, стєркы"),
    ("v1-462-right-l005", "80"): (80, "037264054c20b2862c007e18f10b48010a9d2482", "not_found", [], "No Сторганіе or строганіе form in cited draft; p81 screened. Related carving context alone is insufficient."),
    ("v1-462-right-l008", "319"): (319, "38566f1ddfed36b129269f81e88409b21d9031fe", "reading_conflict", ["daniel-body-l012"], "Draft стремлство versus index Стрельство; both in description of the lion, but not identical."),
    ("v1-462-right-l009", "116"): (116, "a72da3321c5ebf7fc36824e3ae3f2e3478437381", "attested", ["palaea-exegesis-continuation-l010"], "стропотная"),
    ("v1-462-right-l011", "122"): (122, "44299b50b2be7a851e73b579530b5087c48a1225", "attested", ["esau-death-l011","esau-death-l012"], "сулицю twice"),
    ("v1-462-right-l012", "82"): (82, "da112312980313957ccd4e23b025a4ab2491fdaa", "reading_conflict", ["abraham-barisat-continuation-l031"], "Draft съвѣнимъ versus index Съвѣненъ; morphology and reading require facsimile check."),
    ("v1-462-right-l014", "52"): (52, "d2d1b7c27e456929976a480a17cdf7417ce9ca19", "attested", ["enoch-flood-l010"], "тимѣнїе велико"),
    ("v1-462-right-l015", "17"): (17, "38a94d96f49b521547b51e4d7506d1ca1a1a01e9", "attested", ["witness-a-paradise-l013"], "тихостиве; apparatus has a different reading стихостію"),
    ("v1-462-right-l016", "240"): (240, "a6954635b1a97b7096b9d835ef1692ee0dc8bec2", "attested", ["first-stone-end-l001"], "ѿ токы, wound treatment context"),
    ("v1-462-right-l018", "201"): (201, "0cca7570a4cf99f5f3ba3f0cb8bd7a04ae437a73", "attested", ["dan-anger-l024"], "трегубу силу"),
    ("v1-462-right-l020", "232"): (232, "d38e7eccf93c77748df99176ab2a5f8f27341f4f", "attested", ["moses-rod-discovery-l005"], "палица ... трєстата"),
    ("v1-462-right-l023", "53"): (53, "915cd7c08cbb33446bc6f03daef2bf71c4914ac1", "attested", ["enoch-address-l008","enoch-address-l010"], "тучна twice; index conjectures точенъ"),
    ("v1-462-right-l025", "241"): (241, "77988d2ac1fdbabde73695c24466d22b76854cc7", "attested", ["fifth-stone-end-l004"], "тажарь twice on the same line"),
    ("v1-462-right-l026", "124"): (124, "a4b7ee5c42528f5619fdc6e06969fa9005277257", "attested", ["joseph-pit-l007"], "цр҃ьскаго увясла; inflected variant"),
    ("v1-462-right-l027", "176"): (176, "b09717d3027997cf405bd574a112cd27328e9e68", "attested", ["reuben-continuation-l020"], "удолеет"),
    ("v1-462-right-l028", "22"): (22, "7726607b3d45fb42f310a5eb4dec8d99aad6be66", "attested", ["witness-a-continuation-l033"], "оукрыши дрива"),
    ("v1-462-right-l030", "74"): (74, "acccfea4ebf06a816cb1fe119d61826829e9eb71", "reading_conflict", ["munt-nimrod-l002"], "Draft оумлрдися and оумечную; neither securely attests Ѹмеленъ. Recheck print."),
    ("v1-462-right-l031", "303"): (303, "dc9953ffb2fb0182ca760d7232925558930ce841", "attested", ["elisha-prologue-opening-l004"], "златая бо оунници (heifer in the Elisha narrative)"),
    ("v1-462-right-l032", "179"): (179, "708f0bebf3f75a62bdfa2979d91f4d0dfd9adf00", "not_found", [], "No Ѹностенъ form on cited draft; p180 screened."),
    ("v1-462-right-l034", "182"): (182, "22a01b9a5dae2eb3907369a5c39cad0378ddb8ff", "attested", ["levi-angel-l034"], "урода"),
    ("v1-462-right-l035", "242"): (242, "205c99e8703f1cb71bb694ecfa0dacff38a6bcb2", "reading_conflict", ["eighth-stone-l001"], "Draft синь ес[ть] versus index Ѹсинь; colour context but initial vowel absent."),
    ("v1-462-right-l036", "121"): (121, "e784cd27d856d67877ff61081230b78ec1211b2a", "attested", ["jacob-wrestling-l007"], "утропи жилы его"),
    ("v1-462-right-l038", "190"): (190, "77a7f275a4d15c1aa8fe9204723f5ffb473a5ae2", "attested", ["judah-family-continuation-l029","judah-family-continuation-l030"], "утва-/ривши ся"),
    ("v1-462-right-l040", "190"): (190, "77a7f275a4d15c1aa8fe9204723f5ffb473a5ae2", "attested", ["judah-family-continuation-l030"], "утварію"),
    ("v1-462-right-l041", "185"): (185, "93434dacef0b7f696852105200b8d04664e19f0c", "attested", ["levi-enoch-continuation-l006"], "явленици"),
    ("v1-462-right-l042", "205"): (205, "6d9572016803739a0fa6b56c00c2a0e0a10253d1", "attested", ["naphtali-visions-l016"], "съ ядринами"),
    ("v1-462-right-l043", "205"): (205, "6d9572016803739a0fa6b56c00c2a0e0a10253d1", "attested", ["naphtali-visions-l020"], "держа ядра"),
    ("v1-462-right-l045", "12"): (12, "c27fc69f5897903f8e45de15dc026fda2b19f925", "not_found", [], "No Ꙗза form found in cited draft; pp11/13 screened."),
    ("v1-462-right-l045", "148"): (148, "c45e9c7cd4f00ae6d0178074477f675bf0e39eec", "reading_conflict", ["charadrius-l010"], "Draft язву болящаго versus index яза; different stem, same illness context."),
    ("v1-462-right-l047", "226"): (226, "6e6360c9ab0d78ccdb250d4ec307f0c65257f2ae", "attested", ["moses-birth-l019"], "яскъ"),
    ("v1-462-left-l001", "290"): (290, "f4be2ac35e91093e49bcf5ae8f64c6127e7220c5", "attested", ["solomon-bride-riddles-l009","solomon-bride-riddles-l014"], "просатаеве"),
    ("v1-462-left-l002", "11"): (11, "3ea87c2fb9ab462ec7bbd0e6c5bc403e4c336936", "reading_conflict", ["satanail-witness-a-l009"], "Draft просыпас[а] versus index Просѹти ся; distinct reading, similar gloss."),
    ("v1-462-left-l003", "107"): (107, "2f6175ac753d060741c7e2f74b600c66fcd919ae", "attested", ["witness-d-end-l001"], "прузы (plural of пругъ)"),
    ("v1-462-left-l005", "286"): (286, "2c9e8dc4beb1968e7948edebc670d91f4953f484", "attested", ["solomon-test-of-spouses-end-l002"], "мечь прудень; index itself discusses erroneous reading, not an endorsement of the lemma."),
    ("v1-462-left-l010", "68"): (68, "5ddcf7b9684c6384e9d559d2cc493bed2c8720d2", "attested", ["noah-apparatus-continuation-l009"], "лютостьма радьма (apparatus)"),
    ("v1-462-left-l011", "81"): (81, "dcb06e144f035c2781b25d0cf747369e07a406a2", "attested", ["abraham-reflection-l030"], "ратесы"),
    ("v1-462-left-l013", "205"): (205, "6d9572016803739a0fa6b56c00c2a0e0a10253d1", "attested", ["naphtali-visions-l016"], "рухла"),
    ("v1-462-left-l015", "54"): (54, "df4a8004315a422a1bb45c9b11b4989b9ac82344", "attested", ["enoch-knowledge-continuation-l004"], "садовїя"),
    ("v1-462-left-l017", "51"): (51, "b36c7387633e2e1ace6d49f377644afb5df16c00", "attested", ["enoch-eighth-day-l011","enoch-eighth-day-l012"], "самовѣ-/ченъ"),
    ("v1-462-left-l018", "290"): (290, "f4be2ac35e91093e49bcf5ae8f64c6127e7220c5", "attested", ["solomon-bride-riddles-l004"], "сандалъ"),
    ("v1-462-left-l020", "142"): (142, "92128ab338de95004e6cd5d2b6a9397453406b33", "attested", ["joseph-embraces-benjamin-l009"], "сатовных; index conjectures сановенъ"),
    ("v1-462-left-l022", "143"): (143, "e69bae32181729d7672d7e91e842d2185843696c", "attested", ["joseph-embraces-benjamin-end-l003","joseph-embraces-benjamin-end-l004"], "свер-/сти"),
    ("v1-462-left-l023", "227"): (227, "9f2c022715c14c508988ff53d0196b21ed623907", "reading_conflict", ["moses-crown-test-l034"], "Draft сикливъ versus index Свикливъ; consonant discrepancy."),
    ("v1-462-left-l025", "175"): (175, "768be23f0db0afccca9ca7eb06a012268d7f18d8", "attested", ["spirits-continuation-l021"], "сердоболя"),
    ("v1-462-left-l027", "192"): (192, "d4dd9f441617bf3ee0992704c142dd04e4377491", "attested", ["judah-exhortation-continuation-l007"], "сетное"),
    ("v1-462-left-l029", "80"): (80, "037264054c20b2862c007e18f10b48010a9d2482", "attested", ["abraham-idols-l022"], "сечива"),
    ("v1-462-left-l031", "225"): (225, "2c17b484068c5fe7253afca57af0190ed74d3fed", "attested", ["pharaoh-dream-l003","pharaoh-dream-l004","pharaoh-dream-l005"], "скалвы, скалву (three occurrences)"),
    ("v1-462-left-l032", "179"): (179, "708f0bebf3f75a62bdfa2979d91f4d0dfd9adf00", "reading_conflict", ["simeon-exhortation-continuation-l018"], "Draft въ сказѣ; index Скважь conjectures сказъ. No exact attestation of the printed lemma."),
    ("v1-462-left-l034", "278"): (278, "8a425baab12fbfa38c1effb9c2f4a28977ed6eaa", "not_found", [], "No Скѹпь form in cited-page draft; adjacent pp277/279 screened."),
    ("v1-462-left-l036", "239"): (239, "a082132a80faebe611eadb3f81349869f965b888", "attested", ["tabernacle-l005","tabernacle-l012"], "синет; синету"),
    ("v1-462-left-l039", "318"): (318, "4b1f345648abaecccef53e4cbe55e830a38a3fb8", "reading_conflict", ["three-youths-l032"], "Draft слудьбу versus index Слѹдъва; differing consonants."),
    ("v1-462-left-l042", "68"): (68, "5ddcf7b9684c6384e9d559d2cc493bed2c8720d2", "not_found", [], "No Слѹти form in cited-page draft; adjacent pp67/69 screened. Apparatus нарѣцается is another word."),
    ("v1-462-left-l043", "216"): (216, "384ac38e03a72913e434156aaebbf6c72cfd2f22", "attested", ["joseph-l036"], "сока̑чиямъ"),
    ("v1-462-left-l044", "320"): (320, "a78c5745f4488cb42c581b30cddfd896ae9672aa", "attested", ["daniel-body-l003"], "сочивом"),
    ("v1-462-left-l045", "236"): (236, "1ed6b1698d8a957fa0ee488b023f9ea8106b7c6c", "attested", ["joseph-bones-opening-l011","joseph-bones-opening-l012"], "сочити; сочит[и]"),
    ("v1-462-left-l047", "45"): (45, "06466357e56612a89d893ccf4f6310923e1b05e1", "attested", ["enoch-fifth-heaven-continuation-l001"], "сполини"),
    ("v1-461-right-l001", "180"): (180, "a80653e2a4cf2559ecce066e73cdbf9945114cff", "attested", ["simeon-end-l011"], "по закону плачаному"),
    ("v1-461-right-l004", "242"): (242, "205c99e8703f1cb71bb694ecfa0dacff38a6bcb2", "attested", ["twelfth-stone-l005"], "дѣло пленичное"),
    ("v1-461-right-l008", "257"): (257, "18ef6b4719e59c5325669139cd727b1ecdbf4c63", "not_found", [], "No Плесница form in current cited-page draft; adjacent pp256/258 screened."),
    ("v1-461-right-l010", "77"): (77, "174981a415f9241381bbee0e9aab594c41a5f877", "attested", ["witness-b-babel-l006"], "плиньфы"),
    ("v1-461-right-l012", "179"): (179, "708f0bebf3f75a62bdfa2979d91f4d0dfd9adf00", "not_found", [], "No Поваждати form on cited page; pp178/180 screened."),
    ("v1-461-right-l014", "178"): (178, "45ec408d50fffe9632b46758e7c3456bbed462f9", "attested", ["simeon-continuation-l036"], "зла моего не погоня; index quotes погона, inflected/orthographic counterpart in same phrase"),
    ("v1-461-right-l018", "178"): (178, "45ec408d50fffe9632b46758e7c3456bbed462f9", "attested", ["simeon-continuation-l011"], "по помазе паствины; the index also quotes a variant, but cites this page"),
    ("v1-461-right-l022", "176"): (176, "b09717d3027997cf405bd574a112cd27328e9e68", "attested", ["reuben-continuation-l005","reuben-exhortation-l020"], "поноса; поносъ"),
    ("v1-461-right-l023", "199"): (199, "32ec4b99b36b589549c350ea56701f81b002f066", "reading_conflict", ["zebulun-mercy-l014"], "Draft понаву versus index Попава; textile/sail context supports comparison, but consonant differs."),
    ("v1-461-right-l023", "241"): (241, "77988d2ac1fdbabde73695c24466d22b76854cc7", "reading_conflict", ["seventh-stone-l018","seventh-stone-l019"], "Draft понявицею; понявица versus index попавица. Preserve distinct source forms."),
    ("v1-461-right-l025", "187"): (187, "69a107d7e5351c745e8a8734941e5c98203850e6", "attested", ["levi-exhortation-continuation-l017"], "послух да будетъ Бъ҃"),
    ("v1-461-right-l026", "228"): (228, "ce883a2b70b8168f649594928df821011041773c", "attested", ["moses-kikanos-l014"], "потвори"),
    ("v1-461-right-l027", "70"): (70, "8721974b02b174ef9de2fd91b2dab7e3cb2c941f", "reading_conflict", ["witness-b-flood-continuation-l009"], "Draft прадужному versus index Прадѹхный, referring to the rain; consonant differs."),
    ("v1-461-right-l029", "71"): (71, "dc52e638c6260922fa4e37e8cdcd149d6bc0669a", "reading_conflict", ["witness-b-apparatus-l011","witness-b-apparatus-l012"], "Note 51 reads пра-/пражно, index Прапраждно. Retain the split and differing consonant until checked."),
    ("v1-461-right-l034", "55"): (55, "38c3fb40eaa869564da66320803629a9fd94be63", "attested", ["enoch-face-l011"], "превѣсила"),
    ("v1-461-right-l036", "61"): (61, "44c704cb9c87d83fb77271ad715c8cfd09895bd2", "attested", ["enoch-poor-continuation-l001"], "презорство"),
    ("v1-461-right-l038", "66"): (66, "032cee85230a5807d7c4a2f2e136eb6d7eca51e4", "attested", ["noah-ark-l003"], "ѿ древъ преки"),
    ("v1-461-right-l039", "178"): (178, "45ec408d50fffe9632b46758e7c3456bbed462f9", "attested", ["simeon-continuation-l034"], "прилагатая"),
    ("v1-461-right-l041", "100"): (100, "1d01df626b517e2ef28b7f5554595bbbbb826e8d", "not_found", [], "No Притраненъ form on cited page; adjacent pp99/101 screened."),
    ("v1-461-right-l044", "185"): (185, "93434dacef0b7f696852105200b8d04664e19f0c", "reading_conflict", ["levi-priesthood-l013"], "Cited page has noun прокудници, not the verb Прокѹдити. Actual verb прокудихом occurs on p189, but this does not prove that the index intended p189."),
    ("v1-461-right-l046", "185"): (185, "93434dacef0b7f696852105200b8d04664e19f0c", "attested", ["levi-priesthood-l013"], "прокудници"),
    ("v1-461-right-l047", "220"): (220, "d37c2e24251f0f05bd81ea01c204b0dbefe8a5cb", "attested", ["benjamin-l006"], "прокꙋженіе"),
    ("v1-461-right-l048", "194"): (194, "6418d63c5f76e885a24e5e5f98283ed4dc3d339a", "reading_conflict", ["judah-prophecy-continuation-l003"], "Draft земли прикужа versus index Прокѹжа; consonant/vowel discrepancy."),
    ("v1-461-right-l049", "68"): (68, "5ddcf7b9684c6384e9d559d2cc493bed2c8720d2", "attested", ["witness-b-flood-l002"], "пронорливи"),
    ("v1-461-left-l001", "110"): (110, "b8debdc372be7ad0dcc8d8c441b272e0d0c4063a", "attested", ["jacob-sariel-l027"], "могуты племенъ земных; not the verb възмогуть"),
    ("v1-461-left-l003", "284"): (284, "548acb4cfd8c1f3d175a810f4898b9bcb5c45d6d", "attested", ["salt-riddle-l002","salt-riddle-l003"], "мыски; мыска, in the mule riddle"),
    ("v1-461-left-l004", "126"): (126, "9ce3facee020fd0cf58f89324a19b794b598aff4", "reading_conflict", ["joseph-lament-in-pit-l003"], "Draft незрѣлными in the phrase съ въздыханїи незрѣлными; index Нежрѣленъ. Check omitted consonant against facsimile."),
    ("v1-461-left-l007", "130"): (130, "f5459796ea083d6c27f655406f9d99c8c99104dc", "attested", ["jacob-lament-continuation-l012"], "непщуя"),
    ("v1-461-left-l008", "8"): (8, "770cc948a813c9f3cf868fe2d1bd3f5072fa84cd", "attested", ["creation-continuation-l002"], "не растаан'но; source spacing retained"),
    ("v1-461-left-l011", "66"): (66, "032cee85230a5807d7c4a2f2e136eb6d7eca51e4", "attested", ["noah-ark-l014"], "ногъ или слонъ; animal context, not a body part"),
    ("v1-461-left-l012", "138"): (138, "628fd3230a1ef536a9763d8ddc6488c5840a8b8d", "reading_conflict", ["joseph-reunion-continuation-l009"], "Draft нѣга и нам до ѡца без него versus Нѣлга; context supports inability but consonant missing."),
    ("v1-461-left-l015", "256"): (256, "26936be7a321657501e1845c750aa024fb54755f", "attested", ["stones-l024"], "нѹдама"),
    ("v1-461-left-l017", "12"): (12, "c27fc69f5897903f8e45de15dc026fda2b19f925", "attested", ["satanail-witness-a-continuation-l019"], "ѡбавляют"),
    ("v1-461-left-l018", "12"): (12, "c27fc69f5897903f8e45de15dc026fda2b19f925", "attested", ["satanail-witness-a-continuation-l016","satanail-witness-a-continuation-l017"], "ѡбавни- / ком"),
    ("v1-461-left-l019", "283"): (283, "5c22aaabaa7fe0cf87e8d7fb92d310cc54e2a9d7", "not_found", [], "No matching Обадати in cited draft; pp282/284 screened, nearby horn riddle not proof of word occurrence."),
    ("v1-461-left-l021", "156"): (156, "6b14822820b1f6298a187733a146c71c9ef8cad2", "attested", ["imprisonment-l004"], "ѡбади мя"),
    ("v1-461-left-l022", "175"): (175, "768be23f0db0afccca9ca7eb06a012268d7f18d8", "reading_conflict", ["spirits-continuation-l022"], "Draft ѡблаженіє versus Обаженіе; initial cluster differs; do not identify without image."),
    ("v1-461-left-l023", "189"): (189, "8aed8e1d1be5cf3d6594547843d4f84822c04d8d", "reading_conflict", ["judah-further-battles-l015"], "Draft г҃. стѣны их ѡворихом versus Оборити; likely context but different consonant."),
    ("v1-461-left-l025", "53"): (53, "915cd7c08cbb33446bc6f03daef2bf71c4914ac1", "attested", ["enoch-address-l014","enoch-address-l015"], "ѡбѣтїе twice"),
    ("v1-461-left-l027", "24"): (24, "54e3f226a8b8536c21930f9b3e5ea87fce64e5bc", "reading_conflict", ["witness-b-apparatus-continuation-l028"], "Apparatus reads ѡглянѣло; the index has Огланѣти, glossed огладнѣти. Verify variants and meaning against print."),
    ("v1-461-left-l029", "174"): (174, "97a067336bc6fa0652b63dc3692fdb3749518217", "attested", ["reuben-address-l015"], "ѡлоу, after вина ни"),
    ("v1-461-left-l030", "142"): (142, "92128ab338de95004e6cd5d2b6a9397453406b33", "attested", ["joseph-embraces-benjamin-l024"], "душа бо ми ѡмарися"),
    ("v1-461-left-l032", "286"): (286, "2c9e8dc4beb1968e7948edebc670d91f4953f484", "reading_conflict", ["solomon-bone-test-l012"], "Draft ѡнышнїи [sic!] versus Оньший; preserve discrepancy."),
    ("v1-461-left-l034", "72"): (72, "d8f6143d6ca4b4dff95d628da59272c95213aa4a", "attested", ["witness-c-vineyard-l007"], "ѡпакы"),
    ("v1-461-left-l035", "176"): (176, "b09717d3027997cf405bd574a112cd27328e9e68", "reading_conflict", ["reuben-continuation-l002"], "Draft ѡпастье всеи versus Опастко; similar context and stem, different ending."),
    ("v1-461-left-l037", "42"): (42, "1a04bc97189129b53ceaeb5dada25733e9d9d90c", "attested", ["enoch-solar-creatures-l004"], "ѡпа́ши, matches index's explicit variant опашь; same occurrence as adjacent Опашь, not independent spelling"),
    ("v1-461-left-l038", "42"): (42, "1a04bc97189129b53ceaeb5dada25733e9d9d90c", "attested", ["enoch-solar-creatures-l004"], "ѡпа́ши"),
    ("v1-461-left-l039", "77"): (77, "174981a415f9241381bbee0e9aab594c41a5f877", "attested", ["editorial-a-end-l002"], "ѡсклаби ся in quoted narrative"),
    ("v1-461-left-l041", "240"): (240, "a6954635b1a97b7096b9d835ef1692ee0dc8bec2", "attested", ["second-stone-l003"], "по врачебней ослѣ"),
    ("v1-461-left-l043", "132"): (132, "6400c4962e986a0b7d5693c278c64c76627c5567", "attested", ["potiphar-wife-l017"], "ѡслабу"),
    ("v1-461-left-l044", "184"): (183, "b4565c00715c6040158d0e62c55f971232e9cc71", "attested", ["levi-ordination-l004"], "ѡстежь наперсную (p183); no occurrence on cited p184, both drafts inspected"),
    ("v1-461-left-l045", "227"): (227, "9f2c022715c14c508988ff53d0196b21ed623907", "reading_conflict", ["moses-crown-test-l030"], "Draft да ухавим ся ег[о] versus Охабити ся; likely contextual counterpart, uncertain consonant."),
    ("v1-461-left-l047", "288"): (288, "8d5a76d60b397e8fbd76a7df6cada95acd349e0d", "reading_conflict", ["solomon-three-travellers-end-l026"], "Draft ѡхвочь versus Охочь; extra consonant requires image check."),
    ("v1-461-left-l048", "42"): (42, "1a04bc97189129b53ceaeb5dada25733e9d9d90c", "attested", ["enoch-fourth-heaven-l011","enoch-solar-creatures-l006"], "пазят; па́зятъ, two lines"),
    ("v1-461-left-l049", "12"): (12, "c27fc69f5897903f8e45de15dc026fda2b19f925", "attested", ["satanail-witness-a-continuation-l038"], "платиною"),
    ("v1-460-right-l001", "242"): (242, "205c99e8703f1cb71bb694ecfa0dacff38a6bcb2", "reading_conflict", ["eleventh-stone-l002"], "Draft зевръ versus index Зекръ; colour of the eleventh stone, but consonant differs."),
    ("v1-460-right-l002", "205"): (205, "6d9572016803739a0fa6b56c00c2a0e0a10253d1", "attested", ["naphtali-visions-l019"], "зима люта и буря вѣтряна"),
    ("v1-460-right-l003", "319"): (319, "38566f1ddfed36b129269f81e88409b21d9031fe", "reading_conflict", ["daniel-body-l006"], "Draft семена земленая зовла суще; context suggests eating seeds but index Зобати is not literally attested."),
    ("v1-460-right-l004", "339"): (339, "2cfd6a4ada3719a1579aae58433af78476ac98ff", "attested", ["rachmani-end-l014"], "звѣротомитель"),
    ("v1-460-right-l005", "184"): (184, "5dda36ef5c08ff416b3fb202ab1f5b201c4cf11a", "attested", ["levi-warning-l005"], "золь велику"),
    ("v1-460-right-l007", "42"): (42, "1a04bc97189129b53ceaeb5dada25733e9d9d90c", "reading_conflict", ["enoch-punishment-continuation-l005"], "Draft за́влость after студень and жажда; index Заблость. Recheck consonant."),
    ("v1-460-right-l009", "257"): (257, "18ef6b4719e59c5325669139cd727b1ecdbf4c63", "attested", ["stones-ending-l003"], "изекрь; index also redirects to Зекръ"),
    ("v1-460-right-l011", "308"): (308, "0ad07cb37db342c9e054dd540237ef609cad09cc", "reading_conflict", ["three-youths-captivity-l006"], "Draft ѡслы ильскы versus index Имьскъ; matching context, disputed form."),
    ("v1-460-right-l014", "283"): (283, "5c22aaabaa7fe0cf87e8d7fb92d310cc54e2a9d7", "attested", ["sheba-opening-l003"], "капий"),
    ("v1-460-right-l016", "69"): (69, "6dfa76212368d336d4c70655e0d382aeb8a0b58d", "reading_conflict", ["witness-b-flood-continuation-l032"], "Draft клеутнонъ versus index Клехтнонъ; same non-rotting tree, differing letters."),
    ("v1-460-right-l018", "176"): (176, "b09717d3027997cf405bd574a112cd27328e9e68", "attested", ["reuben-continuation-l005"], "клещит"),
    ("v1-460-right-l021", "116"): (116, "a72da3321c5ebf7fc36824e3ae3f2e3478437381", "not_found", [], "No matching form on cited page; pp115/117 screened as well."),
    ("v1-460-right-l023", "140"): (140, "4e2296f1aed5881256ee723d0cc6fe649a4019cf", "attested", ["benjamin-accusation-l010"], "клюсятъ"),
    ("v1-460-right-l025", "183"): (183, "b4565c00715c6040158d0e62c55f971232e9cc71", "attested", ["levi-ordination-l037"], "книгчіа [sic!]; inflected form, preserve editorial marker"),
    ("v1-460-right-l027", "80"): (80, "037264054c20b2862c007e18f10b48010a9d2482", "reading_conflict", ["abraham-idols-l027"], "коконилъ (?) matches index spelling, but draft explicitly marks the reading uncertain."),
    ("v1-460-right-l028", "281"): (281, "f050bf4518a108633a55a6093aceb4d13dc7648d", "attested", ["shamir-l002","shamir-l006","shamir-l008","shamir-l009"], "кокоть; кокот (four occurrences)"),
    ("v1-460-right-l029", "183"): (183, "b4565c00715c6040158d0e62c55f971232e9cc71", "attested", ["levi-ordination-l012","levi-ordination-l013"], "ком- / канія, split across two lines"),
    ("v1-460-right-l031", "106"): (106, "ed959c63522958f8ac390ed767a417dbd7ba016c", "attested", ["witness-d-ishmaelites-l002"], "корнилъ; lexical interpretation remains unclear"),
    ("v1-460-right-l032", "67"): (67, "4c868122c80a9f3b5bbb56e67056e44114222512", "attested", ["noah-flood-continuation-l002"], "котцех (inflected form)"),
    ("v1-460-right-l034", "199"): (199, "32ec4b99b36b589549c350ea56701f81b002f066", "attested", ["zebulun-narrative-continuation-l008","zebulun-narrative-continuation-l012"], "котыгу (two occurrences)"),
    ("v1-460-right-l036", "319"): (319, "38566f1ddfed36b129269f81e88409b21d9031fe", "attested", ["daniel-body-l006"], "кощь"),
    ("v1-460-right-l037", "175"): (175, "768be23f0db0afccca9ca7eb06a012268d7f18d8", "not_found", [], "Draft горчинѣ is a different word; no Кручина form. Nearby pp174/176 screened."),
    ("v1-460-right-l038", "269"): (269, "2d27b4ceb62a722d43191f18d54c54cbf58ba7c6", "reading_conflict", ["gideon-end-l010"], "Draft легомица [sic!] versus index Легомище; same dream episode, recheck ending."),
    ("v1-460-right-l040", "138"): (138, "628fd3230a1ef536a9763d8ddc6488c5840a8b8d", "attested", ["joseph-divination-l002"], "лическы"),
    ("v1-460-right-l041", "45"): (45, "06466357e56612a89d893ccf4f6310923e1b05e1", "not_found", [], "No matching Лыцати form in draft; the shining faces passage does not establish this reading. Nearby pp44/46 screened."),
    ("v1-460-right-l042", "121"): (121, "e784cd27d856d67877ff61081230b78ec1211b2a", "attested", ["jacob-wrestling-l006"], "за лыста"),
    ("v1-460-right-l043", "182"): (182, "22a01b9a5dae2eb3907369a5c39cad0378ddb8ff", "attested", ["levi-angel-l008"], "лѣт[е] (bracketed restoration retained)"),
    ("v1-460-right-l045", "44"): (44, "0acdfc09e67eff05f57f6fc2793ff3323a3efc49", "attested", ["enoch-lunar-gates-continuation-l016"], "мале́нїе"),
    ("v1-460-right-l046", "195"): (195, "171099c509adba8af78987aa50101c031d1c28f4", "attested", ["issachar-opening-l020"], "мъзды; earlier мездрою not counted as a second attestation"),
    ("v1-460-right-l048", "188"): (188, "e088a1c6fb131cc43bdd4963e057456cfd84fe1e", "attested", ["judah-youth-l015"], "мечку"),
    ("v1-460-right-l049", "283"): (283, "5c22aaabaa7fe0cf87e8d7fb92d310cc54e2a9d7", "attested", ["sheba-opening-l010"], "мовь красну"),
    ("v1-460-left-l001", "94"): (94, "06583a9513955ca5615c9f42053ef28a49ae3d14", "not_found", [], "Cited page has вълѡвъ and воловъ, not the indexed adjective; recheck image."),
    ("v1-460-left-l003", "71"): (71, "dc52e638c6260922fa4e37e8cdcd149d6bc0669a", "attested", ["witness-b-apparatus-l004"], "въплашати его (variant in apparatus)"),
    ("v1-460-left-l004", "283"): (283, "5c22aaabaa7fe0cf87e8d7fb92d310cc54e2a9d7", "attested", ["two-headed-servant-end-l015","servant-apparatus-l002"], "вшерше; variant възсерше. Context and apparatus support the indexed lexeme; spelling differs."),
    ("v1-460-left-l005", "205"): (205, "6d9572016803739a0fa6b56c00c2a0e0a10253d1", "attested", ["naphtali-visions-l006"], "вѣи"),
    ("v1-460-left-l007", "95"): (95, "becbedfddbd645472e1eeb4af97b1bd738c6216e", "attested", ["melchizedek-sacrifice-l038"], "вѣршье дубовоє"),
    ("v1-460-left-l009", "175"): (175, "768be23f0db0afccca9ca7eb06a012268d7f18d8", "attested", ["spirits-continuation-l029"], "глумите (verb form)"),
    ("v1-460-left-l011", "56"): (56, "f4c3834d40c411527cdcd76c4a82d4147768115f", "not_found", [], "No matching word on p56 in current draft; nearby pp55/57 also checked."),
    ("v1-460-left-l012", "59"): (59, "90de959d3a44e15cc7f7627c37aed2c027271236", "attested", ["methuselah-request-continuation-l001"], "годѣ"),
    ("v1-460-left-l014", "25"): (25, "2792810a2c92e3e14711f30799efd02ee9b3ee05", "not_found", [], "No matching word in current apparatus reading; nearby pp24/26 also checked."),
    ("v1-460-left-l016", "40"): (40, "0ab41b4436dbe0711bd438209eb4abac34a4bbce", "not_found", [], "No matching word in current cited-page reading; nearby pp39/41 also checked."),
    ("v1-460-left-l019", "111"): (111, "63aa0a1e402e54d4e88d0917d10e6739e34c08ea", "attested", ["jacob-sariel-end-l005","jacob-sariel-end-l006"], "гонь- / знутъ (split word)"),
    ("v1-460-left-l021", "204"): (204, "5c75b798a27b4431aa2d019dca1db628030c1bd2", "attested", ["naphtali-continuation-l012"], "гонѣть"),
    ("v1-460-left-l023", "42"): (42, "1a04bc97189129b53ceaeb5dada25733e9d9d90c", "attested", ["enoch-punishment-continuation-l006"], "гру́жны (index itself suggests грозенъ)"),
    ("v1-460-left-l025", "173"): (173, "e9d5f4a278c23bacc7a18dd94dd729a540d76f62", "not_found", [], "No matching word in current draft; nearby pp172/174 also checked."),
    ("v1-460-left-l026", "291"): (291, "d0002ff3ecb516f269c2e07590535f3e39d274d9", "attested", ["solomon-demons-opening-l002","solomon-demons-challenge-l005","solomon-demons-challenge-l007","solomon-demons-sealing-l003","solomon-demons-sealing-l004"], "делвѣ; делву (five evidenced lines)"),
    ("v1-460-left-l027", "12"): (12, "c27fc69f5897903f8e45de15dc026fda2b19f925", "reading_conflict", ["satanail-witness-a-continuation-l018"], "Current draft другоициж[е], compare index Друговици; check spelling and word boundary in image."),
    ("v1-460-left-l029", "308"): (308, "0ad07cb37db342c9e054dd540237ef609cad09cc", "attested", ["three-youths-captivity-l005"], "дражданаа"),
    ("v1-460-left-l031", "321"): (321, "dc158de3ca4c7583e4ca2892414244a64b648ecd", "attested", ["belshazzar-body-l001"], "драхлу"),
    ("v1-460-left-l033", "44"): (44, "0acdfc09e67eff05f57f6fc2793ff3323a3efc49", "attested", ["enoch-lunar-gates-continuation-l012"], "епа́кти"),
    ("v1-460-left-l036", "133"): (133, "f919e06f96f7787169273e68fb06f2cb639353d9", "attested", ["joseph-flight-l005"], "етеръ"),
    ("v1-460-left-l038", "183"): (183, "b4565c00715c6040158d0e62c55f971232e9cc71", "attested", ["levi-ordination-l004","levi-ordination-l016"], "ефудъ; ефуду"),
    ("v1-460-left-l039", "214"): (214, "b68be53484bf09579f5bc5b69cf8a79caefe7c93", "attested", ["joseph-l021"], "женима"),
    ("v1-460-left-l041", "65"): (65, "a641f34dd7657d1a681d152ef712603228324739", "attested", ["noah-iniquity-l008"], "жироваше"),
    ("v1-460-left-l042", "282"): (282, "fa7b2666258a5ebe422b8209543ce99f023c5933", "attested", ["kitovras-end-l006","kitovras-end-l007"], "жюковину (two occurrences)"),
    ("v1-460-left-l044", "228"): (228, "ce883a2b70b8168f649594928df821011041773c", "attested", ["moses-flight-l019"], "загутья́нъ"),
    ("v1-460-left-l045", "147"): (147, "057d06e0ad6b78e4bcf26ececf4ff3c4281859e6", "not_found", [], "Cited page has заполни, not Заполець; nearby pp146/148 checked. Do not equate distinct forms."),
    ("v1-460-left-l046", "20"): (20, "ee0a66fb061444f5b9e65fcb34a77796bf6269d6", "reading_conflict", ["witness-a-adam-eve-continuation-l028"], "Current draft згрѣва сел'ное, index Згрѣба; verify consonant against image."),
    ("v1-459-left-l001", "39"): (39, "e52bbec8c037981ea4211c5c52af02dd6e35326a", "attested", ["enoch-vision-l010","enoch-vision-l011"], "ба- / гры (word split across two lines)"),
    ("v1-459-left-l003", "52"): (52, "d2d1b7c27e456929976a480a17cdf7417ce9ca19", "attested", ["enoch-flood-l002"], "б л а д о т в о́ р ц ы (spaced type)"),
    ("v1-459-left-l004", "176"): (176, "b09717d3027997cf405bd574a112cd27328e9e68", "attested", ["reuben-exhortation-l011","reuben-exhortation-l015"], "бодрыя; бодрыи (two occurrences)"),
    ("v1-459-left-l007", "63"): (63, "49637c442518962820ba85e4965f70f99353355b", "attested", ["enoch-colophon-l012"], "бравїя"),
    ("v1-459-left-l008", "238"): (239, "a082132a80faebe611eadb3f81349869f965b888", "attested", ["tabernacle-l005"], "брачину (same line as Виса; no occurrence in draft of cited p238)"),
    ("v1-459-left-l010", "107"): (107, "2f6175ac753d060741c7e2f74b600c66fcd919ae", "not_found", [], "No matching word in current cited-page reading; recheck facsimile."),
    ("v1-459-left-l013", "21"): (21, "ee1e6de5b8ef51739de48d93c70a2126f23cd15c", "attested", ["witness-a-adam-eve-continuation-l016","witness-a-adam-eve-continuation-l026","witness-a-adam-eve-continuation-l027"], "бѣлингъ; бѣ- / лингъ (the index gives Бѣлигъ; sign agreed between Adam and Eve)"),
    ("v1-459-left-l015", "195"): (195, "171099c509adba8af78987aa50101c031d1c28f4", "reading_conflict", ["issachar-opening-l015"], "Index quotation прелесть варил; current body draft reads прелесть варна. Reinspect image."),
    ("v1-459-left-l015", "197"): (197, "30adf32dbdd1934efcc6304ecdc0c1395e1ab510", "attested", ["issachar-apparatus-l002"], "прелесть варила (explicit variant)"),
    ("v1-459-left-l021", "188"): (188, "e088a1c6fb131cc43bdd4963e057456cfd84fe1e", "attested", ["judah-youth-l017"], "варивъ"),
    ("v1-459-right-l001", "190"): (190, "77a7f275a4d15c1aa8fe9204723f5ffb473a5ae2", "attested", ["judah-family-continuation-l006"], "виничне (lexical correspondence; spelling differs from index Виничие)"),
    ("v1-459-right-l003", "239"): (239, "a082132a80faebe611eadb3f81349869f965b888", "attested", ["tabernacle-l005"], "вису; index gloss quotes кису, a conflicting initial letter; preserve both"),
    ("v1-459-right-l005", "140"): (140, "4e2296f1aed5881256ee723d0cc6fe649a4019cf", "not_found", [], "No matching word in current cited-page reading; recheck facsimile."),
    ("v1-459-right-l007", "236"): (236, "1ed6b1698d8a957fa0ee488b023f9ea8106b7c6c", "attested", ["pharaoh-petison-end-l007"], "волчби"),
    ("v1-459-right-l009", "182"): (182, "22a01b9a5dae2eb3907369a5c39cad0378ddb8ff", "attested", ["levi-angel-l027"], "врежа"),
    ("v1-459-right-l011", "19"): (19, "223061661d3db30f32d51b4e95d79acf77c0a4c5", "not_found", [], "No matching word in current cited-page reading; recheck facsimile."),
    ("v1-459-right-l014", "212"): (212, "0a9c841b7cd29620a32433da36718169b65bd6d4", "attested", ["joseph-opening-l023"], "врѣжаетъ"),
    ("v1-459-right-l016", "187"): (187, "69a107d7e5351c745e8a8734941e5c98203850e6", "not_found", [], "No matching word in current cited-page reading; recheck facsimile."),
    ("v1-459-right-l018", "217"): (217, "5b0f0be67c424f675c6f0e5d47b41c88b5507131", "reading_conflict", ["joseph-l027"], "Current draft бꙋсиннꙋ, not Вѹсиненъ; textile context supports checking the initial letter in image."),
    ("v1-459-right-l020", "183"): (183, "b4565c00715c6040158d0e62c55f971232e9cc71", "reading_conflict", ["levi-ordination-l016"], "Current draft учину, not Вѹчина; possible initial-letter or word-boundary discrepancy; inspect image."),
    ("v1-459-right-l021", "182"): (182, "22a01b9a5dae2eb3907369a5c39cad0378ddb8ff", "attested", ["levi-angel-l007"], "възбнувъ"),
}


def review_glossary_mentions(files, targets, entry):
    if entry["source"]["blob"] != SOURCE_BLOBS.get(entry["source"]["scan"]):
        return
    for i, citation in enumerate(entry["refs"]):
        spec = GLOSSARY_MENTION_REVIEWS.get((entry["id"], citation["literal"]))
        if spec is None:
            continue
        page, blob, status, line_ids, note = spec
        scan = targets.get(page)
        if scan not in files or files[scan][2] != blob:
            continue
        path, draft, _ = files[scan]
        evidence = []
        for line_id in line_ids:
            hits = [(region, line) for region in draft["reading"]["regions"]
                    for line in region["lines"] if line["id"] == line_id]
            if len(hits) != 1 or hits[0][0]["kind"] not in ("body", "note", "heading"):
                break
            region, line = hits[0]
            evidence.append(dict(line_id=line_id, text=line["text"], region_kind=region["kind"]))
        if len(evidence) != len(line_ids):
            continue
        if str(page) != citation["literal"]:
            # Explicitly reviewed original destinations; both original
            # and corrected page must retain the inspected draft bytes.
            originals = {
                ("v1-459-left-l008", "238"): (238, "55399194398600e093ee9b4a863baa545e1f574e"),
                ("v1-461-left-l044", "184"): (184, "5dda36ef5c08ff416b3fb202ab1f5b201c4cf11a"),
            }
            original_spec = originals.get((entry["id"], citation["literal"]))
            if original_spec is None:
                continue
            original_page, original_blob = original_spec
            old_scan = targets.get(original_page)
            if old_scan not in files or files[old_scan][2] != original_blob:
                continue
            original = citation
            citation = make_ref(str(page), targets, "editorial_citation")
            citation["printed_literal"] = original["literal"]
            citation["original_destination_evidence"] = dict(path="pilot/" + files[old_scan][0].name, blob=files[old_scan][2])
            entry["refs"][i] = citation
        target = next((t for t in citation["targets"] if t["page"] == page and t["scan"] == scan), None)
        if target is None:
            continue
        target["mention_review"] = dict(status=status, path="pilot/" + path.name,
                                        blob=blob, lines=evidence, note=note)
        if status == "attested" and evidence:
            first = evidence[0]
            target["anchor"] = dict(suffix="single_reading", reader_id=draft["reading"]["reader_id"],
                                    line_id=first["line_id"], text=first["text"],
                                    region_kind=first["region_kind"])


def build_printed_indexes(pilot, ref, supplements=None):
    supplements = supplements or {}
    files = {}
    for path in sorted(pilot.glob("vol1_scan*_single_reading.json")):
        data, blob = read_draft(path)
        if data["volume"] != "1":
            raise ValueError(f"wrong volume: {path}")
        scan = data["scan_page"]
        if path.name != f"vol1_scan{scan:05d}_single_reading.json" or scan in files:
            raise ValueError(f"duplicate or mismatched scan: {path}")
        files[scan] = (path, data, blob)
    def observed(d):
        printed = d["printed_page_observed"]
        if printed is None:
            folios = [l["text"] for r in d["reading"]["regions"] if r["id"] == "folio"
                      for l in r["lines"] if re.fullmatch(NUMBER, l["text"])]
            if len(folios) == 1:
                return folios[0]
        return printed
    observations = {scan: observed(d) for scan, (_, d, _) in files.items() if 76 <= scan <= 415}
    # Scan 222 says 247 in the current draft. Its Jacob testament text
    # continues directly from 146 into 148; actual 247 (scan 322) is in
    # the Moses narrative and has neighbours 246/248. Preserve both
    # recorded folios; allow only this exact evidence-pinned exception.
    evidence = {
        221: ("146", "dade7e4824ed53cba87990f2852a987745d5ff74"),
        222: ("247", "057d06e0ad6b78e4bcf26ececf4ff3c4281859e6"),
        223: ("148", "c45e9c7cd4f00ae6d0178074477f675bf0e39eec"),
        321: ("246", "adb444890764aee426f2bcd1ccea335b4177493b"),
        322: ("247", "65050f593b365479157c010bb06bd67b3cd73478"),
        323: ("248", "6df2f8e15a4bc8b09c0112e0f043d735bfd1ad28"),
    }
    if all(scan in files and observations.get(scan) == page and files[scan][2] == blob
           for scan, (page, blob) in evidence.items()):
        observations[222] = None
    targets, estimated = complete_folio_targets(observations.items())
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
        if kind in ("names", "works", "motifs"):
            changed = True
            while changed:
                before = eligible.copy()
                for pair in ATOMIC_PAIRS:
                    if not set(pair) <= eligible:
                        eligible.difference_update(pair)
                changed = before != eligible
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
                        # A region/page boundary never manufactures a new name.
                        prior = entries[-1] if entries else section["entries"][-1]
                        segments = prior.setdefault("segments", [
                            dict(source=prior["source"], region_id=prior["region_id"],
                                 lines=prior["lines"][:])])
                        segments.append(dict(source=source, region_id=region_id, lines=part))
                        prior["lines"].extend(part)
                        parse_lines = []
                        for i, segment in enumerate(segments):
                            texts = [l["text"] for l in segment["lines"]]
                            # Only the actual continuation, never an initial article
                            # elsewhere in this same region (e.g. Pypin).
                            key = (segment["source"]["scan"], segment["region_id"], 1)
                            if i and key in CONTINUATION_PREFIXES:
                                prefix = CONTINUATION_PREFIXES[key]
                                if not texts[0].startswith(prefix):
                                    raise ValueError("changed running continuation heading")
                                texts[0] = texts[0][len(prefix):]
                            parse_lines.extend(texts)
                        prior["label"], prior["detail"], prior["refs"] = parse_entry(
                            kind, parse_lines, targets)
                        previous = stop
                        continue
                    # Keep literal source lines for provenance/anchors, but use
                    # the same validated supplementary projection as the reader
                    # when deriving the navigation label and references.
                    supplement = supplements.get(source["path"])
                    corrections = ({r["line_id"]: r for r in supplement["lines"]}
                                   if supplement and supplement["blob"] == blob else {})
                    effective = [corrections[l["id"]]["text"] if l["id"] in corrections else l["text"] for l in part]
                    label, detail, refs = parse_entry(kind, effective, targets)
                    # Only the explicit Abraham block on the pilot motif page.
                    context = ("Авраам" if kind == "motifs" and scan == 437 and label.startswith("„")
                               else ENTRY_CONTEXTS.get((scan, region_id, previous + 1), "") if kind in ("names", "works", "motifs") else "")
                    entries.append(dict(id=f"v1-{scan}-{part[0]['id']}", source=source,
                                        region_id=region_id, lines=part, label=label,
                                        detail=detail, context=context, refs=refs))
                    if effective != [l["text"] for l in part]:
                        entries[-1]["supplementary_reading"] = [dict(line_id=l["id"], text=corrections[l["id"]]["text"], evidence_url=corrections[l["id"]]["evidence_url"]) for l in part if l["id"] in corrections]
                        if scan == 418 and part[0]["id"] == "index-a-l014":
                            reconcile_achatis_reference(pilot, files, targets, entries[-1])
                    previous = stop
            if seen_regions != set(partitions):
                raise ValueError(f"missing index regions: {path}")
            section["structured_scans"].append(scan)
            section["entries"].extend(entries)
    for section in sections:
        by_id = {e["id"]: e for e in section["entries"]}
        for entry in section["entries"]:
            reconcile_ishmael_reference(files, targets, entry)
            reconcile_darius_reference(files, targets, entry)
            reconcile_motif_reference(files, targets, entry)
            if section["kind"] == "glossary":
                review_glossary_mentions(files, targets, entry)
            entry["crossrefs"] = [dict(id=ident, label=by_id[ident]["label"])
                                  for ident in CROSSREFS.get(entry["id"], []) if ident in by_id]
            for citation in entry["refs"]:
                for target in citation["targets"]:
                    if target["page"] in estimated:
                        target["estimated"] = True
    result = dict(schema_version=1, ref=ref, status="agent_unverified", sections=sections)
    result["link_audit"] = link_audit(result)
    return result
