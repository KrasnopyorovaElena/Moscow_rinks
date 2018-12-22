import pandas as pd, openpyxl
import re
import requests
import Helper
from bs4 import BeautifulSoup


# Ссылка на сайт
home_url = "https://kudago.com"

# Ссылка на статью про катки в парках Москвы
rinks_list_url = home_url + "/msk/list/ledovye-katki-v-parkah-moskvy"

# Вывод сообщения для пользователя
print("Привет! У меня есть информация про катки в парках Москвы.\n"
      "Вы можете ввести номер дня недели (1 - это понедельник ... 7 - это воскресенье), а я подскажу, какие катки работают в этот день :)\n"
      "Или введите 0, чтобы получить информацию по всем каткам\n\nВведите число: ")

# Проверка на корректность введеных данных
correct_data = False
while not correct_data:
    # Считывание введенных пользователем данных
    weekday = input()
    if re.search(r'^[0-7]$', weekday):
        correct_data = True
    #     Если введено некорректное значение, то выводим ошибку
    else:
        print("Введены некорректные данные. Введите число от 0 до 7. ")


# Всего лишь информационное сообщение
print("Идет обработка запроса...")

page = requests.get(rinks_list_url)

# Получаем html-страницу
soup = BeautifulSoup(page.text, 'lxml')

# Получаем все ссылки на катки в парках Москвы из статьи
# Со страницы вытягиваются все блоки статей
rinks_items = []
for item in soup.find_all('article', {'class':'post-list-item'}):
    rinks_items.append(item.attrs['id'])

# Получаем информацию из каждой статьи
rinks_info = []

for item in rinks_items:
    # Получаем ссылку на статью данного блока
    link = soup.find('article', {'class': 'post-list-item', 'id': item}).find('a',{'class': 'post-list-item-title-link'}).attrs['href']
    # Получаем информацию о стоимости на статью данного блока
    for i in soup.find('article', {'class': 'post-list-item', 'id':item}).find_all('p'):
        if i.getText() is not None:
            if 'стоимость' in i.getText().lower():
                rink_ticket_cost = i.getText()
                break

    # Получаем дополниельную информацию из каждой статьи
    info = Helper.GetInfo(home_url + link, rink_ticket_cost)

    if info is not None:
        # Если пользователь ввел 0 , то возвращаем всю информацию о катках
        if int(weekday) == 0:
            rinks_info.append(info)
        #     Если пользователь ввел число !=0 , то ищем катки , которые работают в определенный день
        else:
            if info[6].get(int(weekday)) is not None:
                rinks_info.append(info)


df = pd.DataFrame(rinks_info)
df.columns = ['url', 'title', 'description', 'address', 'phone', 'schedule', 'normalized_schedule', 'cost']
# Выгружаем ответ в xlsx файл
df.to_excel('rinks_info.xlsx')
df_for_view = df[['title','address','cost']]
# Выводим название катка, адрес и инфо о стоимости на экран
print(df_for_view)

