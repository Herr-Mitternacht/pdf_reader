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

#this fix the blurring picture
ctypes.windll.shcore.SetProcessDpiAwareness(1)

class ScrollableFrame(ttk.Frame):
	"""this is a frame that can be used as a normal frame"""
	def __init__(self, container, *args, **kwargs):
		super().__init__(container, *args, **kwargs)
		canvas = tk.Canvas(self, height=900, width=1000)
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
	def __init__(self, root):
		self.current_image_raw = None
		self.current_image = None
		#we cannot save page, only the page number
		self.current_page_num = 0
		self.filename = None
		self.current_size = 1.0
		self.root = root
		
		
		self.pdf_frame = ScrollableFrame(self.root)
		self.pdf_frame.grid(column=0, row=1, columnspan=3, sticky='nswe')
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
		self.button_upsize.grid(column=2, row=0)
				
				
	def open_file(self):
		self.filename = tkinter.filedialog.askopenfilename(initialdir= os.getcwd(), title= "Please select a file:", filetypes= (("pdf file", "*.pdf"),("all files", "*.*")))
		
		if self.filename:
			#open pdf file by name
			pdf_doc = fitz.open(self.filename) 
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


	
if __name__ == '__main__':
	root = tk.Tk()
	funcs = pdf_func(root)
	#create the open file button
	
	
	root.mainloop()
	
		