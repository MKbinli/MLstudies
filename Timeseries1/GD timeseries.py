import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.tsa.stattools as sts 
import statsmodels.graphics.tsaplots as sgt
import re
import warnings

warnings.filterwarnings('ignore')
sns.set()


dfCensus=pd.read_csv("census_starter.csv")

dfSample=pd.read_csv("sample_submission.csv")

dfTest=pd.read_csv("test.csv")

dfTrain=pd.read_csv("train.csv")

"""
dfCensus.to_excel("census_starter.xlsx")

dfSample.to_excel("sample_submission.xlsx")

dfTest.to_excel("test.xlsx")

dfTrain.to_excel("train.xlsx")
"""

#Check for feature inconsistencies
#The function for finding raw date pattern
def findPattern(datePattern,strData):
    try:
        strInfo=re.findall(datePattern,strData)[0]
    except:
        strInfo=""
    return strInfo


#The function for seperating county id from date string
def seperateCountyId(x):
    datePattern=r"([^=\"]*)_[^=\"]*"
    strInfo=findPattern(datePattern,x)
    return strInfo

#The function for seperating date string from county id
def seperateCountyDate(x):
    datePattern=r"[^=\"]*_([^=\"]*)"
    strInfo=findPattern(datePattern,x)
    return strInfo

def checkColumnsEquality(df,col1,col2):
    return df[col1].equals(df[col2])

dfTrain["cfipsChecked"]=pd.to_numeric(dfTrain["row_id"].apply(seperateCountyId))
dfTrain["dateChecked"]=dfTrain["row_id"].apply(seperateCountyDate)

print("Date Columns are equal? : "+str(checkColumnsEquality(dfTrain,col1="dateChecked",col2="first_day_of_month")))
print("CFIPS Columns are equal? : "+str(checkColumnsEquality(dfTrain,col1="cfipsChecked",col2="cfips")))


dfTest["cfipsChecked"]=pd.to_numeric(dfTest["row_id"].apply(seperateCountyId))
dfTest["dateChecked"]=dfTest["row_id"].apply(seperateCountyDate)

print("Date Columns are equal? : "+str(checkColumnsEquality(dfTest,col1="dateChecked",col2="first_day_of_month")))
print("CFIPS Columns are equal? : "+str(checkColumnsEquality(dfTest,col1="cfipsChecked",col2="cfips")))

columnsToRemoveTrain=["dateChecked","cfipsChecked","row_id", "county", "state", "active"]
columnsToRemoveTest=["dateChecked","cfipsChecked","row_id"]

dfTrain=dfTrain.drop(columns=columnsToRemoveTrain)
dfTest=dfTest.drop(columns=columnsToRemoveTest)
print(dfTrain.head(10))
print(dfTest.tail(10))

#See the features 
dfTrain.columns

dfTrain.info()


dfTest.info()

pd.options.display.max_columns = 4000
pd.options.display.max_rows = 4000

oneStateFreq=dfTrain["cfips"].value_counts().iloc[0]

checkFunc=lambda x: 0 if x==oneStateFreq else 1

#All states have same amount of information inside the train dataset
dfTrain["cfips"].value_counts().apply(checkFunc).sum()

oneStateFreq=dfTest["cfips"].value_counts().iloc[0]

#All states have same amount of information inside the test set
dfTest["cfips"].value_counts().apply(checkFunc).sum()


#Check whether "cfips" of the train set and test set are the same
checkCfips=pd.DataFrame(columns=["trainCfips","testCfips"])
checkCfips["trainCfips"]=dfTrain["cfips"].value_counts().index.sort_values()
checkCfips["testCfips"]=dfTest["cfips"].value_counts().index.sort_values()
def checkCfipsFunc(df):
    if df["trainCfips"].equals(df["testCfips"]):
        print("We checked the equality of cfips values w.r.t. train and test set")
        return True
    else:
        return False

checkCfipsFunc(checkCfips)

#Let's convert the dataset by transposing it w.r.t. "cfips"
def convertData(df,cfips):
    newDf=pd.DataFrame()
    newDf.index=df[df.cfips==1001]["first_day_of_month"].copy()
    df.index=df["first_day_of_month"].copy()
    func=lambda x: x
    for cfip in cfips:
        try:
            newDf[str(cfip)]=df[df.cfips==cfip]["microbusiness_density"].copy()#
        except Exception as e:
            print(e)#For 2020, it does not accept column because it confuse with index 2020 values.
            newDf[str(cfip)+"a"]=df[df.cfips==cfip]["microbusiness_density"].copy()
    return newDf
cfips=list(checkCfips["trainCfips"])
dfTrainTrans=convertData(dfTrain.copy(),cfips)
dfTrainTrans.head(10)

#An example for stationary test that shows 1001 is non-stationary
sts.adfuller(dfTrainTrans["1001"])

sgt.plot_acf(dfTrainTrans["1001"], lags=30, zero = False)
plt.title("ACF 1001", size=24)
plt.show()

sgt.plot_pacf(dfTrainTrans["1001"], lags = 30, zero = False, method = ('ols'))
plt.title("PACF 1001", size=24)
plt.show()
