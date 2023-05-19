#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs
from time import sleep

from libs.canvas.Shape import Shape, ShapePoints
from libs.standalones.Vector import Vector2Int

XML_EXT = '.xml'
JPG_EXT = '.jpg'

class PascalVocWriter:

    def __init__(self, folder_name, filename, img_size, database_src='Unknown', local_img_path=None):
        self.folder_name = folder_name
        self.filename = filename
        self.database_src = database_src
        self.img_size = img_size
        self.box_list = []
        self.local_img_path = local_img_path
        self.verified = False

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True, encoding='utf-8').replace("  ".encode(), "\t".encode())
        # minidom does not support UTF-8
        # reparsed = minidom.parseString(rough_string)
        # return reparsed.toprettyxml(indent="\t", encoding='utf-8')

    def gen_xml(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.folder_name is None or \
                self.img_size is None:
            return None

        top = Element('annotation')

        folder = SubElement(top, 'folder')
        folder.text = self.folder_name

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        if self.local_img_path is not None:
            local_img_path = SubElement(top, 'path')
            local_img_path.text = self.local_img_path

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.database_src

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.img_size[0])
        height.text = str(self.img_size[1])
        if len(self.img_size) == 3:
            depth.text = str(self.img_size[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def add_bnd_box(self, x_min, y_min, x_max, y_max, name):
        bnd_box = {'xmin': x_min, 'ymin': y_min, 'xmax': x_max, 'ymax': y_max}
        bnd_box['name'] = name
        self.box_list.append(bnd_box)

    def append_objects(self, top):
        for each_object in self.box_list:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            name.text = each_object['name']
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            if int(float(each_object['ymax'])) == int(float(self.img_size[0])) or (int(float(each_object['ymin'])) == 1):
                truncated.text = "1"  # max == height or min
            elif (int(float(each_object['xmax'])) == int(float(self.img_size[1]))) or (int(float(each_object['xmin'])) == 1):
                truncated.text = "1"  # max == width or min
            else:
                truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = "0"
            bnd_box = SubElement(object_item, 'bndbox')
            x_min = SubElement(bnd_box, 'xmin')
            x_min.text = str(each_object['xmin'])
            y_min = SubElement(bnd_box, 'ymin')
            y_min.text = str(each_object['ymin'])
            x_max = SubElement(bnd_box, 'xmax')
            x_max.text = str(each_object['xmax'])
            y_max = SubElement(bnd_box, 'ymax')
            y_max.text = str(each_object['ymax'])

    def save(self, target_file=None):
        root = self.gen_xml()
        self.append_objects(root)
        out_file = None
        if target_file is None:
            out_file = codecs.open(
                self.filename + XML_EXT, 'w', encoding='utf-8')
        else:
            out_file = codecs.open(target_file, 'w', encoding='utf-8')

        prettify_result = self.prettify(root)
        out_file.write(prettify_result.decode('utf8'))
        out_file.close()


class PascalVocReader:

    def __init__(self, file_path: str):
        if file_path.endswith(JPG_EXT):
            file_path = file_path.replace(JPG_EXT, XML_EXT)
        self.shapes: list[Shape] = []
        self.file_path = file_path
        self.verified = False

        if not os.path.exists(file_path):
            return
        try:
            self.parse_xml()
        except:
            pass

    def get_shapes(self):
        return [shape.copy() for shape in self.shapes] if self.shapes else []

    def get_labels(self):
        return self.box_quantity
            

    def add_shape(self, label, bnd_box):
        x_min = int(float(bnd_box.find('xmin').text))
        y_min = int(float(bnd_box.find('ymin').text))
        x_max = int(float(bnd_box.find('xmax').text))
        y_max = int(float(bnd_box.find('ymax').text))
        points = [Vector2Int(x_min, y_min), Vector2Int(x_max, y_min), Vector2Int(x_max, y_max), Vector2Int(x_min, y_max)]
        self.shapes.append(Shape(label, points))

    #japa
    def find_label(self, label):
        assert self.file_path.endswith(XML_EXT), "Unsupported file format"
        parser = etree.XMLParser(encoding='utf-8')
        try: 
            xml_tree = ElementTree.parse(self.file_path, parser=parser).getroot()
        except FileNotFoundError as e:
            return False

        filename = xml_tree.find('filename').text
        for object_iter in xml_tree.findall('object'):
            if len(object_iter) == 0:
                if label == 'none' or label == 'null':
                    return True
                continue
            _label = object_iter.find('name').text
            if _label == label or label == 'any' or label == '*':
                return True
        return False

    def parse_xml(self):
        assert self.file_path.endswith(XML_EXT), "Unsupported file format"
        parser = etree.XMLParser(encoding='utf-8')
        xml_tree = ElementTree.parse(self.file_path, parser=parser).getroot()

        self.shapes = []

        for object_iter in xml_tree.findall('object'):
            if len(object_iter) == 0:
                continue
            bnd_box = object_iter.find("bndbox")
            label = object_iter.find('name').text
            self.add_shape(label, bnd_box)
        return True
