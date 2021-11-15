import os
import io


class LineOperations:  # класс методов для преобразования строк
    @staticmethod
    def get_words(f_line):  # выделение в лист слов из строки
        return f_line.replace('@', ' ').replace('{', ' ').replace(',', ' ').replace('п»ї', ' ') \
            .replace('\\', '').replace('/', '').replace('\'', '').replace('}', ' ') \
            .replace('"', ' ').replace('=', ' ').split()  # заменяем всё лишнее и split'им

    @staticmethod
    def terminal_chars(f_line, char):  # определяет количество символов, завершающих строку внутри записи
        if f_line[-1:] == char:  # Последний символ равен char
            return 1
        if f_line[-2:] == (char + ","):  # последние два символа соответствуют char+','
            return 2
        else:
            return 0

    @staticmethod
    def fix_ending(f_line):  # отрезаем от строки '\n' и лишние пробелы до '\n'
        if f_line[len(f_line) - 1] == '\n':
            f_line = f_line[:-1]  # убираем переход на новую строку
            if f_line[len(f_line) - 1] == ' ':
                f_line = f_line.rstrip(' ')  # убираем все пробелы справа
        return f_line

    @staticmethod
    def del_extra_comma(f_line):  # удаление лишних запятых в конце строки (когда одна уже имеется)
        while len(f_line) > 2 and f_line[len(f_line) - 3] == ',':  # если предпоследняя позиция (не считая '\n')
            f_line = f_line[:len(f_line) - 3] + f_line[len(f_line) - 2:]  # тоже запятая, то удаляем эту лишнюю запятую
        return f_line

    @staticmethod
    def fix_brackets(f_line):  # коррекция правильности скобок/кавычек внутри описания поля
        open_br_pos = []  # позиции открывающих скобок
        num_of_open = 0  # кол-во открывающий скобок
        pos_in_line = 0  # позиция в строке
        for char in f_line:
            if char == '\"':
                f_line = f_line[:pos_in_line] + "\\" + f_line[pos_in_line:]  # для кавычек в тексте добавляем "\\"
                pos_in_line += 1
            if char == '{':
                num_of_open += 1
                open_br_pos.append(char)
            if char == '}':
                if num_of_open == 0:  # закрывающая появилось еще до любой открывающей - удаляем
                    if char == 0:
                        f_line = f_line[0:]
                    else:
                        f_line = f_line[:pos_in_line - 1] + f_line[pos_in_line:]
                else:  # иначе, уменьшаем число открывающих на один
                    num_of_open -= 1
            pos_in_line += 1
        if num_of_open > 0:
            for char in range(num_of_open - 1, 0):  # все оставшиеся открытые удаляем, начиная изнутри
                num = open_br_pos[char]
                f_line = f_line[:num - 1] + f_line[num:]
        return f_line


class WordOperations:  # класс методов для слов
    @staticmethod
    def get_word_case(word):  # получение регистра слова
        if word.islower() == 1:
            return "S"  # small (все буквы строчные)
        elif word.isupper() == 1:
            return "B"  # BIG (все буквы заглавные)
        else:
            return "T"  # Title (только первая буква - заглавная)

    @staticmethod
    def word_to_case(word, case):  # приведение слова к регистру
        if case == "S":
            word = word.lower()
        elif case == "B":
            word = word.upper()
        else:
            word = word.title()
        return word


class BibFile(object):  # класс, содержащий основные параметры записей bib-файла
    def __init__(self, name, fldr=None, mode="r", err="ignore"):  # создание пути и открытие соотв. файла
        if fldr is None:
            self.path = name
        else:
            self.path = fldr + "\\" + name
        self.file = io.open(self.path, mode=mode, errors=err)

    def next_line(self):
        return self.file.readline()

    keys = set()  # будем сохранять citekey, чтобы не было повторных записей
    inside = 0  # ==1, если внутри структуры записи
    multi_line_text = 0  # ==1, если описание на несколько строк
    spaces_for_multi = 0  # равно числу пробелов для записи строк текста тега друг под другом
    empty_text = 0  # иногда содержимое поля пусто: такие строки мы будем пропускать
    invalid_type = 0  # ==1, если тип корректен
    closing_char = ''  # храним скобочку или кавычку, в которые заключен текст, описывающий тэг


class BibFileParameters:  # класс, хранящий параметры шаблонной записи
    def __init__(self, file: BibFile):
        lines = file.next_line()  # читаем первую строку и заменяем специальные знаки
        f_words = LineOperations.get_words(lines)
        self.type_case = WordOperations.get_word_case(f_words[0])  # получаем регист типа
        lines = file.next_line()  # читаем вторую строку файла
        self.space_before_tag = len(lines) - len(lines.lstrip(' '))  # считаем количество пробелов в начале
        lines = lines.lstrip(' ')  # убираем эти пробелы
        tag_word = ""  # тэг (слово)
        self.space_after_tag = 0  # пробелы перед тэгом
        self.space_after_equals = 0  # пробелы после знака равно
        self.equals_pos = -1  # позиция знака равно
        for char in lines:  # идем по строке
            self.equals_pos += 1
            if char != '=':
                if char == ' ':
                    self.space_after_tag += 1  # увеличиваем кол-во пробелов после имени
                else:
                    tag_word += char  # иначе идет сам тэг
                continue
            break
        for char in range(self.space_after_tag + len(tag_word) + 1, len(lines)):  # идем дальше по строке от знака равно
            if lines[char] == ' ':
                self.space_after_equals += 1
            else:
                break  # если встречается что-то, кроме пробела, то подсчет заканчивается
        self.tag_case = WordOperations.get_word_case(tag_word)
        if lines.find('{') != -1:
            self.tag_bracket = "{}"  # запоминаем во что заключен описывающий текст
        else:
            self.tag_bracket = "\"\""


class BibFileOperations:  # класс операций, связанных с bib-файлами (конкретно здесь - запись в bib-файл)
    @staticmethod
    def write_to_file(dest: BibFile, f_line, param: BibFileParameters, text, notmultiline):
        f_words = LineOperations.get_words(f_line)
        f_words[0] = WordOperations.word_to_case(f_words[0], param.tag_case)
        position = param.space_after_tag
        increment = position + 2 + param.space_after_equals
        if param.space_after_tag > 1:
            position = param.equals_pos - param.space_before_tag - len(f_words[0])  # кол-во пробелов м/у тэгом и "="
            increment = position + 3
        dest.file.write(" " * param.space_before_tag + f_words[0] + " " * position + "=" +
                        " " * param.space_after_equals + param.tag_bracket[0] + text +
                        param.tag_bracket[1] * notmultiline)
        spaces_for_multiline = param.space_before_tag + len(f_words[0]) + increment  # кол-во пробелов для записи
        return spaces_for_multiline                                                  # нескольких строк


print("Введите название файла c шаблонной первой записью")
template = BibFile(input())  # шаблон по первой записи в bib-файле
parameters = BibFileParameters(template)  # берем параметры шаблона
template.file.close()
print("Введите путь к папке, bib файлы внутри которой нужно привести к стилю шаблона")
folder = input()  # папка
path = folder + "\Edited"  # путь к папке с результатами работы
if not os.path.exists(path):  # создаем папку Edited, если еще не создана
    os.makedirs(path)
for files in os.listdir(folder):
    if files.endswith('.bib'):  # для каждого .bib файла
        source_bib = BibFile(files, folder)  # открытый на чтение оригинальный файл
        result_bib = BibFile(files, path, "w")  # открытый на запись файл с результатом
        while True:
            # обработка следующей строки файла
            line = source_bib.next_line()  # читаем строку
            line = LineOperations.del_extra_comma(line)  # удаляем лишнее
            if not line:  # если строк больше нет
                break  # выходим из while (заканчиваем прочтение файла)
            line = line.replace('п»ї', '')  # удаляем символ кодировки UTF-8, если он есть

            # случай пустых строк внутри записи (пропускаются):
            if result_bib.inside == 1 and line[0] == '\n':
                continue

            # ведущие пробелы убираем:
            if line[0] == ' ':
                line = line.lstrip(' ')

            # случай описания на несколько строк:
            if result_bib.multi_line_text == 1:
                result_bib.file.write('\n')  # сначала переходим на новую строку
                line = LineOperations.fix_ending(line)
                line = line.lstrip(' ')
                terminal = LineOperations.terminal_chars(line, result_bib.closing_char)
                if terminal != 0:
                    line = line[:-terminal]  # убираем закрывающую скобочку-кавычку
                    if parameters.tag_bracket[0] == '{':
                        end = '}'
                    else:
                        end = '"'
                    line = line + end  # заменяем на нужный нам по шаблону символ
                    result_bib.multi_line_text = 0  # описание на несколько строк завершилось
                result_bib.file.write(' ' * result_bib.spaces_for_multi + line)  # выводим след. строку с отступом
                continue

            # В случае завершения структуры записи:
            if line[0] == '}':
                result_bib.inside = 0  # отмечаем, что мы выходим из записи
                if result_bib.invalid_type == 1:
                    result_bib.invalid_type = 0
                    continue
                result_bib.file.write("\n")  # ввиду особенности writetofile и правила о запятых
                result_bib.file.write("}\n")  # мы завершаем предыдущую строку либо без запятой (тут)
                result_bib.empty_text = 0
                continue

            # для неправильных записей строки просто пропускаются
            if result_bib.invalid_type == 1:
                continue
            elif result_bib.inside == 1:
                if result_bib.empty_text == 1:
                    result_bib.empty_text = 0
                else:
                    result_bib.file.write(",\n")  # либо с запятой (когда внутри структуры записи)

            # если мы вне записи и строка - не начало записи
            if line[0] != '@' and result_bib.inside == 0:
                result_bib.file.write(line)  # просто печатаем ее без изменений
                continue
            line = LineOperations.fix_ending(line)  # нам будет важен конец строк в структуре, поэтому fix_ending'им

            # если начинается новая запись, а скобка предыдущей не закрыта
            if line[0] == '@' and result_bib.inside == 1:
                result_bib.inside = 0
                result_bib.file.write("}\n\n")  # закрываем скобку и делаем отступы

            # случай первой строки записи
            if line[0] == '@' and result_bib.inside == 0:
                result_bib.inside = 1
                citekey = line[line.find('{') + 1:-1]  # citekey (ключ цитирования) - то, что после скобки и до ','
                citekey = citekey.replace('\\', '').replace('/', '').replace('\'', '')
                if citekey.isnumeric() == 1:  # ключ цитирования не может быть просто числом
                    result_bib.invalid_type = 1
                    continue
                if citekey in result_bib.keys:  # если ключ цитирования уже был, то такую запись не берем
                    result_bib.invalid_type = 1
                    continue
                else:
                    result_bib.keys.add(citekey)  # иначе, добавим ключ цитирования
                words = LineOperations.get_words(line)
                words[0] = WordOperations.word_to_case(words[0], parameters.type_case)
                result_bib.file.write("@" + words[0] + "{" + citekey)
                continue

            # случай внутри записи
            if line[0] != '@' and result_bib.inside == 1:
                equal_pos = line.find('=')  # место "=" для нас важно
                i = 0
                # ищем скобку/кавычку
                while line[equal_pos + i] != '{' and line[equal_pos + i] != '\"' and equal_pos + i != len(line) - 1:
                    i += 1
                bracket_pos = equal_pos + i  # определяем место кавычки (скобочки)
                result_bib.closing_char = line[bracket_pos]  # либо скобочка-кавычка, либо:
                if result_bib.closing_char != '{' and result_bib.closing_char != '"':  # это случай типа: year = 1984
                    j = 1
                    while line[equal_pos + j] == ' ':  # ищем первую позицию текста тэга
                        j += 1
                    if line[len(line) - 1] == ',':
                        tag_text = line[equal_pos+j:-1]
                    else:
                        tag_text = line[equal_pos+j:]
                    tag_text = LineOperations.fix_brackets(tag_text)
                    if tag_text.isspace() or tag_text == "":
                        result_bib.empty_text = 1  # пустые строки некорректны - их мы пропускаем
                        continue
                    BibFileOperations.write_to_file(result_bib, line, parameters, tag_text, 1)
                    continue
                # теперь работаем на обработку конца строки
                if result_bib.closing_char == '{':
                    result_bib.closing_char = '}'  # скобка "переворачивается", а кавычка не изменяется
                terminal = LineOperations.terminal_chars(line, result_bib.closing_char)
                if terminal != 0:  # если описание в одну строку num_of_ending_chars
                    tag_text = line[bracket_pos + 1:-terminal]
                    tag_text = LineOperations.fix_brackets(tag_text)
                    if tag_text.isspace() or tag_text == "":
                        result_bib.empty_text = 1
                        continue
                    BibFileOperations.write_to_file(result_bib, line, parameters, tag_text, 1)
                    continue
                else:  # иначе описание на несколько строк
                    tag_text = line[bracket_pos + 1:]
                    result_bib.multi_line_text = 1
                    tag_text = LineOperations.fix_brackets(tag_text)
                    result_bib.spaces_for_multi = BibFileOperations.write_to_file(result_bib, line,
                                                                                  parameters, tag_text, 0)
        result_bib.keys.clear()  # очищаем сет ключей для нового файла
        source_bib.file.close()  # закрываем исходный файл
        result_bib.file.close()  # закрываем полученный файл
