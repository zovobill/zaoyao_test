from .models import DrugsApproved
from django.db.models.functions import ExtractYear
from django.db.models import Count, Max, Min
from django.db.models.query import EmptyQuerySet
from copy import deepcopy

class DrugDataset(object):
	"""generate dataset for creating echarts"""
	MAX_KEYWORD_NUM = 3
	colnames = ['drug_name_zh', 'production_unit__production_unit_name', 'drug_name_en', 'drug_approval_num']
	view_colnames = ['drug_index', 'drug_approval_num', 'drug_name_zh', 'drug_name_en', 'drug_form','drug_spec', 'production_unit__production_unit_name','production_unit__province', 'approval_date']
	date_columns = ['approval_date']
	one_ending = '_one'
	many_ending = '_many'
	charts_by_column = {
	'default':['approval_date', 'production_unit__province'],
	'drug_name_zh'+one_ending:['approval_date', 'production_unit__province'],
	'drug_name_zh'+many_ending:['approval_date', 'production_unit__province', 'drug_form'],
	# 'drug_name_zh'+one_ending:['drug_spec', 'production_unit__production_unit_name', 'approval_date'],
	# 'drug_name_zh'+many_ending:['drug_name_zh', 'category', 'drug_spec', 'production_unit__production_unit_name', 'approval_date'],
	'production_unit__production_unit_name'+one_ending:['approval_date','drug_form'],
	'production_unit__production_unit_name'+many_ending:['approval_date', 'drug_form', 'production_unit__province'],
	'drug_approval_num'+one_ending:['approval_date','drug_form'],
	'drug_approval_num'+many_ending:['approval_date', 'drug_form', 'production_unit__production_unit_name'],
	'drug_name_en'+one_ending:['approval_date','drug_form'],
	'drug_name_en'+many_ending:['approval_date', 'drug_form', 'production_unit__province'],
	}
	chartbyids = {
	'drug_name_zh':'按药品名称',
	'drug_form':'按剂型',
	'drug_spec':'按规格',
	'production_unit__production_unit_name':'按企业名称',
	'production_unit__province':'按省份',
	'approval_date':'按批准年份',
	}
	x = 'axisX'
	y = 'axisY'
	is_by_and = True
	default_qsets = {}

	model = DrugsApproved
	querys_dict = {}

	def __init__(self):
		super(DrugDataset, self).__init__()

	def _parse_keyword(self, keyword, splitchars=[' ', '+', ',', '，']):
		# split keyword to a list
		keyword = keyword.strip()
		for c in splitchars:
			kwords = keyword.split(c)
			if len(kwords) > 1: 
				if c in [',', '，']:
					self.is_by_and = False
				else:
					self.is_by_and = True
				break
		#drop the space char of list
		kwords = list(filter(None, kwords))
		return kwords or []

	def _get_query_columns(self, kwords):
		# find out the relative columns of kwords
		columns = []
		qwords = []
		for keyword in kwords:
			column = self._get_query_column_by_one(keyword)
			if column :
				columns.append(column)
				qwords.append(keyword)
		print('query kwords:{}, columns:{}'.format(qwords, columns))
		return qwords, columns

	def _get_query_column_by_one(self, keyword):
		# find out the first correct column of a keyword
		for col in self.colnames:
			obj = self.model.objects\
				.filter(**{col+'__icontains' : keyword})\
				.first()
			if obj: return col

	def _get_query_names_by_cols(self, objs, qwords, columns):
		# collect all the different column values of every qword by column
		querys_dict = {}
		cur_words = []
		for i in range(len(columns)):
			dnames = objs.values_list(columns[i], flat = True)
			dnames = list(set(dnames))
			dnames.sort()
			if qwords[i] in dnames:
				cur_words.append(qwords[i])
				j = dnames.index(qwords[i])
				dnames[i], dnames[j] = dnames[j], dnames[i]
			else:
				cur_words.append(dnames[0])
			querys = {'kwords' : dnames, 'column': columns[i], 'active':''}
			# print('querys = {}'.format(querys))
			querys_dict[qwords[i]] = querys
			
		querys_dict = self._collect_same_column(querys_dict)
		return querys_dict, cur_words

	def _collect_same_column(self, querys_dict):
		# collect and group by the same column, space char join keys by same columns
		d = {}
		for k, v in querys_dict.items():
			col = v['column']
			if col in d.keys():
				d[col] = d[col] + ' ' + k
			else:
				d[col] = k
		dd = {}
		for col, keys in d.items():
			for value in querys_dict.values():
				if value['column'] == col:
					dd[keys] = value
					break
		return dd

	def _get_queryset_by_list(self, objs, kwords, columns, by_exact = True, by_and = True):
		# filter with all the kwords by columns from objs of db
		if len(kwords) != len(columns): return []
		if not by_exact:
			cols_methods = [col+'__icontains' for col in columns]
		else:
			cols_methods = [col+'__iexact' for col in columns]
		filter_kw = dict(zip(kwords, cols_methods))
		print('kwords = {}, columns = {}, kw={}'.format(kwords, columns, filter_kw))
		colset = set(filter_kw.values())
		return self._get_queryset_by_recursion(objs, filter_kw, colset, by_and = by_and)

	def _get_queryset_by_recursion(self, objs, filter_kw, colset, by_and = True):
		cur_col = colset.pop()
		qset = objs.none()
		for value, col in filter_kw.items():
			if col == cur_col:	
				print('col = {}, value = {}'.format(col, value))
				if isinstance(qset, EmptyQuerySet):
					qset = objs.filter(**{col: value})
				else:
					qs = objs.filter(**{col: value})
					# QuerySet & QuerySet one by one, intersection
					if by_and:
						qset = qset & qs
					else:
						qset = qset | qs
				# print('queryset by list len:{}'.format(len(qset)))
				# print('qset by list kwords:{} = {}, qset ={}'.format(col, value, qset))
		if len(colset) == 0:
			return qset
		else:
			return self._get_queryset_by_recursion(qset, filter_kw, colset, by_and = by_and)

	def _get_queryset_by_one(self, objs, name, column, is_exact = False):
		# filter withe one kword by column from objs of db
		if is_exact:
			qset = objs.filter(**{column+'__iexact': name})
		else:
			qset = objs.filter(**{column+'__icontains': name})
		print('queryset by one len:{}'.format(len(qset)))
		return qset

	def get_queryset(self, keyword, is_exact = False):
		# get queryset by keyword
		self.keyword = keyword
		kwords = self._parse_keyword(keyword)
		if kwords == []: return [], kwords, []
		qwords, columns = self._get_query_columns(kwords)
		if qwords == []: return [], kwords, []

		kn = len(qwords)
		if kn == 1:
			qset = self._get_queryset_by_one(self.model.objects, qwords[0], columns[0], is_exact = is_exact)
		elif kn > 1:
			qset = self._get_queryset_by_list(self.model.objects, qwords, columns, by_exact = is_exact, by_and = self.is_by_and)
		# print('qset = {}'.format(qset))
		return qset, qwords, columns

	def get_queryset_by_dict(self, **keys_cols):
		# get queryset by dict, to ready for request ajax
		kwords = list(keys_cols.keys())
		columns = list(keys_cols.values())

		qset = self._get_queryset_by_list(self.model.objects, kwords, columns, by_and = False)
		print('qset by dict len:', len(qset))
		return qset

	def get_datasets_by_dict(self, cur_keyword = '', **keys_cols):
		# get datasets by dict, to ready for request ajax
		if cur_keyword != '':
			qset = DrugDataset.default_qsets[cur_keyword]
			chartbycols = self.charts_by_column['default']
			kwords = []
			columns = []
		else:
			kwords = list(keys_cols.keys())
			columns = list(keys_cols.values())
			qset = self._get_queryset_by_list(self.model.objects, kwords, columns, by_and = False)

			if len(columns) > 1:
				chartbycols = self.charts_by_column[columns[0]+self.many_ending]
			else:
				chartbycols = self.charts_by_column[columns[0]+self.one_ending]	
		chartdatas = {}

		# get every chart by specified columns
		for chartbycol in chartbycols:
			# create a dict with zero values of every different chartbycol's key value
			print('chartbycol = ', chartbycol)
			chartdata = {}
			zdataset, new_col = self._init_dataset(qset, chartbycol)

			# count the item data of chartbycol filted by each filter_col and key
			if len(keys_cols) == 0:
				data = self._get_data_count_by(chartbycol, qset, zdataset, new_col)
				chartdata['Catgory with All Results'] = data
			else:
				for key, filter_col in keys_cols.items():
					print('*'*100)
					data = self._get_data_count_by(chartbycol, qset, zdataset, new_col, filter_by_col = filter_col, filter_keyword = key)
					chartdata[key] = data
			chartdatas[self.chartbyids[chartbycol]] = chartdata
			# self._save_dataset_to_db(qset, '', datasets)
		return chartdatas, kwords, columns

	# def _get_dataset_from_cache(self, keyword):
	# 	return [], [], [], [], ''

	def get_query_names(self, keyword, is_exact = False):
		# get query names
		qset, qwords, columns = self.get_queryset(keyword, is_exact)
		print('qset type:{}'.format(type(qset)))
		if len(qset) == 0: return {}, keyword, []
		DrugDataset.default_qsets[self.keyword] = qset
		querys_dict, cur_words = self._get_query_names_by_cols(qset, qwords, columns)
		return querys_dict, cur_words, qset

	def _get_data_count_by(self, count_by_col, qset, zdataset, new_col, filter_by_col = None, filter_keyword = None ):
		# count a column by group by itself
		if filter_by_col:
			qset = qset.filter(**{filter_by_col+'__iexact': filter_keyword})
		if count_by_col in self.date_columns:
			# print('-----------annotate date by year-------------')
			qset = qset.annotate(**{new_col : ExtractYear(count_by_col)}).values(new_col)
		data_count = qset.values(new_col).annotate(**{self.y : Count(new_col)}).values(new_col, self.y).order_by(new_col)
		print('data_count = {}'.format(data_count))

		#union the result dataset with zdataset
		zdataset = deepcopy(zdataset)
		# print('zdataset = {}'.format(zdataset))
		for d in zdataset:
			for cy in data_count:
				if d[new_col] == cy[new_col]: d[self.y] = cy[self.y]

		data_count = [tuple(d.values()) for d in zdataset]
		print('data_count tuple = {}'.format(data_count))
		return data_count or []

	def _init_dataset(self, qset, col):
		# init zero dataset
		if col in self.date_columns:
			qset = qset.annotate(**{self.x : ExtractYear(col)})
			col = self.x
		dset = qset.values_list(col, flat = True).order_by(col)
		dset = list(set(dset))
		dset.sort()
		# print('dset = {}'.format(dset))
		return [{col : i, self.y : 0 } for i in dset], col

	def _save_dataset_to_db(self, qset, query_dict, datasets):
		pass