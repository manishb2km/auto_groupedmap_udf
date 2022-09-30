![Decision Point](https://www.organindia.org/wp-content/uploads/2017/06/AwarenesssessionatDecisionPoint-1.jpg)

# Automatic schema generation for pandas_udf

autoudf is a utility to enable agile development on pySpark grouped map pandas_udfs. This utility automatically generates schemas for grouped map udfs in pySpark on the fly.

## Features

- Automatic schema generation. No need to update the schema every time you make a change in your return dataframe
- Get lesser obscure and hard to understand spark errors and more explicit pandas errors. Allow easy debugging of the udf function by printing the actual error message in the udf function
- Automatic repartitioning of data to ensure faster runtimes
- Some automatic validation of the udf function results and warnings


## Installation

autoudf requires Python v3.7+ to run. Not tested on earlier versions.

Install through pip

```sh
pip install autoudf
```

## How to use

Below is an illustration through a simple function. You will have to define the schema as below

#### Old code
Let's say you have a simple pandas_udf function as below
```sh
def standardise_dataframe(df1: pd.DataFrame) -> pd.DataFrame:
    #df1.display()
    df1 = df1.groupby(['class','group']).sum()
    print(df1.head())
    return (df1)
  
schema = StructType([
    StructField('x', T.DoubleType(), nullable=False),
    StructField('y_lin', T.DoubleType(), nullable=False),
    StructField('y_qua', T.DoubleType(), nullable=False),
])

res = df.groupby(['class','group']).applyInPandas(standardise_dataframe, schema=schema)
res.display()
```

#### New code
No need to define and specify the schema
```sh
from autoudf import groupedmappandas
res = groupedmappandas.auto_groupedmap_udf(df=df, groupby_cols=['class','group'], func=standardise_dataframe,repartition_cols=['class','group'])
returndata = res.compute()
```

#### Additional utilities

1. Repartitioning - The utility repartitions the data basis the count of levels in the specified repartition cols and by the repartition cols
2. Debugging - In case you are in the experimentation phase and just want to see if your function works. You want to print something additional from within your udf which are not displayed while using pandas_udf
```sh
res.debug()
#this will also print any print statements inside your udf
#this will not run the actual pandas_udf on entire data
```
3. Get schema - In case you want to check just the autogenerated schema
```sh
res.get_schema()
```
4. Get warnings about possible obsure error messages in pySpark due to things like wrongly typed columns or nulls

## Caution
At the backend of this utility lies a mapping between pandas dtypes and pySpark data types. It is possible that certain type mappings are absent. In that case please create an issue in the repo.


## License
MIT

