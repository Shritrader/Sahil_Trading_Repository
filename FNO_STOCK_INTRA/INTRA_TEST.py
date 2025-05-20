import pandas as pd
import os
import Indicater
from datetime import datetime

# Global variables

Precision = 0
printtradesheet = 1
csv_folder_path = r"C:\Users\ADMIN\PycharmProjects\BACKTEST_INTRA_stock\FNO_STOCK_INTRA\SCRIPT\FNO_DATA"
output_tradesfile_path = r"C:\Users\ADMIN\PycharmProjects\BACKTEST_INTRA_stock\FNO_STOCK_INTRA\Tradesheet"

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





    # Iterate through data for strategy 1
    for i in range(1, len(data)):
        # ------------------------------- INTRA EXIT -------------------------------------------------------

        # Reset trades at the beginning of a new day
        if data['date'].iloc[i] != data['date'].iloc[i - 1]:
            LongTrade = 0
            ShortTrade = 0
            TradesTaken = 0
            opend = data['open'].iloc[i]

            day_high = data['open'].iloc[i]
            day_low = data['open'].iloc[i]
            x = 1
        else:
            x = 0

        # Initialize trade signals
        LongSignal = 0
        ShortSignal = 0

        if data['time'].iloc[i]  <= 1000 :
            if data['high'].iloc[i] > day_high:
                day_high = data['high'].iloc[i]
            if data['low'].iloc[i] < day_low:
                day_low = data['low'].iloc[i]


        # Signal generation based on myindiz   # code part

        # if Flag < 1  and 920 < data['time'].iloc[i] <= 1515:
        #     if (myratio['myindi'].iloc[i] > value3 and myratio['myindi'].iloc[i - 1] <= value3 and
        #             data['close'].iloc[i] > mysma['sma'].iloc[i]
        #             and data['close'].iloc[i] > myema['ema'].iloc[i] ):
        #         LongSignal = 1
        #
        # if Flag > -1  and 920 < data['time'].iloc[i] < 1515:
        #     if (myratio['myindi'].iloc[i] < value4 and myratio['myindi'].iloc[i - 1] >= value4 and
        #             data['close'].iloc[i] < mysma['sma'].iloc[i]
        #             and data['close'].iloc[i] < myema['ema'].iloc[i]):
        #         ShortSignal = 1

        if Flag < 1  and 1000 < data['time'].iloc[i] <= 1515:
            if ( data['close'].iloc[i] > day_high ):
                LongSignal = 1

        if Flag > -1  and 1000 < data['time'].iloc[i] < 1515:
            if (data['low'].iloc[i] < day_low ):
                ShortSignal = 1








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
            LongEntryPrice = data['low'].iloc[i]
            LastEntryPrice = data['low'].iloc[i]
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
                'strategy': strategy_name,
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
                'strategy': strategy_name,
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
        if Flag !=0 and IntraDayExit == 1 and data['time'].iloc[i] >= IntraExitTime > data['time'].iloc[i - 1]:
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


    return pd.DataFrame(trades)


# 1 . Function to process each file in the folder
def process_files(csv_folder_path, output_tradesfile_path):
    files = os.listdir(csv_folder_path)
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(csv_folder_path, file)
            stock_name = os.path.splitext(file)[0]  # Extract stock name from file name
            print(f"Processing {file} for stock: {stock_name}")

            # Read CSV
            data = pd.read_csv(file_path)

            # Ensure the data is sorted by date and time
            data = data.sort_values(by=['date', 'time'])

            # Apply strategy
            tradesheet = strategy1(data, stock_name)

            # Save tradesheet to CSV
            tradesheet_filename = f"{stock_name}_tradesheet_long.csv"
            tradesheet_filepath = os.path.join(output_tradesfile_path, tradesheet_filename)
            tradesheet.to_csv(tradesheet_filepath, index=False)

            print(f"Tradesheet saved to {tradesheet_filepath}")


# Run the process
process_files(csv_folder_path, output_tradesfile_path)


# 2 . Function to process only one  file in the folder and give tradesheet
# def process_files(csv_folder_path, output_tradesfile_path):
#     files = os.listdir(csv_folder_path)
#     for file in files:
#         if file.endswith('.csv'):
#             file_path = os.path.join(csv_folder_path, file)
#             stock_name = os.path.splitext(file)[0]  # Extract stock name from file name
#             print(f"Processing {file} for stock: {stock_name}")
#
#             # Read CSV
#             data = pd.read_csv(file_path)
#
#             # Ensure the data is sorted by date and time
#             data = data.sort_values(by=['date', 'time'])
#
#             # Apply strategy
#             tradesheet = strategy1(data, stock_name)
#
#             # Save tradesheet to CSV
#             tradesheet_filename = f"{stock_name}_tradesheet_INTRA.csv"
#             tradesheet_filepath = os.path.join(output_tradesfile_path, tradesheet_filename)
#             tradesheet.to_csv(tradesheet_filepath, index=False)
#
#             print(f"Tradesheet saved to {tradesheet_filepath}")
#
# def main():
#
#     process_files(csv_folder_path, output_tradesfile_path)
#
#     # Define directories
#     input_dir = 'Tradesheet'
#     output_dir = 'report_analysis'
#
#     # Create output directory if it does not exist
#     os.makedirs(output_dir, exist_ok=True)
#
#     # Get user inputs for costs
#     percentage_cost = 0 #float(input("Enter the percentage cost (e.g., 0.001 for 0.1%): "))
#     per_unit_cost = 0 #float(input("Enter the per-unit cost: "))
#
#     # Loop through all CSV files in the input directory
#     for file_name in os.listdir(input_dir):
#         if file_name.endswith('.csv'):
#             csv_file = os.path.join(input_dir, file_name)
#             output_excel = os.path.join(output_dir, file_name.replace('.csv', '.xlsx'))
#             # anlyzeing the trdes
#             Indicater.analyze_trades_windos(csv_file, output_excel, percentage_cost, per_unit_cost)
#
# if __name__ == '__main__':
#     main()
#


