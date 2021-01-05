# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 23:44:29 2021

@author: jiangbiyi
"""
import tkinter as tk
import tkinter.filedialog
import fitz
import os
from PIL import Image, ImageTk
from tkscrolledframe import ScrolledFrame
root = tk.Tk()

class pdf_func:
	def __init__(self, root):
		self.current_image_raw = None
		self.current_image = None
		self.current_page = None
		self.current_page_num = 0
		self.root = root
		
		# Create a ScrolledFrame widget
		sf = ScrolledFrame(self.root, width=640, height=480)
		sf.grid(column=0, row=1, columnspan=3)		
		# Bind the arrow keys and scroll wheel
		sf.bind_arrow_keys(self.root)
		sf.bind_scroll_wheel(self.root)
		# Create a frame within the ScrolledFrame
		self.inner_frame = sf.display_widget(tk.Frame)
								
		# zoom factor will control the resolution, not size!!!
		self.zoom = 5    
		self.mat = fitz.Matrix(self.zoom, self.zoom)
		
		self.button_open_file = tk.Button(root, text="open file", bg="steel blue1", command=self.open_file)
		self.button_open_file.grid(column=0, row=0)
				
		
	def show_pdf(self, image):
		pdf_label = tk.Label(self.inner_frame, image=image)
		pdf_label.pack()
		
		
	def open_file(self):
		filename = tkinter.filedialog.askopenfilename(initialdir= os.getcwd(), title= "Please select a file:", filetypes= (("pdf file", "*.pdf"),("all files", "*.*")))
		if filename:
			#open pdf file by name
			pdf_doc = fitz.open(filename) 
			#load first page from file
			page = pdf_doc.loadPage(0)
			self.current_page = page
			self.current_page_num = 0
			#get the image data from page
			pix = page.getPixmap(matrix = self.mat)
			
			#get the image
			mode = "RGBA" if pix.alpha else "RGB"
			self.current_image_raw = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

			#this image must be a global!!!!
			self.current_image = ImageTk.PhotoImage(self.current_image_raw)
			
			self.show_pdf(self.current_image)
	
	
	
if __name__ == '__main__':
	funcs = pdf_func(root)
	#create the open file button
	
	
	root.mainloop()
	
		