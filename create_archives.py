# coding: utf-8

# Install dependencies are installed
#get_ipython().system(u'pip install httpie')
# Download test cases
#get_ipython().system(u'mkdir -p sbml-test-cases')
#get_ipython().system(u'http --download http://sourceforge.net/projects/sbml/files/test-suite/3.1.1/cases-archive/sbml-test-cases-2014-10-22.zip/download --output sbml-test-cases/cases.zip   ')
# Setup destination for archives
#get_ipython().system(u'mkdir -p archives')
# Unzip test cases
#get_ipython().system(u'cd sbml-test-cases && unzip cases.zip > /dev/null')

import xml.etree.ElementTree as ET                                                                                                                                                                             
from os import listdir
from os import path
import os


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Find all sbml test cases
root_path = path.abspath('sbml-test-cases/cases/semantic/')
cases = [case for case in listdir(root_path) if is_number(case)]
cases = sorted(cases)


import re
from xml.dom import minidom

for case in cases:
    folder_path = path.join(root_path, case)
    ls = listdir(folder_path)
    regex_sbml = re.compile(case + '-sbml-l\dv\d\.xml', re.IGNORECASE) 
    regex_sedml = re.compile(case + '-sbml-l\dv\d\-sedml.xml', re.IGNORECASE) 

    sbmlfiles = sorted([file for file in ls if regex_sbml.search(file)])
    sedmlfiles = sorted([file for file in ls if regex_sedml.search(file)])
    plot_file = [file for file in ls if 'plot.jpg' in file][0]

    ET.register_namespace('', 'http://identifiers.org/combine.specifications/omex-manifest')
    manifest_template = '''<?xml version="1.0" encoding="UTF-8"?>
    <omexManifest
        xmlns="http://identifiers.org/combine.specifications/omex-manifest"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://identifiers.org/combine.specifications/omex-manifest combine.xsd "></omexManifest>
    ''' 

    doc = ET.fromstring(manifest_template)
    manifest = ET.SubElement(doc, 'content')
    manifest.attrib['format'] = 'http://identifiers.org/combine.specifications/omex-manifest'
    manifest.attrib['location'] = './manifest.xml'

    for sbmlfile in sbmlfiles:      
        model = ET.SubElement(doc, 'content')
        model.attrib['format'] = 'http://identifiers.org/combine.specifications/sbml'
        model.attrib['location'] = './' + sbmlfile

    for sedmlfile in sedmlfiles:
        sedml = ET.SubElement(doc, 'content')
        sedml.attrib['format'] = 'http://identifiers.org/combine.specifications/sedml'
        sedml.attrib['location'] = './' + sedmlfile

    manifest_path = path.join(folder_path, 'manifest.xml')
    with open(manifest_path, 'wb') as f:
        xml_str = ET.tostring(doc, encoding='UTF-8')
        # reparse the xml string to pretty print it
        reparsed = minidom.parseString(xml_str)
        pretty_xml_str = reparsed.toprettyxml(indent="    ")
        f.write(pretty_xml_str)

    # Zipping Combine archive
    from zipfile import ZipFile
    archive_path = path.join('archives', case + '.zip')
    initial_wd = os.getcwd()
    ls = listdir(folder_path)
    with ZipFile(archive_path, 'w') as archive:
        os.chdir(folder_path)
        for f in ls:
            archive.write(f)

    os.chdir(initial_wd)

