import os

from report_generation import scripting, table_generator
from utils.cappa_constants import CAPPA_CSV_DIR, HTML_REPORT


def generate_tags(html, file):
    """

    :param html:
    :param file:
    :return:
    """
    html += """
    <html>
      <head> 
        <meta content='text/html;charset=utf-8' http-equiv='Content-Type'> 
        <meta content='utf-8' http-equiv='encoding'> 
      </head>
    <body>
    """
    table_generator.add_css(html, file)


def generate_report(podname):
    """

    :return:
    """
    html = ""
    with open('output/{0}/cappa_report.html'.format(podname), "w") as cappa_report:
        generate_tags(html, cappa_report)

        # Updated to not use Path as that is not in Python2.7
        cappa_csvs = [os.path.join(CAPPA_CSV_DIR + podname +"/", csv)
                      for csv in os.listdir(CAPPA_CSV_DIR + podname +"/")]

        for csv in cappa_csvs:
            file_name = os.path.basename(csv).replace('.csv', '')\
                .replace('-', '_')

            with open(csv) as csv_file:
                file_lines = csv_file.readlines()
                header = True
                for line in file_lines:
                    if header:
                        table_generator.generate_headers(line, html, file_name,
                                                         cappa_report)
                        header = False
                    else:
                        table_generator.generate_content(line, html,
                                                         cappa_report, file_name)
                closetable = "</table></div>"
                cappa_report.write(closetable)
        scripting.collapsable_script(html, cappa_report)

        html += "</body></html>"
        cappa_report.write(html)
