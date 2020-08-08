#kucoin project
import json
import os
import threading
import numpy as np
from kucoin.client import Client
from kucoin import exceptions
from datetime import datetime, timedelta, timezone
from scipy.signal import argrelextrema
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import mplfinance
import pandas as pd


class CryptoAnalyst:

	def __init__(self):
		self.api_key = ''
		self.api_secret = ''
		self.passphrase = 'kucoinproject'
		self.client = Client(self.api_key, self.api_secret, self.passphrase)
		self.data = {}

	def get_data(self, market, candles, n_candles, vol_min):
		#1min, 3min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
		try:
			if candles.endswith('min'):
				delta = timedelta(minutes=n_candles*int(candles[:-3]))
			elif candles.endswith('hour'):
				delta = timedelta(hours=n_candles*int(candles[:-4]))
			elif candles == '1day':
				delta = timedelta(days=n_candles)
			elif candles == '1week':
				delta = timedelta(days=7*n_candles)
			now = datetime.now()
			subs = now - delta
			now_ts = int(now.replace(tzinfo=timezone.utc).timestamp())
			subs_ts = int(subs.replace(tzinfo=timezone.utc).timestamp())
			currencies = self.client.get_currencies()
			for currency in currencies:
				try:
					currency_abbr = currency['currency']
					stats = self.client.get_24hr_stats(currency_abbr + '-'+ market)
					if 'volValue' in stats.keys() and stats['volValue'] != None:
						if float(stats['volValue']) > vol_min:
							self.data[currency_abbr+ '-'+ market] = self.client.get_kline_data(currency_abbr + '-' + market, candles, subs_ts, now_ts)
							self.data[currency_abbr+ '-'+ market].reverse()
				except exceptions.KucoinAPIException as e:
					print(currency_abbr + '-' + market + ': ', e.message)
			#self.df = pd.DataFrame(data=d, columns=('time', 'open','close', 'high', 'low', 'amount', 'vol'))
			#self.df['time'] = [datetime.fromtimestamp(int(element)) for element in df['time']]
			return self.data
		except UnboundLocalError as e:
			print(e, 'El tipo de vela solicitado no existe, las opciones son: 1min, 3min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week')


	def find_locals(self, close_prices):
		distances_max = {}
		distances_min = {}
		for key in range(1, len(close_prices) - 1):
			limit = max(key, len(close_prices) - 1 - key)
			for x in range(1, limit):
				if (key - x) >= 0:			
						if (close_prices[key - x] > close_prices[key]):
							distances_max[key] = min(len(close_prices) - key - 1, x) + min(key, x)
							break
				if key + x < len(close_prices):
					if (close_prices[key + x] > close_prices[x]):
							distances_max[key] = min(len(close_prices) - key - 1, x) + min(key, x)
							break
				if x == limit:
					distances_max[key] = x
					break
			for x in range(1, limit):
				if (key - x) >= 0:
						if (close_prices[key - x] < close_prices[key]):
							distances_min[key] = min(len(close_prices) - key - 1, x) + min(key, x) 
				if key + x < len(close_prices):
						if (close_prices[key + x] < close_prices[x]):
							distances_min[key] = min(len(close_prices) - key - 1, x) + min(key, x)
				if x == limit:
					distances_min[key] = x

		distances_max = sorted(distances_max.items(), key=lambda x: x[1])
		distances_min = sorted(distances_min.items(), key=lambda x: x[1])

		return distances_max, distances_min

	def find_maximum_minimum(self, close_prices):
		max_ = max(close_prices)
		max_i = [i for i, j in enumerate(close_prices) if j == max_]
		min_ = min(close_prices)
		min_i = [i for i, j in enumerate(close_prices) if j == min_]
		return max_i, min_i, max_, min_

	def calculate_equations(self, close_prices, max_i, min_i, max_, min_):
		m_max = 0
		m_min = 0
		n_max = max_
		n_min = min_
		x1_max = max_i[0]
		y1_max = max_
		x1_min = min_i[0]
		y1_min = min_
		#cada elemento de la lista tendra el formato [x1, y1, m, n, c]
		max_equations = []
		min_equations = []
		if len(max_i) == 1:
			#iremos cambiando la pendiente en 0.01
			for x in range(1000,-1000,-1):
				#la variacion maxima es la diferencia entre el maximo y el minimo /50. Es un porcentaje en escala de 1 a 0,
				#es el rango de error que puede tener la recta
				max_var = ((max_ - min_)/max_)/50
				m_max = (max_- min_)*x/1000
				n_max = y1_max - m_max*x1_max
				m_min = (max_- min_)*-x/10000
				n_min = y1_min - m_min*x1_min
				#vamos a dar un rango de 3% de error
				c_max = 0
				c_min = 0
				c_max_out = 0
				c_min_out = 0
				for indexes in range(len(close_prices)):
					if (1-max_var)*(m_max*indexes+n_max) <= close_prices[indexes] <= (1+max_var)*(m_max*indexes+n_max):
						c_max += 1
					elif close_prices[indexes] > (1+max_var)*(m_max*indexes+n_max):
						c_max_out += 1
					if (1-max_var)*(m_min*indexes+n_min) <= close_prices[indexes] <= (1+max_var)*(m_min*indexes+n_min):
						c_min += 1
					elif (1-max_var)*(m_min*indexes+n_min) > close_prices[indexes]:
						c_min_out += 1
				if (c_max > 1) and (c_max_out == 0):
					max_equations.append([x1_max, y1_max, m_max, y1_max - m_max*x1_max, c_max])
				if (c_min > 1) and (c_min_out == 0):
					min_equations.append([x1_min, y1_min, m_min, y1_min - m_min*x1_min, c_min])
		else:
			max_equations.append([x1_max, y1_max, 0, y1_max, len(max_i)])
			min_equations.append([x1_min, y1_min, 0, y1_min, len(min_i)])
		
		max_equations.sort(key=lambda x: x[4])
		min_equations.sort(key=lambda x: x[4])
		return max_equations, min_equations

	def calculate_equations_v2(self, close_prices, distances_max, distances_min, n_points_considered, max_, min_, max_i, min_i):
		'''n_points_considered = numero de puntos que seran considerados 
		para armar las ecuaciones. Seran siempre los maximos locales
		de mayores distancias
		'''
		points_max = distances_max[-n_points_considered:]
		points_min = distances_min[-n_points_considered:]
		max_equations = []
		min_equations = []
		for n in range(n_points_considered):
			for x in range(10000,-10000,-1):
				m_max = (max_- min_)*x/10000
				m_min = (max_- min_)*-x/10000
				n_max = close_prices[points_max[n][0]] - m_max*points_max[n][0]
				n_min = close_prices[points_min[n][0]] - m_min*points_min[n][0]
				max_var = ((max_ - min_)/max_)/50
				c_max = 0
				c_min = 0
				c_max_out = 0
				c_min_out = 0
				added = 0
				#no consideramos un % del largo de la lista (extremos)
				for indexes in range(len(close_prices)):
					if (1-max_var)*(m_max*indexes+n_max) <= close_prices[indexes] <= (1+max_var)*(m_max*indexes+n_max):
						c_max += 1
					elif close_prices[indexes] > (1+max_var)*(m_max*indexes+n_max):
						c_max_out += 1
					if (1-max_var)*(m_min*indexes+n_min) <= close_prices[indexes] <= (1+max_var)*(m_min*indexes+n_min):
						c_min += 1
					elif (1-max_var)*(m_min*indexes+n_min) > close_prices[indexes]:
						c_min_out += 1
				if (c_max >= 1) and (c_max_out == 0):
					added += 1
					#print('agregado max', close_prices[0])
					max_equations.append([points_max[n][0], close_prices[points_max[n][0]], m_max, close_prices[points_max[n][0]] - m_max*points_max[n][0], c_max])
				if (c_min >= 1) and (c_min_out == 0):
					added += 1
					#print('agregado min', close_prices[0])
					min_equations.append([points_min[n][0], close_prices[points_min[n][0]], m_min, close_prices[points_min[n][0]] - m_min*points_min[n][0], c_min])
		
			if added == 0:
				max_equations.append([max_i, max_, 0, max_, 1])
				min_equations.append([min_i, min_, 0, min_, 1])

		max_equations.sort(key=lambda x: x[4])
		min_equations.sort(key=lambda x: x[4])
		return max_equations, min_equations


	def get_best_equations(self):
		best_max_equations = {}
		best_min_equations = {}
		for key in self.data.keys():
			currency = self.data[key]
			close_prices = [x[2] for x in currency]
			close_prices = list(map(float, close_prices))
			if currency != []:
				max_i, min_i, max_, min_ = self.find_maximum_minimum(close_prices)
				max_equations, min_equations = self.calculate_equations(close_prices, max_i, min_i, max_, min_)
				if max_equations != []:
					best_max_equations[key] = max_equations[-1]
				if min_equations != []:
					best_min_equations[key] = min_equations[-1]
		return best_max_equations, best_min_equations

	def get_best_equations_v2(self, n_points_considered):
		best_max_equations = {}
		best_min_equations = {}
		for key in self.data.keys():
			currency = self.data[key]
			close_prices = [x[2] for x in currency]
			close_prices = list(map(float, close_prices))
			if currency != []:
				distances_max, distances_min = self.find_locals(close_prices)
				max_i, min_i, max_, min_ = self.find_maximum_minimum(close_prices)
				max_equations, min_equations = self.calculate_equations_v2(close_prices, distances_max, distances_min, n_points_considered, max_, min_, max_i, min_i)
				if max_equations != []:
					best_max_equations[key] = max_equations[-1]
				if min_equations != []:
					best_min_equations[key] = min_equations[-1]
		return best_max_equations, best_min_equations

	def plot_max_equations(self, best_max_equations, best_min_equations, max_c_max, max_c_min):
		best_max_equation = []
		best_min_equation = []
		for key in best_max_equations.keys():
			if best_max_equations[key][4] >= max_c_max:
				best_max_equation = best_max_equations[key]
				best_max_data = self.data[key]
				break
		for key in best_min_equations.keys():
			if best_min_equations[key][4] >= max_c_min:
				best_min_equation = best_min_equations[key]
				best_min_data = self.data[key]
				break
		e_max = [i for i, j in enumerate([x[2] for x in best_max_data])]
		e_min = [i for i, j in enumerate([x[2] for x in best_min_data])]
		trace0_max = go.Candlestick(x=e_max,
	                open=[x[1] for x in best_max_data],
	                high=[x[3] for x in best_max_data],
	                low=[x[4] for x in best_max_data],
	                close=[x[2] for x in best_max_data])
		trace0_min = go.Candlestick(x=e_min,
	                open=[x[1] for x in best_min_data],
	                high=[x[3] for x in best_min_data],
	                low=[x[4] for x in best_min_data],
	                close=[x[2] for x in best_min_data])
		max_line = go.Scatter(x=e_max, y=[best_max_equation[2]*x + best_max_equation[3] for x in e_max])
		min_line = go.Scatter(x=e_min, y=[best_min_equation[2]*x + best_min_equation[3] for x in e_min])
		mydata_max = [trace0_max, max_line]
		mydata_min = [trace0_min, min_line]
		fig_max = go.Figure(data=mydata_max)
		fig_min = go.Figure(data=mydata_min)
		fig_max.show()
		fig_min.show()


	def find_contractions(self, best_max_equations, best_min_equations):
		print(best_max_equations, best_min_equations)
		for key in best_max_equations.keys():
			print('hola')
			if best_max_equations[key][2] < 0 and best_min_equations[key][2] > 0:
				best_data = self.data[key]
				e_max = [i for i, j in enumerate([x[2] for x in best_data])]
				trace0_max = go.Candlestick(x=e_max,
			                open=[x[1] for x in best_data],
			                high=[x[3] for x in best_data],
			                low=[x[4] for x in best_data],
			                close=[x[2] for x in best_data])
				max_line = go.Scatter(x=e_max, 
									y=[best_max_equations[key][2]*x + best_max_equations[key][3] for x in e_max], 
									name="Resistencia")
				min_line = go.Scatter(x=e_max, 
									y=[best_min_equations[key][2]*x + best_min_equations[key][3] for x in e_max], 
									name="Soporte")
				mydata_max = [trace0_max, max_line, min_line]
				fig_max = go.Figure(data=mydata_max)
				fig_max.update_layout(title=key)
				fig_max.show()
				"""fig, ax = plt.subplots()
				plt.xlabel("Date")
				plt.ylabel("Price")
				candlestick2_ohlc(ax, 
								[x[1] for x in best_data], 
								[x[3] for x in best_data], 
								[x[4] for x in best_data], 
								[x[2] for x in best_data], 
								width=1, 
								colorup='g')
				plt.show()"""


CA = CryptoAnalyst()
CA.get_data('BTC', '15min', 800, 10)
best_max_equations, best_min_equations = CA.get_best_equations_v2(3)
CA.find_contractions(best_max_equations, best_min_equations)