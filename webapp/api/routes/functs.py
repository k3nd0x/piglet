from .mysql import sql
from fastapi import HTTPException
from colour import Color
import random as random
from datetime import datetime, timedelta
from dateutil import parser
from PIL import Image
import hashlib
import time

def get_budgetid(user_id):
    mysql = sql()
    query = '''select budget_id from registered_user where id="{}"'''.format(user_id)

    response = mysql.get(query)[0]["budget_id"]

    
    mysql.close()
    return response


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def hex_color():
    L = '0123456789ABCDEF'
     
    return Color('#'+ ''.join([random.choice(L) for i in range(6)][:]))

def check(mysql,budget_id,user_id):
    query = f'''select pig_budgets.* from pig_budgets JOIN pig_userbudgets on pig_budgets.id = pig_userbudgets.budget_id where pig_userbudgets.user_id = {user_id} and {budget_id}'''

    response = mysql.get(query)

    if response:
        return True
    else:
        raise HTTPException(status_code=403, detail="Forbidden")



def _get_uids(mysql,budget_id):
    get_uids = f'''select user_id from pig_userbudgets where budget_id={budget_id}'''

    uid_list = mysql.get(get_uids)

    return uid_list


def get_timestamp(db_time,time_expire=15):
    final_time = db_time + timedelta(minutes=time_expire)

    now_timestamp = datetime.now()

    diff = final_time - now_timestamp

    if diff.seconds > 0:
       return True
    else:
        return False

def get_notisettings(mysql,user_id,notiobj,notitype):

    get_settings = '''select mail, web from pig_notisettings where user_id="{}" and notiobj="{}" and notitype="{}"'''.format(user_id,notiobj,notitype)

    notisettings = mysql.get(get_settings)

    if not notisettings:
        insert_query = '''insert into pig_notisettings VALUES({},{},{},1,1)'''.format(user_id,notiobj, notitype)
        mysql.post(insert_query)

        notisettings = mysql.get(get_settings)

    return notisettings

def normalize_date(date_string):
    try:
        # Parse the date using dateutil.parser
        parsed_date = parser.parse(date_string)

        # Format the parsed date to the desired format
        normalized_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")

        return normalized_date
    except ValueError:
        # Handle invalid date formats
        print(f"Error: Could not parse date string '{date_string}'")
        return None

def random_name():
    names = ['Lara', 'Geralt', 'Ezio', 'Aloy', 'Nathan', 'Ellie', 'Kratos', 'Cortana', 'Joel', 'Trevor', 'Claire', 'Dante', 'Clementine', 'Niko', 'Faith', 'Max', 'Tifa', 'Ciri', 'Marcus', 'Chloe']
    surnames = ['Croft', 'Rivia', 'Auditore', 'Horizon', 'Drake', 'Williams', 'Kratoson', 'Chief', 'Miller', 'Philips', 'Redfield', 'Sparda', 'Everett', 'Bellic', 'Connors', 'Caulfield', 'Lockhart', 'Forden', 'Fenix', 'Price']
    random_name = random.choice(names)
    random_surname = random.choice(surnames)
    return random_name, random_surname


def random_image(size=8, scale=32):
    try:
        image = Image.new('RGB', (size, size), 'white')
        pixels = image.load()
        
        # Generate random colors
        colors = [(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        ) for _ in range(size * size // 2)]
            

        for x in range(size // 2):
            for y in range(size):
                color = random.choice(colors)
                pixels[x, y] = color
                pixels[size - 1 - x, y] = color  # Mirror the left half to the right half
        
        image = image.resize((size * scale, size * scale), Image.NEAREST)

        current_time = str(time.time())
        hash_object = hashlib.sha256(current_time.encode())
        name = hash_object.hexdigest()

        name = f'gen_{name}.png'

        return image,name
    except:
        return None,"default.png"