#!/usr/local/bin/python3.2
#
# In this program the user moves the mouse in the control plane
# and the corresponding graph of the potential function changes accordingly. 
# As the mouse crosses the cusp curvethe shape of the graph changes from 
# two local minima to one (or vice versa). }
#
# I used ActivePython and ActiveTcl dowboaded (free) from ActiveState at
# http://www.activestate.com/activetcl?gclid=CPPy3p3DvbUCFY9AMgodgWQAkA
# Modern Tkinter for busy developers 13.6 and
# http://www.tkdocs.com/tutorial/canvas.html
# are good references.

from tkinter import * 
from tkinter import ttk 
import math

root = Tk() 
root.title("The Cusp Catastrophe")

content=ttk.Frame(root,padding=(10,10,10,10))

CW=400; CH=600 # canvas width, height

#widgets
control=Canvas(content, borderwidth=5, relief="sunken", width=CW, height=CH)
graph=Canvas(content, borderwidth=5, relief="sunken", width=CW, height=CH)

a_label=ttk.Label(content,text="a=")
a_value=StringVar();
a_entry=ttk.Entry(content,textvariable=a_value)
b_label=ttk.Label(content,text="b=")
b_value=StringVar();
b_entry=ttk.Entry(content,textvariable=b_value)

#place the widgets
content.grid(column=0,row=0,sticky=(N,S,E,W))
graph.grid(column=0,row=0,columnspan=6,sticky=(N,S,E,W))
a_label.grid(column=1,row=1)
a_entry.grid(column=2,row=1)
b_label.grid(column=3,row=1)
b_entry.grid(column=4,row=1)

# coordinates
u_min=-1.5;  u_max=1.5    
v_min=-1.0;  v_max=1.5 
def u2x(u): return int(CW*(u-u_min)/(u_max-u_min))
def v2y(v): return CH-int(CH*(v-v_min)/(v_max-v_min))


a_min=-1.3;  a_max=1.3
b_min=-1.3;  b_max=0.3
def x2a(x): return "%0.2f" %(a_min+(a_max-a_min)*x/(1.0*CW))
def y2b(y): return "%0.2f" %(b_min-(b_min-b_max)*(CH-y)/(1.0*CH))
def a2x(a): return int(CW*(a-a_min)/(a_max-a_min))
def b2y(b): return CH-int(CH*(b-b_min)/(b_max-b_min))

def V(u,a,b): 
	#return (u+2)*(u-a)*(u-b)*(u-2)
	return u**4/4+b*u**2/2+a*u

def draw_cusp():
	db=(0-b_min)/100
	b=b_min; a=math.sqrt(4*abs(b)**3/27)
	for i in range(100):
		b1=b+db; a1=math.sqrt(4*abs(b1)**3/27)
		control.create_line(a2x(a),b2y(b),a2x(a1),b2y(b1))
		a=a1; b=b1
	db=(0-b_min)/100
	b=b_min; a=-math.sqrt(4*abs(b)**3/27)
	for i in range(100):
		b1=b+db; a1=-math.sqrt(4*abs(b1)**3/27)
		control.create_line(a2x(a),b2y(b),a2x(a1),b2y(b1))
		a=a1; b=b1

def draw(a,b):
	du=(u_max-u_min)/(100*1.0)
	u=u_min; v=V(u_min,a,b)
	for i in range(100):
		graph.create_line(u2x(u),v2y(v),u2x(u+du),v2y(V(u+du,a,b)))
		u=u+du; v=V(u,a,b)
		
def update():
	a=float(a_value.get())
	b=float(b_value.get())
	print("update",a,b)
	graph.delete(ALL) #http://effbot.org/tkinterbook/canvas.htm
	draw(a,b) 	

ovalx=CW/2; ovaly=CH/2
lastx=CW/2; lasty=CH/2
good_click=False

def xy(event):
	global lastx, lasty, good_click 
	good_click=abs(event.x-lastx)+abs(event.y-lasty)<5
	if not good_click: return
	lastx, lasty = control.canvasx(event.x), control.canvasy(event.y)
	
def addLine(event):  
	global lastx, lasty, good_click
	if not good_click:return
	control.create_line((lastx, lasty, event.x, event.y),
		fill="green", width=1, tags='currentline')
	lastx, lasty = event.x, event.y 
	a_value.set(x2a(lastx))
	b_value.set(y2b(lasty))
	control.delete('currentoval')
	control.create_oval((lastx-5, lasty-5, lastx+5, lasty+5),
		fill="red", width=1, tags='currentoval') 
	update()


def doneStroke(event): 
	global good_click,ovalx,ovaly,lastx,lasty
	if not good_click: return
	control.delete('currentoval')
	print("doneStroke",lastx,lasty)
	#control.create_line((ovalx, ovaly, lastx, lasty),
	#	fill="green", width=5, tags='currentline')
	ovalx,ovaly=lastx,lasty
	control.create_oval((ovalx-5, ovaly-5, ovalx+5, ovaly+5),
		fill="red", width=1, tags='currentoval') 
	a_value.set(x2a(ovalx))
	b_value.set(y2b(ovaly))
	update()

	
control.bind("<Button-1>", xy) 
control.bind("<B1-Motion>", addLine) 
#control.bind("<B1-ButtonRelease>", doneStroke)

content.grid(column=0, row=0, sticky=(N, S, E, W)) 
control.grid(column=0, row=0, columnspan=3, rowspan=2,
	sticky=(N, W),padx=10,pady=10)
graph.grid(column=3, row=0, columnspan=3, rowspan=2,
	sticky=(N,E),padx=10,pady=10)

root.columnconfigure(0,weight=1)
root.rowconfigure(0,weight=1)
content.columnconfigure(0,weight=3)
content.rowconfigure(0,weight=3)
content.columnconfigure(3,weight=3)
content.rowconfigure(3,weight=3)

control.create_line((ovalx, ovaly, ovalx, ovaly),
		fill="red", width=1, tags='currentline')
control.create_oval((ovalx-5, ovaly-5, ovalx+5, ovaly+5),
		fill="red", width=1, tags='currentoval')
draw_cusp()

button=ttk.Button(content,text="Draw",command=update)	
button.grid(column=5,row=1)

a_value.set(x2a(ovalx))
b_value.set(y2b(ovaly))
update()
root.mainloop()