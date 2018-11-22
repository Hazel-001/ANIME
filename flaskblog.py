from flask import Flask, render_template, flash, request, redirect, url_for

app = Flask(__name__)

def get_strong_password(trainingData):
	import random
	data = []
	for index in range(len(trainingData[0])):
		if trainingData[1][index] == 3:
			data.append([trainingData[1][index], trainingData[2][index]])
	password = random.choice(data)[1]
	return password
@app.route('/')
def homepage():
    return render_template("index.html")

def get_password_strength(pw):
	l=0
	uc=0
	lc=0
	d=0
	s=0
	if len(pw)==1:
	    l=20
	elif len(pw)==2:
		l=30
	elif len(pw)==3:
		l=40
	elif len(pw)==4:
		l=50
	elif (len(pw)==5):
	    l=60
	elif len(pw)==6:
	    l=70
	elif len(pw)==7:
	    l=80
	elif len(pw)==8:
		l=90
	else:
	    l=100
	lower=0
	upper=0
	digit=0
	for i in pw:
	    if(i.isnumeric()):
	        digit+=1
	    elif(i.islower()):
	        lower+=1
	    elif(i.isupper()):
	        upper+=1
	if lower==0:
	    lc=20
	elif lower==1:
	    lc=30
	elif lower==2:
	    lc=40
	elif lower==3:
	    lc=60
	elif lower==4:
	    lc=90
	elif lower==5 or lower==6:
	    lc=95
	else:
	    lc=100

	if upper==0:
	    uc=20
	elif upper==1:
	    uc=60
	elif upper==2:
	    uc=80
	elif upper==3:
		uc=90
	else:
	    uc=100

	if digit==0:
	    d=20
	elif digit==2:
	    d=80
	elif digit==3:
		d=90
	elif digit==1:
	    d=60
	else:
	    d=100

	special=len(pw)-(upper+lower+digit)
	if special==0:
	    s=20
	elif special==1:
	    s=60
	elif special==2:
	    s=80
	elif special==3:
		s=90
	else:
	    s=100

	percentage=int((l+uc+lc+s+d)/5)
	return percentage

@app.route('/main/', methods = ["GET", "POST"])
def mainPage():
	suggestion = None
	if request.method == "POST":
		enteredPassword = request.form['password']
		strength = get_password_strength(enteredPassword)

		from sklearn import svm
		import re


		with open('test.txt','w') as test:
			testData = str(enteredPassword) + '|' + str(2)
			test.write(testData)

		# Returns feature & label arrays [ feature, label ]
		def parseData(data):
			features = list()
			labels = list()
			passwords = list()

			with open(data) as f:
				for line in f:
					if line != "":

						both = line.replace('\n', '').split("|")
						password = both[0]
						label = both[1]

						feature = [0,0,0,0,0]

						# FEATURES
						lenMin = False; # more than 8 chars
						specChar = False # special character
						ucChar = False # uppercase character
						numChar = False # numeric character

						# More than 8 characters
						if len(password) > 8:
							lenMin = True

						# Special Character
						specialMatch = re.search(r'([^a-zA-Z0-9]+)', password, re.M)
						if specialMatch:
							specChar = True

						# Uppercase Character
						ucMatch = re.search(r'([A-Z])', password, re.M)
						if ucMatch:
							ucChar = True

						# Numeric Character
						numMatch = re.search(r'([0-9])', password, re.M)
						if numMatch:
							numChar = True

						# Create rules
						if lenMin:
							feature[0] = 1

						if specChar and ucChar and numChar:
							feature[1] = 3

						if ucChar and numChar:
							feature[2] = 1

						if specChar and numChar:
							feature[3] = 2

						if specChar and ucChar:
							feature[4] = 2

						features.append(feature)
						labels.append(int(label))
						passwords.append(password)

			return [features,  labels, passwords]


		# Prepare the data
		trainingData = parseData( 'training.txt' )
		testingData = parseData( 'test.txt' )

		#A SVM Classifier
		clf = svm.SVC(kernel='linear', C = 1.0)

		#Training the classifier with the passwords and their labels.
		clf = clf.fit(trainingData[0], trainingData[1])

		#Predicting a password Strength
		prediction = clf.predict(testingData[0])

		target = len(testingData[1])
		current = 0
		incorrect = 0

		for index in range(target):
				if(prediction[index] == 0):
					predicted = "Very Weak Password"
					suggestion = get_strong_password(trainingData)
				elif(prediction[index] == 1):
					predicted = "Weak Password"
					suggestion = get_strong_password(trainingData)
				elif(prediction[index] == 2):
					predicted = "Strong Password"
				elif(prediction[index] == 3):
					predicted = "Very Strong Password"
	if not suggestion:				
		return render_template("main.html", predicted = predicted, target = len(trainingData[1]), strength = strength)
	else:
		return render_template(
			"main.html",
			predicted=predicted,
			target = len(trainingData[1]),
			suggestion=suggestion, strength = strength)


if __name__ == "__main__":
    app.run(host= '0.0.0.0')


