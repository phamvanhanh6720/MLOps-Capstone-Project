import requests
import json
import streamlit as st

st.title("The price of used cars App")
st.sidebar.title("Features")

year = st.sidebar.text_input('Year of Manufacture', 2020)
location = ''

branch_list = ['Acura', 'Audi', 'BMW', 'Chevrolet', 'Daewoo', 'Ford', 'Honda', 'Hyundai', 'Isuzu', 'Kia', 'LandRover', 'Lexus', 'MG', 'Mazda', 'Mercedes Benz', 'Mini', 'Mitsubishi', 'Nissan', 'Peugeot', 'Porsche', 'Subaru', 'Suzuki', 'Toyota', 'VinFast', 'Volkswagen', 'Volvo']
branch = st.sidebar.selectbox(label='Branch', options=branch_list, index=6)

if branch == 'Honda':
    model_list = ['Accord', 'Brio', 'CRV', 'City', 'Civic', 'HRV', 'Jazz', 'Odyssey', 'Pilot']
    model = st.sidebar.selectbox(label='Model', options=model_list, index=2)
else:
    model = st.text_input('Model', 'CRV')

km_driven = st.sidebar.slider(label='Km Driven', value=10000, min_value=0, max_value=200000)
num_seats = st.sidebar.slider(label='#Seats', value=5, min_value=2, max_value=16)
engine_capacity = st.sidebar.slider(label='Engine capacity', value=1.5, min_value=0.5, max_value=6.0, step=0.1)

origin_list = ['domestic', 'imported']
origin = st.sidebar.selectbox(label='Origin', options=origin_list, index=0)

internal_color_list = ['Bạc', 'Cam', 'Cát', 'Ghi', 'Hồng', 'Kem', 'Màu khác', 'Nhiều màu', 'Nâu', 'Trắng', 'Tím', 'Vàng', 'Xanh', 'Xám', 'Đen', 'Đỏ', 'Đồng']
external_color_list = ['Bạc', 'Cam', 'Cát', 'Ghi', 'Hồng', 'Kem', 'Màu khác', 'Nhiều màu', 'Nâu', 'Trắng', 'Tím', 'Vàng', 'Xanh', 'Xám', 'Đen', 'Đỏ', 'Đồng']

internal_color = st.sidebar.selectbox(label='Internal Color', options=internal_color_list, index=14)
external_color = st.sidebar.selectbox(label='External Color', options=external_color_list, index=9)

gear_box_list = ['Số hỗn hợp', 'automatic', 'manual']
gear_box = st.sidebar.selectbox(label='Gear box', options=gear_box_list)

wheel_drive_list = ['4WD', 'AWD', 'FWD', 'RWD']
wheel_drive = st.sidebar.selectbox(label='Wheel Drive', options=wheel_drive_list, index=3)

feul_list = ['diesel', 'electric', 'gasoline', 'hybrid']
feul = st.sidebar.selectbox(label='Fuels', options=feul_list, index=2)

car_type_list = ['convertible', 'coupe', 'crossover', 'hatchback', 'pickup', 'sedan', 'suv', 'truck', 'van', 'wagon']
car_type = st.sidebar.selectbox(label='Car Type', options=car_type_list, index=6)

is_predict = st.button('Click here to predict')

if is_predict:
    predict_api = 'http://phamvanhanh.ddns.net:8080/api/predict'
    data = {'year': year,
            'location': '',
            'branch': branch,
            'model': model,
            'origin': origin,
            'km_driven': km_driven,
            'external_color': external_color,
            'internal_color': internal_color,
            'num_seats': num_seats,
            'fuels': feul,
            'engine_capacity': engine_capacity,
            'gearbox': gear_box,
            'wheel_drive': wheel_drive,
            'car_type': car_type}

    response = requests.post(url=predict_api, data=json.dumps(data))
    content = json.loads(response.content)
    results = content['price']

    st.text("Price: {:.2f} M VND".format(results))
    st.image('./stores/sample.jpeg')