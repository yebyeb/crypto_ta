import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import schedule
import pytz
#---Binance Connection--------------------------------------------------------------
# binance api
apiKey = ""
secretKey = ""

mailAddress = ""
sendTo = ""

password = ""

# API CONNECT
exchange = ccxt.binance({
"apiKey": apiKey,
"secret": secretKey,
'enableRateLimit': True,

'options': {
'defaultType': 'future' 
},
'enableRateLimit': True
})
#exchange.set_sandbox_mode(True)  
#----PD,TA Integers--------------------------------------------------------------------------
tm = ""
intervalText = ""
###
bool_4h  = True
bool_1d  = True
###
#taAnalysisTime = True
testBool = True
closedCandlePatterns = False
###
barNumber2 = 2 # 2
candleCountLimit = 51 # 37
CandlePattern = ""
Direction = ""
starCount = 0
###
listOfData1Symbol = []
listOfData2Symbol = []
#------------------------
pumbDumpBool = True
i = 0
timeCounter = 60 # 46 normal
###
priceChangePercent = 1000 # 15
priceChangePercentNeg = -1000
###
minVolShowed = -1
maxVolShowed = 8
#################
lenOfSymbolTables = 0
symbol = "BTCUSDT"

processAllPer  = 0 # max 100
dataTxt = ""
startSettingsBool = True
processFutureBool = False

DelistCoPDFuture = ["USDCUSDT"]
DelistCoTAFuture = ["USDCUSDT"]
DelistCoForProcess = ["USDCUSDT"]
OpenPositionsList = []
####### ShortLongProcess --------------------
dataProcessF1 = pd.DataFrame(columns=['currentTime','btcPoz','btcNeg','symbol','symbol2','price','processOption','point','star','candle','rsi','bbands_L','bbands_M','bbands_U','stochrsi_K','stochrsi_D','psar_L','psar_S','psar_R','macd_H','macd_S','ma_25','ma_48'])
listOfProcessOpt = "listOfProcessOpt.txt"
def sortLongInf() :
   
   CurrentTime()
   global dataProcessF1
   #balance = exchange.fetch_balance()
   #if float(balance['total']["USDT"]) >= 1 : # 2
   dataProcessF1.loc[len(dataProcessF1.index)] = [currentTime,btcStarCountPoz,btcStarCountNeg,symbolT,symbolT2,barClosePrice0,Direction,processAllPer,starCount,CandlePattern,tableIndicators['rsi'][1],tableIndicators['bbands_L'][1],tableIndicators['bbands_M'][1],tableIndicators['bbands_U'][1],tableIndicators['stochrsi_K'][1],tableIndicators['stochrsi_D'][1],tableIndicators['psar_L'][1],tableIndicators['psar_S'][1],tableIndicators['psar_R'][1],tableIndicators['macd_H'][1],tableIndicators['macd_S'][1],tableIndicators['ma_25'][1],tableIndicators['ma_48'][1]] 
def processShortLong() : # total yerine free balance ? - acık emirler yok edilsin - anlık close price al

  global dataProcessF,dataProcessF1,BullishProcess,BearishProcess,BearishStart,BullishStart,positionCount  # iki (isimden symbol) bir tane olsun - 

  if not dataProcessF1.empty:
   #reverse data frame
   dataProcessF1 = dataProcessF1.iloc[::-1]

   print("dataProcessF1 : ",dataProcessF1)

   BullishTableCount = 0
   BearishTableCount = 0
   BullishProcess = False
   BearishProcess = False
   BullishStart = False
   BearishStart = False


   #dataProcessF1 = dataProcessF1.sort_values(by='point', ascending=False)      
   dataProcessF = dataProcessF1.reset_index(drop=True) 

   for x in DelistCoForProcess: # eth,btc,bnb.. ayrı bir analiz yhapısı olustur uzun vade veya yuksek kaldırac icin
        dataProcessF = dataProcessF[dataProcessF["symbol"].str.contains(x) == False]


   Recorder()     


   print("BearishTableCount",BearishTableCount,"BullishTableCount",BullishTableCount)
   print("tableDataLenght : ",len(dataProcessF.index))


  else :
      print("empty dataProcessF1")
####### PD --------------------
def PumpDumpData () : 
       
       global i
       
       if i == timeCounter:
        i = 0

       CurrentTime()

       global data2,DelistCoPDFuture,DelistCoTAFuture
       # future
       data = pd.read_json('https://fapi.binance.com/fapi/v1/ticker/24hr')

       data1 = pd.DataFrame(data.sort_values(by=["symbol"], ascending=True), columns=["symbol","lastPrice","quoteVolume","priceChangePercent"])
       

       for x in DelistCoPDFuture:
        data1 = data1[data1["symbol"].str.contains(x) == False]

       data2 = data1[data1['symbol'].str.endswith('USDT')]
       data2 = data2[data2["symbol"].str.endswith('DOWNUSDT') == False]
       data2 = data2[data2["symbol"].str.endswith('UPUSDT') == False]
       data2.drop(data2[data2["lastPrice"] == 0].index, inplace = True)

       pChangePer = data2["priceChangePercent"].values.tolist()

       # delist new listed coins or coins these have not enough candles
       global startSettingsBool,lenOfSymbolTables,listOfData1Symbol,listOfData2Symbol

       if  len(data1.index) != lenOfSymbolTables  :
         if listOfData1Symbol:
          listOfData2Symbol  = data2["symbol"].values.tolist()

          set1 = set(listOfData1Symbol)
          set2 = set(listOfData2Symbol)
          
          missing = list(sorted(set1 - set2))
          added = list(sorted(set2 - set1))

          print('missing:', missing)
          print('added:', added)

          DelistCoPDFuture = DelistCoPDFuture + missing + added  # bir cok koini missing diye yakaliuor düzelt
          DelistCoTAFuture = DelistCoPDFuture + missing + added
          
          #startSettingsBool = True
          print("lenOfSymbolTables not equal data2, symbol length equation started")
          for x in DelistCoPDFuture:
           data2 = data2[data2["symbol"].str.contains(x) == False]
         
          listOfData1Symbol  = data2["symbol"].values.tolist()
          lenOfSymbolTables = len(data1.index)

       if startSettingsBool == True: 
          
          sT = data2['symbol'].to_numpy() 
          for symbolForDel in sT :
            co       = str(symbolForDel[:-4]) + "/USDT"         
            bars   = exchange.fetch_ohlcv(co, timeframe= "1d", since = None, limit = candleCountLimit)
            dfbars = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

            if len(dfbars.index) < candleCountLimit :
             DelistCoTAFuture.append(symbolForDel)
             if len(dfbars.index) < 3 :
              DelistCoPDFuture.append(symbolForDel)
             continue
            time.sleep(0.05)
          for x in DelistCoPDFuture:
           data2 = data2[data2["symbol"].str.contains(x) == False]

          listOfData1Symbol  = data2["symbol"].values.tolist() 
          startSettingsBool = False
          print("updatedSettings","startSettingsBool : ",startSettingsBool) 

       
       # for too many requests
       time.sleep(0.025)

       #i
       global Sdata,Pdata,Vdata
       if i == 0 :
        Sdata = data2["symbol"].values.tolist()
        Pdata = data2["lastPrice"].values.tolist()
        Vdata = data2["quoteVolume"].values.tolist()

       if i != 0:
        Sdata1 = data2["symbol"].values.tolist()
        Pdata1 = data2["lastPrice"].values.tolist()
        Pdata2 = [i - j for i, j in zip(Pdata1, Pdata)]
        Pdata3 = [i / j for i, j in zip(Pdata2, Pdata)]
        PdataACC =  [i * 100 for i in Pdata3]
        
        Vdata1 = data2["quoteVolume"].values.tolist()
        Vdata2 = [i - j for i, j in zip(Vdata1, Vdata)]
        Vdata3 = [i / j for i, j in zip(Vdata2, Vdata)]
        VdataACC =  [i * 100 for i in Vdata3]

        #table0
        global table0,table00
        table0 = pd.DataFrame(list(zip(Sdata,PdataACC,VdataACC,Pdata1,Vdata1,pChangePer)),columns =['Symbol','priceAcc','volAcc','price','volume','pChangePer'])
        table0 = table0[(table0['pChangePer']>= priceChangePercentNeg ) & (table0['pChangePer']<= priceChangePercent)]
        table0 = table0[(table0['volAcc']>= minVolShowed )&(table0['volAcc']<= maxVolShowed )]

        if not table0.empty and Sdata == Sdata1:
         table0.sort_values(by=['priceAcc'], inplace=True, ascending=False)
         table00 = table0.reset_index(drop=True)

         tableNeg0 = table0.iloc[::-1]
         tableNeg00 = tableNeg0.reset_index(drop=True)
   
         #print("symbol",tableNeg00['Symbol'][0],"price",tableNeg00['price'][0],"priceacc",tableNeg00['priceAcc'][0])
         global symbol,symbolPoz2,priceAcc,volAcc,price,symbolNeg,symbolNeg2,priceAccNeg,volAccNeg,priceNeg
         #1 poz
         symbol = table00['Symbol'][0]
         symbolPoz2 = str(symbol[:-4]) + "/USDT"
         priceAcc = table00['priceAcc'][0]
         volAcc = table00['volAcc'][0]
         price = format(float(table00['price'][0]), '.8f')
         #volume = table00['volume'][0]

         #1 neg
         symbolNeg = tableNeg00['Symbol'][0]
         symbolNeg2 = str(symbolNeg[:-4]) + "/USDT"
         priceAccNeg = tableNeg00['priceAcc'][0]
         volAccNeg = tableNeg00['volAcc'][0]
         priceNeg = format(float(tableNeg00['price'][0]), '.8f')
         #volumeNeg = tableNeg00['volume'][0]

# -------------- pump dump test --------------------------------
         if priceAcc > 1 and not symbol :

            print('PUMP0',symbol,'PA0',priceAcc,'VA0',volAcc,'Pr0',price)    

         #1.Dump Datas
         if priceAccNeg < -1 and not symbolNeg :

            print('DUMP0',symbolNeg,'PA0',priceAccNeg,'VA0',volAccNeg,'Pr0',priceNeg)
# ---------------------------------------------------------------
        
        else :
           i = 0
       i = i+1

####### TA --------------------
def CurrentTime() :
   global currentTimeInGreenwich 
   global currentTime

   greenwichTz  = pytz.timezone("Europe/London") 
   timeInGreenwich = datetime.now(greenwichTz)
   currentTimeInGreenwich = timeInGreenwich.strftime("%d/%m/%Y %H:%M:%S")

   #print(timeInGreenwich.hour) # tek tek sayı olarak alma bir döngü yapılabilir

   now = datetime.now()

   currentTime = now.strftime("%d/%m/%Y %H:%M:%S")
   #print("Current Time =", currentTime)
   #print("Current Time G =", currentTimeInGreenwich)
#------------------------------  
def interval_4h():
    global tm,dataTxt,intervalText
    tm = "4h"
    intervalText = "4 hour candle"
    dataTxt = "taDF4h.txt"
    CurrentTime()
    print("I'm working...4h",currentTime)
    TechnicalAnalysis() 
    
def interval_1d():
    global tm,dataTxt,intervalText
    tm = "1d"
    intervalText = "1 day candle"
    dataTxt = "taDF1d.txt"
    CurrentTime()
    print("I'm working...1d",currentTime)  
    TechnicalAnalysis()         

def taTimeIntervals () :
 if bool_4h == True :
  schedule.every().days.at("16:00:10").do(interval_4h) #h_4_00 = 
  schedule.every().days.at("20:00:10").do(interval_4h) #h_4_20 = 
  schedule.every().days.at("00:00:10").do(interval_4h) #h_4_16 = 
  schedule.every().days.at("04:00:10").do(interval_4h) #h_4_12 = 
  schedule.every().days.at("08:00:10").do(interval_4h) #h_4_8 = 
  schedule.every().days.at("12:00:10").do(interval_4h) #h_4_4 = 
 if bool_1d == True :
  schedule.every().day.at("00:00:19").do(interval_1d)
taTimeIntervals()
#------------------------------ 
def Recorder() :
             
             if not dataProcessF.empty :
              with open(dataTxt, 'a') as f:
               df_string = dataProcessF.to_string()
               f.write(df_string)
               f.write('\n')
#------------------------------                    
def Indicators () :

            ################################### (INDICATOR) ########################################

              global tableIndicators,rsi,bbands_L,bbands_M,bbands_U,stochrsi_K,stochrsi_D,psar_L,psar_S,psar_R,macd_H,macd_S,ma_25,ma_48,indicatorPointsBullish,indicatorPointsBearish,rsiPointBullish,rsiPointBearish,bbandPointBullish,bbandPointBearish,stockRSiBullish,stockRSiBearish

              #rsi
              rsi = ta.rsi(dfbarCloseAll, 14) # rsi uyumsuzlugu hesaplama
              rsi = rsi.values.tolist()
              #print(symbolT,rsi,"type",type(rsi))    

              time.sleep(0.01)

              #bbands
              bbands = ta.bbands(dfbarCloseAll,21,2)  # boll ort bant üstü ürta bant altı üst bant üst alt bant üst
              bbands_L = bbands["BBL_21_2.0"].values.tolist()
              bbands_M = bbands["BBM_21_2.0"].values.tolist()
              bbands_U = bbands["BBU_21_2.0"].values.tolist()
              #print(symbolT,bbands,"type",type(bbands))

              time.sleep(0.01)

              #stochrsi 
              stochrsi = ta.stochrsi(dfbarCloseAll,14,14,3,3) # stock rsi kesisim bulma
              stochrsi_K = stochrsi["STOCHRSIk_14_14_3_3"].values.tolist()
              stochrsi_D = stochrsi["STOCHRSId_14_14_3_3"].values.tolist()
              #print(symbolT,stochrsi_K,"type",type(stochrsi_K))

              time.sleep(0.01)

              #psar
              psar = ta.psar(dfbarHighAll,dfbarLowAll,dfbarCloseAll,0.02,0.02,0.2) # sarlar biraz geniş olabilir farklı deger gosteriyor
              psar_L = psar["PSARl_0.02_0.2"].values.tolist()
              psar_S = psar["PSARs_0.02_0.2"].values.tolist()
              psar_R = psar["PSARr_0.02_0.2"].values.tolist()
              #print(symbolT,psar_S,"type",type(psar))  
              #print(symbolT,psar)   
 
              time.sleep(0.01)

              #macd  
              macd = ta.macd(dfbarCloseAll,12,26,9)
              macd_H = macd["MACDh_12_26_9"].values.tolist()
              macd_S = macd["MACDs_12_26_9"].values.tolist()
              #print(symbolT,macd)

              time.sleep(0.01)

              #ma25 ma48
              ma25  = ta.ma("sma",dfbarCloseAll, length = 25)   
              ma_25 = ma25.values.tolist()
              ma48  = ta.ma("sma",dfbarCloseAll, length = 48)  
              ma_48 = ma48.values.tolist()      
              #print(symbolT,ma_25,"type",type(ma_25))

              #fib
              #fibonacci = ta.fwma(dfbarCloseAll,10,True)
              #print(symbolT,fibonacci)
              
              #adx
              #adx = ta.adx(dfbarHighAll,dfbarLowAll,dfbarCloseAll, length = 14)  
              #print(symbolT,adx,"type",type(adx))

              tableIndicators = pd.DataFrame(list(zip(rsi,bbands_L,bbands_M,bbands_U,stochrsi_K,stochrsi_D,psar_L,psar_S,psar_R,macd_H,macd_S,ma_25,ma_48)),columns =['rsi','bbands_L','bbands_M','bbands_U','stochrsi_K','stochrsi_D','psar_L','psar_S','psar_R','macd_H','macd_S','ma_25','ma_48'])
              tableIndicators = tableIndicators.iloc[::-1] # reverse table
              tableIndicators = tableIndicators.reset_index(drop=True)

              indicatorPointsBullish = 0
              indicatorPointsBearish = 0

              rsiPointBullish = 0
              rsiPointBearish = 0
              bbandPointBullish = 0
              bbandPointBearish = 0
              stockRSiBullish = 0
              stockRSiBearish = 0
              # 10 point rsi
              if tableIndicators['rsi'][1] > 75 :
                 indicatorPointsBearish = indicatorPointsBearish + 10
                 rsiPointBearish = rsiPointBearish + 10
              elif tableIndicators['rsi'][1] > 65 :
                 indicatorPointsBearish = indicatorPointsBearish + 5
                 rsiPointBearish = rsiPointBearish + 5
              if tableIndicators['rsi'][1] < 25 :
                 indicatorPointsBullish = indicatorPointsBullish + 10    
                 rsiPointBullish = rsiPointBullish + 10
              elif tableIndicators['rsi'][1] < 35 :
                 indicatorPointsBullish = indicatorPointsBullish + 5  
                 rsiPointBullish = rsiPointBullish + 5
              
              # 10 point bbands
              if tableIndicators['bbands_U'][1] < barHighPrice :
                 indicatorPointsBearish = indicatorPointsBearish + 10
                 bbandPointBearish = bbandPointBearish + 10
              elif tableIndicators['bbands_M'][1] < barClosePrice :
                 indicatorPointsBearish = indicatorPointsBearish + 5
                 bbandPointBearish = bbandPointBearish + 5
                 
              if tableIndicators['bbands_L'][1] > barLowPrice :
                 indicatorPointsBullish = indicatorPointsBullish + 10  
                 bbandPointBullish = bbandPointBullish + 10
              elif tableIndicators['bbands_M'][1] > barClosePrice :
                 indicatorPointsBullish = indicatorPointsBullish + 5
                 bbandPointBullish = bbandPointBullish + 5

              # 10 point stochrsi
              if tableIndicators['stochrsi_K'][1] > 70 :
                 indicatorPointsBearish = indicatorPointsBearish + 5
                 stockRSiBearish = stockRSiBearish + 5
              elif tableIndicators['stochrsi_K'][1] < 20 :
                 indicatorPointsBullish = indicatorPointsBullish + 5
                 stockRSiBullish = stockRSiBullish + 5
              if tableIndicators['stochrsi_D'][1] > 70 :
                 indicatorPointsBearish = indicatorPointsBearish + 5  
                 stockRSiBearish = stockRSiBearish + 5                 # ikiye ayrılabilir stockRSiBearishD stockRSiBearishK diye   
              elif tableIndicators['stochrsi_D'][1] < 20 :
                 indicatorPointsBullish = indicatorPointsBullish + 5
                 stockRSiBullish = stockRSiBullish + 5
                
              #10 point psar
              """if not math.isnan(tableIndicators['psar_S'][1]) :
                 indicatorPoints = indicatorPoints + 5 
                 #print(symbolT,"psar_S",tableIndicators['psar_S'][1],tableIndicators['psar_R'][1])
              if tableIndicators['psar_R'][1] == 1 and not math.isnan(tableIndicators['psar_S'][1]): 
                 print(symbolT,"psar_S",tableIndicators['psar_S'][1],tableIndicators['psar_R'][1],"--------------")
                 indicatorPoints = indicatorPoints + 5  

              if not math.isnan(tableIndicators['psar_L'][1]) :
                 indicatorPoints = indicatorPoints + 5 
                 #print(symbolT,"psar_L",tableIndicators['psar_L'][1],tableIndicators['psar_R'][1])
              if tableIndicators['psar_R'][1] == 1 and not math.isnan(tableIndicators['psar_L'][1]): 
                 print(symbolT,"psar_L",tableIndicators['psar_L'][1],tableIndicators['psar_R'][1],"--------------")
                 indicatorPoints = processHalfPerBearish + 5""" 
#------------------------------
def CheckLowValueInCandles():
              
              global CheckLowValuestar
              global CheckHighValuestar
              global CheckLowValuestar3
              global CheckHighValuestar3
              CheckLowValuestar = 0
              CheckHighValuestar = 0
              CheckLowValuestar3 = 0
              CheckHighValuestar3 = 0

              #global rangeStartValueForAverage

              priceLowCount10 = 0
              priceHighCount10 = 0
              priceLowCount9 = 0
              priceHighCount9 = 0

              for x in range(rangeStartValueForAverage,rangeStartValueForAverage + 10):
                 
                 if barLowPrice < float(dfbarLowAll[len(dfbars.index) - x]) :
                    priceLowCount10 = priceLowCount10 + 1
                 if barHighPrice > float(dfbarHighAll[len(dfbars.index) - x]) :
                    priceHighCount10 = priceHighCount10 + 1

              if  priceLowCount10 == 10 :
                 CheckLowValuestar = CheckLowValuestar + 1 # 1 star - 
                 #print(symbolT,"1 star - low value in 10 candle") 
              if  priceHighCount10 == 10 :
                 CheckHighValuestar = CheckHighValuestar + 1 # 1 star - 
                 #print(symbolT,"1 star - low value in 10 candle")

              for x in range(rangeStartValueForAverage + 1,rangeStartValueForAverage + 10):
                 if x < rangeStartValueForAverage + 9 :
                  if barLowPrice3 < float(dfbarLowAll[len(dfbars.index) - x]) :
                    priceLowCount9 = priceLowCount9 + 1
                  if barHighPrice3 > float(dfbarHighAll[len(dfbars.index) - x]) :
                    priceHighCount9 = priceHighCount9 + 1 

              if  priceLowCount9 == 9 :
                 CheckLowValuestar3 = CheckLowValuestar3 + 1 # 1 star - 
                 #print(symbolT,"1 star - low3 value in 9 candle") 
              if  priceHighCount9 == 9 :
                 CheckHighValuestar3 = CheckHighValuestar3 + 1 # 1 star -
                 #print(symbolT,"1 star - low3 value in 9 candle")                
#------------------------------
def CheckCandles():
              
              ##########CheckCandlesAverageLowOrHigh######################   

              global CheckCandlesAveragePozstar 
              global CheckCandlesAverageNegstar
              CheckCandlesAveragePozstar = 0
              CheckCandlesAverageNegstar = 0 
              global CheckCandlesAveragePozstar3 
              global CheckCandlesAverageNegstar3
              CheckCandlesAveragePozstar3 = 0
              CheckCandlesAverageNegstar3 = 0
   
              global ClosePriceAverage6,ClosePriceAverage12,ClosePriceAverage24,ClosePriceAverage36
              global Close3PriceAverage6,Close3PriceAverage12,Close3PriceAverage24,Close3PriceAverage36
              
              #global Average6CandleCount 
              #global Average12CandleCount 
              #global Average24CandleCount 
              #global Average36CandleCount 

              #global rangeStartValueForAverage

              #Average Close Price 6 Candle

              AllClosePrice6Candle = 0
              AllClose3Price6Candle = 0

              for x in range(rangeStartValueForAverage,rangeStartValueForAverage + Average6CandleCount):

                if x > rangeStartValueForAverage :
                  AllClose3Price6Candle = AllClose3Price6Candle + float(dfbarCloseAll[len(dfbars.index) - x])

                AllClosePrice6Candle = AllClosePrice6Candle + float(dfbarCloseAll[len(dfbars.index) - x])

              ClosePriceAverage6 = (AllClosePrice6Candle / Average6CandleCount ) 
              Close3PriceAverage6 = AllClose3Price6Candle / (Average6CandleCount -1) 
            
              #Average Close Price 12 Candle

              AllLowHighLevel12Candle = 0
              AllClose3Price12Candle = 0
              AllLowHigh3Level12Candle = 0
              AllClosePrice12Candle = 0

              for x in range(rangeStartValueForAverage,rangeStartValueForAverage + Average12CandleCount):
               
                if x > rangeStartValueForAverage :
                 AllLowHigh3Level12Candle = AllLowHigh3Level12Candle + ( float(dfbarHighAll[len(dfbars.index) - x]) - float(dfbarLowAll[len(dfbars.index) - x]) )
                 AllClose3Price12Candle = AllClose3Price12Candle + float(dfbarCloseAll[len(dfbars.index) - x])
             
                AllLowHighLevel12Candle = AllLowHighLevel12Candle + ( float(dfbarHighAll[len(dfbars.index) - x]) - float(dfbarLowAll[len(dfbars.index) - x]) )
                AllClosePrice12Candle = AllClosePrice12Candle + float(dfbarCloseAll[len(dfbars.index) - x])
             
              LowHighLevelAverage12 = AllLowHighLevel12Candle / Average12CandleCount
              LowHighLevel3Average12 = AllLowHigh3Level12Candle / (Average12CandleCount -1 )
              
              ClosePriceAverage12 = (AllClosePrice12Candle / Average12CandleCount)
              Close3PriceAverage12 = AllClose3Price12Candle / (Average12CandleCount -1) 
            
              #Average Close Price 24 Candle

              AllClosePrice24Candle = 0
              AllClose3Price24Candle = 0

              for x in range(rangeStartValueForAverage,rangeStartValueForAverage + Average24CandleCount):

                if x > rangeStartValueForAverage :
                  AllClose3Price24Candle = AllClose3Price24Candle + float(dfbarCloseAll[len(dfbars.index) - x])
                  
                AllClosePrice24Candle = AllClosePrice24Candle + float(dfbarCloseAll[len(dfbars.index) - x])

              ClosePriceAverage24 = (AllClosePrice24Candle / Average24CandleCount)
              Close3PriceAverage24 = AllClose3Price24Candle / (Average24CandleCount -1)
            
              #Average Close Price 36 Candle

              AllLow3Level36Candle = 0
              AllHigh3Level36Candle = 0
              AllClose3Price36Candle = 0
              AllLowLevel36Candle = 0
              AllHighLevel36Candle = 0
              AllClosePrice36Candle = 0

              for x in range(rangeStartValueForAverage,rangeStartValueForAverage + Average36CandleCount):

                if x > rangeStartValueForAverage :
                 AllLow3Level36Candle = AllLow3Level36Candle + float(dfbarLowAll[len(dfbars.index) - x])
                 AllHigh3Level36Candle = AllHigh3Level36Candle + float(dfbarHighAll[len(dfbars.index) - x])
                 AllClose3Price36Candle = AllClose3Price36Candle + float(dfbarCloseAll[len(dfbars.index) - x])

                AllLowLevel36Candle = AllLowLevel36Candle + float(dfbarLowAll[len(dfbars.index) - x])
                AllHighLevel36Candle = AllHighLevel36Candle + float(dfbarHighAll[len(dfbars.index) - x])
                AllClosePrice36Candle = AllClosePrice36Candle + float(dfbarCloseAll[len(dfbars.index) - x])

              HighLevelAverage36  = AllHighLevel36Candle / Average36CandleCount
              High3LevelAverage36 = AllHigh3Level36Candle / (Average36CandleCount - 1)
              

              LowLevelAverage36  = AllLowLevel36Candle / Average36CandleCount  
              Low3LevelAverage36 = AllLow3Level36Candle / (Average36CandleCount - 1) 

              ClosePriceAverage36  = AllClosePrice36Candle / Average36CandleCount
              Close3PriceAverage36 = AllClose3Price36Candle / (Average36CandleCount -1)

              #rangeStartValueForAverage = 3 # reset range star average

              #List Of 4 Average Values 
              ListOfAverage = [ClosePriceAverage6,ClosePriceAverage12,ClosePriceAverage24,ClosePriceAverage36]
              List3OfAverage = [Close3PriceAverage6,Close3PriceAverage12,Close3PriceAverage24,Close3PriceAverage36]
              
              global averageLowCount

              averageLowCount = 0

              for x in ListOfAverage:
                 if x > barClosePrice :
                    averageLowCount = averageLowCount + 1
              if averageLowCount > 3 : 
                CheckCandlesAverageNegstar = CheckCandlesAverageNegstar + 2 #  2 star - lower than 4 average price
                #print(symbolT,"2 star - lower than min 4 average price") 

              elif averageLowCount > 1 : 
                CheckCandlesAverageNegstar = CheckCandlesAverageNegstar + 1 #  1 star - lower than 2 average price
                #print(symbolT,"1 star - lower than min 2 average price")  
              
              if averageLowCount < 1 : 
                CheckCandlesAveragePozstar = CheckCandlesAveragePozstar + 2 #  2 star - lower than 4 average price
                #print(symbolT,"2 star - lower than min 4 average price") 

              elif averageLowCount < 2 : 
                CheckCandlesAveragePozstar = CheckCandlesAveragePozstar + 1 #  1 star - lower than 2 average price
                #print(symbolT,"1 star - lower than min 2 average price")

              averageLow3Count = 0 

              for x in List3OfAverage:
                 if x > barClosePrice3 :
                    averageLow3Count = averageLow3Count + 1
              if averageLow3Count > 3 : 
                CheckCandlesAverageNegstar3 = CheckCandlesAverageNegstar3 + 2 #  2 star - lower than 4 average price
                #print(symbolT,"2 star - lower than min 4 average price") 

              elif averageLow3Count > 1 : 
                CheckCandlesAverageNegstar3 = CheckCandlesAverageNegstar3 + 1 #  1 star - lower than 2 average price
                #print(symbolT,"1 star - lower than min 2 average price")  
              
              if averageLow3Count < 1 : 
                CheckCandlesAveragePozstar3 = CheckCandlesAveragePozstar3 + 2 #  2 star - lower than 4 average price
                #print(symbolT,"2 star - lower than min 4 average price") 

              elif averageLow3Count < 2 : 
                CheckCandlesAveragePozstar3 = CheckCandlesAveragePozstar3 + 1 #  1 star - lower than 2 average price
                #print(symbolT,"1 star - lower than min 2 average price")   

              

              ##########BarLowHighLevelCompareToOtherBars################# 

              global BarLowHighLevelstar
              global BarLowHighLevelstar3
              BarLowHighLevelstar = 0
              BarLowHighLevelstar3 = 0


              if (barHighPrice - barLowPrice) > LowHighLevelAverage12 :
                 
                 BarLowHighLevelstar = BarLowHighLevelstar + 1 # 1 star - low high level higher than average in 10 candle
                 #print(symbolT,"1 star - low high level higher than average in 10 candle")
              if (barHighPrice3 - barLowPrice3) > LowHighLevel3Average12 :
                 
                 BarLowHighLevelstar3 = BarLowHighLevelstar3 + 1   

              ##########BarLowLevelCompareToOtherBars################# 

              global BarLowLevelstar
              global BarHighLevelstar
              global BarLowLevelstar3
              global BarHighLevelstar3
              BarLowLevelstar = 0
              BarHighLevelstar = 0
              BarLowLevelstar3 = 0
              BarHighLevelstar3 = 0

              if barLowPrice < LowLevelAverage36 :
                 
                 BarLowLevelstar = BarLowLevelstar + 1 # 1 star - low level higher than average in 34 candle
                 #print(symbolT,"1 star - low level higher than average in 34 candle") 
              if barHighPrice > HighLevelAverage36 :
                 
                 BarHighLevelstar = BarHighLevelstar + 1

              # candle 3

              if barLowPrice3 < Low3LevelAverage36 :
                 
                 BarLowLevelstar3 = BarLowLevelstar3 + 1 # 1 star - low level higher than average in 34 candle
                 #print(symbolT,"1 star - low level higher than average in 34 candle") 
              if barHighPrice3 > High3LevelAverage36 :
                 
                 BarHighLevelstar3 = BarHighLevelstar3 + 1      
#------------------------------                 
def TechnicalAnalysis () :

         
         global symbolT,dfbars,dataProcessF1

         dataProcessF1.drop(dataProcessF1.index , inplace=True)
         barNumber3 = barNumber2 + 1
         barNumber4 = barNumber3 + 1
         barNumber5 = barNumber4 + 1
         # A
         if not data2.empty:    
           # Coin Candle Data   
           btcRow = data2.loc[data2['symbol'] == 'BTCUSDT']
           tableTA = pd.concat([btcRow, data2.drop(btcRow.index)], axis=0).reset_index(drop=True)
           for x in DelistCoTAFuture:
            tableTA = tableTA[tableTA["symbol"].str.contains(x) == False] 
           #reverse data frame
           #tableTA = tableTA.iloc[::-1]s

           symbolTable = tableTA['symbol'].to_numpy()
           #print("TASymbolTable",symbolTable)

           btcControlBool = True
            
           for symbolT in symbolTable :
            
            global symbolT2

            symbolT2       = str(symbolT[:-4]) + "/USDT"
            
            bars   = exchange.fetch_ohlcv(symbolT2, timeframe= tm, since = None, limit = candleCountLimit)
            dfbars = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
            
            if len(dfbars.index) < candleCountLimit :
             DelistCoTAFuture.append(symbolT)
             if tm == "5m" or tm == "15m" or tm == "30m" :
              DelistCoPDFuture.append(symbolT)
             continue
                
            global dfbarCloseAll,dfbarOpenAll,dfbarHighAll,dfbarLowAll
            
            dfbarOpenAll = dfbars["open"]
            dfbarHighAll = dfbars["high"]
            dfbarLowAll = dfbars["low"]
            dfbarCloseAll = dfbars["close"]

            global barClosePrice0
            # 1 
            barClosePrice0 = float(dfbarCloseAll[len(dfbars.index) - 1])
            barClosePrice0 = format(float(barClosePrice0), '.8f')
            global barOpenPrice,barHighPrice,barLowPrice,barClosePrice
            # 2 3 4 5 6 candle
            barOpenPrice  = float(dfbarOpenAll[len(dfbars.index) - barNumber2])  
            barHighPrice  = float(dfbarHighAll[len(dfbars.index) - barNumber2])
            barLowPrice   = float(dfbarLowAll[len(dfbars.index) - barNumber2])
            barClosePrice = float(dfbarCloseAll[len(dfbars.index) - barNumber2])
            
            global barOpenPrice3,barHighPrice3,barLowPrice3,barClosePrice3

            barOpenPrice3 = float(dfbarOpenAll[len(dfbars.index) - barNumber3])
            barHighPrice3 = float(dfbarHighAll[len(dfbars.index) - barNumber3])
            barLowPrice3 = float(dfbarLowAll[len(dfbars.index) - barNumber3])
            barClosePrice3 = float(dfbarCloseAll[len(dfbars.index) - barNumber3])

            barOpenPrice4 = float(dfbarOpenAll[len(dfbars.index) - barNumber4])
            barClosePrice4 = float(dfbarCloseAll[len(dfbars.index) - barNumber4])

            barOpenPrice5 = float(dfbarOpenAll[len(dfbars.index) - barNumber5])
            barClosePrice5 = float(dfbarCloseAll[len(dfbars.index) - barNumber5])

            #General Values
            global starCount,processPerPoz,processPerNeg,rangeStartValueForAverage,starCountToPrint,CandlePattern,Direction

            mainAllBodyDif = 0.5
            taleAllBodyDif = 0.5
            negBarRealBodyWholeBodyRate = 0.5
            DojiDifference = 0.05 # eksik düzenle yapisini
            RateHeadHandleHammer = 2.2 # farklı formasyonlarda farklı değerler alabilir
            rateNeedles_Body = 2
            RateHeadHandleInverseHammer = 1.8
            starCountToPrint = 3
            rangeStartValueForAverage = barNumber3
            mainbodyDownBodyRate = 1.5
            SpinningUpDownRate = 1.5

            
            global Average6CandleCount,Average12CandleCount,Average24CandleCount,Average36CandleCount,processAllPer

            Average6CandleCount = 4
            Average12CandleCount = 10
            Average24CandleCount = 22
            Average36CandleCount = 34
            
            if (barHighPrice - barLowPrice == 0) or (barHighPrice3 - barLowPrice3 == 0): # because of zero division
               #print(symbolT,"zerodivision")
               continue

            ##########BtcAnalysis#################
            global btcStarCountPoz,btcStarCountNeg,btcAnalysisPointsBullish,btcAnalysisPointsBearish,btcPrice
            if symbolT == "BTCUSDT" and btcControlBool == True :
               btcPrice = barClosePrice
               btcStarCountPoz = 0
               btcStarCountNeg = 0
               btcAnalysisPointsBullish = 0
               btcAnalysisPointsBearish = 0
              
               CheckCandles()
               Indicators ()
 
               btcStarCountPoz = btcStarCountPoz + CheckCandlesAveragePozstar  # bearish if > 2
               btcStarCountNeg = btcStarCountNeg + CheckCandlesAverageNegstar  # bullish if > 2

               # 20 points
               if btcStarCountPoz > 1 :
                 btcAnalysisPointsBearish = btcAnalysisPointsBearish + 10   # test et

               elif btcStarCountPoz >= 1 :
                 btcAnalysisPointsBearish = btcAnalysisPointsBearish + 5  

               if btcStarCountNeg > 1 :
                 btcAnalysisPointsBullish = btcAnalysisPointsBullish + 10  

               elif btcStarCountNeg >= 1 :
                 btcAnalysisPointsBullish = btcAnalysisPointsBullish + 5  

               # btc indicator point
               if indicatorPointsBearish >= 20 : 
                 btcAnalysisPointsBearish = btcAnalysisPointsBearish + 10 
              
               elif indicatorPointsBearish >= 15 :
                 btcAnalysisPointsBearish = btcAnalysisPointsBearish + 5

               if indicatorPointsBullish >= 20 :
                 btcAnalysisPointsBullish = btcAnalysisPointsBullish + 10
             
               elif indicatorPointsBullish >= 15 :
                 btcAnalysisPointsBullish = btcAnalysisPointsBullish + 5 
               
                
               print("btcpozstar",btcStarCountPoz,"btcnegstar",btcStarCountNeg)

               btcControlBool = False 

            # 1A. HAMMER AND DRAGONFLY DOJI (BULLISH) ##############################################################################################################

            #Hammer Values
            hammerstarCount = 0

            # 1a hammer - pozitive (cekic)
            if testBool == True and barClosePrice > barOpenPrice and (barOpenPrice - barLowPrice) > (RateHeadHandleHammer * (barClosePrice - barOpenPrice)) and mainbodyDownBodyRate * (barClosePrice - barOpenPrice) > (barHighPrice - barClosePrice) :


              CheckCandles() # her formasyonda mi hesaplanmali yoksa bir kere tum coinler icin mi (hepsi) ?
              CheckLowValueInCandles()
              hammerstarCount = hammerstarCount + BarLowHighLevelstar + CheckLowValuestar + CheckCandlesAverageNegstar

              # 1 star - pozitive hammer
              hammerstarCount = hammerstarCount + 1
              #print(symbolT," 1 star - pozitive hammer")

              if (barClosePrice - barOpenPrice) / (barHighPrice - barLowPrice) > DojiDifference and hammerstarCount >= starCountToPrint :
                Direction = "Bullish"
                CandlePattern = "Hammer Poz"
                starCount = hammerstarCount
                Indicators()
                processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)
                
              elif hammerstarCount >= starCountToPrint :
                Direction = "Bullish"
                CandlePattern = "Dragonfly Doji Poz"
                starCount = hammerstarCount
                Indicators()
                processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)  # dragonfly - long legged ayrımını yap  
                

            # 1b hammer - negative (cekic)
            elif testBool == True and barOpenPrice > barClosePrice and (barClosePrice - barLowPrice) > (RateHeadHandleHammer * (barOpenPrice - barClosePrice)) and mainbodyDownBodyRate * (barOpenPrice - barClosePrice) > (barHighPrice - barOpenPrice) :
              
              CheckCandles()
              CheckLowValueInCandles()
              hammerstarCount = hammerstarCount + BarLowHighLevelstar + CheckLowValuestar + CheckCandlesAverageNegstar
              
              if (barOpenPrice - barClosePrice) / (barHighPrice - barLowPrice) > DojiDifference and hammerstarCount >= starCountToPrint :
               if closedCandlePatterns == False:
                Direction = "Bullish"
                CandlePattern = "Hammer Neg"
                starCount = hammerstarCount
                Indicators()
                processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)
                
              elif hammerstarCount >= starCountToPrint :
                Direction = "Bullish"
                CandlePattern = "Dragonfly Doji Neg"
                starCount = hammerstarCount
                Indicators()
                processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)  # dragonfly - long legged ayrımını yap   
                


            # 1B. SHOOTING STAR AND GROVESTONE DOJI (BEARISH) ##############################################################################################################################

            #Shooting Star Values
            ShootingStarstarCount = 0

            # 1a shooting star - negative
            if testBool == True and barOpenPrice > barClosePrice and (barHighPrice - barOpenPrice) > (RateHeadHandleHammer * (barOpenPrice - barClosePrice)) and mainbodyDownBodyRate * (barOpenPrice - barClosePrice) > (barClosePrice - barLowPrice) :
              
              CheckCandles()
              CheckLowValueInCandles()
              ShootingStarstarCount = ShootingStarstarCount + CheckCandlesAveragePozstar + CheckHighValuestar + BarLowHighLevelstar
              
              
              #Negative shooting star + 1 star
              ShootingStarstarCount = ShootingStarstarCount + 1


              if (barOpenPrice - barClosePrice) / (barHighPrice - barLowPrice) > DojiDifference and ShootingStarstarCount >= starCountToPrint:
                  Direction = "Bearish"
                  CandlePattern = "Shooting Star Neg"
                  starCount = ShootingStarstarCount
                  Indicators()
                  processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
                  sortLongInf()
                  
                  print(symbolT,Direction,CandlePattern,starCount,processAllPer)
                  
              elif ShootingStarstarCount >= starCountToPrint : 
                  Direction = "Bearish"
                  CandlePattern = "Gravestone Doji Star Neg"
                  starCount = ShootingStarstarCount
                  Indicators()
                  processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
                  sortLongInf()
                  
                  print(symbolT,Direction,CandlePattern,starCount,processAllPer)   # gravestone - long legged ayrımını yap

            # 1b shooting star - positive
            elif testBool == True and barClosePrice > barOpenPrice and (barHighPrice - barClosePrice) > (RateHeadHandleHammer * (barClosePrice - barOpenPrice)) and mainbodyDownBodyRate * (barClosePrice - barOpenPrice) > (barOpenPrice - barLowPrice) :
              
              CheckCandles()
              CheckLowValueInCandles()
              ShootingStarstarCount = ShootingStarstarCount + CheckCandlesAveragePozstar + CheckHighValuestar + BarLowHighLevelstar

              if (barClosePrice - barOpenPrice) / (barHighPrice - barLowPrice) > DojiDifference and ShootingStarstarCount >= starCountToPrint:  
                  Direction = "Bearish"
                  CandlePattern = "Shooting Star Poz"
                  starCount = ShootingStarstarCount
                  Indicators()
                  processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
                  sortLongInf()
                  
                  print(symbolT,Direction,CandlePattern,starCount,processAllPer)  

              elif ShootingStarstarCount >= starCountToPrint :
                  Direction = "Bearish"
                  CandlePattern = "Gravestone Doji Star Poz"
                  starCount = ShootingStarstarCount
                  Indicators()
                  processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
                  sortLongInf()
                  
                  print(symbolT,Direction,CandlePattern,starCount,processAllPer)  # gravestone - long legged ayrımını yap


            # 2A.INVERTED HAMMER (BULLISH) ##############################################################################################################################

            #Inverted Hammer Values
            inversehammerstarCount = 0  

            if closedCandlePatterns == False and testBool == True and barClosePrice > barOpenPrice and (barHighPrice - barClosePrice) > (RateHeadHandleInverseHammer * (barClosePrice - barOpenPrice)) and barClosePrice - barOpenPrice > barOpenPrice - barLowPrice and barOpenPrice3 > barClosePrice and barOpenPrice3 > barClosePrice3 and (barOpenPrice3 - barClosePrice3) / (barHighPrice3 - barLowPrice3) > negBarRealBodyWholeBodyRate and (barClosePrice - barOpenPrice) / (barHighPrice - barLowPrice) > DojiDifference :
              
              CheckCandles()
              inversehammerstarCount = inversehammerstarCount + CheckCandlesAverageNegstar

              # 4 5 candle negative control
              if barOpenPrice4 > barClosePrice4 and barOpenPrice5 > barClosePrice5:
               inversehammerstarCount = inversehammerstarCount + 2
              elif barOpenPrice4 > barClosePrice4 or barOpenPrice5 > barClosePrice5: 
               inversehammerstarCount = inversehammerstarCount + 1 
        
              # 2 yıldız daha eklenecek ( +1 eklenebilir)

              # 1 star - condition is okay
              inversehammerstarCount = inversehammerstarCount + 1

              if inversehammerstarCount >= starCountToPrint : 
               Direction = "Bullish"
               CandlePattern = "Inverted Hammer"
               starCount = inversehammerstarCount
               Indicators()
               processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
               sortLongInf()
               
               print(symbolT,Direction,CandlePattern,starCount,processAllPer)



            # 2B. HANGING MAN (BEARISH) ##############################################################################################################################

            #Hanging Man Values     kullanilmali mi ?
            HangingManstarCount = 0

            # 1a Hanging Man - negative
            if closedCandlePatterns == False and testBool == True and barOpenPrice > barClosePrice and (barClosePrice - barLowPrice) > (RateHeadHandleInverseHammer * (barOpenPrice - barClosePrice)) and barOpenPrice - barClosePrice > barHighPrice - barOpenPrice and (barOpenPrice - barClosePrice) / (barHighPrice - barLowPrice) > DojiDifference :
              
              CheckCandles()
              CheckLowValueInCandles()
              HangingManstarCount = HangingManstarCount + CheckCandlesAveragePozstar + CheckHighValuestar + BarHighLevelstar

              #Negative Hanging Man + 2 star
              HangingManstarCount = HangingManstarCount + 1

              if HangingManstarCount >= starCountToPrint :
               Direction = "Bearish"
               CandlePattern = "Hanging Man Neg"
               starCount = HangingManstarCount
               Indicators()
               processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
               sortLongInf()
               
               print(symbolT,Direction,CandlePattern,starCount,processAllPer)


            # 1b Hanging Man - pozitive
            elif closedCandlePatterns == False and testBool == True and barClosePrice > barOpenPrice and (barOpenPrice - barLowPrice) > (RateHeadHandleInverseHammer * (barClosePrice - barOpenPrice)) and barClosePrice - barOpenPrice > barHighPrice - barClosePrice and (barClosePrice - barOpenPrice) / (barHighPrice - barLowPrice) > DojiDifference :
              
              CheckCandles()
              CheckLowValueInCandles()
              HangingManstarCount = HangingManstarCount + CheckCandlesAveragePozstar + CheckHighValuestar + BarHighLevelstar

              if HangingManstarCount >= starCountToPrint :
               Direction = "Bearish"
               CandlePattern = "Hanging Man Poz"
               starCount = HangingManstarCount
               Indicators()
               processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
               sortLongInf()
               
               print(symbolT,Direction,CandlePattern,starCount,processAllPer)  

     
      
            # 3A.BULLISH SPINNING TOP (BULLISH) ##############################################################################################################################

            
            #Bullish Spinning Top
            bullishSpinningTopstarCount = 0

            if testBool == True and barClosePrice > barOpenPrice and barOpenPrice - barLowPrice > rateNeedles_Body * (barClosePrice - barOpenPrice) and barHighPrice - barClosePrice > rateNeedles_Body * (barClosePrice - barOpenPrice) and SpinningUpDownRate * (barHighPrice - barClosePrice) > barOpenPrice - barLowPrice > barHighPrice - barClosePrice:


              CheckCandles() # her formasyonda mi hesaplanmali yoksa bir kere tum coinler icin mi (hepsi) ?
              CheckLowValueInCandles()
              bullishSpinningTopstarCount = bullishSpinningTopstarCount + BarLowHighLevelstar + CheckLowValuestar + CheckCandlesAverageNegstar

              bullishSpinningTopstarCount = bullishSpinningTopstarCount + 1
              #print(symbolT," 1 star - Bullish Sinning Top")

              if bullishSpinningTopstarCount >= starCountToPrint and (barClosePrice - barOpenPrice) / (barHighPrice - barLowPrice) > DojiDifference:
                Direction = "Bullish"
                CandlePattern = "Bullish Spinning Top"
                starCount = bullishSpinningTopstarCount
                Indicators()
                processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)
 


            # 3B.BEARISH SPINNING TOP (BEARISH) ##############################################################################################################################

            
            #Bearish Sinning Top
            bearishSpinningTopstarCount = 0

            if testBool == True and barOpenPrice > barClosePrice  and barClosePrice - barLowPrice > rateNeedles_Body * (barOpenPrice - barClosePrice) and barHighPrice - barOpenPrice > rateNeedles_Body * (barOpenPrice - barClosePrice)  and SpinningUpDownRate * (barClosePrice - barLowPrice) > barHighPrice - barOpenPrice > barClosePrice - barLowPrice :


              CheckCandles() # her formasyonda mi hesaplanmali yoksa bir kere tum coinler icin mi (hepsi) ?
              CheckLowValueInCandles()
              bearishSpinningTopstarCount = bearishSpinningTopstarCount + BarLowHighLevelstar + CheckCandlesAveragePozstar + CheckHighValuestar

              bearishSpinningTopstarCount = bearishSpinningTopstarCount + 1
              #print(symbolT," 1 star - Bearish Spinning Top")

              if bearishSpinningTopstarCount >= starCountToPrint and (barOpenPrice - barClosePrice) / (barHighPrice - barLowPrice) > DojiDifference:
                Direction = "Bearish"
                CandlePattern = "Bearish Spinning Top"
                starCount = bearishSpinningTopstarCount
                Indicators()
                processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)





            # TWO CANDLE PATTERNS ------------------------------

            # 4A.HARAMI BULLISH AND PIERCING LINE (BULLISH) ##############################################################################################################################              

            #Harami Bullish Values  # bitmedi
            HaramiBullishstarCount = 0

            if closedCandlePatterns == False and testBool == True and barClosePrice > barOpenPrice and barOpenPrice3 - barClosePrice3 > barHighPrice3 - barOpenPrice3 and barOpenPrice3 - barClosePrice3 > barClosePrice3 - barLowPrice3 and barClosePrice - barOpenPrice > barHighPrice - barClosePrice and barClosePrice - barOpenPrice > barOpenPrice - barLowPrice and barOpenPrice3 > barClosePrice3 and barOpenPrice3 > barClosePrice and barHighPrice3 > barHighPrice :
              
              CheckCandles()
              CheckLowValueInCandles()
              HaramiBullishstarCount = HaramiBullishstarCount + BarLowLevelstar + CheckCandlesAverageNegstar
                
              
              if HaramiBullishstarCount >= starCountToPrint :
               
               if barLowPrice > barLowPrice3 :

                HaramiBullishstarCount = HaramiBullishstarCount + CheckLowValuestar3
                HaramiBullishstarCount = HaramiBullishstarCount + BarLowHighLevelstar3

                Direction = "Bullish"
                CandlePattern = "Harami Bullish"
                starCount = HaramiBullishstarCount
                Indicators()
                processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)

               elif closedCandlePatterns == False and barLowPrice < barLowPrice3 :

                HaramiBullishstarCount = HaramiBullishstarCount + BarLowHighLevelstar

                if barClosePrice > ((barOpenPrice3 + barClosePrice3) / 2) :
                 HaramiBullishstarCount = HaramiBullishstarCount + 1

                Direction = "Bullish"
                CandlePattern = "Piercing Line"
                starCount = HaramiBullishstarCount
                Indicators()
                processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)  


            # 4B. HARAMI BEARISH AND DARK CLOUD COVER (BEARISH) ##############################################################################################################################

            #Harami Bearish Method Values  # bitmedi
            HaramiBearishstarCount = 0

            if closedCandlePatterns == False and testBool == True and barOpenPrice > barClosePrice and barClosePrice3 - barOpenPrice3 > barHighPrice3 - barClosePrice3 and barClosePrice3 - barOpenPrice3 > barOpenPrice3 - barLowPrice3 and barOpenPrice - barClosePrice > barHighPrice - barOpenPrice and barOpenPrice - barClosePrice > barClosePrice - barLowPrice and barClosePrice3 > barOpenPrice3 and barClosePrice > barOpenPrice3 and barLowPrice > barLowPrice3 :
                 
              CheckCandles()
              CheckLowValueInCandles()
              HaramiBearishstarCount = HaramiBearishstarCount + BarHighLevelstar + CheckCandlesAveragePozstar  


              if HaramiBearishstarCount >= starCountToPrint :
               
               if barHighPrice3 > barHighPrice :

                HaramiBearishstarCount = HaramiBearishstarCount + CheckHighValuestar3
                HaramiBearishstarCount = HaramiBearishstarCount + BarLowHighLevelstar3

                Direction = "Bearish"
                CandlePattern = "Harami Bearish"
                starCount = HaramiBearishstarCount
                Indicators()
                processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)

               elif closedCandlePatterns == False and barHighPrice3 < barHighPrice :

                HaramiBearishstarCount = HaramiBearishstarCount + BarLowHighLevelstar

                if ((barOpenPrice3 + barClosePrice3) / 2 ) > barClosePrice:
                 
                 HaramiBearishstarCount = HaramiBearishstarCount + 1

                Direction = "Bearish"
                CandlePattern = "Dark Cloud Cover"
                starCount = HaramiBearishstarCount
                Indicators()
                processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
                sortLongInf()
                
                print(symbolT,Direction,CandlePattern,starCount,processAllPer)  



            # 5A. BULLISH ENGULFING (BULLISH) ##############################################################################################################################

            #Bullish Engulfing Method Values 
            BullishEngulfingstarCount = 0

            if closedCandlePatterns == False and testBool == True and barClosePrice > barOpenPrice and barClosePrice - barOpenPrice > barHighPrice - barClosePrice and barClosePrice - barOpenPrice > barOpenPrice - barLowPrice and barOpenPrice3 > barClosePrice3 and  barClosePrice > barOpenPrice3 and barHighPrice > barHighPrice3 :
                 
              CheckCandles()
              CheckLowValueInCandles()
              BullishEngulfingstarCount = BullishEngulfingstarCount + BarLowLevelstar + CheckCandlesAverageNegstar + CheckLowValuestar

              if barLowPrice3 > barLowPrice :
               BullishEngulfingstarCount = BullishEngulfingstarCount + 1

              if BullishEngulfingstarCount >= starCountToPrint :
               
               Direction = "Bullish"
               CandlePattern = "Bullish Engulfing"
               starCount = BullishEngulfingstarCount
               Indicators()
               processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
               sortLongInf()
               
               print(symbolT,Direction,CandlePattern,starCount,processAllPer)

            # 5B. BEARISH ENGULFING (BEARISH) ##############################################################################################################################

            #Bearish Engulfing Method Values 
            BearishEngulfingstarCount = 0      

            if closedCandlePatterns == False and testBool == True and barOpenPrice > barClosePrice and barOpenPrice - barClosePrice > barHighPrice - barOpenPrice and barOpenPrice - barClosePrice > barClosePrice - barLowPrice and barClosePrice3 > barOpenPrice3 and barOpenPrice3 > barClosePrice and barLowPrice3 > barLowPrice :
                 
              CheckCandles()
              CheckLowValueInCandles()
              BearishEngulfingstarCount = BearishEngulfingstarCount + BarHighLevelstar + CheckCandlesAveragePozstar + CheckHighValuestar

              if barHighPrice > barHighPrice3 :
               BearishEngulfingstarCount = BearishEngulfingstarCount + 1

              if BearishEngulfingstarCount >= starCountToPrint :
               
               Direction = "Bearish"
               CandlePattern = "Bearish Engulfing"
               starCount = BearishEngulfingstarCount
               Indicators()
               processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
               sortLongInf()
               
               print(symbolT,Direction,CandlePattern,starCount,processAllPer)      

            
            # 6A. TWEEZER BOTTOM (BULLISH) ##############################################################################################################################

            #Tweezer Bottom Method Values 
            TweezerBottomstarCount = 0

            if closedCandlePatterns == False and testBool == True and barClosePrice > barOpenPrice and taleAllBodyDif > (( barHighPrice3 - barOpenPrice3 ) / (barHighPrice3 - barLowPrice3)) and barOpenPrice3 > barClosePrice3 and barClosePrice - barOpenPrice > barHighPrice - barClosePrice and barClosePrice - barOpenPrice > barOpenPrice - barLowPrice and barLowPrice == barLowPrice3 :
                 
              CheckCandles()
              TweezerBottomstarCount = TweezerBottomstarCount + BarLowLevelstar + CheckCandlesAverageNegstar 
              
              if barClosePrice > barOpenPrice3 : 
               TweezerBottomstarCount = TweezerBottomstarCount + 1

              if (barClosePrice - barOpenPrice) / (barHighPrice - barLowPrice ) > mainAllBodyDif :
                TweezerBottomstarCount = TweezerBottomstarCount + 1

              if TweezerBottomstarCount >= starCountToPrint :
               Direction = "Bullish"
               CandlePattern = "Tweezer Bottom"
               starCount = TweezerBottomstarCount
               Indicators()
               processAllPer = indicatorPointsBullish + btcAnalysisPointsBullish + (starCount * 10)
               sortLongInf()
               
               print(symbolT,Direction,CandlePattern,starCount,processAllPer)

            # 6B. TWEEZER TOP (BEARISH) ##############################################################################################################################

            #Tweezer Top Method Values 
            TweezerTopstarCount = 0

            if closedCandlePatterns == False and testBool == True and barOpenPrice > barClosePrice and taleAllBodyDif > (( barOpenPrice3 - barLowPrice3 ) / (barHighPrice3 - barLowPrice3)) and barClosePrice3 > barOpenPrice3 and barOpenPrice - barClosePrice > barHighPrice - barOpenPrice and barOpenPrice - barClosePrice > barClosePrice - barLowPrice and barHighPrice == barHighPrice3 :
                 
              CheckCandles()
              TweezerTopstarCount = TweezerTopstarCount + BarHighLevelstar + CheckCandlesAveragePozstar 
              
              if barClosePrice < barOpenPrice3 : 
               TweezerTopstarCount = TweezerTopstarCount + 1

              if (barOpenPrice - barClosePrice) / (barHighPrice - barLowPrice ) > mainAllBodyDif :
                TweezerTopstarCount = TweezerTopstarCount + 1

              if TweezerTopstarCount >= starCountToPrint :
               Direction = "Bearish"
               CandlePattern = "Tweezer Top"
               starCount = TweezerTopstarCount
               Indicators()
               processAllPer = indicatorPointsBearish + btcAnalysisPointsBearish + (starCount * 10)
               sortLongInf()
               
               print(symbolT,Direction,CandlePattern,starCount,processAllPer)


            # THREE AND MORE CANDLE PATTERNS ------------------------------
            #...

            # Loop reset values and others..


            ################################### (Classic Chart Patterns) ########################################

            # 1. Triangles  ###################
            # 2. Head & Shoulders  ###################
            # .....


            global averageLowCount
            starCount = 0
            processPerNeg = 0
            processPerPoz = 0
            averageLowCount = 0

            #time sleep for API rate
            time.sleep(0.05)
              

         if not dataProcessF1.empty:
          processShortLong()

while True:
    try:

      if pumbDumpBool == True :
       PumpDumpData ()

      schedule.run_pending() # schedule ta to get data
      
      time.sleep(1.3) # 1.25

    except ccxt.BaseError as Error:
         print ("[ERROR] ", Error )
          
         baslik = "[ERROR] "
         message = Error

         def lastWord(string):   
            # taking empty string
            newstring = ""
     
            # calculating length of string
            length = len(string)
     
            # traversing from last
            for i in range(length-1, 0, -1):
        
             # if space is occurred then return
             if(string[i] == " "):
           
                # return reverse of newstring
                return newstring[::-1]
             else:
                newstring = newstring + string[i]
         

         if "binance does not have market symbol" in str(message):
            lastWord(str(message))
            print("message",message)
            

            DelistedSymbol = str(lastWord(str(message))[:-5]) + "USDT"
            print("DelistedSymbol: ", DelistedSymbol)
            DelistCoPDFuture.append(DelistedSymbol)
            DelistCoTAFuture.append(DelistedSymbol)

         schedule.clear()
         print("cleared schedule.")
         dataProcessF1.drop(dataProcessF1.index , inplace=True)
         listOfData1Symbol = []
         listOfData2Symbol = []
         lenOfSymbolTables = 0
         startSettingsBool = True   # normalde acik
         PumpDumpData ()
         print("cleared dataProcessF1.")
         taTimeIntervals()
         print("start again schedule..")
         continue
    except ConnectionResetError as Error1:
         print ("[ERROR1] ", Error1 )

         baslik = "[ERROR1] "
         message = Error1

         schedule.clear() 
         print("cleared schedule.")
         dataProcessF1.drop(dataProcessF1.index , inplace=True)
         startSettingsBool = True
         PumpDumpData ()
         taTimeIntervals()
         print("start again schedule..")

         continue
    except ConnectionRefusedError as Error2:
         print ("[ERROR2] ", Error2 )

         baslik = "[ERROR2] "
         message = Error2

         schedule.clear() 
         print("cleared schedule.")
         dataProcessF1.drop(dataProcessF1.index , inplace=True)
         startSettingsBool = True
         PumpDumpData ()
         taTimeIntervals()
         print("start again schedule..")

         continue
    except ConnectionAbortedError as Error3:
         print ("[ERROR3] ", Error3 )

         baslik = "[ERROR3] "
         message = Error3

         schedule.clear() 
         print("cleared schedule.")
         dataProcessF1.drop(dataProcessF1.index , inplace=True)
         startSettingsBool = True
         PumpDumpData ()
         taTimeIntervals()
         print("start again schedule..")
         continue
    except ZeroDivisionError as Error4:
         print ("[ERROR4] ", Error4 )
         print("symbol", symbol)
         baslik = "[ERROR4] "
         message = Error4

         if "division" in str(message):
            schedule.clear() 
            print("cleared schedule.")
            dataProcessF1.drop(dataProcessF1.index , inplace=True)
            startSettingsBool = True
            PumpDumpData ()
            taTimeIntervals()
            print("start again schedule..")

         continue
    except Exception as Error5:
         print ("[ERROR5] ", Error5 )

         baslik = "[ERROR5] "
         message = Error5

         schedule.clear()
         print("cleared schedule.")
         dataProcessF1.drop(dataProcessF1.index , inplace=True)
         startSettingsBool = True
         PumpDumpData ()
         print("cleared dataProcessF1.")
         taTimeIntervals()
         print("start again schedule..")

         continue
