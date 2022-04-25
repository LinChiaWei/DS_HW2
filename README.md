# DS_HW2

# **策略想法 :**
  使用預言家模型，預測接續訓練資料的未來天數的股市價格。  
  利用預測出的價格，搭配設計的股市策略演算法，決定在未來實際上要執行的投資動作。
  
# **資料預處理：**
    * 為了使用預言家模型，給予訓練及測試資料假定的日期
    * 因為此模型加入資料特徵的訓練，因此將訓練及測試資料進行合併，加入計算的特徵資料型態，後續再分割
    * 分別計算各個特徵，包含移動平均線(Simple Moving Average,SMA)、指數移動平均線(Exponential Moving Average,EMA)、相對強弱指數(Relative Strong Index,RSI)、異同平滑移動平均線(Moving Average Convergence & Divergence,MACD)

## **特徵介紹 :**
  總共新增9個新的特徵，分別是SMA_3, SMA_7, SMA_30, EMA_3, EMA_7, EMA_30, RSI, MACD, MACD_signal
  * SMA : 一段時間的股價的平均值
  * EMA : 根據日期指數遞減加權，計算移動平均值，日期越近權重越高
  * RSI : （一定時間內）漲幅平均值 ÷〔 （一定時間內）漲幅平均值 ＋（一定時間內）日跌幅平均值 〕× 100
  * MACD : 透過EMA指數計算出離差值(DIF)，再取DIF的移動平均


# **模型建立：**
    使用facebook開發的時間序列預測模型Prophet
    模型架構如下：
        使用加法模型：y(t)=g(t)+s(t)+h(t)+ε(t)
         g(t)：趨勢的影響
         s(t)：季節性的影響
         h(t)：節日的影響
         ε(t)：誤差

### Trend
   ##### prophet使用兩種趨勢函數：
      1.Linear用於不飽和預測，公式如下：
 ![image](https://github.com/LinChiaWei/DS_HW/blob/main/images/4.png)
      
      2.Logistic用於飽和預測，公式如下：
   ![image](https://github.com/LinChiaWei/DS_HW/blob/main/images/5.png)      
   
   ##### 轉折點
      此外Prophet加入了轉折點(change point)的概念，讓趨勢函數在不同時間內有不同的成長率k，公式如下：
   ![image](https://github.com/LinChiaWei/DS_HW/blob/main/images/3.png) 
      
### Seasonlity
      prophet用傅立葉級數描述季節性，公式如下：
   ![image](https://github.com/LinChiaWei/DS_HW/blob/main/images/1.png) 
   
### Holiday
      將不同假日所造成的影響列入考量，公式如下：
   ![image](https://github.com/LinChiaWei/DS_HW/blob/main/images/2.png)    
   
  
# **股市投資演算法 :**
  想法主要是透過未來的股票漲跌趨勢，去判斷要買進還是要賣出。因為利益計算皆使用開盤價，因此過程皆使用開盤價判斷。  
  漲跌情況一共可以分成四種:
  1. 未來2天皆大於今天   
    `此趨勢為漲幅，如果是第一天或是沒有股票的情況下會進行買進；如果狀態為賣空，會進行買進；其他情況則不進行操作`
  2. 未來2天皆小於今天  
    `此趨勢為跌幅，如果身上有股票，進行賣出；如果身上沒有，則進行賣空；其他情況則不進行操作`
  3. 未來第1天漲；第2天跌   
    `此趨勢為上下浮動，因此策略不進行操作`
  4. 未來第1天跌；第2天漲  
    `此趨勢為上下浮動，因此策略不進行操作`  
    
最後兩天弱趨勢為漲，第18天進行買進，反之，進行賣出，盡可能清空身上的股票
