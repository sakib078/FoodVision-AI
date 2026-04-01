import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.h5')
CLASSES_PATH = os.path.join(BASE_DIR, 'classes.txt')

model = None
class_names = []

# --- COMPREHENSIVE CALORIE DATABASE FOR ALL 101 FOOD-101 CLASSES ---
CALORIE_DATABASE = {
    'apple_pie': {'per_100g': 237, 'portions': {'small': {'grams': 100, 'description': '1 small slice'}, 'medium': {'grams': 150, 'description': '1 regular slice'}, 'large': {'grams': 200, 'description': '1 large slice'}}},
    'baby_back_ribs': {'per_100g': 290, 'portions': {'small': {'grams': 150, 'description': '3-4 ribs'}, 'medium': {'grams': 250, 'description': '5-6 ribs'}, 'large': {'grams': 350, 'description': '7-8 ribs'}}},
    'baklava': {'per_100g': 428, 'portions': {'small': {'grams': 40, 'description': '1 small piece'}, 'medium': {'grams': 70, 'description': '1 regular piece'}, 'large': {'grams': 100, 'description': '1 large piece'}}},
    'beef_carpaccio': {'per_100g': 142, 'portions': {'small': {'grams': 60, 'description': 'Appetizer'}, 'medium': {'grams': 100, 'description': 'Regular serving'}, 'large': {'grams': 150, 'description': 'Large serving'}}},
    'beef_tartare': {'per_100g': 188, 'portions': {'small': {'grams': 80, 'description': 'Appetizer'}, 'medium': {'grams': 120, 'description': 'Regular serving'}, 'large': {'grams': 180, 'description': 'Main course'}}},
    'beet_salad': {'per_100g': 65, 'portions': {'small': {'grams': 100, 'description': 'Side salad'}, 'medium': {'grams': 200, 'description': 'Regular bowl'}, 'large': {'grams': 300, 'description': 'Large bowl'}}},
    'beignets': {'per_100g': 350, 'portions': {'small': {'grams': 50, 'description': '2 beignets'}, 'medium': {'grams': 100, 'description': '4 beignets'}, 'large': {'grams': 150, 'description': '6 beignets'}}},
    'bibimbap': {'per_100g': 105, 'portions': {'small': {'grams': 250, 'description': 'Small bowl'}, 'medium': {'grams': 400, 'description': 'Regular bowl'}, 'large': {'grams': 550, 'description': 'Large bowl'}}},
    'bread_pudding': {'per_100g': 186, 'portions': {'small': {'grams': 100, 'description': 'Small serving'}, 'medium': {'grams': 150, 'description': 'Regular serving'}, 'large': {'grams': 225, 'description': 'Large serving'}}},
    'breakfast_burrito': {'per_100g': 151, 'portions': {'small': {'grams': 150, 'description': 'Small burrito'}, 'medium': {'grams': 250, 'description': 'Regular burrito'}, 'large': {'grams': 350, 'description': 'Large burrito'}}},
    'bruschetta': {'per_100g': 195, 'portions': {'small': {'grams': 50, 'description': '2 pieces'}, 'medium': {'grams': 100, 'description': '4 pieces'}, 'large': {'grams': 150, 'description': '6 pieces'}}},
    'caesar_salad': {'per_100g': 85, 'portions': {'small': {'grams': 150, 'description': 'Side salad'}, 'medium': {'grams': 300, 'description': 'Regular bowl'}, 'large': {'grams': 450, 'description': 'Large bowl'}}},
    'cannoli': {'per_100g': 330, 'portions': {'small': {'grams': 50, 'description': '1 mini cannoli'}, 'medium': {'grams': 85, 'description': '1 regular cannoli'}, 'large': {'grams': 120, 'description': '1 large cannoli'}}},
    'caprese_salad': {'per_100g': 160, 'portions': {'small': {'grams': 100, 'description': 'Appetizer'}, 'medium': {'grams': 200, 'description': 'Regular serving'}, 'large': {'grams': 300, 'description': 'Large serving'}}},
    'carrot_cake': {'per_100g': 350, 'portions': {'small': {'grams': 80, 'description': 'Small slice'}, 'medium': {'grams': 120, 'description': 'Regular slice'}, 'large': {'grams': 160, 'description': 'Large slice'}}},
    'ceviche': {'per_100g': 97, 'portions': {'small': {'grams': 100, 'description': 'Appetizer'}, 'medium': {'grams': 180, 'description': 'Regular serving'}, 'large': {'grams': 250, 'description': 'Large serving'}}},
    'cheese_plate': {'per_100g': 350, 'portions': {'small': {'grams': 80, 'description': 'Appetizer portion'}, 'medium': {'grams': 120, 'description': 'Regular portion'}, 'large': {'grams': 180, 'description': 'Large portion'}}},
    'cheesecake': {'per_100g': 321, 'portions': {'small': {'grams': 80, 'description': 'Small slice'}, 'medium': {'grams': 125, 'description': 'Regular slice'}, 'large': {'grams': 170, 'description': 'Large slice'}}},
    'chicken_curry': {'per_100g': 118, 'portions': {'small': {'grams': 200, 'description': 'Small bowl'}, 'medium': {'grams': 350, 'description': 'Regular bowl'}, 'large': {'grams': 500, 'description': 'Large bowl'}}},
    'chicken_quesadilla': {'per_100g': 206, 'portions': {'small': {'grams': 100, 'description': '2 slices'}, 'medium': {'grams': 200, 'description': '4 slices'}, 'large': {'grams': 300, 'description': '6 slices'}}},
    'chicken_wings': {'per_100g': 290, 'portions': {'small': {'grams': 100, 'description': '4-5 wings'}, 'medium': {'grams': 180, 'description': '8-10 wings'}, 'large': {'grams': 270, 'description': '12-15 wings'}}},
    'chocolate_cake': {'per_100g': 371, 'portions': {'small': {'grams': 70, 'description': 'Small slice'}, 'medium': {'grams': 110, 'description': 'Regular slice'}, 'large': {'grams': 150, 'description': 'Large slice'}}},
    'chocolate_mousse': {'per_100g': 189, 'portions': {'small': {'grams': 80, 'description': 'Small serving'}, 'medium': {'grams': 120, 'description': 'Regular serving'}, 'large': {'grams': 180, 'description': 'Large serving'}}},
    'churros': {'per_100g': 375, 'portions': {'small': {'grams': 50, 'description': '2-3 churros'}, 'medium': {'grams': 100, 'description': '4-5 churros'}, 'large': {'grams': 150, 'description': '6-8 churros'}}},
    'clam_chowder': {'per_100g': 85, 'portions': {'small': {'grams': 200, 'description': 'Cup'}, 'medium': {'grams': 350, 'description': 'Bowl'}, 'large': {'grams': 500, 'description': 'Large bowl'}}},
    'club_sandwich': {'per_100g': 240, 'portions': {'small': {'grams': 150, 'description': 'Half sandwich'}, 'medium': {'grams': 250, 'description': 'Full sandwich'}, 'large': {'grams': 350, 'description': 'Large sandwich'}}},
    'crab_cakes': {'per_100g': 214, 'portions': {'small': {'grams': 60, 'description': '1 small cake'}, 'medium': {'grams': 100, 'description': '1-2 regular cakes'}, 'large': {'grams': 150, 'description': '2-3 cakes'}}},
    'creme_brulee': {'per_100g': 280, 'portions': {'small': {'grams': 80, 'description': 'Small ramekin'}, 'medium': {'grams': 120, 'description': 'Regular ramekin'}, 'large': {'grams': 160, 'description': 'Large ramekin'}}},
    'croque_madame': {'per_100g': 260, 'portions': {'small': {'grams': 150, 'description': 'Small sandwich'}, 'medium': {'grams': 250, 'description': 'Regular sandwich'}, 'large': {'grams': 350, 'description': 'Large sandwich'}}},
    'cup_cakes': {'per_100g': 305, 'portions': {'small': {'grams': 40, 'description': '1 mini cupcake'}, 'medium': {'grams': 70, 'description': '1 regular cupcake'}, 'large': {'grams': 110, 'description': '1 large cupcake'}}},
    'deviled_eggs': {'per_100g': 206, 'portions': {'small': {'grams': 30, 'description': '1 egg half'}, 'medium': {'grams': 60, 'description': '2 egg halves'}, 'large': {'grams': 120, 'description': '4 egg halves'}}},
    'donuts': {'per_100g': 452, 'portions': {'small': {'grams': 40, 'description': '1 mini donut'}, 'medium': {'grams': 75, 'description': '1 regular donut'}, 'large': {'grams': 110, 'description': '1 large donut'}}},
    'dumplings': {'per_100g': 206, 'portions': {'small': {'grams': 100, 'description': '4-5 dumplings'}, 'medium': {'grams': 180, 'description': '8-10 dumplings'}, 'large': {'grams': 270, 'description': '12-15 dumplings'}}},
    'edamame': {'per_100g': 122, 'portions': {'small': {'grams': 80, 'description': 'Small bowl'}, 'medium': {'grams': 150, 'description': 'Regular bowl'}, 'large': {'grams': 220, 'description': 'Large bowl'}}},
    'eggs_benedict': {'per_100g': 254, 'portions': {'small': {'grams': 150, 'description': '1 egg portion'}, 'medium': {'grams': 250, 'description': '2 eggs portion'}, 'large': {'grams': 350, 'description': '3 eggs portion'}}},
    'escargots': {'per_100g': 90, 'portions': {'small': {'grams': 50, 'description': '3-4 escargots'}, 'medium': {'grams': 80, 'description': '6 escargots'}, 'large': {'grams': 120, 'description': '9-12 escargots'}}},
    'falafel': {'per_100g': 333, 'portions': {'small': {'grams': 60, 'description': '2-3 balls'}, 'medium': {'grams': 120, 'description': '5-6 balls'}, 'large': {'grams': 180, 'description': '8-9 balls'}}},
    'filet_mignon': {'per_100g': 227, 'portions': {'small': {'grams': 150, 'description': '6 oz steak'}, 'medium': {'grams': 225, 'description': '8 oz steak'}, 'large': {'grams': 340, 'description': '12 oz steak'}}},
    'fish_and_chips': {'per_100g': 215, 'portions': {'small': {'grams': 200, 'description': 'Small portion'}, 'medium': {'grams': 350, 'description': 'Regular portion'}, 'large': {'grams': 500, 'description': 'Large portion'}}},
    'foie_gras': {'per_100g': 462, 'portions': {'small': {'grams': 40, 'description': 'Appetizer'}, 'medium': {'grams': 60, 'description': 'Regular serving'}, 'large': {'grams': 90, 'description': 'Large serving'}}},
    'french_fries': {'per_100g': 312, 'portions': {'small': {'grams': 80, 'description': 'Small fries'}, 'medium': {'grams': 140, 'description': 'Medium fries'}, 'large': {'grams': 200, 'description': 'Large fries'}}},
    'french_onion_soup': {'per_100g': 63, 'portions': {'small': {'grams': 200, 'description': 'Cup'}, 'medium': {'grams': 350, 'description': 'Bowl'}, 'large': {'grams': 500, 'description': 'Large bowl'}}},
    'french_toast': {'per_100g': 224, 'portions': {'small': {'grams': 100, 'description': '2 slices'}, 'medium': {'grams': 150, 'description': '3 slices'}, 'large': {'grams': 200, 'description': '4 slices'}}},
    'fried_calamari': {'per_100g': 175, 'portions': {'small': {'grams': 100, 'description': 'Appetizer'}, 'medium': {'grams': 180, 'description': 'Regular serving'}, 'large': {'grams': 270, 'description': 'Large serving'}}},
    'fried_rice': {'per_100g': 163, 'portions': {'small': {'grams': 150, 'description': 'Side dish'}, 'medium': {'grams': 300, 'description': 'Regular bowl'}, 'large': {'grams': 450, 'description': 'Large bowl'}}},
    'frozen_yogurt': {'per_100g': 127, 'portions': {'small': {'grams': 100, 'description': 'Small cup'}, 'medium': {'grams': 150, 'description': 'Regular cup'}, 'large': {'grams': 225, 'description': 'Large cup'}}},
    'garlic_bread': {'per_100g': 350, 'portions': {'small': {'grams': 50, 'description': '2 slices'}, 'medium': {'grams': 100, 'description': '4 slices'}, 'large': {'grams': 150, 'description': '6 slices'}}},
    'gnocchi': {'per_100g': 147, 'portions': {'small': {'grams': 150, 'description': 'Side dish'}, 'medium': {'grams': 250, 'description': 'Regular serving'}, 'large': {'grams': 350, 'description': 'Large serving'}}},
    'greek_salad': {'per_100g': 90, 'portions': {'small': {'grams': 150, 'description': 'Side salad'}, 'medium': {'grams': 300, 'description': 'Regular bowl'}, 'large': {'grams': 450, 'description': 'Large bowl'}}},
    'grilled_cheese_sandwich': {'per_100g': 303, 'portions': {'small': {'grams': 100, 'description': 'Half sandwich'}, 'medium': {'grams': 150, 'description': 'Full sandwich'}, 'large': {'grams': 225, 'description': 'Large sandwich'}}},
    'grilled_salmon': {'per_100g': 206, 'portions': {'small': {'grams': 100, 'description': 'Small fillet'}, 'medium': {'grams': 175, 'description': 'Regular fillet'}, 'large': {'grams': 250, 'description': 'Large fillet'}}},
    'guacamole': {'per_100g': 160, 'portions': {'small': {'grams': 50, 'description': 'Small serving'}, 'medium': {'grams': 100, 'description': 'Regular serving'}, 'large': {'grams': 150, 'description': 'Large serving'}}},
    'gyoza': {'per_100g': 211, 'portions': {'small': {'grams': 80, 'description': '4 pieces'}, 'medium': {'grams': 120, 'description': '6 pieces'}, 'large': {'grams': 180, 'description': '9 pieces'}}},
    'hamburger': {'per_100g': 295, 'portions': {'small': {'grams': 100, 'description': 'Slider'}, 'medium': {'grams': 200, 'description': 'Regular burger'}, 'large': {'grams': 300, 'description': 'Large burger'}}},
    'hot_and_sour_soup': {'per_100g': 35, 'portions': {'small': {'grams': 200, 'description': 'Cup'}, 'medium': {'grams': 350, 'description': 'Bowl'}, 'large': {'grams': 500, 'description': 'Large bowl'}}},
    'hot_dog': {'per_100g': 290, 'portions': {'small': {'grams': 80, 'description': '1 regular hot dog'}, 'medium': {'grams': 120, 'description': '1 large hot dog'}, 'large': {'grams': 180, 'description': '2 hot dogs'}}},
    'huevos_rancheros': {'per_100g': 145, 'portions': {'small': {'grams': 200, 'description': '1 egg portion'}, 'medium': {'grams': 300, 'description': '2 eggs portion'}, 'large': {'grams': 400, 'description': '3 eggs portion'}}},
    'hummus': {'per_100g': 166, 'portions': {'small': {'grams': 50, 'description': 'Small serving'}, 'medium': {'grams': 100, 'description': 'Regular serving'}, 'large': {'grams': 150, 'description': 'Large serving'}}},
    'ice_cream': {'per_100g': 207, 'portions': {'small': {'grams': 70, 'description': '1 scoop'}, 'medium': {'grams': 140, 'description': '2 scoops'}, 'large': {'grams': 210, 'description': '3 scoops'}}},
    'lasagna': {'per_100g': 135, 'portions': {'small': {'grams': 200, 'description': 'Small serving'}, 'medium': {'grams': 350, 'description': 'Regular serving'}, 'large': {'grams': 500, 'description': 'Large serving'}}},
    'lobster_bisque': {'per_100g': 88, 'portions': {'small': {'grams': 200, 'description': 'Cup'}, 'medium': {'grams': 300, 'description': 'Bowl'}, 'large': {'grams': 450, 'description': 'Large bowl'}}},
    'lobster_roll_sandwich': {'per_100g': 208, 'portions': {'small': {'grams': 120, 'description': 'Small roll'}, 'medium': {'grams': 180, 'description': 'Regular roll'}, 'large': {'grams': 250, 'description': 'Large roll'}}},
    'macaroni_and_cheese': {'per_100g': 164, 'portions': {'small': {'grams': 150, 'description': 'Side dish'}, 'medium': {'grams': 300, 'description': 'Regular bowl'}, 'large': {'grams': 450, 'description': 'Large bowl'}}},
    'macarons': {'per_100g': 407, 'portions': {'small': {'grams': 20, 'description': '1 macaron'}, 'medium': {'grams': 40, 'description': '2 macarons'}, 'large': {'grams': 60, 'description': '3 macarons'}}},
    'miso_soup': {'per_100g': 40, 'portions': {'small': {'grams': 150, 'description': 'Small bowl'}, 'medium': {'grams': 250, 'description': 'Regular bowl'}, 'large': {'grams': 350, 'description': 'Large bowl'}}},
    'mussels': {'per_100g': 172, 'portions': {'small': {'grams': 100, 'description': 'Appetizer'}, 'medium': {'grams': 200, 'description': 'Regular serving'}, 'large': {'grams': 300, 'description': 'Large serving'}}},
    'nachos': {'per_100g': 306, 'portions': {'small': {'grams': 100, 'description': 'Small plate'}, 'medium': {'grams': 200, 'description': 'Regular plate'}, 'large': {'grams': 350, 'description': 'Large plate'}}},
    'omelette': {'per_100g': 154, 'portions': {'small': {'grams': 100, 'description': '2-egg omelette'}, 'medium': {'grams': 150, 'description': '3-egg omelette'}, 'large': {'grams': 225, 'description': '4-egg omelette'}}},
    'onion_rings': {'per_100g': 411, 'portions': {'small': {'grams': 80, 'description': 'Small serving'}, 'medium': {'grams': 140, 'description': 'Regular serving'}, 'large': {'grams': 200, 'description': 'Large serving'}}},
    'oysters': {'per_100g': 81, 'portions': {'small': {'grams': 60, 'description': '3 oysters'}, 'medium': {'grams': 100, 'description': '6 oysters'}, 'large': {'grams': 150, 'description': '9 oysters'}}},
    'pad_thai': {'per_100g': 150, 'portions': {'small': {'grams': 200, 'description': 'Small plate'}, 'medium': {'grams': 350, 'description': 'Regular plate'}, 'large': {'grams': 500, 'description': 'Large plate'}}},
    'paella': {'per_100g': 139, 'portions': {'small': {'grams': 250, 'description': 'Small serving'}, 'medium': {'grams': 400, 'description': 'Regular serving'}, 'large': {'grams': 550, 'description': 'Large serving'}}},
    'pancakes': {'per_100g': 227, 'portions': {'small': {'grams': 100, 'description': '2 pancakes'}, 'medium': {'grams': 150, 'description': '3 pancakes'}, 'large': {'grams': 225, 'description': '4-5 pancakes'}}},
    'panna_cotta': {'per_100g': 240, 'portions': {'small': {'grams': 80, 'description': 'Small serving'}, 'medium': {'grams': 120, 'description': 'Regular serving'}, 'large': {'grams': 180, 'description': 'Large serving'}}},
    'peking_duck': {'per_100g': 337, 'portions': {'small': {'grams': 100, 'description': 'Small serving'}, 'medium': {'grams': 175, 'description': 'Regular serving'}, 'large': {'grams': 250, 'description': 'Large serving'}}},
    'pho': {'per_100g': 62, 'portions': {'small': {'grams': 350, 'description': 'Small bowl'}, 'medium': {'grams': 550, 'description': 'Regular bowl'}, 'large': {'grams': 750, 'description': 'Large bowl'}}},
    'pizza': {'per_100g': 266, 'portions': {'small': {'grams': 100, 'description': '1 slice'}, 'medium': {'grams': 200, 'description': '2 slices'}, 'large': {'grams': 400, 'description': '4 slices'}}},
    'pork_chop': {'per_100g': 231, 'portions': {'small': {'grams': 120, 'description': 'Small chop'}, 'medium': {'grams': 180, 'description': 'Regular chop'}, 'large': {'grams': 270, 'description': 'Large chop'}}},
    'poutine': {'per_100g': 510, 'portions': {'small': {'grams': 150, 'description': 'Small serving'}, 'medium': {'grams': 250, 'description': 'Regular serving'}, 'large': {'grams': 400, 'description': 'Large serving'}}},
    'prime_rib': {'per_100g': 338, 'portions': {'small': {'grams': 150, 'description': '6 oz cut'}, 'medium': {'grams': 225, 'description': '8 oz cut'}, 'large': {'grams': 340, 'description': '12 oz cut'}}},
    'pulled_pork_sandwich': {'per_100g': 179, 'portions': {'small': {'grams': 150, 'description': 'Small sandwich'}, 'medium': {'grams': 250, 'description': 'Regular sandwich'}, 'large': {'grams': 350, 'description': 'Large sandwich'}}},
    'ramen': {'per_100g': 71, 'portions': {'small': {'grams': 300, 'description': 'Small bowl'}, 'medium': {'grams': 500, 'description': 'Regular bowl'}, 'large': {'grams': 700, 'description': 'Large bowl'}}},
    'ravioli': {'per_100g': 175, 'portions': {'small': {'grams': 150, 'description': 'Small serving'}, 'medium': {'grams': 250, 'description': 'Regular serving'}, 'large': {'grams': 350, 'description': 'Large serving'}}},
    'red_velvet_cake': {'per_100g': 364, 'portions': {'small': {'grams': 75, 'description': 'Small slice'}, 'medium': {'grams': 115, 'description': 'Regular slice'}, 'large': {'grams': 160, 'description': 'Large slice'}}},
    'risotto': {'per_100g': 134, 'portions': {'small': {'grams': 150, 'description': 'Side dish'}, 'medium': {'grams': 300, 'description': 'Regular serving'}, 'large': {'grams': 450, 'description': 'Large serving'}}},
    'samosa': {'per_100g': 262, 'portions': {'small': {'grams': 50, 'description': '1 samosa'}, 'medium': {'grams': 100, 'description': '2 samosas'}, 'large': {'grams': 150, 'description': '3 samosas'}}},
    'sashimi': {'per_100g': 127, 'portions': {'small': {'grams': 80, 'description': '4-5 pieces'}, 'medium': {'grams': 120, 'description': '6-8 pieces'}, 'large': {'grams': 180, 'description': '10-12 pieces'}}},
    'scallops': {'per_100g': 111, 'portions': {'small': {'grams': 80, 'description': '3-4 scallops'}, 'medium': {'grams': 120, 'description': '5-6 scallops'}, 'large': {'grams': 180, 'description': '8-9 scallops'}}},
    'seaweed_salad': {'per_100g': 70, 'portions': {'small': {'grams': 80, 'description': 'Side dish'}, 'medium': {'grams': 150, 'description': 'Regular bowl'}, 'large': {'grams': 220, 'description': 'Large bowl'}}},
    'shrimp_and_grits': {'per_100g': 143, 'portions': {'small': {'grams': 200, 'description': 'Small serving'}, 'medium': {'grams': 350, 'description': 'Regular serving'}, 'large': {'grams': 500, 'description': 'Large serving'}}},
    'spaghetti_bolognese': {'per_100g': 122, 'portions': {'small': {'grams': 200, 'description': 'Small plate'}, 'medium': {'grams': 350, 'description': 'Regular plate'}, 'large': {'grams': 500, 'description': 'Large plate'}}},
    'spaghetti_carbonara': {'per_100g': 166, 'portions': {'small': {'grams': 200, 'description': 'Small plate'}, 'medium': {'grams': 350, 'description': 'Regular plate'}, 'large': {'grams': 500, 'description': 'Large plate'}}},
    'spring_rolls': {'per_100g': 150, 'portions': {'small': {'grams': 60, 'description': '2 rolls'}, 'medium': {'grams': 120, 'description': '4 rolls'}, 'large': {'grams': 180, 'description': '6 rolls'}}},
    'steak': {'per_100g': 271, 'portions': {'small': {'grams': 150, 'description': '6 oz steak'}, 'medium': {'grams': 225, 'description': '8 oz steak'}, 'large': {'grams': 340, 'description': '12 oz steak'}}},
    'strawberry_shortcake': {'per_100g': 285, 'portions': {'small': {'grams': 80, 'description': 'Small slice'}, 'medium': {'grams': 125, 'description': 'Regular slice'}, 'large': {'grams': 180, 'description': 'Large slice'}}},
    'sushi': {'per_100g': 143, 'portions': {'small': {'grams': 100, 'description': '6 pieces'}, 'medium': {'grams': 180, 'description': '12 pieces'}, 'large': {'grams': 270, 'description': '18 pieces'}}},
    'tacos': {'per_100g': 217, 'portions': {'small': {'grams': 100, 'description': '2 tacos'}, 'medium': {'grams': 180, 'description': '3 tacos'}, 'large': {'grams': 270, 'description': '4-5 tacos'}}},
    'takoyaki': {'per_100g': 190, 'portions': {'small': {'grams': 80, 'description': '4 balls'}, 'medium': {'grams': 120, 'description': '6 balls'}, 'large': {'grams': 180, 'description': '9 balls'}}},
    'tiramisu': {'per_100g': 320, 'portions': {'small': {'grams': 80, 'description': 'Small slice'}, 'medium': {'grams': 120, 'description': 'Regular slice'}, 'large': {'grams': 180, 'description': 'Large slice'}}},
    'tuna_tartare': {'per_100g': 144, 'portions': {'small': {'grams': 80, 'description': 'Appetizer'}, 'medium': {'grams': 120, 'description': 'Regular serving'}, 'large': {'grams': 180, 'description': 'Main course'}}},
    'waffles': {'per_100g': 291, 'portions': {'small': {'grams': 75, 'description': '1 waffle'}, 'medium': {'grams': 150, 'description': '2 waffles'}, 'large': {'grams': 225, 'description': '3 waffles'}}}
}

def load_resources():
    global model, class_names
    print("--- Loading Resources ---")
    
    # 1. Load Class Names
    if os.path.exists(CLASSES_PATH):
        try:
            with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if '\n' in content:
                    class_names = [line.strip() for line in content.split('\n') if line.strip()]
                else:
                    class_names = content.replace(',', ' ').split()
            print(f"✅ Loaded {len(class_names)} names from file.")
        except Exception as e:
            print(f"❌ Error reading classes file: {e}")
            class_names = []
    else:
        print(f"⚠️ Warning: classes.txt not found.")

    # 2. Load Model
    if os.path.exists(MODEL_PATH):
        try:
            print(f"⏳ Loading model...")
            model = tf.keras.models.load_model(MODEL_PATH)
            
            try:
                output_shape = model.output_shape[-1]
                print(f"✅ Model loaded. Expects {output_shape} classes.")
                
                if len(class_names) != output_shape:
                    print(f"⚠️ SHAPE MISMATCH: File has {len(class_names)} names, Model has {output_shape} outputs.")
                    if len(class_names) > output_shape:
                        print(f"   -> Truncating list to first {output_shape} names.")
                        class_names = class_names[:output_shape]
                    else:
                        print(f"   -> Padding list to run.")
                        while len(class_names) < output_shape:
                            class_names.append(f"Class_{len(class_names)}")
            except:
                pass
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    else:
        print(f"⚠️ CRITICAL: Model file not found.")

def preprocess_image(image_bytes):
    """
    Using ResNet50 preprocessing to match training
    """
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    img = img.resize((224, 224))
    arr = tf.keras.preprocessing.image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    arr = tf.keras.applications.resnet50.preprocess_input(arr)
    
    return arr

@app.route('/predict', methods=['POST'])
def predict():
    global model
    print("\n📩 Request received...")

    if 'file' not in request.files: 
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '': 
        return jsonify({'error': 'No selected file'}), 400
    if model is None: 
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        print(f"📸 Image: {file.filename}")
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        print(f"   Input Stats: Min={processed_image.min():.2f}, Max={processed_image.max():.2f}")

        print("🧠 Inferencing...")
        predictions = model.predict(processed_image)
        
        # Print top 3 predictions for debugging
        top_k = 3
        top_indices = predictions[0].argsort()[-top_k:][::-1]
        print(f"   Top {top_k} predictions:")
        for idx in top_indices:
            label = class_names[idx] if idx < len(class_names) else f"Class {idx}"
            score = predictions[0][idx]
            print(f"   - {label}: {score:.4f}")

        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx])
        
        if predicted_idx < len(class_names):
            predicted_label = class_names[predicted_idx]
        else:
            predicted_label = f"Class {predicted_idx}"

        # Get calorie data for this food
        lookup_key = predicted_label.lower().replace(' ', '_')
        food_data = CALORIE_DATABASE.get(lookup_key)
        
        if food_data:
            # Build portion options
            portion_options = []
            for size, info in food_data['portions'].items():
                calories = int((food_data['per_100g'] / 100) * info['grams'])
                portion_options.append({
                    'size': size,
                    'grams': info['grams'],
                    'description': info['description'],
                    'calories': calories
                })
            
            # Default to medium portion
            default_portion = food_data['portions'].get('medium', list(food_data['portions'].values())[0])
            default_calories = int((food_data['per_100g'] / 100) * default_portion['grams'])
        else:
            # Fallback for foods not in database
            portion_options = [
                {'size': 'small', 'grams': 100, 'description': 'Small serving', 'calories': 150},
                {'size': 'medium', 'grams': 200, 'description': 'Regular serving', 'calories': 300},
                {'size': 'large', 'grams': 300, 'description': 'Large serving', 'calories': 450}
            ]
            default_calories = 300

        return jsonify({
            'label': predicted_label,
            'confidence': confidence,
            'calories': default_calories,  # Default medium portion
            'portion_options': portion_options,  # All available portions
            'class_id': int(predicted_idx)
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    load_resources()
    app.run(debug=True, port=5000)
