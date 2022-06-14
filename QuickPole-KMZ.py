from tkinter.filedialog import askdirectory, askopenfilename
import os, time, pandas, shutil


path = askdirectory(title='Please select In-Span, Utilization, Report files location.')

# Check for files

for r, d, f in os.walk(path):
    if len(f) != 3:
        print('Incorrect files in folder, should only have 3 reports.')
        time.sleep(3)
        exit('Exiting.')
    for file in f:
        if file[:19] == 'Project Utilization' and file.endswith('.csv'):
            PUtil = path + '/' + file
        elif file[-22:] == 'Quick Pole Report.xlsx':
            QPex = path + '/' + file
        elif file[:7] == 'In-span' and file.endswith('.csv'):
            Span = path + '/' + file
        else:
            print("Unexpected files found, check names.")
            time.sleep(3)
            exit('Exiting.')

exc = pandas.read_excel(QPex, engine='openpyxl', header=1, usecols='A:B')
comments = exc.values.tolist()

cfile = open(PUtil, 'r')
poles = []

for line in cfile:
    li = line.split(',')
    if li[0] == 'Structure':
        if li[7].find('Insufficient') >= 0:
            cond = 'Pre-analysis failure'
        else:
            cond = 'Good'

        comment = 'NULL'

        for item in comments:
            if item[0] == li[2]:
                comment = item[1]

        poles.append([li[2], li[5][1:], li[6][:-1], comment, cond])

cfile.close()
cfile = open(Span, 'r')
lines = []

for line in cfile:
    li = line.split(',')
    if li[0] == 'Span':
        ass = 'Good'
        for item in poles:
            if item[0] == li[10] or item[0] == li[16]:
                if item[3] != 'NULL':
                    ass = 'Pre-analysis failure'

        comment = 'NULL'
        if item in comments:
            if item[0] == li[2]:
                comment = item[1]

        coord = li[15][:-1] + ',' + li[14][1:] + ',0,' + li[21][:-3] + ',' + li[20][1:] + ',0'
        lines.append([li[2], li[3], ass, comment, coord])

cfile.close()

# Assemble kml
cpath = askopenfilename(title="Select the header file ('base.txt')", defaultextension=".txt")
cfile = open(cpath, 'r') #K:\Personal Files\Patrick Wilkie\Design + Engineering\Python
outfile = open(path + '/doc.kml', 'w')

for line in cfile:
    outfile.write(line)
    

# add poles

pid = 0
for line in poles:
    comment = '<![CDATA[<html><body><table border ="1"><tr><th>Latitude</th><td>' + line[1] + \
              '</td></tr><tr><th>Longitude</th><td>' + line[2] + \
              '</td><tr><tr><th>Comments</th><td>' + line[3] + \
              '</td></tr><tr><th>Condition</th><td>' + line[4] + \
              '</td></tr></table></body></html>]]>'
    outfile.write('\n<Placemark id="ID_' + str(pid).zfill(5) + '">')
    pid = pid + 1
    outfile.write('\n<name>' + line[0] + '</name>')
    outfile.write('\n<snippet></snippet>')
    outfile.write('\n<description>' + comment + '</description>')
    if line[4] == 'Good':
        outfile.write('\n<styleUrl>#IconStyle00</styleUrl>')
    else:
        outfile.write('\n<styleUrl>#IconStyle0108</styleUrl>')

    outfile.write('\n<Point>'
                  '\n<coordinates>' + line[2] + ',' + line[1] + ',0</coordinates>'
                                                                '\n</Point>'
                                                                '\n</Placemark>')

outfile.write('\n</Document>')

# add lines

outfile.write('\n<Document id="Line_layer" xsi:schemaLocation="http://www.opengis.net/kml/2.2 '
              'http://schemas.opengis.net/kml/2.2.0/ogckml22.xsd http://www.google.com/kml/ext/2.2 '
              'http://code.google.com/apis/kml/schema/kml22gx.xsd">'
              '\n<name>Line layer</name><snippet></snippet>'
              '\n<Style id="LineStyle09"><LabelStyle><color>00000000</color><scale>0</scale></LabelStyle><LineStyle>'
              '<color>ff00a838</color><width>2.5</width></LineStyle><PolyStyle><color>00000000</color>'
              '<outline>0</outline></PolyStyle></Style>'
              '<Style id="LineStyle00"><LabelStyle><color>00000000</color><scale>0</scale></LabelStyle><LineStyle>'
              '<color>ff0098e6</color><width>2.5</width></LineStyle><PolyStyle><color>00000000</color>'
              '<outline>0</outline></PolyStyle></Style>')

pid = 0
for line in lines:
    comment = '<![CDATA[<html><body><table border ="1"><tr><th>Span</th><td>' + line[1] + \
              '</td></tr><tr><th>Assessment</th><td>' + line[2] + \
              '</td><tr><tr><th>Comments</th><td>' + line[3] + \
              '</td></tr></table></body></html>]]>'
    outfile.write('\n<Placemark id="ID_' + str(pid).zfill(5) + '">' + '\n<name>' + line[0] + '</name>' +
                  '\n<snippet></snippet>' + '\n<description>' + comment + '</description>')
    pid = pid + 1
    if line[2] == 'Good' and line[3] == 'NULL':
        outfile.write('\n<styleUrl>#LineStyle09</styleUrl>')
    else:
        outfile.write('\n<styleUrl>#LineStyle00</styleUrl>')

    outfile.write('\n<LineString>\n<coordinates>' + line[4] + '</coordinates>\n</LineString>\n</Placemark>')


# finish kml

outfile.write('\n</Document>'
              '\n</Folder>'
              '\n</kml>')

cfile.close()
outfile.close()

# shutil.copyfile()
# shutil.make_archive(path + '\output', 'zip', 'K:\Personal Files\Grigori Bereg\kml\kmz')
# os.remove(os.path.join(path + '\doc.kml'))
# os.remove('K:\Personal Files\Grigori Bereg\kml\kmz\doc.kml')
# os.rename(path + '\output.zip', path + '\output.kmz')
