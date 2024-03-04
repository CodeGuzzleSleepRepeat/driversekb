import requests
import time
import datetime
from threading import Thread
import google_table as gt
import json



TOKEN = '5363932719:AAFPjX1oxBmSlSaDQisWiCvwLNTQYnwtO8w'
URL = 'https://api.telegram.org/bot'


group_id = -757291925
update_time = datetime.datetime.now()
drivers = []
trips = []
changes = []
active_drivers = {}
active_drivers2 = {}
prior_table = {}
prior_table2 = {}
cur_driver = {}
cur_time = {}
company = []
chat_cars = {}

admins = set()
admin_id = set()
new_admins = set()
ready_cars = set()

flag_start = {}
flag_date = {}
flag_date2 = {}
flag_date3 = {}
flag_task = {}
flag_driver = {}
flag_table = {}
flag_ready = {}
flag_ready2 = {}
flag_took = {}
flag_admin = {}
flag_num_cars = {}
flag_new_car = {}
flag_new_distr = {}
longing = {}

flag_time = 0

num_of_orders = 0
taken_orders = 0


def get_updates(offset=0):
	result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
	return result['result']

def send_message(chat_id, text):
	return requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={chat_id}&text={text}')

def reply_markup(chat_id, text):
	reply_markup = { "keyboard": [['Изменить данные']], "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data)

def reply_ip_markup(chat_id, text, table):
	arr = []
	for car in company[table]:
		if car != '':
			arr.append([car])
	reply_markup = { "keyboard": arr, "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data)

def reply_markup_cars(chat_id, text, ip, table):
	arr = []
	for car in company[table][ip][1:]:
		if car != '':
			arr.append([car])
	arr.append(['Сменить ИП'])
	reply_markup = { "keyboard": arr, "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data)

def reply_markup2(chat_id, text):
	reply_markup = { "keyboard": [['Не согласен']], "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data)

def reply_markup_new_ip(chat_id, text):
	arr = []
	for car in chat_cars:
		if chat_cars[car] == chat_id:
			arr.append([car])
	reply_markup = { "keyboard": arr, "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def reply_admin_markup(chat_id, text):
	reply_markup = { "keyboard": [['Начать опрос водителей ЕКБ'], ['Начать опрос водителей ЧБ'], ['Начать опрос водителей Пермь'], ['Отправить заявки ЕКБ'],
	 ['Отправить заявки ЧБ'], ['Отправить заявки Пермь'], ['Добавить логиста'], ['Показать логистов']], "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data)

def inline_keyboard(chat_id, text, id_trip):
	id_num = chat_id.split('_')[1]
	chat_id = chat_id.split('_')[0]
	id_trip2 = id_trip
	if len(id_trip) > 20:
		id_trip2 = id_trip[:20]
	longing[id_trip2] = id_trip
	reply_markup = {'inline_keyboard': [[{'text' : 'Согласен', 'callback_data' : 'Согласен' + id_trip2 + '_' + id_num}, {'text' : 'Не согласен', 'callback_data' : 'Не согласен' + id_trip2 + '_' + id_num}]]}
	data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
	return requests.get(f'{URL}{TOKEN}/sendMessage', data = data)

def in_key(chat_id, text, id_trip, id_table):
	reply_markup = {'inline_keyboard': [[{'text' : 'Согласен', 'callback_data' : 'Согласен ' + id_trip + ' ' + str(id_table)}, {'text' : 'Не согласен', 
		'callback_data' : 'Не согласен ' + id_trip + ' ' + str(id_table)}]]}
	data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
	return requests.get(f'{URL}{TOKEN}/sendMessage', data = data)

def inline_keyboard2(chat_id, text, table):
	reply_markup = {'inline_keyboard': [[{'text' : 'Да', 'callback_data' : 'Да ' + str(table)}, {'text' : 'Нет', 'callback_data' : 'Нет ' + str(table)}]]}
	data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
	return requests.get(f'{URL}{TOKEN}/sendMessage', data = data)

def inline_keyboard3(chat_id, text, table):
	reply_markup = {'inline_keyboard': [[{'text' : 'Новое ИП', 'callback_data' : 'Новое ИП ' + str(table)}]]}
	data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
	return requests.get(f'{URL}{TOKEN}/sendMessage', data = data)


def check_drivers(table):
	for driver in drivers:
		flag_driver[driver] = 0
	if True:	
		#flag_date[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car[table], table)
		except:
			pass
		for driver in drivers:
			flag_ready[driver] = 1
			for car in company[table]:
				if company[table][car][0] == driver:
					flag_driver[driver] = 1
					
					reply_markup_cars(driver, 'Готовы ли вы взять заказ, ' + car + '? Если да - выберите, пожалуйста, номер машины', car, table)
					break
			else:
				if flag_table[driver] == 0:
					if table == 0:
						loc = 'ЕКБ'
					elif table == 1:
						loc = 'ЧБ'
					else:
						loc = 'Пермь'
					reply_ip_markup(driver, 'Готовы ли вы работать в городе ' + loc + '? Если да - выберите ИП', table)

		active_drivers.clear()
	#if datetime.datetime.now().hour == 0 and datetime.datetime.now().minute == 0:
	#	flag_date[datetime.date.today().strftime("%d.%m.%y")] = 0
	#	for driver in drivers:
	#		flag_ready[driver] = 0

def check_time():
	if datetime.datetime.now().hour == 14 and datetime.datetime.now().minute == 0 and flag_date2[datetime.date.today().strftime("%d.%m.%y")] == 0:		
		flag_date2[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car)
		except:
			pass
		for driver in drivers:
			flag_ready[driver] = 1

			for car in company:
				if company[car][0] == driver:
					flag_driver[driver] = 1
					reply_markup_cars(driver, 'Готовы ли вы работать сегодня после обеда? Если да - выберите, пожалуйста, номер машины', car)
					break
			else:
				reply_ip_markup(driver, 'Готовы ли вы работать сегодня после обеда? Если да - выберите ИП')

		active_drivers.clear()
	if datetime.datetime.now().hour == 0 and datetime.datetime.now().minute == 0:
		flag_date2[datetime.date.today().strftime("%d.%m.%y")] = 0
		for driver in drivers:
			flag_ready[driver] = 0

def check_driver_time():
	for driver in active_drivers:
		try:
			now = datetime.datetime.now()
			if flag_task[driver] == 1 and (now - cur_time[driver]).total_seconds() > 3600:
				cur_time[driver] = now
				try:
					trip = find_trip(driver.split('_')[0])
					if trip == -1:
						flag_task[driver] = 0
						continue
					reject_driver(int(driver.split('_')[0]), trip, 'Вы не согласились на заказ за час - он предложен другому исполнителю')

				except:
					print('Something wrong with time rejection')
		except:
			return

def check_updates():
	global update_time
	global changes

	update_time = datetime.datetime.now()
	to_del = []
	print('Parsing changes')
	changes_new, i = gt.parse_changes()
	length = len(changes)
	length2 = len(changes_new)
	for i in range(length):
		if changes_new[i][1:] == changes[i][1:] or (changes_new[1] == '' and changes_new[2] == '' and changes_new[3] == ''):
			to_del.append(i)			
		else:
			changes[i] = changes_new[i]

	for i in range(length, length2):
		if changes_new[i][1] == '' and changes_new[i][2] == '' and changes_new[i][3] == '':
			to_del.append(i)
			changes.append(changes_new[i])
		else:
			changes.append([])

	if len(to_del) > 0:
		for t in to_del[::-1]:
			del changes_new[t]
	if i == -1:
		return

	send_changes(changes_new)

def check_car_new_vol(line, num):
	ind_car = gt.find_car_ind(active_drivers[prior_table[line[0]][3]][0], data_car)
	try:
		'''
		if data_car[ind_car][4] == 'v' and int(data[1]) > 10:		#Грузоподъемность
			return False
		if data_car[ind_car][5] == 'v' and int(data[1]) > 20:
			return False
		if data_car[ind_car][6] == 'v' and int(data[1]) > 25:
			return False
		if data_car[ind_car][7] == 'v' and int(data[1]) > 30:
			return False
		if data_car[ind_car][8] == 'v' and int(data[1]) > 35:
			return False
		if data_car[ind_car][9] == 'v' and int(data[1]) > 40:
			return False
		if data_car[ind_car][10] == 'v' and int(data[1]) > 45:
			return False
		if data_car[ind_car][11] == 'v' and int(data[1]) > 50:
			return False
		'''
		try:
			if line[1][len(line[1]) - 1] == '+' or line[1][len(line[1]) - 1] == '-':
				line[1] = line[1][:len(line[1]) - 1]
			if int(data_car[ind_car][2]) < int(line[1]):
				return False
		except:
			return True
	except:
		return True
	return True

def send_changes(data):
	length = len(data)
	for j in range(length):
		num = str(j)
		if j < 10:
			num = '0' + num
		try:
			for i in range(3):
				if data[j][i + 1] != '':
					prior_table[data[j][0]][i] = data[j][i + 1]
		except:
			print('Bad sending changes')


		try:
			if not check_car_new_vol(data[j], num):
				reject_driver(prior_table[data[j][0]][3].split('_')[0], data[j][0], 'Объем груза изменен и больше не подходит вашей машине')
				return
		except:
			k = 0

		
		try:
			mes = form_mes(prior_table[data[j][0]], data[j][0] + num)
			send_message(prior_table[data[j][0]][3].split('_')[0], 'Детали поездки изменились:\n' + mes)
		except:
			return


def find_trip(chat_id):
	for prior in prior_table:
		if len(prior_table[prior]) < 4:
			continue
		if prior_table[prior][3].split('_')[0] == chat_id:
			return prior
	return -1


def no_drivers_alert(trip_id):
	global group_id
	
	mes = form_mes(prior_table[trip_id], trip_id)
	try:
		send_message(group_id, mes + '\nНе закрыт!')
	except:
		return

def reject_driver(chat_id, prior, text):
	try:
		prior_table[prior] = prior_table[prior][:3] + prior_table[prior][4:]
		request_driver(prior, chat_id)
	except:
		cc = 0
		if text != '':
			send_message(chat_id, text)

def form_mes(data, prior):
	return 'Маршрут: ' + str(prior)[:len(prior) - 2] + '\nОбъем: ' + str(data[0]) + '\nВремя: ' + str(data[1]) + '\nВорота: ' + str(data[2])

def form_mes2(way, car, vol, time, gate):
	return 'Маршрут: ' + way + '\nМашина: ' + car + '\nОбъем: ' + str(vol) + '\nВремя: ' + str(time) + '\nВорота: ' + str(gate)

def request_driver(prior, chat_id):
	global num_of_orders

	mes = form_mes(prior_table[prior], prior)



	try:
		driver = prior_table[prior][3]
	except:
		no_drivers_alert(prior)
		return

	try:
		flag_task[prior_table[prior][3]] = 1
	except:
		jj = 0

	if gt.check_driver(active_drivers[driver][0], prior_table[prior], prior, data_car, data_trip):
		inline_keyboard(driver, mes, str(prior))
		num_of_orders += 1 
		cur_time[driver] = datetime.datetime.now()
	else:
		reject_driver(chat_id, prior, '')

def pathetic_news():
	for driver in active_drivers:
		for prior in prior_table:
			try:
				if prior_table[prior][3] == driver:	
					break
			except:
				continue
		else:
			send_message(driver.split('_')[0], 'К сожалению, заказов для машины ' + active_drivers[driver][0] + ' на сегодня больше не осталось (если только кто-то не откажется от уже принятого)')

def check_message(message):
	global trips
	global taken_orders
	global num_of_orders

	if str(message).find('callback_query') > -1:
		chat_id = message['callback_query']['message']['chat']['id']
		ddd = message['callback_query']['data']
		if str(message['callback_query']['data']).find('Новое ИП') > -1:
			table = message['callback_query']['data'].split(' ')[2]
			flag_driver[chat_id] = 0
			flag_ready[chat_id] = 1 
			reply_ip_markup(chat_id, 'Выберите ИП', int(table))
			return


		if str(message['callback_query']['data']).find('Согласен') > -1:
			args = message['callback_query']['data'].split(' ')
			gt.agree(args[1], int(args[2]))
			send_message(chat_id, 'Вы назначены на заказ')			
			send_message(chat_id, 'В случае, если потребуется отказаться от заказа - нажмите Не согласен')
			return
		'''
		if str(message['callback_query']['data']).find('Согласен') > -1:
			ddd = longing[ddd[8:].split('_')[0]] + '_' + ddd.split('_')[1]
			#if flag_took[str(chat_id) + '_' + ddd.split('_')[1]] == 1:
			#	send_message(chat_id, 'Вы уже согласились на другой заказ. Чтобы принять данный заказ - отмените прежний')
			#	return
			flag_took[str(chat_id) + '_' + ddd.split('_')[1]] = 1 

			try:
				if prior_table[ddd.split('_')[0][8:]][3].split('_')[0] != str(chat_id):
					send_message(chat_id, 'Этот заказ уже передан другому исполнителю')
					return
			except:
				j = 0

			#if active_drivers[str(chat_id) + '_' + ddd.split('_')[1]][3] == -1:
			#	active_drivers[str(chat_id) + '_' + ddd.split('_')[1]][3] = int(ddd[len(ddd.split('_')[0]) - 2:].split('_')[0])

			send_message(chat_id, 'Вы назначены на заказ')			
			send_message(chat_id, 'В случае, если потребуется отказаться от заказа - нажмите Не согласен')
			gt.input_data(int(ddd[len(ddd.split('_')[0]) - 2:].split('_')[0]), prior_table, active_drivers[str(chat_id) + '_' + ddd.split('_')[1]], data_car, data_trip, trips)
			taken_orders += 1
			if taken_orders == num_of_orders:
				pathetic_news()
			return 
		'''
		'''
		if str(message['callback_query']['data']).find('Не согласен') > -1:			
			taken_orders -= 1
			ddd = longing[ddd[11:].split('_')[0]] + '_' + ddd.split('_')[1]
			flag_took[str(chat_id) + '_' + ddd.split('_')[1]] = 0

			if active_drivers[str(chat_id) + '_' + ddd.split('_')[1]][3] >= 0:
				gt.clear_data(int(ddd[len(ddd.split('_')[0]) - 2:].split('_')[0]), prior_table, active_drivers[str(chat_id) + '_' + ddd.split('_')[1]], data_car, data_trip, trips)
			reject_driver(chat_id, ddd.split('_')[0], 'Вы отказались от заказа')
			active_drivers[str(chat_id) + '_' + ddd.split('_')[1]][3] = -1
			flag_task[str(chat_id) + '_' + ddd.split('_')[1]] = 0
			return
		'''
		if str(message['callback_query']['data']).find('Не согласен') > -1:
			args = message['callback_query']['data'].split(' ')
			gt.rejection(args[2], int(args[3]))
			send_message(chat_id, 'Вы отказались от заказа')
			return
		if str(message['callback_query']['data']).find('Да') != -1:
			flag_driver[chat_id] = 0
			flag_ready[chat_id] = 1
			table = int(message['callback_query']['data'].split(' ')[1])
			for car in company[table]:
				if company[table][car][0] == chat_id:
					cur_company = car
			reply_markup_cars(chat_id, 'Выберите номер машины', cur_company, table)
			flag_driver[chat_id] = 1
			return
		if str(message['callback_query']['data']).find('Нет') != -1:	
			table = message['callback_query']['data'].split(' ')[1]	
			send_message(chat_id, 'Вы закончили ввод машин')
			inline_keyboard3(chat_id, 'Нажмите Новое ИП, чтобы добавить еще одно ип для этого аккаунта', table)
			
			return


	chat_id = message['message']['chat']['id']
	if chat_id == group_id:
		return

	try:
		user = message['message']['chat']['username']
	except:
		user = ''

	if set([user]).issubset(new_admins):
		reply_admin_markup(chat_id, 'Вас назначили логистом')
		new_admins.remove(user)
		admin_id.add(chat_id)
		drivers.remove(chat_id)
		return

	if message['message']['text'] == 'Добавить машину':
		send_message(chat_id, 'Введите номер машины')
		flag_new_car[chat_id] = 1
		return
	if flag_new_car[chat_id] == 1:
		flag_new_car[chat_id] = 0
		for car in company:
			if company[car][0] == chat_id:
				cur_company = car
		if gt.input_new_car(message['message']['text'], cur_company, data_car) == -1:
			send_message(chat_id, 'Не удалось добавить машину, попробуйте позже')
			return
		data_car.append([message['message']['text'], '', cur_company, '', '', '','','','','','','','','','','','','','','','','','','',''])
		company[cur_company].append(message['message']['text'])
		reply_markup_cars(chat_id, 'Машина успешно добавлена', cur_company)

		return

	if message['message']['text'] == 'Сменить ИП':
		flag_driver[chat_id] = 0
		reply_markup_new_ip(chat_id, 'Выберите ИП')
		return

	if not set([str(chat_id) + '_' + str(flag_num_cars[chat_id])]).issubset(active_drivers) and flag_ready[chat_id] == 1:
		if flag_driver[chat_id] == 0:
			cur_driver[chat_id] = ['', message['message']['text'], '', -1]
			for i in range(3):
				try:
					company[i][message['message']['text']][0] = chat_id
					table = i
					break
				except:
					pass
			else:
				send_message(chat_id, 'Такого ИП нет в базе, проверьте правильность введенных данных')
				return
			#cur_driver[chat_id].append(message['message']['text'])
			ip = no_brackets(message['message']['text'])

			chat_cars[ip] = message['message']['chat']['id']
			reply_markup_cars(chat_id, 'Выберите машину', message['message']['text'], table)
			flag_driver[chat_id] = 1
		elif flag_driver[chat_id] == 1:
			cur_driver[chat_id][0] = message['message']['text']
			flag_driver[chat_id] = 2
			ready_cars.add(message['message']['text'])
			send_message(chat_id, 'Введите ФИО водителя')
		else:
			cur_driver[chat_id][2] = message['message']['text']
			#cur_driver[chat_id].append(-1)
			active_drivers[str(chat_id) + '_' + str(flag_num_cars[chat_id])] = ['', '', '', -1]
			for i in range(3):
				active_drivers[str(chat_id) + '_' + str(flag_num_cars[chat_id])][i] = cur_driver[chat_id][i]
			flag_took[str(chat_id) + '_' + str(flag_num_cars[chat_id])] = 0
			flag_ready[chat_id] = 0


			send_message(chat_id, 'Готово! Вы в списке водителей на завтрашний день')
			flag_table[chat_id] = 1
			table = get_table_num(chat_id)
			inline_keyboard2(chat_id, 'Хотите добавить еще одну машину?', table)
			flag_num_cars[chat_id] += 1
			try:
				gt.km[cur_driver[chat_id][0]][0]
			except:
				gt.km[cur_driver[chat_id][0]] = [0]
				gt.prev_km[cur_driver[chat_id][0]] = 0


			
			if table == -1:
				print('Getting table num problem')
				return
			

			if gt.add_driver_to_table(cur_driver[chat_id][0], prior_table, data_car[table], table) == -1:
				send_message(chat_id, 'Машины с таким номером нет в списке исполнителей и она не может быть назначена на заказ. Пожалуйста, проверьте правильность данных и, если все верно, свяжитесь с заказчиком')
		return

	if str(message['message']['text']).find('Начать опрос водителей') != -1 and set([chat_id]).issubset(admin_id):
		ready_cars.clear()
		loc = message['message']['text'].split(' ')[3] 
		table_num = -1
		if loc == 'ЕКБ':
			table_num = 0
		elif loc == 'ЧБ':
			table_num = 1
		elif loc == 'Пермь':
			table_num = 2
		else:
			send_message(message['message']['chat']['id'], 'Такой таблицы нет')
			return
		check_drivers(table_num)
		send_message(message['message']['chat']['id'], 'Запросы готовности отправлены водителям')
		
	if str(message['message']['text']).find('Отправить заявки') != -1 and set([chat_id]).issubset(admin_id):
		loc = message['message']['text'].split(' ')[2] 
		table_num = -1
		if loc == 'ЕКБ':
			table_num = 0
		elif loc == 'ЧБ':
			table_num = 1
		elif loc == 'Пермь':
			table_num = 2
		else:
			send_message(message['message']['chat']['id'], 'Такой таблицы нет')
			return

		data_distrib = []

		gt.parse_ready_distrib(data_distrib, table_num)
		for line in data_distrib:
			if line[2] == '':
				continue
			mes = form_mes2(line[0], line[1], line[3], line[4], line[5])
			try:
				chat = chat_cars[no_brackets(line[2])]
				if not set([line[1]]).issubset(ready_cars):
					1 / 0
			except:
				send_message(message['message']['chat']['id'], 'Вы назначили на заказ ' + line[0] + ' машину, не заявившуюся на опросе')
				continue
			hm = line[5].split(':')
			now = datetime.datetime.now()
			if now.hour <= int(hm[0]) or (now.hour == int(hm[0]) and now.minute < int(hm[1])):
				flag_new_distr[chat] = 1
				in_key(chat, mes, str(line[len(line) - 1]), table_num)

		for driver in active_drivers:
			chat_id = int(driver.split('_')[0])
			if flag_new_distr[chat_id] == 0:
				send_message(chat_id, 'Заказов для машины нет')
		send_message(message['message']['chat']['id'], 'Заявки отправлены')




	'''
	if message['message']['text'] == 'Начать распределение' and set([chat_id]).issubset(admin_id):
		taken_orders = 0
		num_of_orders = 0
		flag_admin[chat_id] = 0
		for i in range(50):
			num = str(i)
			if i < 10:
				num = '0' + num
			flag_took[str(chat_id) + '_' + num] = 0
		for driver in active_drivers:
			gt.orders[active_drivers[driver][0]] = 0
		trips, i = gt.parse_table()
		if i == -1:
			send_message(chat_id, 'Невозможно получить все данные из таблицы, попробуйте позже')
			return
		gt.find_priorities(trips, prior_table, active_drivers, data_car, data_trip)
		for driver in active_drivers:
			flag_task[driver] = 0
		for prior in prior_table:
			if not gt.taken[prior]:
				request_driver(prior, chat_id)
		send_message(chat_id, 'Маршруты распределены, ожидаем ответов от исполнителей')
		return
	'''
	

	if message['message']['text'] == 'Добавить логиста' and set([chat_id]).issubset(admin_id):
		flag_admin[chat_id] = 1
		send_message(chat_id, 'Введите ник')
		return

	if flag_admin[chat_id] == 1:
		flag_admin[chat_id] = 0
		if message['message']['text'][0] != '@':
			send_message(chat_id, 'Неправильный ник')
		admins.add(message['message']['text'][1:])
		new_admins.add(message['message']['text'][1:])
		send_message(chat_id, 'Логист успешно добавлен')
		return

	if message['message']['text'] == 'Показать логистов' and set([chat_id]).issubset(admin_id):
		flag_admin[chat_id] = 0
		for admin in admins:
			send_message(chat_id, admin)
		return

	if message['message']['text'] == 'Изменить данные':
		flag_ready[chat_id] = 1
		flag_driver[chat_id] = 0
		if flag_num_cars[chat_id] == 0:
			res = '0'
		else:
			res = str(flag_num_cars[chat_id] - 1)
		del active_drivers[str(chat_id) + '_' + res]
		send_message(chat_id, 'Пришлите, пожалуйста, номер машины')
		return


def get_table_num(chat_id):
	for i in range (3):
		for ip in company[i]:
			if company[i][ip][0] == chat_id:
				return i
	return -1


def no_brackets(text):
	try:
		ip = text.split('(')[1]
		ip = ip.split(')')[0]
	except:
		ip = text
	return ip

def prepare_cars():
	global data_car
	for i in range(3):
		company.append({})
	i = 0
	for j in range(3):
		for line in data_car[j]:
			i += 1
			if line[1] == '':
				data_car[j] = data_car[j][:i]
				return
			ip = no_brackets(line[1])
			try:
				company[j][ip].append(line[2])
			except:
				company[j][ip] = [-1, line[2]]


def checking():
	global update_time

	#check_time()
	#check_time2()
	#check_time3()
	check_driver_time()
	#update_time = check_updates(update_time)

def main():
	global admin_id
	global data_trip
	global data_car

	#gt.north = gt.get_north()

	admins.add('fcknmaggot')

	f = True
	flag_date[datetime.date.today().strftime("%d.%m.%y")] = 0
	flag_date2[datetime.date.today().strftime("%d.%m.%y")] = 0

	flag_date3[datetime.date.today().strftime("%d.%m.%y")] = 0


	data_trip, data_car = gt.parse_secondary()
	prepare_cars()
	print(datetime.datetime.now())

	while f: 
	    try:
	        update_id = get_updates()[-1]['update_id']
	        f = False
	    except:
	        time.sleep(1)


	while True:
		try:
			thread_check = Thread(target = checking, args = [])
			thread_check.start()
			#if (datetime.datetime.now() - update_time).total_seconds() > 180:
			#	thread_update = Thread(target = check_updates, args = [])
			#	thread_update.start()
		except:
			pass

		messages = get_updates(update_id)
		for message in messages:
			if update_id < message['update_id']:
				update_id = message['update_id']

				try:					
					if str(message).find('query') == -1:
						flag_start[message['message']['chat']['id']]					
				except:
					try:

						flag_start[message['message']['chat']['id']] = 1
						#flag_task[message['message']['chat']['id']] = 0
						flag_table[message['message']['chat']['id']] = 0
						flag_driver[message['message']['chat']['id']] = 0
						flag_ready[message['message']['chat']['id']] = 0
						flag_admin[message['message']['chat']['id']] = 0
						flag_num_cars[message['message']['chat']['id']] = 0
						flag_new_car[message['message']['chat']['id']] = 0
						flag_new_distr[message['message']['chat']['id']] = 0


						try:
							username = message['message']['chat']['username']
						except:
							username = ''
						if set([username]).issubset(admins):
							admin_id.add(message['message']['chat']['id'])
							reply_admin_markup(message['message']['chat']['id'], 'Добро пожаловать')
						elif message['message']['chat']['id'] != group_id:
							send_message(message['message']['chat']['id'], 'Добро пожаловать')
							drivers.append(message['message']['chat']['id'])
					except:
						pass

				try:
					thread = Thread(target = check_message, args = [message])
					thread.start()
				except:
					continue

		time.sleep(0.1)


main()


