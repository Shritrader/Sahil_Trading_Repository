import pandas as pd
import os
from datetime import datetime

# Global variables
Precision = 0
printtradesheet = 1
csv_folder_path = r"C:\Users\ADMIN\PycharmProjects\BACKTEST_INTRA_stock\SCRIPT"
output_tradesfile_path = r"C:\Users\ADMIN\PycharmProjects\BACKTEST_INTRA_stock\Tradesheet"


def strategy1(data, stock_name):
    # Local trades variable
    trades = []

    # Read settings from settings.csv file
    settings_df = pd.read_csv('settings.csv')

    # Extract the settings for strategy 1 (case-sensitive match)
    strategy1_settings = settings_df[settings_df['Strategy'] == 'strategy1'].iloc[0]

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

        # next day trade reset
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
        # indicator calculation code

        if data['time'].iloc[i] <= value6:
            if data['high'].iloc[i] > day_high:
                day_high = data['high'].iloc[i]

        if data['time'].iloc[i] <= value7:
            if data['low'].iloc[i] < day_low:
                day_low = data['low'].iloc[i]

        # trade initialize
        LongSignal = 0
        ShortSignal = 0

        # Signal generation based on myindiz
        if Flag < 1 and Flag == 0 and value6 < data['time'].iloc[i] <= 1515:
            if data['close'].iloc[i] > day_high and data['close'].iloc[i - 1] <= day_high:
                LongSignal = 1

        if Flag > -1 and Flag == 0 and value7 < data['time'].iloc[i] < 1515:
            if data['close'].iloc[i] < day_low and data['close'].iloc[i - 1] >= day_low:
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
                'TP': LongTargetP,
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
                'SL': ShortStopP ,
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



    return pd.DataFrame(trades)  # Return trades from strategy1 function
def analyze_trades(csv_file, output_excel, percentage_cost=0.000125, per_unit_cost=1.5):
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
            tradesheet_filename = f"{stock_name}_tradesheet.csv"
            tradesheet_filepath = os.path.join(output_tradesfile_path, tradesheet_filename)
            tradesheet.to_csv(tradesheet_filepath, index=False)

            print(f"Tradesheet saved to {tradesheet_filepath}")

            trades_df = pd.DataFrame(tradesheet)

            # Calculate costs
            trades_df['PercentageCost'] = trades_df['entry_price'] * percentage_cost * abs(trades_df['qty'])
            trades_df['PerUnitCost'] = per_unit_cost * abs(trades_df['qty'])

            # Calculate MTM for each trade, considering the costs
            trades_df['MTM'] = ((trades_df['exit_price'] - trades_df['entry_price']) * trades_df['qty']) - trades_df[
                'PercentageCost'] - trades_df['PerUnitCost']

            # Calculate cumulative MTM
            trades_df['CumulativeMTM'] = trades_df['MTM'].cumsum()

            # Convert entry_date to datetime
            trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date'], format='%Y%m%d')

            # Calculate daily profit analysis
            daily_profit = trades_df.groupby(trades_df['entry_date'].dt.strftime('%Y%m%d')).agg(
                DailyMTM=('MTM', 'sum')
            ).reset_index()

            # Calculate cumulative MTM per day
            daily_profit['CumulativeMTM'] = daily_profit['DailyMTM'].cumsum()

            # Calculate drawdown
            daily_profit['Drawdown'] = daily_profit['CumulativeMTM'].cummax() - daily_profit['CumulativeMTM']

            # Calculate monthly profit analysis
            trades_df['entry_month'] = trades_df['entry_date'].dt.to_period('M')
            monthly_profit = trades_df.groupby(trades_df['entry_month']).agg(
                MonthlyMTM=('MTM', 'sum')
            ).reset_index()

            # Calculate cumulative MTM per month
            monthly_profit['CumulativeMTM'] = monthly_profit['MonthlyMTM'].cumsum()

            # Calculate drawdown
            monthly_profit['Drawdown'] = monthly_profit['CumulativeMTM'].cummax() - monthly_profit['CumulativeMTM']

            # Format the month for the output
            monthly_profit['entry_month'] = monthly_profit['entry_month'].dt.strftime('%Y%m')

            # Calculate yearly profit analysis
            trades_df['entry_year'] = trades_df['entry_date'].dt.year
            yearly_profit = trades_df.groupby(trades_df['entry_year']).agg(
                YearlyMTM=('MTM', 'sum')
            ).reset_index()

            # Calculate cumulative MTM per year
            yearly_profit['CumulativeMTM'] = yearly_profit['YearlyMTM'].cumsum()

            # Calculate drawdown
            yearly_profit['Drawdown'] = yearly_profit['CumulativeMTM'].cummax() - yearly_profit['CumulativeMTM']

            # Helper function to calculate analysis metrics
            def calculate_metrics(df):
                if 'Drawdown' not in df.columns:
                    df['Drawdown'] = df['CumulativeMTM'].cummax() - df['CumulativeMTM']

                net_profit = df['MTM'].sum()
                max_dd = df['Drawdown'].max()
                num_months = len(df['entry_date'].dt.to_period('M').unique())
                calma_ratio = (net_profit / max_dd) / (num_months / 12) if max_dd != 0 else float('inf')
                max_qty = df['qty'].max()
                gross_profit = df[df['MTM'] > 0]['MTM'].sum()
                gross_loss = df[df['MTM'] < 0]['MTM'].sum()
                profit_factor = gross_profit / -gross_loss if gross_loss != 0 else float('inf')
                day_max_profit = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().max()
                day_max_loss = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().min()
                total_trades = len(df)
                max_daily_dd = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['Drawdown'].max().max()
                max_monthly_dd = 0
                max_yearly_dd = 0

                return {
                    'Net profit': net_profit,
                    'MAX DD': max_dd,
                    'CALMA ratio': calma_ratio,
                    'Max qty': max_qty,
                    'Gross Profit': gross_profit,
                    'Gross Loss': gross_loss,
                    'Profit Factor': profit_factor,
                    'Day Max Profit': day_max_profit,
                    'Day Max Loss': day_max_loss,
                    'Total Trades': total_trades,
                    'Max daily DD': max_daily_dd,
                    'Max monthly DD': max_monthly_dd,
                    'Max Yearly DD': max_yearly_dd,
                    'Average Daily Profit': df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().mean(),
                    'Average Monthly Profit': df.groupby(df['entry_month'])['MTM'].sum().mean(),
                    'Average Yearly Profit': df.groupby(df['entry_year'])['MTM'].sum().mean()
                }

            # Separate long and short trades
            long_trades = trades_df[trades_df['qty'] > 0]
            short_trades = trades_df[trades_df['qty'] < 0]

            # Calculate metrics for all, long, and short trades
            all_metrics = calculate_metrics(trades_df)
            long_metrics = calculate_metrics(long_trades)
            short_metrics = calculate_metrics(short_trades)

            # Create an Excel writer object
            with pd.ExcelWriter(output_excel) as writer:
                # Write trade analysis to the first sheet
                trades_df[['entry_price', 'exit_price', 'qty', 'MTM', 'CumulativeMTM']].to_excel(writer,
                                                                                                 sheet_name='Trade Analysis',
                                                                                                 index=False)

                # Write daily profit analysis to the second sheet
                daily_profit.to_excel(writer, sheet_name='Daily Profit', index=False)

                # Write monthly profit analysis to the third sheet
                monthly_profit.to_excel(writer, sheet_name='Monthly Profit', index=False)

                # Write yearly profit analysis to the fourth sheet
                yearly_profit.to_excel(writer, sheet_name='Yearly Profit', index=False)

                # Write analysis metrics to the fifth sheet
                analysis_df = pd.DataFrame({
                    'Metric': ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty', 'Gross Profit', 'Gross Loss',
                               'Profit Factor',
                               'Day Max Profit', 'Day Max Loss', 'Total Trades', 'Max daily DD', 'Max monthly DD',
                               'Max Yearly DD',
                               'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit'],
                    'All Trades': [all_metrics.get(m) for m in
                                   ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty', 'Gross Profit',
                                    'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                                    'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                                    'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit']],
                    'Long Trades': [long_metrics.get(m) for m in
                                    ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty', 'Gross Profit',
                                     'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                                     'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                                     'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit']],
                    'Short Trades': [short_metrics.get(m) for m in
                                     ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty', 'Gross Profit',
                                      'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                                      'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                                      'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit']]
                })
                analysis_df.to_excel(writer, sheet_name='Analysis', index=False)

            print(f"Trade analysis has been written to {output_excel}")

# D efine directories
input_dir = 'Tradesheet'
output_dir = 'report_analysis'

# Create output directory if it does not exist
os.makedirs(output_dir, exist_ok=True)

# Get user inputs for costs
percentage_cost = float(input("Enter the percentage cost (e.g., 0.001 for 0.1%): "))
per_unit_cost = float(input("Enter the per-unit cost: "))

# Loop through all CSV files in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith('.csv'):
        csv_file = os.path.join(input_dir, file_name)
        output_excel = os.path.join(output_dir, file_name.replace('.csv', '.xlsx'))

        analyze_trades(csv_file, output_excel, percentage_cost, per_unit_cost)

