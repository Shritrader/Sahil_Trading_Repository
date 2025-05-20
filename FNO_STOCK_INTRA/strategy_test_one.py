import pandas as pd
import tkinter as tk
import time
import csv
from datetime import datetime
import pytz

# Global variables
Precision = 2
trades = []

# Read data from CSV
data = pd.read_csv(r"US500m_S_engine.csv")

def update_data():
    global data
    data = pd.read_csv(r"US500m_S_engine.csv")
    data.to_csv('data_up.csv', index=False)

printtradesheet = 1


# --------------------------------INDICATER ------------------------------------------------------

def strategy1():
    global trades, data

    # Initialize strategy-specific variables
    ShortEntryPrice = 0
    LongEntryPrice = 0
    Flag = 0
    LongTarget = 0
    ShortTarget = 0
    LongStopP = 0
    ShortStopP = 0
    LongStopA = 0
    ShortStopA = 0
    LongStop = 0
    ShortStop = 0
    LongTargetP = 0
    ShortTargetP = 0
    LongTargetA = 0
    ShortTargetA = 0
    LastEntryPrice = 0
    ShortTrades = 0
    LongTrades = 0
    HighestHigh = 0
    LowestLow = 0
    LongTrailP = 0
    ShortTrailP = 0
    LongTrailA = 0
    ShortTrailA = 0
    ExitBarNo = 0
    TradeBarnumber = 0
    TradesTaken = 0
    LongTrade = 0
    ShortTrade = 0
    LongSignal = 0
    ShortSignal = 0
    DateOfTrade = 0
    DateOfTime = 0
    LastTradeType = 0
    Exit_price = 0
    Exit_time = 0
    Exit_action = ""

    # Read settings from settings.csv file
    settings_df = pd.read_csv('settings.csv')

    # Extract the settings for strategy 1 (case-sensitive match)
    strategy1_settings = settings_df[settings_df['Strategy'] == 'strategy1'].iloc[0]

    # Assign settings to variables

    strategy_name = (strategy1_settings['Strategy'])
    Segment = int(strategy1_settings['Segment'])
    QtyAbs = int(strategy1_settings['QtyAbs'])
    Qty = int(strategy1_settings['Qty'])
    Capital = int(strategy1_settings['Capital'])
    IntraDayExit = int(strategy1_settings['IntraDayExit'])
    IntraExitTime = int(strategy1_settings['IntraExitTime'])
    LongOnly = int(strategy1_settings['LongOnly'])
    ShortOnly = int(strategy1_settings['ShortOnly'])
    LongAlternate = int(strategy1_settings['LongAlternate'])
    ShortAlternate = int(strategy1_settings['ShortAlternate'])
    UndisputedLong = int(strategy1_settings['UndisputedLong'])
    UndisputedShort = int(strategy1_settings['UndisputedShort'])
    LSL_P = float(strategy1_settings['LSL_P'])
    SSL_P = float(strategy1_settings['SSL_P'])
    LSL_A = float(strategy1_settings['LSL_A'])
    SSL_A = float(strategy1_settings['SSL_A'])
    LT_P = float(strategy1_settings['LT_P'])
    ST_P = float(strategy1_settings['ST_P'])
    LT_A = float(strategy1_settings['LT_A'])
    ST_A = float(strategy1_settings['ST_A'])
    LTrailPercent = float(strategy1_settings['LTrailPercent'])
    STrailPercent = float(strategy1_settings['STrailPercent'])
    LTrailAbs = float(strategy1_settings['LTrailAbs'])
    STrailAbs = float(strategy1_settings['STrailAbs'])
    AllowedTradesLong = int(strategy1_settings['AllowedTradesLong'])
    AllowedTradesShort = int(strategy1_settings['AllowedTradesShort'])
    AllowedTrades = int(strategy1_settings['AllowedTrades'])
    LETime = int(strategy1_settings['LETime'])
    LXTime = int(strategy1_settings['LXTime'])
    SETime = int(strategy1_settings['SETime'])
    SXTime = int(strategy1_settings['SXTime'])
    value1 = int(strategy1_settings['value1'])
    value2 = int(strategy1_settings['value2'])
    value3 = float(strategy1_settings['value3'])
    value4 = float(strategy1_settings['value4'])
    value5 = float(strategy1_settings['value5'])
    value6 = float(strategy1_settings['value6'])
    value7 = float(strategy1_settings['value7'])
    value8 = float(strategy1_settings['value8'])
    value9 = float(strategy1_settings['value9'])
    value10 = float(strategy1_settings['value10'])

    # Pre-calculate indicators outside the loop
    data['value1'] = data['open'] - data['close']
    data['value2'] = data['high'] - data['low']
    data['value1_sum'] = data['value1'].rolling(window=value1).sum()
    data['value2_sum'] = data['value2'].rolling(window=value2).sum()
    data['myindi'] = (data['value1_sum'] / data['value2_sum']) * 100

    # Iterate through data for strategy 1
    for i in range(1, len(data)):
        # ------------------------------- INTRA EXIT -------------------------------------------------------

        # next day trade reset
        if data['date'].iloc[i] != data['date'].iloc[i - 1]:
            LongTrade = 0
            ShortTrade = 0
            TradesTaken = 0
            opend = data['open'].iloc[i]
            x = 1
        else:
            x = 0

        # trade initialize
        LongSignal = 0
        ShortSignal = 0

        # Signal generation based on myindiz
        if Flag < 1 and Flag == 0 and 1000 < data['time'].iloc[i] <= 1530:
            if data['myindi'].iloc[i] > value3 and data['myindi'].iloc[i - 1] <= value3:
                LongSignal = 1

        if Flag > -1 and Flag == 0 and 1000 < data['time'].iloc[i] < 1530:
            if data['myindi'].iloc[i] < value4 and data['myindi'].iloc[i - 1] >= value4:
                ShortSignal = 1

        # ------------------------------BUY SELL CHECK--------------------------------------------

        if LongSignal == 1 and ShortSignal == 1:
            LongSignal = 0
            ShortSignal = 0

        if LongOnly == 1 and ShortSignal == 1:
            if Flag == 1:
                # exit long position
                Exit_Date = data['date'].iloc[i]
                Exit_price = data['close'].iloc[i]
                Exit_time = data['time'].iloc[i]
                Exit_action = "El"
                Flag = 0
            ShortSignal = 0

        if ShortOnly == 1 and LongSignal == 1:
            if Flag == -1:
                # exit short position
                Exit_price = data['close'].iloc[i]
                Exit_Date = data['date'].iloc[i]
                Exit_time = data['time'].iloc[i]
                Exit_action = "ES"
                Flag = 0
            LongSignal = 0

        # ------------------------------Signal Entry--------------------------------------------

        if LongSignal == 1 and Flag != 1 and Flag == 0 and LETime <= data['time'].iloc[
            i] <= LXTime and LongTrade < AllowedTradesLong and TradesTaken < AllowedTrades and (
                LongAlternate == 0 or (LongAlternate == 1 and (LastTradeType == -1 or LastTradeType == 0))
        ) and (
                UndisputedShort == 0
        ):
            Action = "BUY"
            Flag = 1
            LastTradeType = 1
            DateOfTrade = data['date'].iloc[i]
            DateOfTime = data['time'].iloc[i]
            TradeBarnumber = i
            HighestHigh = data['high'].iloc[i]
            LowestLow = data['low'].iloc[i]
            LongTrade += 1
            TradesTaken += 1
            LongEntryPrice = data['close'].iloc[i]
            LastEntryPrice = data['close'].iloc[i]
            if LSL_P != 0:
                LongStopP = LongEntryPrice - (LongEntryPrice * 0.01 * LSL_P)
            if LT_P != 0:
                LongTargetP = LongEntryPrice + (LongEntryPrice * 0.01 * LT_P)
            if LTrailPercent != 0:
                LongTrailP = (data['close'].iloc[i] * 0.01 * LTrailPercent)
            if LTrailAbs != 0:
                LongTrailA = LTrailAbs
            if LSL_A != 0:
                LongStopA = LongEntryPrice - LSL_A
            if LT_A != 0:
                LongTargetA = LongEntryPrice + LT_A

            # Qty, entrydate,entrytime,entryprice,exitdate,exittime,exitprice,absqty

            trades.append({
                'strategy': strategy_name,
                'entry_action': Action,
                'SL': LongStopP  if LongStopP > LongStopA else LongStopA ,
                'TP': LongTargetP if LongTargetP <  LongTargetA else LongTargetA,
                'qty': +Qty,
                'entry_date': DateOfTrade,
                'entry_time': DateOfTime,
                'entry_price': LastEntryPrice,

            })

        if ShortSignal == 1 and Flag != -1 and Flag == 0 and SETime <= data['time'].iloc[
            i] <= SXTime and ShortTrade < AllowedTradesShort and TradesTaken < AllowedTrades and (
                ShortAlternate == 0 or (ShortAlternate == 1 and (LastTradeType == 1 or LastTradeType == 0))
        ) and (
                UndisputedLong == 0
        ):
            Action = "SELL"
            Flag = -1
            LastTradeType = -1
            DateOfTrade = data['date'].iloc[i]
            DateOfTime = data['time'].iloc[i]
            TradeBarnumber = i
            HighestHigh = data['high'].iloc[i]
            LowestLow = data['low'].iloc[i]
            ShortTrade += 1
            TradesTaken += 1
            ShortEntryPrice = data['close'].iloc[i]
            LastEntryPrice = data['close'].iloc[i]
            if SSL_P != 0:
                ShortStopP = ShortEntryPrice + (ShortEntryPrice * 0.01 * SSL_P)
            if ST_P != 0:
                ShortTargetP = ShortEntryPrice - (ShortEntryPrice * 0.01 * ST_P)
            if STrailPercent != 0:
                ShortTrailP = (data['close'].iloc[i] * 0.01 * STrailPercent)
            if STrailAbs != 0:
                ShortTrailA = STrailAbs
            if SSL_A != 0:
                ShortStopA = ShortEntryPrice + SSL_A
            if ST_A != 0:
                ShortTargetA = ShortEntryPrice - ST_A

            # Qty, entrydate,entrytime,entryprice,exitdate,exittime,exitprice,absqty

            trades.append({
                'strategy': strategy_name,
                'entry_action': Action,
                'SL': ShortStopP if ShortStopP < ShortStopA else ShortStopA,
                'TP': ShortTargetP if ShortTargetP > ShortTargetA else ShortTargetA,
                'qty': -Qty,
                'entry_date': DateOfTrade,
                'entry_time': DateOfTime,
                'entry_price': LastEntryPrice,

            })

        # ----------------------------STOP TGT SELECTION-----------------------------------------------

        if Flag == 1 and data['high'].iloc[i] > HighestHigh:
            HighestHigh = data['high'].iloc[i]
        if Flag == 1 and data['low'].iloc[i] < LowestLow:
            LowestLow = data['low'].iloc[i]

        LongStop = 0
        if LSL_P != 0 and LongStop == 0:
            LongStop = LongStopP
        if LTrailPercent != 0 and (LongStop == 0 or HighestHigh - LongTrailP > LongStopP):
            LongStop = round(HighestHigh - LongTrailP, Precision)
        if LTrailAbs != 0 and (LongStop == 0 or HighestHigh - LongTrailA > LongStop):
            LongStop = round(HighestHigh - LongTrailA, Precision)
        if LSL_A != 0 and (LongStop == 0 or LongStopA > LongStop):
            LongStop = LongStopA

        LongTarget = 0
        if LT_A != 0 and LongTargetA > LongTarget:
            LongTarget = LongTargetA
        if LT_P != 0 and (LongTarget == 0 or LongTargetP < LongTarget):
            LongTarget = LongTargetP

        ShortStop = 0
        if SSL_P != 0 and ShortStop == 0:
            ShortStop = ShortStopP
        if STrailPercent != 0 and (ShortStop == 0 or (LowestLow + ShortTrailP) < ShortStop):
            ShortStop = round(LowestLow + ShortTrailP, Precision)
        if STrailAbs != 0 and (ShortStop == 0 or (LowestLow + ShortTrailA) < ShortStop):
            ShortStop = round(LowestLow + ShortTrailA, Precision)
        if SSL_A != 0 and (ShortStop == 0 or ShortStopA < ShortStop):
            ShortStop = ShortStopA

        ShortTarget = 0
        if ST_A != 0 and ShortTargetA < ShortTarget:
            ShortTarget = ShortTargetA
        if ST_P != 0 and (ShortTarget == 0 or ShortTargetP < ShortTarget):
            ShortTarget = ShortTargetP

        # ----------------------------Exit Conditions-----------------------------------------------

        if Flag == 1 and data['close'].iloc[i] >= LongTarget and LongTarget != 0:
            Exit_price = LongTarget
            Exit_time = data['time'].iloc[i]
            Exit_action = "LT"
            Flag = 0
        if Flag == 1 and data['close'].iloc[i] <= LongStop and LongStop != 0:
            Exit_price = LongStop
            Exit_time = data['time'].iloc[i]
            Exit_action = "LSL"
            Flag = 0
        if Flag == -1 and data['close'].iloc[i] <= ShortTarget and ShortTarget != 0:
            Exit_price = ShortTarget
            Exit_time = data['time'].iloc[i]
            Exit_action = "ST"
            Flag = 0
        if Flag == -1 and data['close'].iloc[i] >= ShortStop and ShortStop != 0:
            Exit_price = ShortStop
            Exit_time = data['time'].iloc[i]
            Exit_action = "SSL"
            Flag = 0

        # Intra-day exit logic
        if Flag != 0 and IntraDayExit == 1 and data['time'].iloc[i] >= IntraExitTime:
            Exit_price = data['close'].iloc[i]
            Exit_time = data['time'].iloc[i]
            Exit_action = "INTRA"
            Flag = 0

        if Exit_action:
            trades[-1].update({
                'exit_date': data['date'].iloc[i],
                'exit_time': Exit_time,
                'exit_price': Exit_price,
                'exit_action': Exit_action,
            })

            Exit_action = ""

    if printtradesheet == 1:
        # Convert trades list to DataFrame and save to CSV
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(f"trades_{strategy_name}.csv", index=False)

        # print(f"{strategy_name} tradesheet generated successfully.")
def strategy2():
    global trades, data

    # Initialize strategy-specific variables
    ShortEntryPrice = 0
    LongEntryPrice = 0
    Flag = 0
    LongTarget = 0
    ShortTarget = 0
    LongStopP = 0
    ShortStopP = 0
    LongStopA = 0
    ShortStopA = 0
    LongStop = 0
    ShortStop = 0
    LongTargetP = 0
    ShortTargetP = 0
    LongTargetA = 0
    ShortTargetA = 0
    LastEntryPrice = 0
    ShortTrades = 0
    LongTrades = 0
    HighestHigh = 0
    LowestLow = 0
    LongTrailP = 0
    ShortTrailP = 0
    LongTrailA = 0
    ShortTrailA = 0
    ExitBarNo = 0
    TradeBarnumber = 0
    TradesTaken = 0
    LongTrade = 0
    ShortTrade = 0
    LongSignal = 0
    ShortSignal = 0
    DateOfTrade = 0
    DateOfTime = 0
    LastTradeType = 0
    Exit_price = 0
    Exit_time = 0
    Exit_action = ""

    # Read settings from settings.csv file
    settings_df = pd.read_csv('settings.csv')

    # Extract the settings for strategy 1 (case-sensitive match)
    strategy1_settings = settings_df[settings_df['Strategy'] == 'strategy2'].iloc[0]

    # Assign settings to variables

    strategy_name = (strategy1_settings['Strategy'])
    Segment = int(strategy1_settings['Segment'])
    QtyAbs = int(strategy1_settings['QtyAbs'])
    Qty = int(strategy1_settings['Qty'])
    Capital = int(strategy1_settings['Capital'])
    IntraDayExit = int(strategy1_settings['IntraDayExit'])
    IntraExitTime = int(strategy1_settings['IntraExitTime'])
    LongOnly = int(strategy1_settings['LongOnly'])
    ShortOnly = int(strategy1_settings['ShortOnly'])
    LongAlternate = int(strategy1_settings['LongAlternate'])
    ShortAlternate = int(strategy1_settings['ShortAlternate'])
    UndisputedLong = int(strategy1_settings['UndisputedLong'])
    UndisputedShort = int(strategy1_settings['UndisputedShort'])
    LSL_P = float(strategy1_settings['LSL_P'])
    SSL_P = float(strategy1_settings['SSL_P'])
    LSL_A = float(strategy1_settings['LSL_A'])
    SSL_A = float(strategy1_settings['SSL_A'])
    LT_P = float(strategy1_settings['LT_P'])
    ST_P = float(strategy1_settings['ST_P'])
    LT_A = float(strategy1_settings['LT_A'])
    ST_A = float(strategy1_settings['ST_A'])
    LTrailPercent = float(strategy1_settings['LTrailPercent'])
    STrailPercent = float(strategy1_settings['STrailPercent'])
    LTrailAbs = float(strategy1_settings['LTrailAbs'])
    STrailAbs = float(strategy1_settings['STrailAbs'])
    AllowedTradesLong = int(strategy1_settings['AllowedTradesLong'])
    AllowedTradesShort = int(strategy1_settings['AllowedTradesShort'])
    AllowedTrades = int(strategy1_settings['AllowedTrades'])
    LETime = int(strategy1_settings['LETime'])
    LXTime = int(strategy1_settings['LXTime'])
    SETime = int(strategy1_settings['SETime'])
    SXTime = int(strategy1_settings['SXTime'])
    value1 = int(strategy1_settings['value1'])
    value2 = int(strategy1_settings['value2'])
    value3 = float(strategy1_settings['value3'])
    value4 = float(strategy1_settings['value4'])
    value5 = float(strategy1_settings['value5'])
    value6 = float(strategy1_settings['value6'])
    value7 = float(strategy1_settings['value7'])
    value8 = float(strategy1_settings['value8'])
    value9 = float(strategy1_settings['value9'])
    value10 = float(strategy1_settings['value10'])

    # Pre-calculate indicators outside the loop
    data['value1'] = data['open'] - data['close']
    data['value2'] = data['high'] - data['low']
    data['value1_sum'] = data['value1'].rolling(window=value1).sum()
    data['value2_sum'] = data['value2'].rolling(window=value2).sum()
    data['myindi'] = (data['value1_sum'] / data['value2_sum']) * 100

    # Iterate through data for strategy 1
    for i in range(1, len(data)):
        # ------------------------------- INTRA EXIT -------------------------------------------------------

        # next day trade reset
        if data['date'].iloc[i] != data['date'].iloc[i - 1]:
            LongTrade = 0
            ShortTrade = 0
            TradesTaken = 0
            opend = data['open'].iloc[i]
            x = 1
        else:
            x = 0

        # trade initialize
        LongSignal = 0
        ShortSignal = 0

        # Signal generation based on myindiz
        if Flag < 1 and Flag == 0 and 1000 < data['time'].iloc[i] <= 1530:
            if data['myindi'].iloc[i] > value3 and data['myindi'].iloc[i - 1] <= value3:
                LongSignal = 1

        if Flag > -1 and Flag == 0 and 1000 < data['time'].iloc[i] < 1530:
            if data['myindi'].iloc[i] < value4 and data['myindi'].iloc[i - 1] >= value4:
                ShortSignal = 1

        # ------------------------------BUY SELL CHECK--------------------------------------------

        if LongSignal == 1 and ShortSignal == 1:
            LongSignal = 0
            ShortSignal = 0

        if LongOnly == 1 and ShortSignal == 1:
            if Flag == 1:
                # exit long position
                Exit_Date = data['date'].iloc[i]
                Exit_price = data['close'].iloc[i]
                Exit_time = data['time'].iloc[i]
                Exit_action = "El"
                Flag = 0
            ShortSignal = 0

        if ShortOnly == 1 and LongSignal == 1:
            if Flag == -1:
                # exit short position
                Exit_price = data['close'].iloc[i]
                Exit_Date = data['date'].iloc[i]
                Exit_time = data['time'].iloc[i]
                Exit_action = "ES"
                Flag = 0
            LongSignal = 0

        # ------------------------------Signal Entry--------------------------------------------

        if LongSignal == 1 and Flag != 1 and Flag == 0 and LETime <= data['time'].iloc[
            i] <= LXTime and LongTrade < AllowedTradesLong and TradesTaken < AllowedTrades and (
                LongAlternate == 0 or (LongAlternate == 1 and (LastTradeType == -1 or LastTradeType == 0))
        ) and (
                UndisputedShort == 0
        ):
            Action = "BUY"
            Flag = 1
            LastTradeType = 1
            DateOfTrade = data['date'].iloc[i]
            DateOfTime = data['time'].iloc[i]
            TradeBarnumber = i
            HighestHigh = data['high'].iloc[i]
            LowestLow = data['low'].iloc[i]
            LongTrade += 1
            TradesTaken += 1
            LongEntryPrice = data['close'].iloc[i]
            LastEntryPrice = data['close'].iloc[i]
            if LSL_P != 0:
                LongStopP = LongEntryPrice - (LongEntryPrice * 0.01 * LSL_P)
            if LT_P != 0:
                LongTargetP = LongEntryPrice + (LongEntryPrice * 0.01 * LT_P)
            if LTrailPercent != 0:
                LongTrailP = (data['close'].iloc[i] * 0.01 * LTrailPercent)
            if LTrailAbs != 0:
                LongTrailA = LTrailAbs
            if LSL_A != 0:
                LongStopA = LongEntryPrice - LSL_A
            if LT_A != 0:
                LongTargetA = LongEntryPrice + LT_A

            # Qty, entrydate,entrytime,entryprice,exitdate,exittime,exitprice,absqty

            trades.append({
                'strategy': strategy_name,
                'entry_action': Action,
                'SL': LongStopP  if LongStopP > LongStopA else LongStopA ,
                'TP': LongTargetP if LongTargetP <  LongTargetA else LongTargetA,
                'qty': +Qty,
                'entry_date': DateOfTrade,
                'entry_time': DateOfTime,
                'entry_price': LastEntryPrice,

            })

        if ShortSignal == 1 and Flag != -1 and Flag == 0 and SETime <= data['time'].iloc[
            i] <= SXTime and ShortTrade < AllowedTradesShort and TradesTaken < AllowedTrades and (
                ShortAlternate == 0 or (ShortAlternate == 1 and (LastTradeType == 1 or LastTradeType == 0))
        ) and (
                UndisputedLong == 0
        ):
            Action = "SELL"
            Flag = -1
            LastTradeType = -1
            DateOfTrade = data['date'].iloc[i]
            DateOfTime = data['time'].iloc[i]
            TradeBarnumber = i
            HighestHigh = data['high'].iloc[i]
            LowestLow = data['low'].iloc[i]
            ShortTrade += 1
            TradesTaken += 1
            ShortEntryPrice = data['close'].iloc[i]
            LastEntryPrice = data['close'].iloc[i]
            if SSL_P != 0:
                ShortStopP = ShortEntryPrice + (ShortEntryPrice * 0.01 * SSL_P)
            if ST_P != 0:
                ShortTargetP = ShortEntryPrice - (ShortEntryPrice * 0.01 * ST_P)
            if STrailPercent != 0:
                ShortTrailP = (data['close'].iloc[i] * 0.01 * STrailPercent)
            if STrailAbs != 0:
                ShortTrailA = STrailAbs
            if SSL_A != 0:
                ShortStopA = ShortEntryPrice + SSL_A
            if ST_A != 0:
                ShortTargetA = ShortEntryPrice - ST_A

            # Qty, entrydate,entrytime,entryprice,exitdate,exittime,exitprice,absqty

            trades.append({
                'strategy': strategy_name,
                'entry_action': Action,
                'SL': ShortStopP if ShortStopP < ShortStopA else ShortStopA,
                'TP': ShortTargetP if ShortTargetP > ShortTargetA else ShortTargetA,
                'qty': -Qty,
                'entry_date': DateOfTrade,
                'entry_time': DateOfTime,
                'entry_price': LastEntryPrice,

            })

        # ----------------------------STOP TGT SELECTION-----------------------------------------------

        if Flag == 1 and data['high'].iloc[i] > HighestHigh:
            HighestHigh = data['high'].iloc[i]
        if Flag == 1 and data['low'].iloc[i] < LowestLow:
            LowestLow = data['low'].iloc[i]

        LongStop = 0
        if LSL_P != 0 and LongStop == 0:
            LongStop = LongStopP
        if LTrailPercent != 0 and (LongStop == 0 or HighestHigh - LongTrailP > LongStopP):
            LongStop = round(HighestHigh - LongTrailP, Precision)
        if LTrailAbs != 0 and (LongStop == 0 or HighestHigh - LongTrailA > LongStop):
            LongStop = round(HighestHigh - LongTrailA, Precision)
        if LSL_A != 0 and (LongStop == 0 or LongStopA > LongStop):
            LongStop = LongStopA

        LongTarget = 0
        if LT_A != 0 and LongTargetA > LongTarget:
            LongTarget = LongTargetA
        if LT_P != 0 and (LongTarget == 0 or LongTargetP < LongTarget):
            LongTarget = LongTargetP

        ShortStop = 0
        if SSL_P != 0 and ShortStop == 0:
            ShortStop = ShortStopP
        if STrailPercent != 0 and (ShortStop == 0 or (LowestLow + ShortTrailP) < ShortStop):
            ShortStop = round(LowestLow + ShortTrailP, Precision)
        if STrailAbs != 0 and (ShortStop == 0 or (LowestLow + ShortTrailA) < ShortStop):
            ShortStop = round(LowestLow + ShortTrailA, Precision)
        if SSL_A != 0 and (ShortStop == 0 or ShortStopA < ShortStop):
            ShortStop = ShortStopA

        ShortTarget = 0
        if ST_A != 0 and ShortTargetA < ShortTarget:
            ShortTarget = ShortTargetA
        if ST_P != 0 and (ShortTarget == 0 or ShortTargetP < ShortTarget):
            ShortTarget = ShortTargetP

        # ----------------------------Exit Conditions-----------------------------------------------

        if Flag == 1 and data['close'].iloc[i] >= LongTarget and LongTarget != 0:
            Exit_price = LongTarget
            Exit_time = data['time'].iloc[i]
            Exit_action = "LT"
            Flag = 0
        if Flag == 1 and data['close'].iloc[i] <= LongStop and LongStop != 0:
            Exit_price = LongStop
            Exit_time = data['time'].iloc[i]
            Exit_action = "LSL"
            Flag = 0
        if Flag == -1 and data['close'].iloc[i] <= ShortTarget and ShortTarget != 0:
            Exit_price = ShortTarget
            Exit_time = data['time'].iloc[i]
            Exit_action = "ST"
            Flag = 0
        if Flag == -1 and data['close'].iloc[i] >= ShortStop and ShortStop != 0:
            Exit_price = ShortStop
            Exit_time = data['time'].iloc[i]
            Exit_action = "SSL"
            Flag = 0

        # Intra-day exit logic
        if Flag != 0 and IntraDayExit == 1 and data['time'].iloc[i] >= IntraExitTime:
            Exit_price = data['close'].iloc[i]
            Exit_time = data['time'].iloc[i]
            Exit_action = "INTRA"
            Flag = 0

        if Exit_action:
            trades[-1].update({
                'exit_date': data['date'].iloc[i],
                'exit_time': Exit_time,
                'exit_price': Exit_price,
                'exit_action': Exit_action,
            })

            Exit_action = ""

    if printtradesheet == 1:
        # Convert trades list to DataFrame and save to CSV
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(f"trades_{strategy_name}.csv", index=False)

        # print(f"{strategy_name} tradesheet generated successfully.")

def print_open_positions(trades):
    open_positions = [trade for trade in trades if 'exit_action' not in trade]
    strategy_quantities = {}
    for trade in open_positions:
        strategy = trade['strategy']
        if strategy in strategy_quantities:
            strategy_quantities[strategy] += trade['qty']
        else:
            strategy_quantities[strategy] = trade['qty']

    # Uncomment to print strategy-wise quantities
    # for strategy, qty in strategy_quantities.items():
    #     print(f"Strategy: {strategy}, Total QTY: {qty}")  # this gives open position

    total_qty = sum(trade['qty'] for trade in open_positions)

    # Write total quantity to CSV
    with open('position.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([total_qty])

    # with open(r'C:\MT5POS\US500m\position.csv', mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow([total_qty])

    # print(f"Total QTY across all strategies: {total_qty}")  # this gives net position

    # Write open positions to CSV
    with open('open_positions.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow([
            'Strategy', 'Entry Date', 'Entry Time', 'Entry Price',
            'Entry Action', 'QTY', 'SL','TP',
        ])
        # Write the trade details
        for trade in open_positions:
            writer.writerow([
                trade['strategy'], trade['entry_date'], trade['entry_time'],
                trade['entry_price'], trade['entry_action'], trade['qty'],
                trade['SL'], trade['TP']
            ])

    # Uncomment to print open position descriptions
    for trade in open_positions:
        print(
            f"Strategy: {trade['strategy']}, Entry Date: {trade['entry_date']}, "
            f"Entry Time: {trade['entry_time']}, Entry Price: {trade['entry_price']}, "
            f"Entry Action: {trade['entry_action']}, QTY: {trade['qty']} ,"
            f"SL: {trade['SL']}, TP: {trade['TP']}"
        )
    return total_qty


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.total_qty_label = tk.Label(self, text="Total QTY: ")
        self.total_qty_label.pack()

        self.debug_label = tk.Label(self, text="Debug Mode: ON")
        self.debug_label.pack()

        self.time_label = tk.Label(self, text="")
        self.time_label.pack()

        self.update_total_qty()

    def update_total_qty(self):
        total_qty = print_open_positions(trades)
        self.total_qty_label['text'] = f"Total QTY: {total_qty}"

        # Get current time in New York time zone (Eastern Time)
        ny_tz = pytz.timezone('America/New_York')
        ny_time = datetime.now(ny_tz)
        current_time = ny_time.strftime("%H%M")
        self.time_label['text'] = f"Current Time: {current_time}"

        self.after(1000, self.update_total_qty)  # update every 1 second

    def update_data_and_run_strategies(self):
        start_time = time.time()  # Start time before updating data and running strategies

        # Update data and run strategies
        update_data()
        trades.clear()
        strategy1()
        strategy2()



        # Print open positions
        print("Open Positions:")
        # total_qty = print_open_positions(trades)
        # print(f"Total QTY across all strategies: {total_qty}")


        # Your code to update data and run strategies
        end_time = time.time()  # End time after updating data and running strategies
        print(f"Runtime of update_data_and_run_strategies: {end_time - start_time} seconds")


        # Schedule the next update
        self.master.after(1000, self.update_data_and_run_strategies)


if __name__ == "__main__":
    start_time = time.time()  # Start time before initializing the application
    root = tk.Tk()
    app = Application(master=root)
    app.update_data_and_run_strategies()  # Start the first update
    end_time = time.time()  # End time after the first update
    # print(f"Runtime of main code: {end_time - start_time} seconds")
    app.mainloop()






