from flask import Flask, render_template, request, jsonify
from chatbot import get_gemini_response
from utils.geneReport import genereport_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.register_blueprint(genereport_bp)

@app.route('/')
def home():
    return render_template('Home/home.html')

@app.route('/about')
def about():
    return render_template('Home/about.html')

@app.route('/explore')
def explore():
    return render_template('Home/explore.html')

@app.route('/research')
def research():
    return render_template('Home/research.html')

@app.route('/dashboard')
def dashboard():
    return render_template('Home/dashboard.html')

# user

@app.route('/userDashboard')
def userDashboard():
    return render_template('User/userDashboard.html')
@app.route('/chatbot')
def chatbot():
    return render_template('User/chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    bot_response = get_gemini_response(user_message)
    return jsonify({'response': bot_response})

# 3 combined test
from userASDTest import handle_prediction

@app.route('/ASDTest')
def ASDTest():
    return render_template('User/ASDTest.html')

@app.route('/predict', methods=['POST'])
def predict():
    return handle_prediction()


from flask import Flask, render_template, request, session, redirect, url_for
from utils.emotion_test import get_random_images, check_emotion


app.secret_key = 'a3d95fbc1e07c64b45b1f9e8c12a7b8d'

@app.route('/userinfo')
def userinfo():
    return redirect(url_for('user_info'))

@app.route('/user-info', methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        session.clear()
        session['user_info'] = {
            'name': request.form['name'],
            'age': request.form['age'],
            'gender': request.form['gender']
        }
        session['emotion_images'] = get_random_images()
        session['current_emotion_index'] = 0
        session['emotion_score'] = 0
        return redirect('/emotion-test')
    return render_template('ASDTest/user_info.html')

@app.route('/emotion-test', methods=['GET', 'POST'])
def emotion_test():
    if 'user_info' not in session:
        return redirect('/user-info')

    index = session.get('current_emotion_index', 0)
    images = session.get('emotion_images', [])

    if request.method == 'POST':
        user_input = request.form.get('emotion')
        image_name = images[index]
        if check_emotion(image_name, user_input):
            session['emotion_score'] += 1
        session['current_emotion_index'] += 1
        return redirect('/emotion-test')

    if index >= len(images):
        return redirect('/speechTest')

    image_name = images[index]
    return render_template('ASDTest/emotion_test.html', image_name=image_name, current=index + 1, total=len(images))

@app.route('/speechTest', methods=['GET', 'POST'])
def speechTest():
    if 'user_info' not in session:
        return redirect('/user-info')

    if request.method == 'POST':
        score = request.form.get('score')
        session['speech_score'] = int(score) if score else 0
        return redirect('/result')
    return render_template('ASDTest/speechTest.html')

#user openCV remaining

@app.route('/result')
def result():
    user = {
        'name':session.get('user_info',''),
        'emotion': session.get('emotion_score', 0),
        'speech': session.get('speech_score', 0),
        'eye': session.get('eye_score', 0)

    }
    return render_template('ASDTest/result.html', user=user)







#researcher section

@app.route('/researchDashboard')
def researchDashboard():
    return render_template('Researcher/researchDashboard.html')


@app.route('/researchChatbot')
def researchChatbot():
    return render_template('Researcher/researchChatbot.html')

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('home'))

# if __name__ == '__main__':
#     app.run(debug=True)


import os

port = int(os.environ.get("PORT"))
app.run(host='0.0.0.0', port=port, debug=True)