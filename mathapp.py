# created on 5/9/22 at 23:13

import json
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog
import webbrowser

root = Tk()
root.title('Worksheet Browser')
root.geometry('400x300')
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)


class nestedSelector():
    # tkinter combobox that update its options when the value of its parent combobox changed

    def __init__(self, options=None, default=None, disabled=True, updator=None, *args, **kwargs):

        self.child = None  # the child that is supposed to change when *this* box changes
        self.disabled = disabled  # whether if the box starts disabled
        self.selector_var = StringVar(root)  # the variable of the box, for tracing
        self.selector_var.trace_add("write", self.demand_child)

        self.updator = updator  # function that returns the list of updated options upon demand

        self.default = default  # defaulted value
        if options is not None:  # wrangling with the default states...
            if default is not None:
                if isinstance(default,int):  # default is given as the index in the options list
                    self.default = options[default]
                    self.selector_var.set(options[default])
                elif default not in options:  # given explicit default, but not included
                    options = [default] + options
                    self.selector_var.set(options[0])
                else:  # given explicit default, and is included in the options
                    self.selector_var.set(default)

        # the combobox itself
        self.selector = ttk.Combobox(root, textvariable=self.selector_var, width=30)
        self.selector['values'] = options
        self.selector.configure(state="disabled" if disabled else 'readonly')  # readonly = typing not allowed
        self.selector.grid(*args, **kwargs)

    def demand_child(self,*args):  # asks the child to do stuff
        if self.child is not None:
            self.child.obey_parent(instruction=self.value)

    def obey_parent(self,instruction):  # receiving signal from parent, along with an instruction
        self.enable()
        self.update_options(instruction=instruction)

    def enable(self):  # de-disable the box
        self.disabled = False
        self.selector.configure(state="readonly")

    def update_options(self, instruction):  # update the options of the box when the parent demands
        if self.updator is not None:
            try:
                self.selector['values'] = tuple()
                default = [self.default] if self.default is not None else []
                new_options = default + self.updator(instruction)
                self.selector['values'] = new_options
                if self.default is not None:
                    self.selector.set(new_options[self.default])
                else: self.selector.set(new_options[0])
            except: pass

    def add_child(self, child):
        self.child = child
        self.demand_child()

    @property
    def value(self):
        return self.selector_var.get()

    @property
    def specified(self):
        return not self.value == self.default


class respondingDictionary():
    # tkinter Treeview with two columns, representing a dictionary with key:value in each row
    # updates the values when a parent demands

    def __init__(self, columns, updator, widths=None, *args, **kwargs):
        self.updator = updator

        # columns: the names of columns
        # updator: same as nestedSelectors
        # widths: a list of numbers, indicating the width of each column

        # the Treeview table
        self.table = ttk.Treeview(root, columns=tuple(columns))
        self.table.column("#0", width=0, stretch=False)
        for i, col in enumerate(columns):
            self.table.heading(col, text=col, anchor=CENTER)
            if widths is None:
                self.table.column(col, stretch=True)
            else:
                self.table.column(col, minwidth=widths[i], width=widths[i], stretch=True)
        self.table.grid(*args, **kwargs)

        # opens link upon double click or ENTER key
        self.table.bind("<Double-1>", self.open_link)
        self.table.bind("<Return>", self.open_link)

    def update(self,instruction):  # update the entries in the table
        try:
            new_data = self.updator(instruction)  # get the new entries from the updator function
            self.table.delete(*self.table.get_children())  # delete all entries
            for id,key in enumerate(list(new_data.keys())):
                self.table.insert(parent='', index='end', text='', values=(key, new_data[key]))
        except: pass

    def obey_parent(self,instruction):
        self.update(instruction=instruction)

    def open_link(self,*args):
        selections = self.table.selection()  # get the selected items in the Treeview
        selections = tuple(selections)
        for selection in selections:
            url = self.table.item(selection, 'values')[1]
            webbrowser.open(str(url))


with open('sheet_links.json', 'r') as file:
    data = json.load(file)
print(json.dumps(data, sort_keys=True, indent=4))

# structure of [data]:
# [term=Prelims - Michaelmas]:              # first level: (name of term):(dict of courses in term)
#   [class=1]:                                  # second level: (course):(dict of sheets in course)
#       [sheet id=1]:                               # third level: (sheet number):(dict of files in the sheet)
#           [filename=a]: link                          # fourth level: (file name):(link to file)
#           [filename=b]: link
#       [sheet id=2]:
#           [...]: ...
#   [class=2]:
#      [...]
# [term=...]:
#    [...]

# instructions
inst1 = Label(root, text='Choose the worksheet, and open with double click,')
inst1.grid(row=0,column=0,columnspan=3)
inst2 = Label(root, text='or select multiple files and press ENTER to open all.')
inst2.grid(row=1,column=0,columnspan=3)

# dropdown menu for selecting the term
years = ['Prelims'] # 'Part A', 'Part B', 'Part C']
terms = ['Michaelmas', 'Hilary', 'Trinity']
term_options = [year + ' - ' + term for year in years for term in terms]
term_selector = nestedSelector(options=term_options, default=2, disabled=False, row=2, column=1)  # default is the Trinity
term_label = Label(root, text='Year')
term_label.grid(row=2,column=0)

course_updator = lambda term: list(data[term].keys())
course_selector = nestedSelector(default='Select Course', disabled=False, updator=course_updator, row=3, column=1)
term_selector.add_child(course_selector)
course_label = Label(root, text='Course')
course_label.grid(row=3, column=0)

# sheet_options = data[course_selector.value].keys()
sheet_updator = lambda course: ['Sheet ' + key for key in data[term_selector.value][course].keys()]
sheet_selector = nestedSelector(default='Select Sheet', disabled=True, row=4, column=1, updator=sheet_updator)
course_selector.add_child(sheet_selector)
sheet_label = Label(root, text='Sheet')
sheet_label.grid(row=4, column=0)


link_updator = lambda sheet: data[term_selector.value][course_selector.value][sheet.split(' ')[-1]]
print(data['Prelims - Michaelmas']['M3: Probability']['2'])
link_display = respondingDictionary(columns=('File','Link'),widths=[200,100], updator=link_updator,
                                    row=5, column=0, columnspan=2, sticky='we')
sheet_selector.add_child(link_display)

root.mainloop()