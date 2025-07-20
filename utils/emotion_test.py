import os
import random

IMAGE_FOLDER = './static/emotions'
CORRECT_EMOTIONS = {
    'happy.jpeg': 'happy',
    'sad.jpeg': 'sad',
    'angry.jpeg': 'angry',
    'happy1.jpg': 'happy',
    'sad1.jpg' : 'sad',
    'confused.jpeg' : 'confuse',
    'fear.jpeg' :'fear',
    'surprised.jpeg' : 'suprised',
    'anxity.jpg' : 'anxity',
    'angry1.jpg' : 'angry'
}

def get_random_images(n=6):
    images = list(CORRECT_EMOTIONS.keys())
    return random.sample(images, n)

def check_emotion(image_name, user_input):
    correct = CORRECT_EMOTIONS.get(image_name, '').lower()
    return correct == user_input.strip().lower()
