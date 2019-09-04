# Author: Jonathan Dorsey
# Last updated: 6/10/2019

import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

BLUE = '#adccff'
LIGHT_GRAY = '#FFF'
GRAY = '#EAECEE'

class Table(ttk.Frame):
    """
    Class to represent a data table using a tk Treeview. The table is
    sortable (by clicking on any column header) and scalable (simply add more
    rows or columns).
    """

    def __init__(self, master=None, cols=None, data=None):
        """
        Returns a newly initialized Table containing the underlying Treeview
        and table metadata.
        master - the container the table will fit in
        cols - the headers of each column in the table
        data - 2-d array consisting of a list of rows where each row has
                the corresponding column data
                [[row1 data1, row1 data2, row1 data3], [row2 data1, ...],...]
        """

        self.master = master
        self.cols = cols
        self.data = data
        self.descending = True
        self.last_focus = {'iid' : None, 'tags' : None}
        self.init_table()

    def init_table(self):
        """
        Method that performs the majority of the table (treeview) setup
        """

        # create treeview
        self.tree = ttk.Treeview(columns=self.cols, show='headings')
        self.tree.tag_configure('evenrow', background=LIGHT_GRAY)
        self.tree.tag_configure('oddrow', background=GRAY)
        self.tree.tag_configure('hovered_row', background=BLUE)
        self.tree.bind('<Motion>', self.highlight_row)

        # add scrollbars
        ysb = ttk.Scrollbar(orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set

        # grid table and scollbars
        # [table ysb]
        # [xsb      ]
        self.tree.grid(in_=self.master, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.master, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.master, row=1, column=0, sticky=tk.EW)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # change heading style
        style = ttk.Style()
        style.configure('Treeview.Heading', font=('Helvetica', 15, 'bold'), 
                        background=BLUE)
        style.configure('Treeview', font=('Helvetica', 12))
        self.insert_data()

    def insert_data(self):
        """
        Method that inserts each row in data to our Treeview tree. Each row
        is assigned a tag 'odd' or 'even' indicating the shade of its 
        background.
        """

        for c in self.cols:
            # add sorting functionality to headers when clicked
            self.tree.heading(c, text=c, command=lambda c=c: self.sort_cols(c))
            self.tree.column(c, width=Font().measure(c))
        
        odd = True
        for item in self.data:
            # add each row in data
            if odd:
                self.tree.insert('', 'end', values=item, tags=('oddrow',))
            else:
                self.tree.insert('', 'end', values=item, tags=('evenrow',))
            odd = not odd
            for idx, val in enumerate(item):
                # add more space to column if needed
                iwidth = Font().measure(val)
                if self.tree.column(self.cols[idx], 'width') < iwidth:
                    self.tree.column(self.cols[idx], width=iwidth)
        
    def sort_cols(self, col):
        """
        Method to sort each column in the table by ascending or descending
        value. As each cell in the table is stored as a string, numerical 
        strings must be cast to floats to compare numerically. Non-numerical
        strings are sorted lexicographically.
        """

        data = [(self.tree.set(child, col), child) for child in 
                self.tree.get_children('')]
        if data[0][0][0:1] in "0123456789":
            # if the cell begins with number, assume it is numerical string
            data = [(float(x[0]), x[1]) for x in data]
        data.sort(reverse=self.descending)
        odd = True
        for i, item in enumerate(data):
            # move each row in table to correspond with newly sorted column
            self.tree.move(item[1], '', i)
            if odd:
                self.tree.item(item[1], tags=('oddrow',))
            else:
                self.tree.item(item[1], tags=('evenrow',))
            odd = not odd
        # reverse order
        self.descending = not self.descending

    def highlight_row(self, event):
        """
        Method to highlight each row in the table when hovered. Exploits
        <motion> attribute of widgets.
        """

        iid = self.tree.identify_row(event.y)
        if iid != self.last_focus['iid']:
            # do nothing if hovering same row
            if self.last_focus['iid']:
                self.tree.item(self.last_focus['iid'], 
                                tags=self.last_focus['tags'])
            self.last_focus['tags'] = self.tree.item(iid)['tags']
            self.tree.item(iid, tags=['hovered_row'])
            self.last_focus['iid'] = iid
