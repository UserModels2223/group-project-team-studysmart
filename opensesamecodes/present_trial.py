trial_start_time = clock.time()

# Textbox coordinates
n1 = -125,125
n2 = 125,125
n3 = 125,75
n4 = -125,75

a1 = 200,-200
a2 = -200,-200
a3 = -200,-150
a4 = 200,-150
num_words_tested = 0
num_tested_correct = 0

def is_a_test(x): #check if its a word not a sentence
	return len(x.split(" ")) ==1
	
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
my_canvas.polygon([n1, n2, n3, n4], fill=True, color="white")
my_canvas.text("Type here...", font_size=30, y=100, color="gray")

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
#	if new:
#		my_canvas.text(answer, y = 50, font_size = 20)
	my_canvas.polygon([n1, n2, n3, n4], fill=True, color="white")
	my_canvas.text(keyboard_response, y = 100)

	#my_canvas['achi'] = polygon([a1, a2, a3, a4], fill=True, color="white")
	my_canvas.prepare()
	my_canvas.show()
	print(m.responses)
	


# Check if the response is correct
if [keyboard_response == x for x in answer].count(True) >0:
	correct = True
else:
	correct = False

# Log response
response = Response(next_fact, trial_start_time, rt, correct)
m.register_response(response) 

# Show feedback
feedback_color = "green" if correct else "red"
my_canvas.polygon([n1, n2, n3, n4], fill=True, color=feedback_color)
my_canvas.text(keyboard_response, y = 100, color="white")
if is_a_test(prompt) == True:
	my_canvas.polygon([a1, a2, a3, a4], fill=True, color="white")
	num_words_tested += 1

def create_statistics(responses):
	dat_resp = pd.DataFrame(responses)
	dat_facts = pd.DataFrame([r.fact for r in responses])
	dat = pd.concat([dat_resp, dat_facts], axis = 1)

	# Add column for rate of forgetting estimate after each observation
	#dat["alpha"] = dat.apply(self.calc_rof, axis = 1)
	#dat["reading_time"] = dat.apply(self.calc_reading_time, axis =1)
	#dat["fogetting_rate"] = dat.apply(self.calc_rof, axis = 1)
	# dat["chosen_context"] = dat.apply(chosen_context_finder, axis =1)
	dat.drop(columns = "fact", inplace = True)

	# Add trial number column
	dat.index.name = "trial"
	dat.index = dat.index + 1

	return dat

def achievement(responses,num_words_tested,num_tested_correct):
	"""
	All stats for user achievements
	"""
	dat = create_statistics(responses)
	correct, wrong = 0,0
	try:
		correct, wrong = dat["correct"].value_counts().values
	except:
		correct = dat["correct"].value_counts()
	mean_correct = correct/(correct+wrong)
	mean_wrong = wrong/(correct+wrong)
	
	correct = num_tested_correct
	wrong = num_words_tested - num_tested_correct
	return f"{int(correct)}/{int(num_words_tested)} so far!!"

	# return f"""
	#     Trial Index : {str(dat.index)}\r
	#     Total Correct : {correct}\r
	#     Total Wrong : {wrong}\r
	#     Mean Correct : {mean_correct}\r
	#     Mean Wrong : {mean_wrong}\r
	#     """
ach = None
try:
	ach = achievement(m.responses, num_words_tested,num_tested_correct)
except Exception as e:
	print(e)
if ach!=None and is_a_test(prompt) == True:
	my_canvas.text(ach, y = -175)

if correct:
	my_canvas.text("Correct!", y=150, color="green")
	if is_a_test(prompt) == True:
		num_tested_correct+=1
if not correct:
	my_canvas.text(answer[0], y = 150)
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

