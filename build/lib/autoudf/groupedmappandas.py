from typing import Callable
import warnings
from pyspark.sql.types import *


class auto_groupedmap_udf():

	#the df here is a pyspark.sql.dataframe.DataFrame
	@staticmethod
	def get_num_partitions(df, repartition_cols: list):
		num_paritions = df.groupby(repartition_cols).count().count()
		return(num_paritions)
	
	#the df here is a pyspark.sql.dataframe.DataFrame
	def __init__(self, df, groupby_cols: list, func: Callable, repartition_cols: list = None):
		self.df = df
		self.groupby_cols = groupby_cols
		self.repartition_cols = repartition_cols
		self.func = func
		self.datatype_mapping = {}
		
		for key in ["object","string_","unicode_"]:
			self.datatype_mapping[key] = StringType
		for key in ["int64","int_","int8","int16","int32","uint8","uint16","uint32","uint64"]:
			self.datatype_mapping[key] = IntegerType
		for key in ["float64","float","float_","float16","float32","float64"]:
			self.datatype_mapping[key] = DoubleType
		for key in ["bool","bool_"]:
			self.datatype_mapping[key] = BooleanType
		for key in ["datetime64","datetime64[ns]"]:
			self.datatype_mapping[key] = TimestampType

		"""
		self.datatype_mapping = {"float64": DoubleType,
								   "object":StringType,
								   "int64":IntegerType,
								   "bool":BooleanType,
								   "datetime64": TimestampType
								   ""}
		"""
		
		#partitioning upfront
		if self.repartition_cols is not None:
			self.df = self.df.repartition(auto_groupedmap_udf.get_num_partitions(self.df, self.repartition_cols), self.repartition_cols)

	@staticmethod
	#This function takes a pandas dataframe and checks if any nulls are present
	def check_for_nulls(df):

		null_cols = []
		for col in df.columns:
			if df[col].isnull().values.any():
				null_cols.append(str(col))

		if (len(null_cols)>0):
			warnings.warn("Columns |" + ", ".join(null_cols) + "| found to have nulls. This will cause error in udf. Remove null values from return dataframe in the udf.")
			print("\x1b[31mColumns |" + ", ".join(null_cols) + "| found to have nulls. This will cause error in udf. Remove null values from return dataframe in the udf.")

	@staticmethod
	#result is a pandas dataframe
	def correct_wrong_types(result):

		mistyped_cols = []
		# converting int cols to int from object
		for key in result.columns:
			if result.dtypes[key] == 'object':
				try:
					result[key].astype('int')
					result[key] = result[key].astype('int')
					mistyped_cols.append(str(key))
				except:
					pass

		if(len(mistyped_cols)>0):
			mistyped_cols = [str(col) for col in mistyped_cols]
			warnings.warn("Columns |" + ", ".join(mistyped_cols) + "| found of object type, should be numeric. Forcing conversion to int. Manually correct to the right dtype in the udf")
			print("\x1b[31mWARNING: Columns | %s | found of object type, should be numeric. Forcing conversion to int. Manually correct to the right dtype in the udf" % ", ".join(mistyped_cols))

		return(result)



	def run_as_pandas(self):

		#get the first subset of dataframe for first elements of the group by cols
		first_row = self.df.first().asDict()
		first_row_vals = [first_row.get(i) for i in self.groupby_cols]
		filter_expression_list = []
		for col, val in zip(self.groupby_cols,first_row_vals):
			if (isinstance(val,str)):
				exp = str(str(col) + " == '" + str(val) +"'")
			else:
				exp = str(str(col) + " == " + str(val))
			filter_expression_list.append(exp)

		filter_expression = " AND ".join(filter_expression_list)

		#apply the actual filter
		dfChunk = self.df.filter(filter_expression).toPandas()


		#Convert any spark dataframes to pandas dataframes
		result = self.func(dfChunk)

		return(result)

	def get_schema(self):

		result = self.run_as_pandas()

		result = auto_groupedmap_udf.correct_wrong_types(result)
		auto_groupedmap_udf.check_for_nulls(result)

		column_types  = [StructField(key, self.datatype_mapping[str(result.dtypes[key])]()) for key in result.columns]
		schema = StructType(column_types)
		return(schema)

	def debug(self):

		result = self.run_as_pandas()
		result.display()

	def compute(self):

		schema = self.get_schema()
		res = self.df.groupby(self.groupby_cols).applyInPandas(self.func, schema=schema)
		return(res)
