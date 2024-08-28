import pathlib
import base64

contents = pathlib.Path("./base64").iterdir()
for path in contents:
    base64.encode(open(path, 'rb'), open("writeFile.txt", 'wb'))

    a_file = open("writeFile.txt", "r")
    string_without_line_breaks = ""
    for line in a_file:
        stripped_line = line.rstrip()
        string_without_line_breaks += stripped_line
    a_file.close()
    print(path)
    print(string_without_line_breaks)


