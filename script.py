import os
import io


def param(file):                                        # Функция взятия параметров из файла
    line = file.readline()                              # Читаем первую линию и заменяем специальные знаки
    words = line.replace('@', ' ').replace('{', ' ').replace(',', ' ').replace('п»ї', ' ').split()
    if words[0].islower() == 1:                         # Проверка на регистр
        tag = "S"                                       # запоминаем тэг Small
    elif words[0].isupper() == 1:
        tag = "B"                                       # Тэг - Big
    else:
        tag = "T"                                       # Тэг - Title
    line = f.readline()                                 # Читаем вторую строку файла
    spaceinfront = len(line) - len(line.lstrip(' '))    # Считаем количество пробелом в начале
    line = line.lstrip(' ')                             # Убираем эти пробелы
    firstword = ""
    spaceaftertype = 0
    cnt = -1
    for i in line:                                      # Идем по строке
        cnt += 1
        if i != '=':
            if i == ' ':
                spaceaftertype += 1                     # Увеличиваем пробелы после имени
            else:
                firstword += i                          # Длина первого слова
            continue
        break
    if firstword.islower() == 1:
        typetag = "S"                                   # Запоминаем регистр "имени" Small
    elif firstword.isupper() == 1:
        typetag = "B"                                   # Big
    else:
        typetag = "T"                                   # Title
    if line.find('{') != -1:
        tagsymbol = '{'                                 # Запоминаем во что заключен описывающий текст
    else:
        tagsymbol = '"'
    return tag, spaceinfront, spaceaftertype, tagsymbol, cnt, typetag


def writelinetofile(edit, line, Temp, cont, notmultiline):
    words = line.replace('{', ' ').replace('}', ' ').replace('"', ' ').replace('=', ' ').split()
    spacesbeforecont = 0                                   # Пробелы до начала текста (для случая MultiLine)
    if Temp[5] == "S":
        words[0] = words[0].lower()
    elif Temp[5] == "B":
        words[0] = words[0].upper()
    else:
        words[0] = words[0].title()
    if Temp[2] > 1:
        position = Temp[4] - Temp[1] - len(words[0])       # Высчитываются пробелы от имени до фикс. позиции "="
        if Temp[3] == '{':                                 # Конструируется сама строка:
            edit.write(" " * Temp[1] + words[0] + " " * position + "= {" + cont + "}" * notmultiline)
        else:
            edit.write(" " * Temp[1] + words[0] + " " * position + "= \"" + cont + "\"" * notmultiline)
        spacesbeforecont = Temp[1] + len(words[0]) + position + 3
    elif Temp[3] == '{':
        edit.write(" " * Temp[1] + words[0] + " " * Temp[2] + "= {" + cont + "}" * notmultiline)
    else:
        edit.write(" " * Temp[1] + words[0] + " " * Temp[2] + "= \"" + cont + "\"" * notmultiline)
        spacesbeforecont = Temp[1] + len(words[0]) + Temp[2] + 3
    return spacesbeforecont


def ifmultiline(line, char):
    if line[-1:] == char:           # Последний символ равен char
        return 1
    if line[-2:] == (char + ","):   # Последние два символа соответствуют char+','
        return 2
    else:
        return 0


def fix(line):
    if line[len(line) - 1] == '\n':
        line = line[:-1]
        if line[len(line) - 1] == ' ':
            line = line.rstrip(' ')
    return line


print("Введите название файла c шаблонной первой записью")
name = input()
f = io.open(name, "r", encoding="utf8")
Temp = param(f)                                 # Сохраняем нужные параметры
f.close()
print("Введите путь к папке, bib файлы внутри которой нужно привести к стилю шаблона")
folder = input()
path = folder + "\Edited"
if not os.path.exists(path):                    # Если папа Edited еще не создана
    os.makedirs(path)                           # Создаем
for file in os.listdir(folder):
    if file.endswith('.bib'):                   # Для каждого .bib файла
        with io.open(os.path.join(folder, file), mode="r", errors='ignore') as fa:
            edit = io.open(path + "\\" + file, mode="w")
            inside = 0                          # =1, если внутри структуры записи
            multilinecont = 0                   # =1, если описание на несколько строк
            multispace = 0                      # равно числу пробелов для записи друг под другом
            a = ''                              # храним скобочку или кавычку
            while True:
                line = fa.readline()
                if not line:                    # Если строк больше нет
                    break                       # Выходим из while (заканчиваем прочтение файла)
                line = line.replace('п»ї', '')
                if inside == 1 and line[0] == '\n':
                    continue
                if line[0] == ' ':
                    line = line.lstrip(' ')     # ведущие пробелы больше не нужны
                if multilinecont == 1:          # случай описания на несколько строк
                    edit.write('\n')
                    line = fix(line)
                    line = line.lstrip(' ')
                    if ifmultiline(line, a) != 0:
                        line = line[:-(ifmultiline(line, a))] # убираем закрывающую скобочку-кавычку
                        if Temp[3] == '{':
                            end = '}'
                        else:
                            end = '"'
                        line = line + end                     # заменяем на нужный нам по шаблону символ
                        multilinecont = 0                     # описание на несколько строк завершилось
                    edit.write(' ' * multispace + line)       # в любом случае нам нужно вывести строку
                    continue
                if line[0] == '}':                            # только в случае завершения структуры записи
                    edit.write("\n")                          # ввиду особенности writetofile и правила о запятых
                    edit.write("}\n")                         # мы завершаем предыдущую строку либо без запятой (тут)
                    inside = 0
                    continue
                elif inside == 1:
                    edit.write(",\n")                         # либо с запятой (когда внутри структуры записи)
                if line[0] != '@' and inside == 0:            # если мы вне записи и строка - не начало записи
                    edit.write(line)                          # просто печатаем ее без изменений
                    continue
                line = fix(line)                              # нам будет важен конец строк в структуре, поэтому fix'им
                if line[0] == '@' and inside == 0:
                    inside = 1
                    cont = line[line.find('{') + 1:-1]
                    words = line.replace('@', ' ').replace('{', ' ').replace(',', ' ').split()
                    if Temp[0] == "B":
                        words[0] = words[0].upper()
                    elif Temp[0] == "S":
                        words[0] = words[0].lower()
                    else:
                        words[0] = words[0].title()
                    edit.write("@" + words[0] + "{" + cont)
                    continue
                if line[0] != '@' and inside == 1:
                    posEqual = line.find('=')              # место "=" для нас важно
                    pos = posEqual + 1
                    a = line[pos]                          # либо скобочка-кавычка идет сразу после равно
                    if a == ' ':
                        pos += 1
                        a = line[pos]                      # либо через один символ после равно
                    if a != '{' and a != '"':              # это случай типа " year = 1984 "
                        if line[len(line) - 1] == ',':
                            cont = line[pos:-1]
                        else:
                            cont = line[pos:]
                        writelinetofile(edit, line, Temp, cont, 1)
                        continue
                    if a == '{':
                        a = '}'                            # теперь работаем на обработку конца строки
                    if ifmultiline(line, a) != 0:          # если описание на несколько строк
                        cont = line[pos + 1:-(ifmultiline(line, a))]
                        writelinetofile(edit, line, Temp, cont, 1)
                        continue
                    else:                                  # иначе описание заканчивается на той же строке
                        cont = line[pos + 1:]
                        multilinecont = 1
                        multispace = writelinetofile(edit, line, Temp, cont, 0)
            edit.close()                                   # закрываем новый файл
        fa.close()                                         # закрываем исходный файл
