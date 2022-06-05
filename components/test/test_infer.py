import sys
sys.path.append("..")
from components import inference, trainer
from configs.config import logger
def test_one_input():
    input = {
        "year": 2022,
        "branch": 'Ford',
        "model": 'Ranger',
        "origin": 'domestic',
        "km_driven":380,
        "external_color": "Trắng",
        "internal_color": "Đen", 
        "num_seats": 5,
        "engine_capacity": 2.0,
        "gearbox": "automatic",
        "wheel_drive": "4WD",
        "car_type":"pickup"
    }

    inference.run([input])
    logger.info("Complete with one input")

def test_many_input():
    input1 = {
        "year": 2022,
        "branch": 'Ford',
        "model": 'Ranger',
        "origin": 'domestic',
        "km_driven":380,
        "external_color": "Trắng",
        "internal_color": "Đen", 
        "num_seats": 5,
        "engine_capacity": 2.0,
        "gearbox": "automatic",
        "wheel_drive": "4WD",
        "car_type":"pickup"
    }
    input2 = {
        "year": 2022,
        "branch": 'Ford',
        "model": 'Ranger',
        "origin": 'domestic',
        "km_driven":380,
        "external_color": "Trắng",
        "internal_color": "Đen", 
        "num_seats": 5,
        "engine_capacity": 2.0,
        "gearbox": "automatic",
        "wheel_drive": "4WD",
        "car_type":"pickup"
    }
    inference.run([input1,input2])
    logger.info("Complete with one input")

if __name__ == "__main__":
    trainer.optimzer()
    test_one_input()
    test_many_input()