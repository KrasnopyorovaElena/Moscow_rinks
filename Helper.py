import re
import requests
from bs4 import BeautifulSoup


def GetNumberOFWeekDay(weekday):
    """
    :param weekday: сокращенное название дня недели на кириллице
    :return: номер дня недели
    """
    return {
        'пн': 1,
        'вт': 2,
        'ср': 3,
        'чт': 4,
        'пт': 5,
        'сб': 6,
        'вс': 7,
    }[weekday]


def GetNormalizedSchedule(schedule):
    """
    :param schedule: расписание в виде листа строк
    :return: словарь ключ-значение , где ключ - это номер дня недели, а значение - время работы катка
    """
    # Создаем пустой словарь
    schedule_dict = dict()

    # Если расписание не пустое, то идем на его обработку
    if schedule is not None:
        for item in schedule:
            # Приводим строку к нижнему регистру (чтобы искать по вхождением слов было легче)
            # Если встретилось слова "ежедневно", то всем дням неделям проставляем время
            if "ежедневно" in str(item).lower().replace(' ', ''):
                for i in range(1, 8):
                    schedule_dict.update({i: item.replace("ежедневно", '')})
                break

            # С помощью регулярного выращения находим и обрабатываем подстроку типа "пн-пт"
            work_period = re.findall(r'[а-яА-Я]+–[а-яА-Я]+', item)

            # Если подстрока типа "пн-пт" найдена, то заполняем период графиком работы
            if work_period.__len__() != 0:
                days_in_period = re.findall(r'[а-яА-Я]+', work_period[0])
                for i in range(GetNumberOFWeekDay(days_in_period[0]), GetNumberOFWeekDay(days_in_period[1]) + 1):
                    schedule_dict.update({i: item.replace(work_period[0], '')})
            # Если подстрока типа "пн-пт" НЕ найдена, то ищем отдельне значения дней недели и проставляем для них график
            else:
                work_days = re.findall(r'[а-яА-Я]+', item.replace(',', ' ').replace('.', ' '))
                for work_day in work_days:
                    schedule_dict.update({GetNumberOFWeekDay(work_day): re.sub(r'[а-яА-Я]+', '', item).replace(',','').replace('.', '').strip()})

    return schedule_dict


def GetInfo(url, additional_info):
    """
    :param url: ссылка на статью
    :param additional_info: дополнительная информация
    :return: кортеж с url статьи, названием, описанием, адресом, телефоном и расписанием работы
    """
    page = requests.get(url)

    # Получаем html-страницу
    soup = BeautifulSoup(page.text, 'lxml')

    title = soup.find('h1', {'class': 'post-big-title'}).getText()
    description = soup.find('div', {'id': 'item-description'}).find('p').getText()
    address = soup.find('div', {'class': 'post-big-address'})
    if address is not None:
        address = address.getText().replace('\n', '').replace('  ', '')

    # Считаем, что если на данной странице нет адреса, то эта статья не о конкретном ледовом катке
    # в таком случае вовзращаем объект None
    if address is '' or address is None: return None

    phone = soup.find('div', {'class': 'post-big-phone'})
    if phone is not None:
        phone = soup.find('div', {'class': 'post-big-phone'}).attrs['data-post-phone']

    schedule = []
    for s in soup.findAll('div', {'class': 'schedule-item'}):
        schedule_title = s.parent.find('div', {'class', 'post-big-detail-title'}).find('big').getText()
        if schedule_title is not None and schedule_title.lower() == 'расписание работы':
            schedule.append(s.getText())

    normalized_schedule = GetNormalizedSchedule(schedule)

    return url, title, description, address, phone, schedule, normalized_schedule, additional_info
