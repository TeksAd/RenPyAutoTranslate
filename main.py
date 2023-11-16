import argostranslate.package
import argostranslate.translate
import os
from pprint import pprint


class Translator:
    """
    Обёртка для argostranslate
    """
    def __init__(self, from_code: str, to_code: str, file_code: str = ""):
        self.file_code = file_code
        self.from_code = from_code
        self.to_code = to_code
        self.path = self.download_translate_tackage(from_code, to_code)
        self.count = 0

    @staticmethod
    def download_translate_tackage(from_code: str, to_code: str) -> str:
        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x:
                x.from_code == from_code and x.to_code == to_code,
                available_packages
            )
        )
        path = package_to_install.download()
        print("Языковой пакет скачан в файл: ", path)
        return path

    def translate(self, text_to_translate: str) -> str:
        '''
        Принимает строку, которую нужно перевести, возвращает переведённую строку, в начале которой стоит
        id файла (передаётся в конструкторе) символ @ и номер строки в файле
        т.е. id@НомерСтроки ПереведённаяСтрока
        :param text_to_translate:
        :return:
        '''
        self.count += 1
        return (self.file_code +
                "@" +
                str(self.count) +
                " " +
                argostranslate.translate.translate(text_to_translate, self.from_code, self.to_code)
                )


class Phrase:
    def __init__(self, line: str):
        line = line[4:]
        if line[-2] == '"':
            self.after = ""
        else:
            self.after = line[line.rfind('"')+1:-1]
            line = line[:line.rfind('"')+1]
        if line[:3] == "old":
            self.speaker = "old"
            self.is_system = True
            self.speech = line[5:-2]
        elif line[:3] == '# "':
            if line[3:-2].find('"') == -1:# or line[3:-2].find('"') != line[3:-2].find('\\"'):
                self.speaker = None
                self.speech = line[1:-2]
                self.is_system = False
            else:
                line = line[2:]
                line.find('"',1)
                self.speaker = line[:line.find('"',1)+1]
                self.speech = line[line.find('"',1)+2:-2]
                self.is_system = False
        else:
            line = line[2:]
            self.speaker, self.speech = line.split(" ", 1)
            self.speech = self.speech[1:-1]
            self.is_system = False

    def __str__(self):
        return f"-\nspeaker: {self.speaker} \nspeech: {self.speech} \nafter: {self.after}"


class Block:
    def __init__(self):
        self.before_lines = []
        self.old_line = None
        self.new_line = None
        self.repeats = []

    def append_before_line(self, line):
        self.before_lines.append(line)

    def set_old_line(self, line):
        self.old_line = Phrase(line)

    def append_repeat(self, repeat):
        self.repeats.append(repeat)


class File:
    def __init__(self, lines, tr):
        self.blocks = []
        self.tr = tr

        bl = Block()
        i = 0
        l = len(lines)
        while i < l:
            if lines[i][:4] != "    " or (lines[i][:5] == "    #" and ".rpy" in lines[i]):
                bl.append_before_line(lines[i])
            else:
                bl.append_before_line(lines[i])
                bl.set_old_line(lines[i])
                self.blocks.append(bl)
                bl = Block()
                i += 2
            i += 1

    def translate(self):
        for i in self.blocks:
            i.new_line = "    "
            if i.old_line.is_system:
                i.new_line += "new "
            elif i.old_line.speaker is not None:
                i.new_line += i.old_line.speaker + " "
            i.new_line += '"'
            i.new_line += self.tr(i.old_line.speech)
            # print(i.old_line)
            i.new_line += '"'
            i.new_line += i.old_line.after
            i.new_line += '\n'

    def get_lines(self):
        result = []
        for i in self.blocks:
            for j in i.before_lines:
                result.append(j)
            result.append(i.new_line)
            result.append("\n")
        return result


def get_rpy_files(top=".", quiet = False):
    files = []
    for rt, ds, fs in os.walk(top):
        for i in fs:
            if i[-4:] == ".rpy":
                file = os.path.join(rt, i)
                if not quiet:
                    print(file)
                files.append(file)
    return files


def read_file(file: str):
    with open(file, "r", encoding='UTF8') as f:
        result = f.readlines()
    return result


def write_file(file: str, lines):
    with open(file, "w", encoding='UTF8') as f:
        f.writelines(lines)


def placeholertranslate(s: str):
    return ""


def test_file(file):
    test = read_file(file)
    f = File(test, placeholertranslate)
    f.translate()
    res = f.get_lines()
    if res != test:
        print(file)
        # print(len(res) == len(test))
        for j in range(len(res)):
            if res[j] != test[j]:
                print(f'Строка {j}:')
                pprint(test[j])
                pprint(res[j])


def test_all_files():
    for i in get_rpy_files(quiet=True):
        test_file(i)


def test_piece_of_file(file, begin, end):
    t = []
    test = read_file(file)[begin: end]
    f = File(test, "tr")
    f.translate()
    res = f.get_lines()
    for i in range(end-begin):
        print(f'Строка {i}:')
        pprint(test[i])
        pprint(res[i])
        t.append(test[i])
    return t


if __name__ == '__main__':
    # test_all_files()
    translator = Translator("en", "ru", "common.rpy")
    f = File(read_file("common.rpy"), translator.translate)
    f.translate()
    lines = f.get_lines()
    write_file("common.rpy", lines)
