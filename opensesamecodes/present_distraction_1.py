# Place inside run file
# Textbox coordinates
n1 = -125,300
n2 = 125,300
n3 = 125,250
n4 = -125,250

a1 = 200,-200
a2 = -200,-200
a3 = -200,-150
a4 = 200,-150
	
prompt = 'Count the number of blue dots'
nr_of_dots = random.randint(20,40)
nr_distract = random.randint(10,30)
dot = u'\u2022'

# Show prompt
my_canvas = Canvas()
my_canvas.text(prompt, font_size = 30, y = -250)
for i in range(nr_of_dots):
	f_size = random.randint(20,50)
	y_random = random.randint(-200,200)
	x_random = random.randint(-400,400)
	my_canvas.text(dot, font_size = f_size, y = y_random, x = x_random, color='blue')
		
for i in range(nr_distract):
	f_size = random.randint(20,50)
	y_random = random.randint(-200,200)
	x_random = random.randint(-400,400)
	my_canvas.text(dot, font_size = f_size, y = y_random, x = x_random, color='red')
		
my_canvas.polygon([n1, n2, n3, n4], fill=True, color="white")
my_canvas.text("Type here...", font_size=30, y=275, color="gray")

my_canvas.prepare()
my_canvas.show()

# Listen for keyboard input and show keypresses on screen as they occur
my_keyboard = Keyboard()
keyboard_response = ""
erased_answer = False
rt = float("inf")

# Keep listening for key presses until the user presses Enter
while True:
	key, time = my_keyboard.get_key()
	
	
	if key == "return":
		break
		
	if key == "backspace":
		keyboard_response = keyboard_response[:-1]
		# If the answer is completely erased, the RT is no longer informative
		if keyboard_response == "":
			erased_answer = True
			rt = float("inf")
	
	elif key == "space":
		keyboard_response += " "
	
	else:
		keyboard_response += my_keyboard.to_chr(key)

	# Update what's on screen'
	my_canvas.clear()
	my_canvas.text(prompt, font_size = 30, y=-250)

	my_canvas.polygon([n1, n2, n3, n4], fill=True, color="white")
	my_canvas.text(keyboard_response, y = 275)

	my_canvas.prepare()
	my_canvas.show()
	print(m.responses)
	
# Clear the screen between trials
my_canvas.clear()
my_canvas.prepare()
my_canvas.show()
