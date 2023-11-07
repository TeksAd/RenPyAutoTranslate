import argostranslate.package
import argostranslate.translate
from pprint import pprint
import os


class Translator:
    def __init__(self, from_code: str, to_code: str):
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

    def translate(self, text_to_translate: str):
        self.count += 1
        return ("@" +
                str(self.count) +
                " " +
                argostranslate.translate.translate(text_to_translate, self.from_code, self.to_code)
                )


tr = Translator("en", "ru")


def get_files(top="."):
    files = []
    for rt, ds, fs in os.walk(top):
        for i in fs:
            if i[-4:] == ".rpy":
                file = os.path.join(rt, i)
                print(file)
                files.append(file)
    return files


def parse(row: str) -> str:
    parts = row.split(sep='"', maxsplit=1)
    parts += (parts.pop().rsplit(sep='"', maxsplit=1))
    if parts[0][4:7] == "old":
        parts[0] = parts[0][:4] + "new" + parts[0][7:]

    parts[1] = tr.translate(parts[1])
    return parts[0] + '"' + parts[1] + '"' + parts[2]


def edit(file: str):
    result = []
    with open(file, "r", encoding='UTF8') as f:
        rows = f.readlines()

    for row in rows:
        # pprint("="*80)
        # pprint(row)
        if row[0:4] != "    " or row[0:5] == "    #" or row[0:8] == "    old ":
            result.append(row)
            # pprint(row)
        else:
            result.append(parse(result[-1]))
            # pprint(result[-1])
    pprint(result)
    with open(file, "w", encoding='UTF8') as f:
        f.writelines(result)


def main():
    # tr = translator("en", "ru")
    # print(tr.translate("Hello World"))

    files = get_files()

    edit(files[0])
    # for i in files:
    #     edit(i)


main()
