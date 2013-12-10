# -*- coding: utf-8 -*-
import sys

from PySide import QtGui, QtCore
from node import Node


class DictionaryTreeModel(QtCore.QAbstractItemModel):
    """Data model providing a tree view of an arbitrary dictionary"""

    def __init__(self, root, parent=None):
        super(DictionaryTreeModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        """the number of rows is the number of children"""
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        """Number of columns is always 2 since dictionaries consist of key-value pairs"""
        return 2

    def data(self, index, role):
        """returns the data requested by the view"""
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """this method gets called when the user changes data"""
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setData(index.column(), value)
                return True
        return False

    def headerData(self, section, orientation, role):
        """returns the name of the requested column"""
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Key"
            if section == 1:
                return "Value"

    def flags(self, index):
        """everything is editable"""
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsEditable)

    def parent(self, index):
        """returns the parent from given index"""
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        """returns an index from given row, column and parent"""
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        """returns a Node() from given index"""
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        """insert rows from starting position and number given by rows"""
        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()
        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        """remove the rows from position to position+rows"""
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()
        return success

    def to_dict(self):
        return self._rootNode.to_dict()


def node_structure_from_dict(datadict, parent=None, root_node=None):
    """returns a hierarchical node stucture required by the TreeModel"""
    if not parent:
        root_node = Node('Root')
        parent = root_node

    for name, data in datadict.items():
        node = Node(name, parent)
        if isinstance(data, dict):
            node = node_structure_from_dict(data, node, root_node)
        else:
            node.value = data

    return root_node


class DictionaryTreeWidget(QtGui.QTreeView):
    """returns an object containing the tree of the given dictionary d.
    example:

    tree = DictionaryTree(d)
    tree.edit()
    d_edited = tree.dict()

    d_edited contains the dictionary with the edited data.
    this has to be refactored...
    """

    def __init__(self, d):
        super(DictionaryTreeWidget, self).__init__()
        self.load_dictionary(d)
        #hbox = QtGui.QHBoxLayout()
        #hbox.addWidget(self._view)
        #        self.setLayout(hbox)

    def load_dictionary(self,d):
        """load a dictionary into my tree applicatoin"""
        self._d = d
        self._nodes = node_structure_from_dict(d)
        self._model = DictionaryTreeModel(self._nodes)
        #self._view = QtGui.QTreeView()
        self.setModel(self._model)

    def to_dict(self):
        """returns a dictionary from the tree-data"""
        return self._model.to_dict()


class DictionaryTreeDialog(QtGui.QDialog):
    """TODO"""
    def __init__(self, d):
        super(DictionaryTreeDialog, self).__init__()
        self.treeWidget = DictionaryTreeWidget(d)

        buttonOk = QtGui.QPushButton('Ok', self)
        buttonCancel = QtGui.QPushButton('Cancel', self)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.treeWidget)

        bhbox = QtGui.QHBoxLayout(self)
        bhbox.addWidget(buttonOk)
        bhbox.addWidget(buttonCancel)

        vbox.addLayout(bhbox)
        self.setLayout(vbox)

    def edit(self):
        return self.exec_()

    def to_dict(self):
        return self.treeWidget.to_dict()


if __name__=='__main__':
    try:
        app = QtGui.QApplication(sys.argv)
    except:
        app = QtGui.qApp

    d = {'First name': 'Maximus',
         'Last name': 'Mustermann',
         'Nickname': 'Max',
         'Address':{ 'Street': 'Musterstr.',
                     'House number': 13,
                     'Place': 'Orthausen',
                     'Zipcode': 76123},
         'An Object': float,
         'Great-grandpa':{
             'Grandpa':{
                 'Pa': 'Child'}}
     }

    tree = DictionaryTreeDialog(d)
    tree.edit()

    print(tree.to_dict())
    edited_dict = tree.to_dict()
    print('my object is still of type: {}'.format(edited_dict['An Object']))

    #sys.exit(app.exec_())
