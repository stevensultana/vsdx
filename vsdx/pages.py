from __future__ import annotations
from typing import Optional, List, Dict
from typing import TYPE_CHECKING

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import vsdx
from vsdx import namespace
from vsdx import Connect
from vsdx import Shape

if TYPE_CHECKING:
    from vsdx import VisioFile

# if TYPE_CHECKING:
    # from vsdx import Connect
    # from vsdx import Shape


class Page:
    """Represents a page in a vsdx file

    :param vis: the VisioFile object the page belongs to
    :type vis: :class:`VisioFile`
    :param name: the name of the page
    :type name: str
    :param connects: a list of Connect objects in the page
    :type connects: List of :class:`Connect`

    """
    def __init__(self, xml: ET.ElementTree, filename: str, page_name: str, vis: VisioFile):
        self._xml = xml
        self.filename = filename
        self.name = page_name
        self.vis = vis
        self.max_id = 0

    def __repr__(self):
        return f"<Page name={self.name} file={self.filename} >"

    @property
    def connects(self):
        return self.get_connects()

    def set_name(self, value: str):
        # todo: change to name property
        pages_filename = self.vis._pages_filename()  # pages contains Page name, width, height, mapped to Id
        pages = vsdx.file_to_xml(pages_filename)  # this contains a list of pages with rel_id and filename
        page = pages.getroot().find(f"{namespace}Page[{self.index_num + 1}]")
        #print(f"set_name() page={pretty_print_element(page)}")
        if page:
            page.attrib['Name'] = value
            self.name = value
            self.vis.pages_xml = pages

    @property
    def xml(self):
        return self._xml

    @xml.setter
    def xml(self, value):
        self._xml = value

    @property
    def shapes(self):
        """Return a list of :class:`Shape` objects

        Note: typically returns one :class:`Shape` object which itself contains :class:`Shape` objects

        """
        return [Shape(xml=shapes, parent=self, page=self) for shapes in self.xml.findall(f"{namespace}Shapes")]

    def sub_shapes(self) -> List[Shape]:
        """Return list of Shape objects at top level of Page

        :returns: list of `Shape` objects
        :rtype: List[Shape]
        """
        # note that self.shapes should always return a single shape
        return self.shapes[0].sub_shapes()

    def set_max_ids(self):
        # get maximum shape id from xml in page
        for shapes in self.shapes:
            for shape in shapes.sub_shapes():
                id = shape.get_max_id()
                if id > self.max_id:
                    self.max_id = id

        return self.max_id

    @property
    def index_num(self):
        # return zero-based index of this page in parent pages list
        return self.vis.pages.index(self)

    def add_connect(self, connect: Connect):
        connects = self.xml.find(f".//{namespace}Connects")
        if connects is None:
            connects = ET.fromstring(f"<Connects xmlns='{namespace[1:-1]}' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships'/>")
            self.xml.getroot().append(connects)
            connects = self.xml.find(f".//{namespace}Connects")

        connects.append(connect.xml)

    def get_connects(self):
        elements = self.xml.findall(f".//{namespace}Connect")  # search recursively
        connects = [Connect(xml=e, page=self) for e in elements]
        return connects

    def get_connectors_between(self, shape_a_id: str='', shape_a_text: str='',
                              shape_b_id: str='', shape_b_text: str=''):
        shape_a = self.find_shape_by_id(shape_a_id) if shape_a_id else self.find_shape_by_text(shape_a_text)
        shape_b = self.find_shape_by_id(shape_b_id) if shape_b_id else self.find_shape_by_text(shape_b_text)
        connector_ids = set(a.ID for a in shape_a.connected_shapes).intersection(
            set(b.ID for b in shape_b.connected_shapes))

        connectors = set()
        for id in connector_ids:
            connectors.add(self.find_shape_by_id(id))
        return connectors

    def apply_text_context(self, context: dict):
        for s in self.shapes:
            s.apply_text_filter(context)

    def find_replace(self, old: str, new: str):
        for s in self.shapes:
            s.find_replace(old, new)

    def find_shape_by_id(self, shape_id) -> Shape:
        for s in self.shapes:
            found = s.find_shape_by_id(shape_id)
            if found:
                return found

    def _find_shapes_by_id(self, shape_id) -> List[Shape]:
        # return all shapes by ID - should only be used internally
        found = list()
        for s in self.shapes:
            found = s.find_shapes_by_id(shape_id)
            if found:
                return found
        return found

    def find_shapes_with_same_master(self, shape: Shape) -> List[Shape]:
        # return all shapes with master
        found = list()
        for s in self.shapes:
            found = s.find_shapes_by_master(master_page_ID=shape.master_page_ID,
                                            master_shape_ID=shape.master_shape_ID)
            if found:
                return found
        return found

    def find_shape_by_text(self, text: str) -> Shape:
        for s in self.shapes:
            found = s.find_shape_by_text(text)
            if found:
                return found

    def find_shapes_by_text(self, text: str) -> List[Shape]:
        shapes = list()
        for s in self.shapes:
            found = s.find_shapes_by_text(text)
            if found:
                shapes.extend(found)
        return shapes

    def find_shape_by_property_label(self, property_label: str) -> Shape:
        # return first matching shape with label
        # note: use label rather than name as label is more easily visible in diagram
        for s in self.shapes:
            found = s.find_shape_by_property_label(property_label)
            if found:
                return found

    def find_shapes_by_property_label(self, property_label: str) -> List[Shape]:
        # return all matching shapes with property label
        shapes = list()
        for s in self.shapes:
            found = s.find_shapes_by_property_label(property_label)
            if found:
                shapes.extend(found)
        return shapes
