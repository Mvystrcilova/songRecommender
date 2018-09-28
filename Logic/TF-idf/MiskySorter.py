import os

directory = os.fsencode("Songs_with_distances")

for file in os.listdir(directory):
    filename = os.fdecode(file)
    lines = open(filename, 'r', encoding='utf-8').readlines
    out = open(filename + '_' + "sorted", 'a', encoding='utf8')

    for line in sorted(lines, key=float, line.split('\t')[2])
        out.write(line)
    out.close()


