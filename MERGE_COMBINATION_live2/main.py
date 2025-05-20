import pandas as pd
import numpy as np
import os
import Indicater
from datetime import datetime
import tkinter as tk
import time
import csv
import threading

folder1_path = os.path.join(os.getcwd(), 'Call')
folder2_path = os.path.join(os.getcwd(), 'Put')

def merge_data(Call, Put):
    data_call = Call
    data_put = Put

    merge_data = pd.DataFrame()

    merge_data['date'] = data_call['date']
    merge_data['time'] = data_call['time']
    merge_data['open'] = 0
    merge_data['high'] = 0
    merge_data['low'] = 0
    merge_data['close'] = data_call['close'] + data_put['close']
    merge_data['volume'] = data_call['volume'] + data_put['volume']
    merge_data['vwap'] = (merge_data['close'] * merge_data['volume']).cumsum() / merge_data['volume'].cumsum()

    return merge_data

def strategy1(data, stock_name):
    # Local trades variable
    trades = []

    # Read settings from settings.csv file
    settings_df = pd.read_csv('settings.csv')

    # Extract the settings for strategy 1 (case-sensitive match)
    strategy1_settings = settings_df[settings_df['Strategy'] == 'strategy1'].iloc[0]

    # Convert data to the desired timeframe

    Timeframe = int(strategy1_settings['Timeframe'])
    data = Indicater.convert_to_timeframe(data, f'{Timeframe}min', '09:15', '15:30')

    # Initialize strategy-specific variables
    Precision = 2
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
    day_high = 0
    day_low = 0

    # Assign settings to variables
    strategy_name = strategy1_settings['Strategy']
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


    # indicater part

    myratio =  Indicater.myratio(data, value1, value2)
    mysma = Indicater.calculate_sma(data,window=6)
    myema = Indicater.calculate_ema(data,window=9)
    myvwap = Indicater.calculate_vwap(data=data)




    # Iterate through data for strategy 1
    for i in range(1, len(data)):
        # ------------------------------- INTRA EXIT -------------------------------------------------------

        # Reset trades at the beginning of a new day
        if data['date'].iloc[i] != data['date'].iloc[i - 1]:
            LongTrade = 0
            ShortTrade = 0
            TradesTaken = 0
            opend = data['open'].iloc[i]

            day_high = data['high'].iloc[i]
            day_low = data['low'].iloc[i]
            x = 1
        else:
            x = 0

        # Initialize trade signals
        LongSignal = 0
        ShortSignal = 0

        # Signal generation based on myindiz
        if Flag < 1  and 1000 < data['time'].iloc[i] <= 1500 and data['time'].iloc[i] <= IntraExitTime:
            if (data['time'].iloc[i] == 1525):
                LongSignal = 1

        if Flag > -1  and 920 < data['time'].iloc[i] <= 1500 and data['time'].iloc[i] <= IntraExitTime :
            # if (data['close'].iloc[i] < myvwap['vwap'].iloc[i]*1.1):
            #     ShortSignal = 1
            if (data['time'].iloc[i] == 1118):
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

        # Handle reversal situations

        if LongSignal == 1 and Flag == -1:  # Reverse from Short to Long
            Exit_price = data['close'].iloc[i]
            Exit_time = data['time'].iloc[i]
            Exit_action = "Reversal to Long"
            trades[-1].update({
                'exit_date': data['date'].iloc[i],
                'exit_time': Exit_time,
                'exit_price': Exit_price,
                'exit_action': Exit_action,
            })
            Flag = 0  # Exit the short trade before entering the long

        if ShortSignal == 1 and Flag == 1:  # Reverse from Long to Short
            Exit_price = data['close'].iloc[i]
            Exit_time = data['time'].iloc[i]
            Exit_action = "Reversal to Short"
            trades[-1].update({
                'exit_date': data['date'].iloc[i],
                'exit_time': Exit_time,
                'exit_price': Exit_price,
                'exit_action': Exit_action,
            })
            Flag = 0  # Exit the long trade before entering the short




        # ------------------------------BUY SELL CHECK--------------------------------------------



        # Entry logic after handling potential reversals
        if LongSignal == 1 and Flag !=1 and LETime <= data['time'].iloc[
            i] <= LXTime and LongTrade < AllowedTradesLong and TradesTaken < AllowedTrades and (
                LongAlternate == 0 or (LongAlternate == 1 and (LastTradeType == -1 or LastTradeType == 0))
        ) and UndisputedShort == 0:
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
            if LSL_A != 0:
                LongStopA = LongEntryPrice - LSL_A
            if LT_A != 0:
                LongTargetA = LongEntryPrice + LT_A
            if LTrailAbs != 0:
                LongTrailA = LTrailAbs

            # Determine final Long Stop and Target values
            # Determine final Long Stop value
            LongStop = max([val for val in [LongStopP, LongStopA] if val not in (None, 0)], default=0)
            LongTarget = min([val for val in [LongTargetP, LongTargetA] if val not in (None, 0)], default=0)

            trades.append({
                'strategy': stock_name,
                'entry_action': Action,
                'SL': LongStop,
                'TP': LongTarget,
                'qty': +Qty if QtyAbs ==1 else int(Capital/data['close'].iloc[i]),
                'entry_date': DateOfTrade,
                'entry_time': DateOfTime,
                'entry_price': LastEntryPrice,

            })

        if ShortSignal == 1 and Flag !=-1 and SETime <= data['time'].iloc[
            i] <= SXTime and ShortTrade < AllowedTradesShort and TradesTaken < AllowedTrades and (
                ShortAlternate == 0 or (ShortAlternate == 1 and (LastTradeType == 1 or LastTradeType == 0))
        ) and UndisputedLong == 0:
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
            if SSL_A != 0:
                ShortStopA = ShortEntryPrice + SSL_A
            if ST_A != 0:
                ShortTargetA = ShortEntryPrice - ST_A
            if STrailAbs != 0:
                ShortTrailA = STrailAbs

            # Determine final Short Stop value
            ShortStop = min([val for val in [ShortStopP, ShortStopA] if val not in (None, 0)], default=0)
            ShortTarget = max([val for val in [ShortTargetP, ShortTargetA] if val not in (None, 0)], default=0)

            trades.append({
                'strategy': stock_name,
                'entry_action': Action,
                'SL': ShortStop ,
                'TP': ShortTarget,
                'qty': -Qty if QtyAbs ==1 else -int(Capital/data['close'].iloc[i]),
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
        if  Flag !=0 and IntraDayExit == 1 and (data['time'].iloc[i] == IntraExitTime or (data['time'].iloc[i] >= IntraExitTime and data['time'].iloc[i-1] < IntraExitTime))  :
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


    # Convert trades list to DataFrame and save to CSV
    # trades_df = pd.DataFrame(trades)
    # trades_df.to_csv(f"trades_{stock_name}.csv", index=False)

    # print(f"{stock_name} tradesheet generated successfully.")

    return pd.DataFrame(trades)

required_columns = [
    'strategy', 'entry_action', 'SL', 'TP', 'qty', 'entry_date', 'entry_time',
    'entry_price', 'exit_date', 'exit_time', 'exit_price', 'exit_action'
]

def calculate_positions(trades_df):
    open_positions = trades_df[trades_df['exit_price'].isna()]
    strike_positions = {}

    for _, row in open_positions.iterrows():
        strikes = row['strategy'].split('_')
        qty = row['qty']
        for strike in strikes:
            if strike in strike_positions:
                strike_positions[strike] += qty
            else:
                strike_positions[strike] = qty

    return strike_positions

# Tkinter setup
root = tk.Tk()
root.title("Live Prices")

labels = {}

def create_labels_for_strikes(strike_positions):
    for strike, qty in strike_positions.items():
        if strike not in labels:
            labels[strike] = tk.Label(root, text=f"Strike: {strike}, Position: {qty}")
            labels[strike].pack()
        else:
            labels[strike].config(text=f"Strike: {strike}, Position: {qty}")

def update_tkinter_window():
    while True:
        start_time = time.time()
        try:
            folder1_files = [f for f in os.listdir(folder1_path) if f.endswith('.csv')]
            folder2_files = [f for f in os.listdir(folder2_path) if f.endswith('.csv')]

            merged_dataframes = {}

            for file1 in folder1_files:
                for file2 in folder2_files:
                    try:
                        df1 = pd.read_csv(os.path.join(folder1_path, file1))
                        df2 = pd.read_csv(os.path.join(folder2_path, file2))
                        merged_df = merge_data(df1, df2)
                        combo_name = f"{file1[:-4]}_{file2[:-4]}"
                        merged_dataframes[combo_name] = merged_df
                    except Exception as e:
                        print(f"Error merging {file1} and {file2}: {e}")

            all_trades = pd.DataFrame(columns=required_columns)

            for combo_name, df in merged_dataframes.items():
                trades = strategy1(df, combo_name)
                if isinstance(trades, pd.DataFrame):
                    all_trades = pd.concat([all_trades, trades], ignore_index=True)
                else:
                    print(f"Warning: {combo_name} did not return a DataFrame. Skipping this combination.")

            output_file = 'all_combined_trades.csv'
            all_trades.to_csv(output_file, index=False)
            print(all_trades.head())  # Print the first few rows of the DataFrame
            print(all_trades.columns)  # Print the column names

            strike_positions = calculate_positions(all_trades)
            create_labels_for_strikes(strike_positions)

        except Exception as e:
            print(f"Error in update_tkinter_window: {e}")

        end_time = time.time()
        print(f"Runtime of main code: {end_time - start_time} seconds")
        time.sleep(2)  # Adjust sleep interval as needed

# Example initial call to create labels
create_labels_for_strikes({'example_strike': 0})

# Start the Tkinter window update in a separate thread
tkinter_thread = threading.Thread(target=update_tkinter_window, daemon=True)
tkinter_thread.start()

# Run Tkinter main loop
root.mainloop()
