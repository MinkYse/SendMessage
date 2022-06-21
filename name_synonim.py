import random
import sys


class Synonims:

    def __init__(self):
        self.synonims = list()
        self.unique = set()

    def add_synonim(self, string_synonim: str):
        data = string_synonim.split('>')
        self.synonims.append((data[0].lstrip('{').rstrip('}').split('|'), data[1].lstrip('{').rstrip('}').split('|')))

    def add_unique(self, unique_string: str): self.unique.add(unique_string);

    def __str__(self):
        return "\n".join(["{" + '|'.join(c[0]) + "}>{" + "|".join(c[1]) + '}' for c in self.synonims] + sorted([i for i in self.unique]))


def transliterateAndCut(name: str) -> str:
    transliteration_array = [{"olga": "ольга"}, {"sch": "щ"}, {"ch": "ч"}, {"sh": "ш"},
                             {"yu": "ю"}, {"ya": "я"}, {"yo": "ё"}, {"zh": "ж"}, {"kh": "х"}, {"eh": "э"},
                             {"jo": "ё"}, {"ly": "ли"}, {"a": "а"}, {"b": "б"}, {"v": "в"}, {"g": "г"},
                             {"d": "д"}, {"e": "е"}, {"z": "з"}, {"i": "и"}, {"j": "й"}, {"k": "к"}, {"l": "л"},
                             {"m": "м"}, {"n": "н"}, {"o": "о"}, {"p": "п"}, {"r": "р"}, {"s": "с"}, {"t": "т"},
                             {"u": "у"}, {"f": "ф"}, {"h": "х"}, {"c": "ц"}, {"“": "ъ"}, {"‘": "ь"}, {"q": "?"},
                             {"w": "в"}, {"x": "х"}, {"y": "у"}]
    for replace_key in transliteration_array:  # транслитерация имени
        while name.find(list(replace_key.keys())[0]) != -1:
            name = name.replace(list(replace_key.keys())[0], replace_key[list(replace_key.keys())[0]])
    name_clean = ""
    for letter in name:
        if letter.isalpha() or letter == " ":
            name_clean += letter
    for word in name_clean.split():
        if len(word) > 2:
            return word
    return "ERROR"


def readSynonimFile(filename: str):
    synonims = Synonims()
    with open(filename, 'r', encoding='utf-8') as file:
        strings = file.readlines()
    for string in strings:
        string = string.rstrip('\n').lstrip('\ufeff')
        if '>' in string:
            synonims.add_synonim(string)
        else:
            synonims.add_unique(string)
    return synonims


def findSynonimAndUpdateObject(name: str, synonims: Synonims):
    for calls_array in synonims.synonims:
        for call in calls_array[0]:
            if name == call:
                return random.choice(calls_array[1])
            if name in call:
                calls_array[0].append(name)
                return random.choice(calls_array[1])
    synonims.add_unique(name)
    return name


def writeBack(filename, synonims):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(synonims))


if __name__ == '__main__':
    name = ' '.join(sys.argv[1:]).lower()  # если программно закидывать имя в переменную, то сюда
    name = transliterateAndCut(name)
    filename = 'Name_Synonim.txt'
    synonims = readSynonimFile(filename)
    name = list(findSynonimAndUpdateObject(name, synonims))
    name[0] = name[0].upper()
    print("".join(name))
    writeBack(filename, synonims)
