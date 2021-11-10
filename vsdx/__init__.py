from __future__ import annotations
import zipfile
import shutil
import os
import re
from enum import IntEnum
from jinja2 import Template
from typing import Optional, List, Dict

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import xml.dom.minidom as minidom   # minidom used for prettyprint

namespace = "{http://schemas.microsoft.com/office/visio/2012/main}"  # visio file name space
ext_prop_namespace = '{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}'
vt_namespace = '{http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes}'
r_namespace = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
document_rels_namespace = "{http://schemas.openxmlformats.org/package/2006/relationships}"
cont_types_namespace = '{http://schemas.openxmlformats.org/package/2006/content-types}'

# utility functions
def to_float(val: str):
    try:
        if val is None:
            return
        return float(val)
    except ValueError:
        return 0.0


class PagePosition(IntEnum):
    FIRST =  0
    LAST  = -1
    END   = -1
    AFTER = -2
    BEFORE= -3

def pretty_print_element(xml: Element) -> str:
    if type(xml) is Element:
        return minidom.parseString(ET.tostring(xml)).toprettyxml()
    elif type(xml) is ET.ElementTree:
        return minidom.parseString(ET.tostring(xml.getroot())).toprettyxml()
    else:
        return f"Not an Element. type={type(xml)}"


# TODO: This is here temporarily to appease Page.set_name()
# Ideally, messing with the direct contents of the vsdx directory tree should
# only be done by VisioFile class.
def file_to_xml(filename: str) -> ET.ElementTree:
    """Import a file as an ElementTree"""
    try:
        tree = ET.parse(filename)
        return tree
    except FileNotFoundError:
        pass  # return None




from vsdx.shapes import Cell
from vsdx.shapes import DataProperty
from vsdx.shapes import Shape
from vsdx.connectors import Connect
from vsdx.pages import Page
from vsdx.vsdxfile import VisioFile
