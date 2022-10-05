trial_start_time = clock.time()

# Get next fact from the model
next_fact, new = m.get_next_fact(current_time = trial_start_time)
#prompt = next_fact.question
prompt = next_fact.chosen_context
answer = next_fact.answer.split(";") #delimiter ;

# Show prompt
my_canvas = Canvas()
my_canvas.text(prompt, font_size = 30)
#if new:
#	my_canvas.text(answer, y = 50, font_size = 20)
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
	
	# The first keypress determines the response time
	if keyboard_response == "" and not erased_answer:
		rt = clock.time() - trial_start_time
	
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
	my_canvas.text(prompt, font_size = 30)
	if new:
		my_canvas.text(answer, y = 50, font_size = 20)
	my_canvas.text(keyboard_response, y = 100)
	my_canvas.prepare()
	my_canvas.show()


# Check if the response is correct
# correct = keyboard_response == answer
if [keyboard_response == x for x in answer].count(True) >0:
    correct = True
else:
    correct = False
# Log response
response = Response(next_fact, trial_start_time, rt, correct)
m.register_response(response) 

# Show feedback
feedback_color = "green" if correct else "red"
my_canvas.text(keyboard_response, y = 100, color = feedback_color)
if not correct:
	my_canvas.text(answer, y = 150)
my_canvas.prepare()
my_canvas.show()
clock.sleep(var.feedback_duration)

# Clear the screen between trials
my_canvas.clear()
my_canvas.prepare()
my_canvas.show()
clock.sleep(var.inter_trial_interval)

# Check if time is up
if clock.time() - var.session_start_time >= var.session_duration:
	var.time_up = True
	
# Increment trial number
var.trial_num += 1
