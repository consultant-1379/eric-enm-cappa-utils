from utils.cappa_constants import CSS_FILE
from report_generation import scripting


def generate_headers(line1, html, filename, file):
    """

    :param line1:
    :param html:
    :param filename:
    :param file:
    :return:
    """
    split = line1.split(",")
    scripting.filter_script(file, split, filename)
    button = """
    <button type='button' class='collapsible'>{file}</button>
    <div class='content'>""".format(file=filename)

    filters = """
    <input type='text' 
        id='Input_{file}' 
        onkeyup='{file}_Function()' 
        placeholder='Search' 
        title='Type'>
    <select id='list_{file}'>""".format(file=filename)

    for i in range(len(split)):
        filters += "\n<option value='" + split[i] + "'>" + split[i] + "</option>"
    filters += "</select>"
    html += "<table border='1' id='Table_" + filename + "'><tr>"
    for i in range(len(split)):
        html += "<th>" + split[i] + "</th>"
    html += "</tr>"
    file.write(button)
    file.write(filters)
    file.write(html)


def generate_content(main_content, html, file, filename):
    """

    :param main_content:
    :param html:
    :param file:
    :param filename:
    :return:
    """
    split = main_content.split(",")

    html += "<tr>"

    if filename == "all_files":
        if split[3] == "\"/sys/fs/cgroup/cpu":
            split[3:5] = [','.join(split[3:5])]
            # print(split)
    length = len(split)

    for i in range(length):
        if filename == "Interesting_sockets":
            if i == 6:
                split[6] = split[6].replace("<", "")
                split[6] = split[6].replace(">", "")
        html += "<td>" + split[i] + "</td>"
    html += "</tr>"
    file.write(html)


def add_css(html, file):
    """

    :param html:
    :param file:
    :return:
    """
    with open(CSS_FILE) as f:
        html += f.read()
    file.write(html)


