import gspread
import datetime
import time



gc = gspread.service_account(filename='driversdistrib-ff44f21c020e.json')
sh = gc.open("DriversDistribTable")


data_car = []
data_trip = []

north = ''

km = {}
prev_km = {}
timing = {}
orders = {}
num_of_days = {}
taken = {}


def prev_order(str, prior):
	hm = str.split(':')
	now = datetime.datetime.now()
	if num_of_days[prior] > 0:
		return False
	if now.hour > int(hm[0]) or (now.hour == int(hm[0]) and now.minute > int(hm[1])):
		return True
	return False

def parse_table():
	counter = 0
	flag = 0
	while True:
		try:
			sh = gc.open("DriversDistribTable").get_worksheet(0)
			break
		except:
			if counter == 10:
				print('Something went wrong in parsing changes')
				return data, -1
			time.sleep(10)
			counter += 1
	data_changes = sh.get_all_values()[2:]
	res_data = []
	i = 0
	for line in data_changes:
		try:
			num = str(i)
			if i < 10:
				num = '0' + num

			num_of_days[num] = flag

			if line[0][2] == '.':
				flag += 1
			res_data.append([line[0], line[1], line[2], line[3], line[4], line[5]])
		except:
			continue
		i += 1
	print(i)
	return res_data, i

def parse_changes():
	counter = 0
	while True:
		try:
			sh = gc.open("DriversDistribTable").get_worksheet(0)
			break
		except:
			if counter == 10:
				print('Something went wrong in parsing changes')
				return data, -1
			time.sleep(10)
			counter += 1
	data_changes = sh.get_all_values()[2:]
	res_data = []
	i = 0
	for line in data_changes:
		try:
			#line[3][0]
			#if line[0].find('день') == len(line[0]) - 4:
				#num_of_days[line[0] + num] = 1
			num = str(i)
			if i < 10:
				num = '0' + num
			res_data.append([line[0] + num, line[7], line[8], line[9]])
		except:
			continue
		i += 1
	print(i)
	return res_data, i




def parse_secondary():
	sh = gc.open("DriversDistribTable").get_worksheet(3)
	data_trip = sh.get_all_values()
	sh = gc.open("DriversDistribTable").get_worksheet(4)
	data_car = sh.get_all_values()
	data_trip = data_trip[2:]
	length = len(data_trip)
	for i in range(length):
		num = str(i)
		if i < 10:
			num = '0' + str(i)
		data_trip[i][0] += num
	data_car = data_car[2:]
	for line in data_car:
		tmp = line[1]
		line[1] = line[2]
		line[2] = tmp

	len_car = len(data_car)
	for i in range(len_car):
		timing[i] = [datetime.datetime.today(), '-1']

	return data_trip, data_car


def input_rdy(driver_id):
	length_car = len(data_car)
	ind_car = -1
	for i in range(length_car):
		if data_car[i][0] == driver_data[0]:
			ind_car = i

	counter = 0
	while counter < 10:
		try:
			sh = gc.open("DriversDistribTable").get_worksheet(4)
			sh.update_cell(ind_car, 24, 'v')
			break
		except:
			time.sleep(10)
			counter += 1

def find_ind(driver_id, prior_table, data_car, data_trip):
	length_car = len(data_car)
	ind_car = -1
	for i in range(length_car):
		if data_car[i][0] == driver_id:
			ind_car = i
			break


	length_trip = len(data_trip)
	ind_trip = -1
	for i in range(length_trip):
		if prior_table[data_trip[i][0]][0][0][0] == driver_id:
			ind_trip = i
			break
	return ind_car, ind_trip

def find_trip_ind(trip, data_trip):
	length_trip = len(data_trip)
	ind_trip = -1
	for i in range(length_trip):
		if data_trip[i][0][:len(data_trip[i][0]) - 2] == trip:
			ind_trip = i
			break
	return ind_trip

def find_car_ind(car, data_car):
	length_trip = len(data_car)
	ind_car = -1
	for i in range(length_trip):
		if data_car[i][0] == car:
			ind_car = i
			break
	return ind_car

def plus_km(ind_car, ind_trip, data_car, data_trip, driver_id):
	try:
		prev = int(data_car[ind_car][22]) 
	except:
		prev = 0

	counter = 0
	while counter < 10:
		try:
			sh = gc.open("DriversDistribTable").get_worksheet(4)
			sh.update_cell(ind_car + 3, 24, str(int(data_trip[ind_trip][1]) + prev - km[driver_id][0]))
			break
		except:
			time.sleep(10)
			counter += 1

	prev_km[driver_id] = km[driver_id][0]
	if len(km[driver_id]) > 6:
		km[driver_id] = km[driver_id][1:]
	km[driver_id].append(data_trip[ind_trip][2])


def minus_km(ind_car, data_car, data_trip, driver_id):
	try:
		prev = int(data_car[ind_car][22]) 
	except:
		prev = 0

	counter = 0
	while counter < 10:
		try:
			sh = gc.open("DriversDistribTable").get_worksheet(4)
			sh.update_cell(ind_car + 3, 24, str(prev - prev_km[driver_id]))
			break
		except:
			time.sleep(10)
			counter += 1

	km[driver_id].insert(0, prev_km[driver_id])
	if len(km[driver_id]) > 7:
		km[driver_id] = km[driver_id][:8]

def get_return_time(data_trip, ind_trip):
	num = 0
	if data_trip[ind_trip][9] == 'Возврат во второй день':
		num = 1
	elif data_trip[ind_trip][9] == 'Возврат на третий день':
		num = 2
	return_day = datetime.datetime.today() + datetime.timedelta(days = num)
	

	return_time = data_trip[ind_trip][10][3:]
	if return_time == '':
		return_time = '-1'
	return [return_day, return_time]


def save_north(north):
	file = open('north.txt', 'w')
	file.write(north)
	file.close()

def get_north():
	file = open('north.txt', 'r')
	north = file.read()
	file.close()
	return north

def input_new_car(car, company, data_car):
	counter = 0
	ind = len(data_car) - 1
	while counter < 10:
		try:
			sh = gc.open("DriversDistribTable").get_worksheet(4)
			sh.update_cell(ind + 3, 1, car)
			sh.update_cell(ind + 3, 3, company)
			return 1
		except:
			time.sleep(10)
			counter += 1
	return -1

def input_data(ind, prior_table, driver_data, data_car, data_trip, data):
	global north

	ind_car = find_car_ind(driver_data[0], data_car)
	ind_trip = find_trip_ind(data[ind][0], data_trip)
	timing[ind_car] = get_return_time(data_trip, ind_trip)
	counter = 0
	while counter < 10:
		try:
			sh.sheet1.update_cell(ind + 3, 2, driver_data[0])
			sh.sheet1.update_cell(ind + 3, 3, driver_data[1] + ' ' + driver_data[2])
			break
		except:
			time.sleep(10)
			counter += 1

	

	if data_trip[ind_trip][11] == 'Север (C)':
		north = chat_id

	plus_km(ind_car, ind_trip, data_car, data_trip, driver_data[0])


	

	


def clear_data(ind, prior_table, driver_data, data_car, data_trip, data):
	global north

	counter = 0
	while counter < 10:
		try:
			print(sh.sheet1.update_cell(ind + 3, 2, ''))
			print(sh.sheet1.update_cell(ind + 3, 3, ''))
			break
		except:
			time.sleep(10)
			counter += 1

	
	ind_car = find_car_ind(driver_data[0], data_car)
	ind_trip = find_trip_ind(data[ind], data_trip)

	if data_trip[ind_trip][11] == 'Север (C)':
		north = ''

	minus_km(ind_car, data_car, data_trip, driver_data[0])

	timing[ind_car] = [datetime.datetime.today(), '-1']

def del_driver_from_table(data_car):
	counter = 0
	while counter < 1:
		try:
			sh2 = gc.open("DriversDistribTable").get_worksheet(4)
			length = len(data_car)
			for i in range(length):
				sh2.update_cell(3 + i, 25, '')
			break
		except:
			time.sleep(10)
			counter += 1
	return 0


def add_driver_to_table(cur_driver, prior_table, data_car):
	ind_car = find_car_ind(cur_driver, data_car)

	if ind_car == -1:
		print('Bad car')
		return -1

	counter = 0
	while counter < 10:
		try:
			sh2 = gc.open("DriversDistribTable").get_worksheet(4)
			sh2.update_cell(ind_car + 3, 25, 'v')
			break
		except:
			time.sleep(10)
			counter += 1
	return 0

def check_driver(driver, line, prior, data_car, data_trip):
	ind_car = find_car_ind(driver, data_car)
	try:
		if orders[driver] == 1:
			return False
	except:
		orders[driver] = 0

	num_of_nums = 0
	llll = len(prior)
	for i in range(llll):
		try:
			int(prior[llll - i - 1])
			num_of_nums += 1
		except:
			break
	if timing[ind_car][0] > datetime.datetime.today() + datetime.timedelta(num_of_days[prior[len(prior) - num_of_nums:]]):									# Время
		print('Here', prior)
		return False

	if int(timing[ind_car][1].split(':')[0]) > int(line[1].split(':')[0]) or (int(timing[ind_car][1].split(':')[0]) == int(line[1].split(':')[0]) and int(timing[ind_car][1].split(':')[1]) > int(line[1].split(':')[1])):
		print('Days ', num_of_days[prior[len(prior) - num_of_nums:]])
		return False
	print('Success', prior)
	orders[driver] = 1
	return True

def find_best(ind_trip, line, drivers, i, data_car, data_trip):
	sorted_drivers = []
	sorted_drivers_sec = []


	if data_trip[ind_trip][11] == 'Север (С)' and north != '':				#Север
		return [north]

	for driver in drivers:
		ind_car = find_car_ind(drivers[driver][0], data_car)

		try:
			if len(data_car[ind_car][5]) == 0 and line[1] == '10':
					continue
			if line[1][len(line[1]) - 1] == '+' or line[1][len(line[1]) - 1] == '-':
				#line[1] = line[1][:len(line[1]) - 1]
				if len(data_car[ind_car][6]) == 0 and line[1] == '20-':		#Грузоподъемность
					continue
				if len(data_car[ind_car][7]) == 0 and line[1] == '20+':
					continue
				if len(data_car[ind_car][8]) == 0 and line[1] == '30-':
					continue
				if len(data_car[ind_car][9]) == 0 and line[1] == '30+':
					continue
				if len(data_car[ind_car][10]) == 0 and line[1] == '40-':
					continue
				if len(data_car[ind_car][11]) == 0 and line[1] == '40+':
					continue
				if len(data_car[ind_car][12]) == 0 and line[1] == '50-':
					continue
				if len(data_car[ind_car][13]) == 0 and line[1] == '50+':
					continue
			elif line[1] == 'фура':
				if len(data_car[ind_car][14]) == 0:
					continue
			elif int(data_car[ind_car][2]) < int(line[1]):
				#print('Vol', data_car[ind_car][0], line[1], int(line[1]))
				continue
		except:
			time.sleep(0.1)
			continue
		
		if len(data_trip[ind_trip][13]) == 0 and data_car[ind_car][20] == 'т20':		#Тип машины
			continue
		if len(data_trip[ind_trip][14]) == 0 and data_car[ind_car][20] == 'т30':
			continue
		if len(data_trip[ind_trip][15]) == 0 and data_car[ind_car][20] == 'т40':
			continue
		if len(data_trip[ind_trip][16]) == 0 and data_car[ind_car][20] == 'т50':
			continue
		if len(data_trip[ind_trip][17]) == 0 and data_car[ind_car][20] == 'фура':
			continue
		if len(data_trip[ind_trip][12]) == 0 and data_car[ind_car][20] == 'фургон':
			continue
		

		if len(data_car[ind_car][18]) == 0 and data_trip[ind_trip][11] == 'ЕКБ МЕГА':
			continue
		if len(data_car[ind_car][19]) == 0 and data_trip[ind_trip][11].find('Новоуральск') > -1:
			continue
		if len(data_car[ind_car][20]) == 0 and data_trip[ind_trip][11] == 'шатл':
			continue

		if data_trip[ind_trip][11] == 'город' and len(data_car[ind_car][15]) == 0:
			continue
		if data_trip[ind_trip][11] == 'межгород' and len(data_car[ind_car][17]) == 0:
			continue


		if len(data_car[ind_car][22]) != 0:
			sorted_drivers.append(driver)										#Приоритет
		else:
			sorted_drivers_sec.append(driver)


	length_1 = len(sorted_drivers)
	length_2 = len(sorted_drivers_sec)

	for i in range(length_1):
		ind_car = find_car_ind(drivers[sorted_drivers[i]][0], data_car)
		if data_trip[ind_trip][11] == 'город' and data_car[ind_car][14] == 'v':					#Тип поездки
			tmp = sorted_drivers[i]
			del sorted_drivers[i]
			sorted_drivers.insert(0, tmp)
			
		if data_trip[ind_trip][11] == 'город' and data_car[ind_car][14] != 'v' and data_car[ind_car][15] != 'v':			
			tmp = sorted_drivers[i]
			del sorted_drivers[i]
			sorted_drivers.append(tmp)
		if data_trip[ind_trip][11] != 'город' and data_car[ind_car][14] == 'v':
			tmp = sorted_drivers[i]
			del sorted_drivers[i]
			sorted_drivers.append(tmp)
			

	for j in range(length_1):
		for i in range(length_1 - 1):											#Километраж за неделю
			ind_car1 = find_car_ind(drivers[sorted_drivers[i]][0], data_car)
			ind_car2 = find_car_ind(drivers[sorted_drivers[i + 1]][0], data_car)
			try:
				num1 = int(data_car[ind_car1][14][23])
			except:
				num1 = 0
			try:
				num2 = int(data_car[ind_car2][14][23])
			except:
				num2 = 0
			if data_trip[ind_trip][11] != 'город' and num1 > num2:
				tmp = sorted_drivers[i]
				sorted_drivers[i] = sorted_drivers[i + 1]
				sorted_drivers[i + 1] = tmp


	for i in range(length_2):
		ind_car = find_car_ind(drivers[sorted_drivers_sec[i]][0], data_car)
		if data_trip[ind_trip][11] == 'город' and data_car[ind_car][14] == 'v':					#Тип поездки
			tmp = sorted_drivers_sec[i]
			del sorted_drivers_sec[i]
			sorted_drivers_sec.insert(0, tmp)
		if data_trip[ind_trip][11] == 'город' and data_car[ind_car][14] != 'v' and data_car[ind_car][15] != 'v':	
			tmp = sorted_drivers_sec[i]
			del sorted_drivers_sec[i]
			sorted_drivers_sec.append(tmp)
		if data_trip[ind_trip][11] != 'город' and data_car[ind_car][14] == 'v':
			tmp = sorted_drivers_sec[i]
			del sorted_drivers_sec[i]
			sorted_drivers_sec.append(tmp)

	for j in range(length_2):
		for i in range(length_2 - 1):											#Километраж за неделю
			ind_car1 = find_car_ind(drivers[sorted_drivers_sec[i]][0], data_car)
			ind_car2 = find_car_ind(drivers[sorted_drivers_sec[i + 1]][0], data_car)
			try:
				num1 = int(data_car[ind_car1][14][23])
			except:
				num1 = 0
			try:
				num2 = int(data_car[ind_car2][14][23])
			except:
				num2 = 0
			if data_trip[ind_trip][11] != 'город' and num1 > num2:
				tmp = sorted_drivers_sec[i]
				sorted_drivers_sec[i] = sorted_drivers_sec[i + 1]
				sorted_drivers_sec[i + 1] = tmp

	return sorted_drivers + sorted_drivers_sec





def find_priorities(data, prior_table, drivers, data_car, data_trip):
	prior_table.clear()
	length = len(data)
	for i in range(length):
		num = str(i)
		if i < 10:
			num = '0' + str(i)
		try:
			if data[i][3] == '' or prev_order(data[i][4], num):
					continue
			if data[i][1] != '':
				taken[data[i][0] + num] = True
				continue
		except:
			continue

		try:
			if prior_table[data[i][0] + num][3] != '':
				taken[data[i][0] + num] = True
				continue
		except:
			kk = 0

		taken[data[i][0] + num] = False

		ind_trip = find_trip_ind(data[i][0], data_trip)

		data[i] = [data[i][0], data[i][3], data[i][4], data[i][5]]
		sorted_drivers = find_best(ind_trip, data[i], drivers, i, data_car, data_trip)
		prior_table[data[i][0] + num] = data[i][1:] + sorted_drivers
		try:
			drivers[sorted_drivers[0]][3] = i
		except:
			jj = 0

 
 
 
 
