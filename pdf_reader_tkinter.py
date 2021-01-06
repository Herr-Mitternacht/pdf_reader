# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 23:44:29 2021

@author: jiangbiyi
"""
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import fitz
import os
from PIL import Image, ImageTk
import ctypes
import sqlite3

#this fix the blurring picture
ctypes.windll.shcore.SetProcessDpiAwareness(1)


#def create_database():
#	annot_database = sqlite3.connect("annote.db")
#	c = annot_database.cursor()
#	c.execute("""CREATE TABLE annot(
#			id interger,
#			marked_text text,
#			x0 real,
#			y0 real,
#			x1 real,
#			y1 real
#			)
#		   """)
#	annot_database.commit()
#	annot_database.close()	
#	return annot_database
#
##this is the database
#annot_database = create_database()

class ScrollableFrame(ttk.Frame):
	"""this is a frame that can be used as a normal frame"""
	def __init__(self, container, *args, **kwargs):
		super().__init__(container, *args, **kwargs)
		canvas = tk.Canvas(self, height=850, width=1000)
		scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
		scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
		
		self.scrollable_frame = ttk.Frame(canvas)

		self.scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

		canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.CENTER)

		canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

		canvas.grid(row=0, column=0, sticky="nsew")
		scrollbar_x.grid(row=1, column=0, sticky="ew")
		scrollbar_y.grid(row=0, column=1, sticky="ns")

class pdf_func:
	def __init__(self, root, database):
		self.current_image_raw = None
		self.current_image = None
		#we cannot save page, only the page number
		self.current_page_num = 0
		
		self.filename = None
		self.current_size = 1.0
		self.root = root
		#total number of page in pdf
		self.page_sum = 0
		
		self.pdf_frame = ScrollableFrame(self.root)
		self.pdf_frame.grid(column=0, row=1, columnspan=6, rowspan=5, sticky='nswe')
		self.pdf_label = tk.Label(self.pdf_frame.scrollable_frame)
						
		#resolution factor will control the resolution and size
		self.resolution = 120/72
		self.mat = fitz.Matrix(self.resolution, self.resolution)
		
		#zoom factor:
		self.zoom = 1.2

		self.button_open_file = tk.Button(root, text="open file", bg="steel blue1", command=self.open_file)
		self.button_open_file.grid(column=0, row=0)
		
		self.button_downsize = tk.Button(root, text="downsize", bg="steel blue1", command=self.downsize)
		self.button_downsize.grid(column=1, row=0)
		
		self.button_upsize = tk.Button(root, text="upsize", bg="steel blue1", command=self.upsize)
		self.button_upsize.grid(column=2, row=0 )
		
		self.button_nextpage = tk.Button(root, text="next page", bg="steel blue1", command=self.next_page)
		self.button_nextpage.grid(column=0, row=6)	
		
		self.button_previous = tk.Button(root, text="previous page", bg="steel blue1", command=self.previous_page)
		self.button_previous.grid(column=1, row=6)
		
		#for show current page number
		self.page_num_label = tk.Label(root, text=str(self.current_page_num))
		self.page_num_label.grid(column=2, row=6, sticky='e')
		#fors show total number
		self.page_sum_label = tk.Label(root, text="/"+ str(self.page_sum))
		self.page_sum_label.grid(column=3, row=6, sticky='w')
				
		self.entry_goto_page = tk.Entry(root, width=5)
		self.entry_goto_page.grid(column=4, row=6, sticky='e')
		self.buttom_goto = tk.Button(root, text="goto", bg="steel blue1", command=self.goto_page)
		self.buttom_goto.grid(column=5, row=6, sticky='w')
		
		
		#from now we have the for annotation things
		
		self.label_annot = tk.Label(root, text="Enter the numbering and text  ")
		self.label_annot.grid(column=6, row=0, columnspan=2)	
		
		self.entry_number = tk.Entry(root, width=5)
		self.entry_number.grid(column=6, row=1, sticky='w')		
		
		self.entry_text = tk.Entry(root, width=20)
		self.entry_text.grid(column=6, row=2, columnspan=2, sticky='w')
		
		self.button_search = tk.Button(root, text="search", bg="steel blue1", command=self.search_show_save_delete)
		self.button_search.grid(column=6, row=3)
		
		self.button_search_confirm = tk.Button(root, text="confirm", bg="steel blue1", command=self.confirm_marked_result)
		self.button_search_confirm.grid(column=7, row=3)
		
		#when no result after search
		self.pop_no_result = None		
		#exactly one result after search
		self.pop_one_result = None			
		#multiple results after search
		self.pop_mul_result = None
		self.var = tk.IntVar()
		
		self.database = database
		#store current text
		self.text = None
		#for store the correct location after searching
		self.correct_location = None
		#for store the current annotation
		self.annotation = None
		
		
		#for now it is the thing for search the annotation
		self.label_annot_search = tk.Label(root, text="Enter the numbering and text  ")
		self.label_annot_search.grid(column=6, row=4, columnspan=2)
		
		#entry for entering the numbering
		self.entry_number_search = tk.Entry(root, width=5)
		self.entry_number_search.grid(column=6, row=5, sticky='w')

		self.button_search_search = tk.Button(root, text="search", bg="steel blue1", command=self.search_show_save_delete)
		self.button_search_search.grid(column=6, row=6)		
		
	def open_file(self):
		self.filename = tkinter.filedialog.askopenfilename(initialdir= os.getcwd(), title= "Please select a file:", filetypes= (("pdf file", "*.pdf"),("all files", "*.*")))
		
		if self.filename:
			#open pdf file by name
			pdf_doc = fitz.open(self.filename)
			#get the total page number and update the label
			self.page_sum = pdf_doc.pageCount
			self.page_sum_label.configure(text = "/"+str(self.page_sum)) 
			#load first page from file
			page = pdf_doc.loadPage(0)
			self.current_page_num = 0
			#get the image data from page
			pix = page.getPixmap(matrix=self.mat)
			#get the image
			self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

			#this image must be a global!!!!
			self.current_image = ImageTk.PhotoImage(self.current_image_raw)
			
			self.pdf_label.config(image = self.current_image)
			self.pdf_label.grid(column=0, row=0)
			
			
			
	def downsize(self):		
		"""
		function for downsize button
		"""		
		pdf_doc = fitz.open(self.filename) 
		#load page from file
		page = pdf_doc.loadPage(self.current_page_num)
		
		#this controls the current resolution
		self.current_size = self.current_size/self.zoom
		
		martix = fitz.Matrix(self.resolution*self.current_size, self.resolution*self.current_size)
		
		pix = page.getPixmap(matrix=martix)
		#get the image
		self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

		self.current_image = ImageTk.PhotoImage(self.current_image_raw)
		
		self.pdf_label.config(image = self.current_image)
		self.pdf_label.grid(column=0, row=0)
	
	def upsize(self):						
		"""
		function for upsize button
		"""
		pdf_doc = fitz.open(self.filename) 
		#load first page from file
		page = pdf_doc.loadPage(self.current_page_num)
		
		self.current_size = self.current_size * self.zoom
		martix = fitz.Matrix(self.resolution*self.current_size, self.resolution*self.current_size)
		
		pix = page.getPixmap(matrix=martix)
		#get the image
		self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

		self.current_image = ImageTk.PhotoImage(self.current_image_raw)
		
		self.pdf_label.config(image = self.current_image)
		self.pdf_label.grid(column=0, row=0)

	def change_page_num(self):
		self.page_num_label.configure(text=str(self.current_page_num))
	
	def next_page(self):
		"""
		go to next page of the pdf
		"""
		self.current_page_num = self.current_page_num + 1
		self.change_page_num()
		
		pdf_doc = fitz.open(self.filename) 
		#load first page from file
		page = pdf_doc.loadPage(self.current_page_num)		
		martix = fitz.Matrix(self.resolution*self.current_size, self.resolution*self.current_size)		
		pix = page.getPixmap(matrix=martix)
		
		#get the image
		self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
		self.current_image = ImageTk.PhotoImage(self.current_image_raw)
		
		self.pdf_label.config(image = self.current_image)
		self.pdf_label.grid(column=0, row=0)
		
	def previous_page(self):
		"""
		go to previous page of the pdf
		"""
		self.current_page_num = self.current_page_num - 1
		self.change_page_num()
		
		pdf_doc = fitz.open(self.filename) 
		#load first page from file
		page = pdf_doc.loadPage(self.current_page_num)		
		martix = fitz.Matrix(self.resolution*self.current_size, self.resolution*self.current_size)		
		pix = page.getPixmap(matrix=martix)
		#get the image
		self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
		self.current_image = ImageTk.PhotoImage(self.current_image_raw)
		
		self.pdf_label.config(image = self.current_image)
		self.pdf_label.grid(column=0, row=0)

	def goto_page(self):
		self.current_page_num = int(self.entry_goto_page.get())
		self.entry_goto_page.delete(0, tk.END)
		self.change_page_num()
		
		pdf_doc = fitz.open(self.filename) 
		#load first page from file
		page = pdf_doc.loadPage(self.current_page_num)		
		martix = fitz.Matrix(self.resolution*self.current_size, self.resolution*self.current_size)		
		pix = page.getPixmap(matrix=martix)
		#get the image
		self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
		self.current_image = ImageTk.PhotoImage(self.current_image_raw)
		
		self.pdf_label.config(image = self.current_image)
		#self.pdf_label.grid(column=0, row=0)
		
	def search_and_locate(self):
		"""
		search for the place that you want to annotate
		"""
		self.text = str(self.entry_text.get())
		doc = fitz.open(self.filename)
		#only can search for the content on the current page
		page = doc[self.current_page_num]
		location = page.searchFor(self.text)
		if len(location) == 0:
			self.pop_no_result = tk.Toplevel(self.root)
			label_pop_no_result = tk.Label(self.pop_no_result, text="no searched result")
			label_pop_no_result.pack()
			button_no_close = tk.Button(self.pop_no_result, text="Close", command=self.pop_no_result.destroy)
			button_no_close.pack(fill='x')
			self.correct_location = 0
		
		elif len(location) == 1:
			location = location[0]
			self.correct_location = location
			searched_text = page.getText("text", clip=location, flags=1)
			print(searched_text)
			self.pop_one_result = tk.Toplevel(self.root)
			label_pop_one_result = tk.Label(self.pop_one_result, text="searched_result:  "+searched_text)
			label_pop_one_result.grid(column=1, row=0, sticky='s')
			button_one_close = tk.Button(self.pop_one_result, text="Close", command=self.pop_one_result.destroy)
			button_one_close.grid(column=0, row=1, columnspan=2)
		
		#when finding multiple results
		elif len(location) > 1:
			self.pop_mul_result = tk.Toplevel(self.root)
			i = 0
			labels = []
			for loc in location:
				searched_content = page.getText("text", clip=loc, flags=1)								
				print("this is the searched result {}:".format(i), searched_content)
				label = tk.Label(self.pop_mul_result, text="this is the searched result {}:".format(i)+searched_content)
				label.grid(column=0, row=i)
				labels.append(label)
				i = i + 1
				
			label_correct_num = tk.Label(self.pop_mul_result, text="type the correct numbering")
			label_correct_num.grid(column=0, row=i)
			
			entry_correct_num = tk.Entry(self.pop_mul_result, width=5)
			entry_correct_num.grid(column=1, row=i)
			
			
			#correct_result = page.getText("text", clip=location, flags=1)			
			def	display_correct(i=i, location = location):
				correct_num = int(entry_correct_num.get())
				self.correct_location = location[correct_num]
				label_correct_result = tk.Label(self.pop_mul_result, text="this is the number you choose:  "+str(correct_num))
				label_correct_result.grid(column=0, row=i+1)
				self.var.set(1)
				
			button_correct_num = tk.Button(self.pop_mul_result, text="confirm", command=display_correct)
			button_correct_num.grid(column=2, row=i)
			button_correct_num.wait_variable(self.var)
		print(self.correct_location)	
		
		
	def add_annotate(self):
		doc = fitz.open(self.filename)
		#only can search for the content on the current page
		page = doc[self.current_page_num]
		self.annotation = page.addHighlightAnnot(self.correct_location)
		doc.save(self.filename, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
		
		pdf_doc = fitz.open(self.filename) 
		#load first page from file
		page = pdf_doc.loadPage(self.current_page_num)		
		martix = fitz.Matrix(self.resolution*self.current_size, self.resolution*self.current_size)		
		pix = page.getPixmap(matrix=martix)
		
		#get the image
		self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
		self.current_image = ImageTk.PhotoImage(self.current_image_raw)
		
		self.pdf_label.config(image = self.current_image)
		self.pdf_label.grid(column=0, row=0)
		print("added")
	
	def save_annotate(self):		
		numbering = self.entry_number.get()		
		
		annot_database = sqlite3.connect(str(self.database))
		c = annot_database.cursor()
		c.execute("INSERT INTO annot VALUES (:id, :marked_text, :x0, :y0, :x1, :y1)", {
				'id':numbering,
				'marked_text': self.text,
				'x0': self.correct_location.x0,
				'y0': self.correct_location.y0,
				'x1': self.correct_location.x1,
				'y1':self.correct_location.y1
				}
			   )
		print("saved")
		annot_database.commit()
		annot_database.close()
	
	def delete_annotate(self):
		doc = fitz.open(self.filename)
		#only can search for the content on the current page
		page = doc[self.current_page_num]
		#strangely the self.annotation cannot cross functions(same as self.page)
		#make sure there will only be one annotation one time
		self.annotation = page.firstAnnot
		if self.annotation:
			page.deleteAnnot(self.annotation)
			print("deleted")
		print("not deleted")
		doc.save(self.filename, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
		
		pdf_doc = fitz.open(self.filename) 
		page = pdf_doc.loadPage(self.current_page_num)		
		martix = fitz.Matrix(self.resolution*self.current_size, self.resolution*self.current_size)		
		pix = page.getPixmap(matrix=martix)
		
		#get the image
		self.current_image_raw = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
		self.current_image = ImageTk.PhotoImage(self.current_image_raw)
		
		self.pdf_label.config(image = self.current_image)
		self.pdf_label.grid(column=0, row=0)
		
	def search_show_save_delete(self):
		self.search_and_locate()
		self.annotation = self.add_annotate()
		
	def confirm_marked_result(self):
		print("confirm works?")
		#self.save_annotate()
		self.delete_annotate()
		
		
if __name__ == '__main__':
	root = tk.Tk()
	funcs = pdf_func(root, database = "annote.db")
	#create the open file button
	
	
	root.mainloop()
	
		