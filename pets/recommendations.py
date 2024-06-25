# recommendations.p
import psycopg2
from collections import namedtuple

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="petgeed",
    user="postgres",
    password="prowarrior77",
    host="localhost",
    port="5432"
)

# Создание namedtuple для хранения информации о корме
FoodInfo = namedtuple('FoodInfo', 'energy_value protein fat calcium phosphorus vitamin_a vitamin_d vitamin_e iron copper zinc manganese iodine selenium')

def parse_food_info(info_str):
    # Распарсивание строки info
    info_values = [float(x) for x in info_str.split(';')]
    return FoodInfo(*info_values)

def get_foods():
    # Получение списка кормов из базы данных
    with conn.cursor() as cur:
        cur.execute("SELECT id, feed_name, info FROM foods")
        foods = [(row[0], row[1], parse_food_info(row[2])) for row in cur.fetchall()]
    return foods

def calculate_recommended_food_amount(pet):
    weight = pet.pet_weight
    activity_level = 1
    if pet.pet_type:
        coefficient = 30
    if pet.pet_sterilized:
        activity_level = 1
    else:
        activity_level = 0.8
    recommended_amount = weight ** (2/3) * coefficient * activity_level
    return recommended_amount

def calculate_min_nutrients(pet):
    weight = pet.pet_weight
    if pet.pet_type:
        min_protein = weight * 0.25
        min_fat = weight * 0.15
        min_carbs = weight * 0.1
        min_calcium = weight * 0.005
        min_phosphorus = weight * 0.0045
        min_vitamin_a = weight * 0.0001
        min_vitamin_d = weight * 0.000025
        min_vitamin_e = weight * 0.0001
        min_iron = weight * 0.00005
        min_copper = weight * 0.00001
        min_zinc = weight * 0.00002
        min_manganese = weight * 0.000002
        min_iodine = weight * 0.000001
        min_selenium = weight * 0.000001
    return (min_protein, min_fat, min_carbs,
            min_calcium, min_phosphorus, min_vitamin_a, min_vitamin_d, min_vitamin_e,
            min_iron, min_copper, min_zinc, min_manganese, min_iodine, min_selenium)

def recommend_food(pet):
    min_nutrients = calculate_min_nutrients(pet)
    recommended_amount = calculate_recommended_food_amount(pet)

    foods = get_foods()

    # отфильтровать корма по болезням питомца
    diseases = pet.pet_diseases.split(';')
    recommended_foods = []
    for food_id, food_name, food_info in foods:
        if any(disease in food_name.lower() for disease in diseases):
            continue
        recommended_foods.append((food_id, food_name, food_info))

    # отсортировать корма по градации значимости полезных элементов
    recommended_foods.sort(key=lambda x: sum([abs(x[2][i] - min_nutrients[i]) for i in range(len(min_nutrients))]))

    # выбрать первый подходящий корм
    recommended_food = recommended_foods[0] if recommended_foods else None

    # рассчитать количество корма в граммах в день
    if recommended_food:
        food_id, food_name, food_info = recommended_food
        recommended_amount_g = recommended_amount / food_info.energy_value * 100
        min_nutrients_g = [min_nutrient / food_info.energy_value * 100 for min_nutrient in min_nutrients]
        return food_name, recommended_amount_g, min_nutrients_g
    else:
        return None, None, None
