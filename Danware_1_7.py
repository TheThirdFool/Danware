#!/usr/bin/env python

#Ha ha get it - Danware - like radware.. Get it?

from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import os
import struct

from ROOT import TFile
from ROOT import TH1
from ROOT import TH1D
from ROOT import gROOT
from ROOT import TSpectrum

def List_Files(option):
	basepath = os.getcwd()
	#basepath = os.path.dirname(cwd)#os.path.realpath(__file__))
	print "Directory: ", basepath
	print "Files: "
	print ""
	for entry in os.listdir(basepath):
		if os.path.isfile(os.path.join(basepath, entry)):
			if '.root' in entry:
				print entry
			if "c" in option and ".CNF" in entry:
				print entry
	print ""

def Read_File():
	print "" 
	print "What is the file name?"
	while True:	
		filename = raw_input("Filename =  ")
		print ""

		if filename == "q":	#q quits the file name bit
			print "Quitting"
			print ""
			return "q"

		if filename == "l":
			List_Files("r")	#l lists the files 
			continue

		if filename == "e":
			Extract_Data()
			return "c"

		if filename == "o":		
			Overlay()
			return "c"

		if filename == "h":
			print "Error Reading File"
			print ""
			print "File list : l"
			print "Overlay   : o"
			print "Extract   : e"
			print "Quit      : q"
			print ""
			continue

		try:
			File = TFile(filename) #apparently this should open the file
			print "File read!"
			print ""
			break
		except:
			print "Error Reading File"
			print ""
			print "File list : l"
			print "Quit      : q"
			print ""
	
	return File    

def ReadCNF(filename, x_array, y_array):
	data = []
	with open(filename, mode='rb') as b_file: # b is important -> binary
		byte_s = b_file.read(4)
		while byte_s != "":
			try:
				buffer_b = struct.unpack('i',byte_s)[0]
				data.append(buffer_b)
				#data.append(str(byte_s))      #.decode("utf-8")) #couldnt decode besause only 3 bytes left! lost bytes!
			except ValueError:
				print "ERROR READING FILE!"
				print "bytes:"
				print byte_s
				print "^ Broken Bytes ^"
				print ""
				
			byte_s = b_file.read(4)
	
	offset = len(data) - 4096

	i = offset + 1
	while i < len(data):
		x_array.append(i - offset)
		y_array.append(data[i])
		i += 1

	print "Read file ", filename, "!"

def Get_Data(hist, index_out, count_out):
	
	hist_o = gROOT.FindObject(hist)

	x_max = hist_o.GetNbinsX()
	#print x_max
	#val = hist_o.GetBinContent(x_max)
	i = 0
	while i < x_max: #Iterates over all the bins getting their content
		count_out.append(hist_o.GetBinContent(i))
		index_out.append(i)
		i += 1
	#return val

def Get_Data_2D(hist, index_x, index_y, count_y):  #, val_x, val_y):
	
	hist_o = gROOT.FindObject(hist)

	x_max = hist_o.GetNbinsX()
	y_max = hist_o.GetNbinsY()
	#val_x = hist_o.GetBinContent(x_max)
	#val_y = hist_o.GetBinContent(y_max)
	i = 0
	while i < x_max: #Iterates over all the bins getting their content
		j = 0
		while j < y_max: #Iterates over all the bins getting their content
			z = hist_o.GetBinContent(i,j)
			index_x.append(i)	
			#print z
			count_y.append(z)
			#print index_x[i], index_y[j], hist_o.GetBinContent(i,j) 
			index_y.append(j)
			#print index_x[i], index_y[j], hist_o.GetBinContent(i,j) 
			j += 1
		i += 1

def Clean_Hist(x, y, x_o, y_o):
	i = 0
	while i < len(x):
		if i > 0 and x[i] == x[0]: #This could be a problem if x axis goes down
			break
		j = i + 1
		sum_y = y[i]
		while j < len(x):
			if x[j] == x[i]:
				sum_y += y[j]
			j += 1
		x_o.append(x[i])
		y_o.append(sum_y)
		i += 1 

def Find_Cal_Consts():
	print ""
	t1 = float(raw_input("True value 1 = "))
	x1 = float(raw_input("Observed value 1 = "))
	print ""
	t2 = float(raw_input("True value 2 = "))
	x2 = float(raw_input("Observed value 2 = "))
	a = (t2 - t1) / (x2 - x1)
	b = t2 - a * x2
	print ""
	print "a = ", a
	print "b = ", b 
	return (a, b)

def Calibrate(in_x, out_x):
	print ""
	print "For Ax + B : ('?' for calculator)"
	a = raw_input('Scaling factor = ')
	if a == "?": 
		(a, b) = Find_Cal_Consts()
	else:
		b = float(raw_input('Constant = '))
	print ""
	for point in in_x:
		new_p = float(a) * point + b 
		out_x.append(new_p)
	print "Calibration complete"
	print ""

def Draw_Hist(x, y):
	plt.plot(x, y)
	plt.show()

def Draw_2D(x, y, z):
	#Scan across x and y and plot z
	#Project
	print ""
	print "Projections"
	print "-----------"
	print ""
	low = float(raw_input('low = '))
	print ""
	high = float(raw_input('high = '))
	print ""
	out_x = []
	out_count = []
	i = 0 
	while i < len(x) and i < len(y) and i < len(z):
		#print x[i], y[i], z[i]
		if low <= x[i] <= high:
			#print y[i], z[i]
			out_x.append(y[i])
			out_count.append(z[i])
		i += 1
	x_new = []
	y_new = []
	Clean_Hist(out_x, out_count, x_new, y_new)
	Draw_Hist(x_new, y_new)

def Hist_create(hist_name):
	x_index = []
	x_count = []
	x_index_out = []

	hist_o = gROOT.FindObject(hist_name)

	if "TH1" in hist_o.ClassName():
		print ""
		b_s_ans = raw_input("Background subtract? [y/ n] ")
		print ""
		if b_s_ans == "y":
			Background_Sub(hist_name)
			return
		cal_ans = raw_input("Calibrate? [y / n] ")
		Get_Data(hist_name, x_index, x_count)
		if cal_ans == "y":
			Calibrate(x_index, x_index_out)
			print ""
			print "Drawing graph..."
			plt.plot(x_index_out, x_count, "m")
			plt.show()
		else:
			print "Drawing graph..."
			print ""
			#val = Get_Data(hist_name, x_index, x_count)
			Draw_Hist(x_index, x_count)
 	
	if "TH2" in hist_o.ClassName():
		#print "YES"
		#val_x = 0
		#val_y = 0
		y_index = []
		z_count = []
		Get_Data_2D(hist_name, x_index, y_index, z_count) #, val_x, val_y)
		Draw_2D(x_index, y_index, z_count)
		#Project

def Overlay_array(n):
	print ""
	print "Overlaying ", n, " histograms..."
	print ""
	cal_ans = raw_input("Calibrate? [y / n] ")
	c_list = ['b','r','g','c','m','k']
	for i in range(0,(n)):
		print ""
		print "Number ", i

		while True:
			print ""
			filename = raw_input('Filename = ')

			if filename == "l":
				List_Files("r")	#l lists the files 
				continue

			try:
				File = TFile(filename)
				print ""
				print "File read!"
				print ""
				break
			except:
				print ""
				print "Oh no!"

		print "File Content: "
		print ""

		File.ls()

		print ""
		print "Which histogram do you want to look at? (1D only) "
		hist_name = raw_input("Hist name = ")
		print ""

		x_index = []
		x_index_in = []
		x_count = []
	
		hist_o = gROOT.FindObject(hist_name)
	
		if "TH1" in hist_o.ClassName():
			print "Drawing graph..."
			print ""
			#val = Get_Data(hist_name, x_index, x_count)
			Get_Data(hist_name, x_index_in, x_count)
			if cal_ans == "y":
				Calibrate(x_index_in, x_index)
				plt.plot(x_index, x_count, c_list[i])	
			else: 
				plt.plot(x_index_in, x_count, c_list[i % 6])

		#if "TH2" in hist_o.ClassName():
		else:
			print "BROKEN!!!"
			print ""

	plt.show()

def Overlay():

		print ""
		print "Overlay Mode"
		print "------------"
		print ""
		print "How many overlays?"
		n = int(raw_input('N = '))
		print ""

		Overlay_array(n)

def B_Sub_Work(hist_name, it, b_num, count):

	hist_o = gROOT.FindObject(hist_name)
	s = TSpectrum()
	B_hist = s.Background(hist_o, it, "same")

	b_x = []
	b_count = []
	nb_x = []
	nb_count = []

	b_x_max = B_hist.GetNbinsX()
	i = 0
	while i < b_x_max: #Iterates over all the bins getting their content
		b_count.append(B_hist.GetBinContent(i))
		b_x.append(i)
		i += 1
	
	nb_x_max = hist_o.GetNbinsX()
	j = 0
	while j < nb_x_max: #Iterates over all the bins getting their content
		nb_count.append(hist_o.GetBinContent(j))
		nb_x.append(j)
		j += 1

	k = 0 
	while k < len(b_x):
		count.append(nb_count[k] - b_count[k])
		b_num.append(k) 
		k += 1

def Background_Sub(hist_name):
	#c_list = ['b','r','g','c','m','k']
	#print ""
	#print "Which histogram do you want to look at? (1D only) "
	#hist_name = raw_input("Hist name = ")
	print ""
	iterations = raw_input("How many iterations do you want? ")
	if iterations == "": iterations = 20
	else: iterations = int(iterations)
	print ""
	cal_ans = raw_input("Calibrate? [y / n] ")
	print ""
	x_index = []
	x_index_in = []
	x_count = []
	
	hist_o = gROOT.FindObject(hist_name)
	
	if "TH1" in hist_o.ClassName():
		print "Drawing graph..."
		print ""
		#val = Get_Data(hist_name, x_index, x_count)
		#Get_Data(hist_name, x_index_in, x_count)
		B_Sub_Work(hist_name, iterations, x_index_in, x_count)

		if cal_ans == "y":
			Calibrate(x_index_in, x_index)
			plt.plot(x_index, x_count)#, c_list[i % 6])	
		else: 
			plt.plot(x_index_in, x_count)#, c_list[i % 6])
		#if "TH2" in hist_o.ClassName():
	else:
		print "BROKEN!!!"
		print ""

	plt.show()


def Extract_Data():
	CNF_bool = False
	while True:
		print ""
		print "Which file do you want to extract from?"
		filename = raw_input("Filename = ")

		if filename == "l":
			List_Files("c")	#l lists the files 
			continue
		if ".CNF" in filename:
			CNF_bool = True
			break		
		else:
			try:
				File_1 = TFile(filename)
				break
			except:
				print "Not a real file!"
				continue
	if CNF_bool:
		hist_name = "CNF"
		print ""
		print "Reading '.CNF' file..."
		print ""

	else:
		while True:
			File_1.ls()
			print ""
			print "Which histogram do you want to look at? (1D only) "
			hist_name = raw_input("Hist name = ")	
			print ""
			hist_o = gROOT.FindObject(hist_name)
 			if hist_name == "q": break	
			if "TDirectoryFile" in hist_o.ClassName():
				hist_o.cd()
				continue
			else:
				break

	print "What filename do you want to output to? (blank = automatic)"
	out_file = raw_input('Filename = ')

	while True:
		print ""
		print "What file type?"
		print " .txt : t"
		print " .dat : d"
		print " .csv : c"
		print ".root : r"
		print ""
		file_type = raw_input("File type = ")
		print ""
		
		if file_type == "t":
			file_type = ".txt"
			break
		elif file_type == "d":
			file_type = ".dat"
			break
		elif file_type == "c":
			file_type = ".csv"
			break
		elif file_type == "r":
			file_type = ".root"
			break
		else: 
			print "Enter a value!"
			continue


	if out_file == "":
		if CNF_bool:
			n_fn = filename[:-4] + "_"
		else:
			n_fn = filename.replace(".root","_")
		out_file = "Extracted_" + n_fn + hist_name

	endfile = out_file + file_type

	if file_type == ".root":
		output_file = TFile(endfile, "recreate")
		output_file.cd()
		if CNF_bool:
			#makehist
			hist_o = TH1D(out_file,out_file,4096,0,4096);
			x_index = []
			x_count = []
			ReadCNF(filename, x_index, x_count)
			i = 0
			while i < len(x_index):
				hist_o.SetBinContent(x_index[i],x_count[i])
				i += 1

		hist_o.Write()
		output_file.Close()
		print ""
		print "Extracted ", hist_name, " from ", filename, " into ", endfile, "."
		print ""
		return

	file_print = open(endfile, "w")

	if CNF_bool:
		x_index = []
		x_count = []
		ReadCNF(filename, x_index, x_count)
		i = 0
		while i < len(x_index):
			print >> file_print, x_index[i], ",", x_count[i]
			i += 1

	else:
		if "TH1" in hist_o.ClassName():
			print ""
			x_index = []
			x_count = []
			Get_Data(hist_name, x_index, x_count)
			i = 0
			while i < len(x_index):
	 			print >> file_print, x_index[i], ",", x_count[i]
				i += 1
			file_print.close()
	
		if "TH2" in hist_o.ClassName():
			x_index = []
			y_index = []
			z_count = []
			Get_Data_2D(hist_name, x_index, y_index, z_count) #, val_x, val_y)
			i = 0
			while i < len(x_index):
	 			print >> file_print, x_index[i], ",", y_index[i], ",", z_count[i]
				i += 1		
	file_print.close()

	print ""
	print "Extracted ", hist_name, " from ", filename, " into ", endfile, "."
	print ""

def main():
	Quit = False
	print ""
	print "DanWare - V.1.7"
	print "---------------"
	print ""
	print "Ha ha get it - DanWare - like radware.. Get it?"
	print ""
	print "The point of this is to see if I can make a grutinizer-esque program"
	print "in python. I will attempt to use PyROOT to do this."
	print ""
	print "--------------------------------------"
	print ""
	print "Enter 'h' for help."

	while True:

		File_1 = Read_File()
		
		if File_1 == "q": break
		if File_1 == "c": continue

		while True:
			print "File Content: "
			print ""
	
			File_1.ls()
	
			print ""
			print "Which histogram do you want to look at? (1D only) "
			hist_name = raw_input("Hist name = ")
			print ""
			if hist_name == "q": break	
			hist_o = gROOT.FindObject(hist_name)
			if "TDirectoryFile" in hist_o.ClassName():
				hist_o.cd()
				continue
			Hist_create(hist_name)
 			break

		if hist_name == "q": continue			
		print "" 
		print "Quit?"
		q_answer = raw_input("[y / n] = ")
		if q_answer == "y": break	

	print ""
	print "Exiting..."
	print ""

main()











