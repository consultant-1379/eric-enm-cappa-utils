def collapsable_script(html, file):
    """

    :param html:
    :param file:
    :return:
    """
    html += """
    <script> var coll = document.getElementsByClassName('collapsible');
    var i;
    for (i = 0; i < coll.length; i++)
    {coll[i].addEventListener('click', function() {this.classList.toggle('active');
    var content = this.nextElementSibling;if (content.style.display === 'block')
    {content.style.display = 'none';} else {content.style.display = 'block';}});}</script>
    """

    file.write(html)


def filter_script(file, lst, filename):
    """

    :param file:
    :param lst:
    :param filename:
    :return:
    """
    # i = 0
    html = "<script> function " + filename + "_Function() {"
    html += "var list = ["
    length = len(lst)
    lst[-1] = lst[-1].rstrip()
    string = "["
    for i in range(length):
        html += "'" + lst[i] + "'"
        string += "'" + lst[i] + "'"
        if (i + 1) < length:
            html += ","
            string += ","
        else:
            html += "];"
            string += "]"

    # print(string)

    html += "var x=document.getElementById('list_" + filename + "').value; "\
            "var location=list.indexOf(x); "\
            "var input, filter, table, tr, td, i, txtValue; "\
            "input=document.getElementById('Input_" + filename + "'); "\
            "filter=input.value.toUpperCase();" \
            "table=document.getElementById('Table_" + filename + "'); "\
            "tr=table.getElementsByTagName('tr'); "\
            "for (i = 0; i < tr.length; i++) {  "\
            "    td = tr[i].getElementsByTagName('td')[location]; "\
            "    if (td) { txtValue = td.textContent || td.innerText; "\
            "    if (txtValue.toUpperCase().indexOf(filter) > -1) { "\
            "   tr[i].style.display = ''; "\
            "} else { tr[i].style.display = 'none';}}} " \
            "} "\
            "</script> "
    file.write(html)







