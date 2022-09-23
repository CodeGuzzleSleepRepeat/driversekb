import requests
import time
import datetime
from threading import Thread
import google_table as gt
import json



TOKEN = '5363932719:AAFPjX1oxBmSlSaDQisWiCvwLNTQYnwtO8w'		
#TOKEN = '5436969391:AAGZPyZn659hqnwYpL_3nVSCipTSDp9oTaA'	#test
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
company = {}

admins = set()
admin_id = set()

flag_start = {}
flag_date = {}
flag_date2 = {}
flag_date3 = {}
flag_date4 = {}
flag_date5 = {}
flag_date6 = {}
flag_task = {}
flag_driver = {}
flag_ready = {}
flag_ready2 = {}
flag_took = {}
flag_admin = {}
flag_num_cars = {}
flag_new_car = {}
flag_new_admin = {}
longing = {}

flag_time = 0
flag_sec = 0

num_of_orders = 0
taken_orders = 0


proxies = {
	'http' : 'http://proxy.server:3128'
}

def get_updates(offset=0):
	result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}', proxies=proxies).json()
	return result['result']

def send_message(chat_id, text):
	return requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={chat_id}&text={text}', proxies=proxies)

def reply_markup(chat_id, text):
	reply_markup = { "keyboard": [['Изменить данные']], "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data, proxies=proxies)

def reply_ip_markup(chat_id, text):
	arr = []
	for car in company:
		if car != '':
			arr.append([car])
	reply_markup = { "keyboard": arr, "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data, proxies=proxies)

def reply_markup_cars(chat_id, text, ip):
	arr = []
	for car in company[ip][1:]:
		if car != '':
			arr.append([car])
	reply_markup = { "keyboard": arr, "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data, proxies=proxies)

def reply_markup2(chat_id, text):
	reply_markup = { "keyboard": [['Не согласен']], "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data, proxies=proxies)

def reply_admin_markup(chat_id, text):
	reply_markup = { "keyboard": [['Начать распределение'], ['Добавить админа'], ['Удалить админа'], ['Показать админов']], "resize_keyboard": True, "one_time_keyboard": False}
	data = {'chat_id': chat_id, 'text' : text, 'reply_markup': json.dumps(reply_markup)}
	return requests.post(f'{URL}{TOKEN}/sendMessage', data=data, proxies=proxies)

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

def inline_keyboard2(chat_id, text):
	reply_markup = {'inline_keyboard': [[{'text' : 'Да', 'callback_data' : 'Да'}, {'text' : 'Нет', 'callback_data' : 'Нет'}]]}
	data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
	return requests.get(f'{URL}{TOKEN}/sendMessage', data = data, proxies=proxies)



def check_time():
	global flag_sec
	try:
		flag_date[datetime.date.today().strftime("%d.%m.%y")]
	except:
		flag_date[datetime.date.today().strftime("%d.%m.%y")] = 0

	if datetime.datetime.now().hour == 16 and datetime.datetime.now().minute == 30 and flag_date[datetime.date.today().strftime("%d.%m.%y")] == 0:		
		flag_date[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car)
		except:
			ii = 0
		for driver in drivers:
			flag_ready[driver] = 1

			for car in company:
				if company[car][0] == driver:
					flag_driver[driver] = 1
					reply_markup_cars(driver, 'Готовы ли вы работать завтра утром? Если да - выберите, пожалуйста, номер машины', car)
					break
			else:
				reply_ip_markup(driver, 'Готовы ли вы работать завтра утром? Если да - выберите ИП')

		active_drivers.clear()

	if datetime.datetime.now().hour == 0 and datetime.datetime.now().minute == 0:
		flag_sec = 0
		flag_date[datetime.date.today().strftime("%d.%m.%y")] = 0
		for driver in drivers:
			flag_ready[driver] = 0

def check_time2():
	try:
		flag_date2[datetime.date.today().strftime("%d.%m.%y")]
	except:
		flag_date2[datetime.date.today().strftime("%d.%m.%y")] = 0

	if datetime.datetime.now().hour == 10 and datetime.datetime.now().minute == 00 and flag_date2[datetime.date.today().strftime("%d.%m.%y")] == 0:		
		flag_date2[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car)
		except:
			ii = 0
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

def check_time3():
	try:
		flag_date3[datetime.date.today().strftime("%d.%m.%y")]
	except:
		flag_date3[datetime.date.today().strftime("%d.%m.%y")] = 0
	if datetime.datetime.now().hour == 12 and datetime.datetime.now().minute == 0 and flag_date3[datetime.date.today().strftime("%d.%m.%y")] == 0:		
		flag_date3[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car)
		except:
			ii = 0
		for driver in drivers:
			flag_ready[driver] = 1

			for car in company:
				if company[car][0] == driver:
					flag_driver[driver] = 1
					reply_markup_cars(driver, 'Готовы ли вы работать завтра утром? Если да - выберите, пожалуйста, номер машины', car)
					break
			else:
				reply_ip_markup(driver, 'Готовы ли вы работать сегодня после обеда? Если да - выберите ИП')

		active_drivers.clear()
	if datetime.datetime.now().hour == 0 and datetime.datetime.now().minute == 0:
		flag_date3[datetime.date.today().strftime("%d.%m.%y")] = 0
		for driver in drivers:
			flag_ready[driver] = 0

def check_time4():
	try:
		flag_date4[datetime.date.today().strftime("%d.%m.%y")]
	except:
		flag_date4[datetime.date.today().strftime("%d.%m.%y")] = 0
	if datetime.datetime.now().hour == 14 and datetime.datetime.now().minute == 0 and flag_date4[datetime.date.today().strftime("%d.%m.%y")] == 0:		
		flag_date4[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car)
		except:
			ii = 0
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
		flag_date4[datetime.date.today().strftime("%d.%m.%y")] = 0
		for driver in drivers:
			flag_ready[driver] = 0

def check_time5():
	try:
		flag_date5[datetime.date.today().strftime("%d.%m.%y")]
	except:
		flag_date5[datetime.date.today().strftime("%d.%m.%y")] = 0
	if datetime.datetime.now().hour == 15 and datetime.datetime.now().minute == 0 and flag_date5[datetime.date.today().strftime("%d.%m.%y")] == 0:		
		flag_date5[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car)
		except:
			ii = 0
		for driver in drivers:
			flag_ready[driver] = 1

			for car in company:
				if company[car][0] == driver:
					flag_driver[driver] = 1
					reply_markup_cars(driver, 'Готовы ли вы работать завтра утром? Если да - выберите, пожалуйста, номер машины', car)
					break
			else:
				reply_ip_markup(driver, 'Готовы ли вы работать сегодня после обеда? Если да - выберите ИП')

		active_drivers.clear()
	if datetime.datetime.now().hour == 0 and datetime.datetime.now().minute == 0:
		flag_date5[datetime.date.today().strftime("%d.%m.%y")] = 0
		for driver in drivers:
			flag_ready[driver] = 0

def check_time6():
	try:
		flag_date6[datetime.date.today().strftime("%d.%m.%y")]
	except:
		flag_date6[datetime.date.today().strftime("%d.%m.%y")] = 0
	if datetime.datetime.now().hour == 16 and datetime.datetime.now().minute == 0 and flag_date6[datetime.date.today().strftime("%d.%m.%y")] == 0:		
		flag_date3[datetime.date.today().strftime("%d.%m.%y")] = 1
		try:
			gt.del_driver_from_table(data_car)
		except:
			ii = 0
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
		flag_date6[datetime.date.today().strftime("%d.%m.%y")] = 0
		for driver in drivers:
			flag_ready[driver] = 0

def check_driver_time():
	for driver in active_drivers:
		try:
			now = datetime.datetime.now()
			if flag_task[driver] == 1 and (now - cur_time[driver]).total_seconds() > 36:
				cur_time[driver] = now
				try:
					trip = find_trip(driver.split('_')[0])
					if trip == -1:
						flag_task[driver] = 0
						continue
					#reject_driver(int(driver.split('_')[0]), trip, 'Вы не согласились на заказ за час - он предложен другому исполнителю')

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
	try:
		changes_new, i = gt.parse_changes()
	except:
		return
	length = len(changes)
	length2 = len(changes_new)
	for i in range(min(length, length2)):
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
				try:
					if active_drivers[str(chat_id) + '_' + prior_table[data[j][0]][3].split('_')[1]][3] >= 0:
						gt.clear_data(int(prior_table[data[j][0]][3][len(prior_table[data[j][0]][3].split('_')[0]) - 2:].split('_')[0]), prior_table, active_drivers[str(chat_id) + '_' + prior_table[data[j][0]][3].split('_')[1]], data_car, data_trip, trips)
				except:
					print('Trouble with clearing data in table')
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
	if text != '':
		send_message(chat_id, text)
	try:
		prior_table[prior] = prior_table[prior][:3] + prior_table[prior][4:]	
		request_driver(prior, chat_id)
	except:
		return

def form_mes(data, prior):
	llll = len(prior)
	num_of_nums = 0
	for i in range(llll):
		try:
			int(prior[llll - i - 1])
			num_of_nums += 1
		except:
			break
		if prior.find('ЕКБ склад') == 0:
			num_of_nums -= 1
	return 'Маршрут: ' + str(prior)[:len(prior) - num_of_nums] + '\nОбъем: ' + str(data[0]) + '\nВремя: ' + str(data[1]) + '\nВорота: ' + str(data[2])

def request_driver(prior, chat_id):
	global num_of_orders

	mes = form_mes(prior_table[prior], prior)



	try:
		driver = prior_table[prior][3]
	except:
		print(prior)
		no_drivers_alert(prior)
		return

	try:
		flag_task[prior_table[prior][3]] = 1
	except:
		kk = 0

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
	global admin_id

	if str(message).find('callback_query') > -1:
		chat_id = message['callback_query']['message']['chat']['id']
		ddd = message['callback_query']['data']
		if str(message['callback_query']['data']).find('Согласен') > -1:
			ddd = longing[ddd[8:].split('_')[0]] + '_' + ddd.split('_')[1]
			flag_took[str(chat_id) + '_' + ddd.split('_')[1]] = 1 

			try:
				if prior_table[ddd.split('_')[0][8:]][3].split('_')[0] != str(chat_id):
					send_message(chat_id, 'Этот заказ уже передан другому исполнителю')
					return
			except:
				kk = 0

			

			send_message(chat_id, 'Вы назначены на заказ')			
			send_message(chat_id, 'В случае, если потребуется отказаться от заказа - нажмите Не согласен')
			llll = len(ddd.split('_')[0])
			num_of_nums = 0
			for i in range(llll):
				try:
					int(ddd[llll - i - 1])
					num_of_nums += 1
				except:
					break
			if ddd.find('ЕКБ склад') == 0:
				num_of_nums -= 1
			gt.input_data(int(ddd[llll - num_of_nums:].split('_')[0]), prior_table, active_drivers[str(chat_id) + '_' + ddd.split('_')[1]], data_car, data_trip, trips)
			taken_orders += 1

			flag_task[str(chat_id) + '_' + ddd.split('_')[1]] = 0
			if taken_orders == num_of_orders:
				pathetic_news()
			return 
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

		if message['callback_query']['data'] == 'Да':
			flag_driver[chat_id] = 0
			#flag_ready[chat_id] = 1
			for car in company:
				if company[car][0] == chat_id:
					cur_company = car
			reply_markup_cars(chat_id, 'Выберите номер машины', cur_company)
			flag_driver[chat_id] = 1
			return
		if message['callback_query']['data'] == 'Нет':
			send_message(chat_id, 'Вы закончили ввод машин')
			return


	try:
		chat_id = message['message']['chat']['id']
		if chat_id == group_id:
			return
	except:
		return


	try:
		if set([message['message']['chat']['username']]).issubset(admins) and flag_new_admin[chat_id] == 0:		
			admin_id.add(chat_id)
			lll = length(drivers)
			for i in range(lll):
				if str(drivers[i]) == str(chat_id):
					del drivers[i]	
					break
			print('New admin')
			reply_admin_markup(chat_id, 'Вас назначили админом')
			flag_new_admin[chat_id] = 1
	except:
		jj = 0

	'''
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
	'''

	if not set([str(chat_id) + '_' + str(flag_num_cars[chat_id])]).issubset(active_drivers) and flag_ready[chat_id] == 1:
		if flag_driver[chat_id] == 0 and set([message['message']['text']]).issubset(company):
			cur_driver[chat_id] = ['', message['message']['text'], '', -1]
			try:
				company[message['message']['text']][0] = chat_id
			except:
				send_message(chat_id, 'Такого ИП нет в базе, проверьте правильность введенных данных')
				return
			#cur_driver[chat_id].append(message['message']['text'])
			print(flag_driver[chat_id], message['message']['text'])
			reply_markup_cars(chat_id, 'Выберите машину', message['message']['text'])
			flag_driver[chat_id] = 1
		elif flag_driver[chat_id] == 1:
			cur_driver[chat_id][0] = message['message']['text']
			flag_driver[chat_id] = 2
			send_message(chat_id, 'Введите ФИО водителя')
		else:
			cur_driver[chat_id][2] = message['message']['text']
			active_drivers[str(chat_id) + '_' + str(flag_num_cars[chat_id])] = ['', '', '', -1]
			for i in range(3):
				active_drivers[str(chat_id) + '_' + str(flag_num_cars[chat_id])][i] = cur_driver[chat_id][i]
			flag_took[str(chat_id) + '_' + str(flag_num_cars[chat_id])] = 0
			flag_ready[chat_id] = 0

			send_message(chat_id, 'Готово! Вы в списке водителей на завтрашний день')
			inline_keyboard2(chat_id, 'Хотите добавить еще одну машину?')
			flag_num_cars[chat_id] += 1
			try:
				gt.km[cur_driver[chat_id][0]][0]
			except:
				gt.km[cur_driver[chat_id][0]] = [0]
				gt.prev_km[cur_driver[chat_id][0]] = 0

			if gt.add_driver_to_table(cur_driver[chat_id][0], prior_table, data_car) == -1:
				send_message(chat_id, 'Машины с таким номером нет в списке исполнителей и она не может быть назначена на заказ. Пожалуйста, проверьте правильность данных и, если все верно, свяжитесь с заказчиком')
		return

		


	if message['message']['text'] == 'Начать распределение' and set([chat_id]).issubset(admin_id):
		print(active_drivers)
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


	if message['message']['text'] == 'Добавить админа' and set([chat_id]).issubset(admin_id):
		flag_admin[chat_id] = 1
		send_message(chat_id, 'Введите ник')
		return

	if flag_admin[chat_id] == 1:
		flag_admin[chat_id] = 0
		if message['message']['text'][0] != '@':
			send_message(chat_id, 'Неправильный ник')
			return
		admins.add(message['message']['text'][1:])
		send_message(chat_id, 'Админ успешно добавлен')
		return

	if message['message']['text'] == 'Удалить админа' and set([chat_id]).issubset(admin_id):
		flag_admin[chat_id] = -1
		send_message(chat_id, 'Введите ник')
		return

	if flag_admin[chat_id] == -1:
		flag_admin[chat_id] = 0
		if message['message']['text'][0] != '@':
			send_message(chat_id, 'Неправильный ник')
		admins.discard(message['message']['text'][1:])
		send_message(chat_id, 'Админ успешно удален')
		for driver in drivers:
			try:
				if message['message']['chat']['username'] == message['message']['text'][1:]:
					reply_markup_cars(chat_id, 'Вас удалили из админов')
			except:
				continue
		return

	if message['message']['text'] == 'Показать админов' and set([chat_id]).issubset(admin_id):
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


def prepare_cars():
	global data_car

	i = 0
	for line in data_car:
		i += 1
		if line[1] == '':
			data_car = data_car[:i]
			return
		tmp = line[1]
		if line[1][len(line[1]) - 1] == ' ':
			tmp = line[1][:len(line[1]) - 1]
		try:
			company[tmp].append(line[0])
		except:
			company[tmp] = [-1, line[0]]


def checking():
	global update_time

	check_time()
	check_time2()
	#check_time3()
	#check_time4()
	#check_time5()
	#check_time6()
	check_driver_time()

def main():
	global admin_id
	global data_trip
	global data_car
	global flag_sec


	admins.add('fcknmaggot')
	admins.add('as_mironov')
	admins.add('Logist92')
	admins.add('Antibi96')

	f = True
	flag_date[datetime.date.today().strftime("%d.%m.%y")] = 0
	flag_date2[datetime.date.today().strftime("%d.%m.%y")] = 0

	flag_date3[datetime.date.today().strftime("%d.%m.%y")] = 0
	flag_date4[datetime.date.today().strftime("%d.%m.%y")] = 0
	flag_date5[datetime.date.today().strftime("%d.%m.%y")] = 0

	flag_date6[datetime.date.today().strftime("%d.%m.%y")] = 0

	data_trip, data_car = gt.parse_secondary()
	prepare_cars()
	print(datetime.datetime.now())
	
	send_message(group_id, 'Бот запущен')

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
			if (datetime.datetime.now() - update_time).total_seconds() > 180:
				thread_update = Thread(target = check_updates, args = [])
				thread_update.start()
			if (datetime.datetime.now() - update_time).total_seconds() > 1800:
				data_trip, data_car = gt.parse_secondary()
				prepare_cars()
		except:
			k = 0

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
						flag_driver[message['message']['chat']['id']] = 0
						flag_ready[message['message']['chat']['id']] = 0
						flag_admin[message['message']['chat']['id']] = 0
						flag_num_cars[message['message']['chat']['id']] = 0
						flag_new_car[message['message']['chat']['id']] = 0
						flag_new_admin[message['message']['chat']['id']] = 0

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
							k = 0

				try:
					thread = Thread(target = check_message, args = [message])
					thread.start()
				except:
					continue

		time.sleep(0.1)


main()












































