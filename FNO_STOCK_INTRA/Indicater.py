import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Frame, Label, Text, ttk, END
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import pandas as pd

def convert_to_timeframe(df, timeframe, session_start, session_end):
    """
    Convert 1-minute OHLC data to a specified timeframe, ensuring correct live updates.
    Supports hourly timeframes with proper session alignment.
    """
    df['time'] = df['time'].astype(str).str.zfill(4)
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + df['time'], format='%Y%m%d%H%M')
    df.set_index('datetime', inplace=True)

    # Convert session start and end to full datetime
    session_start_time = df.index.normalize() + pd.to_timedelta(session_start + ':00')
    session_end_time = df.index.normalize() + pd.to_timedelta(session_end + ':00')

    # Filter data within session times
    df = df[(df.index >= session_start_time) & (df.index <= session_end_time)]

    # Ensure resampling aligns to session start (e.g., 09:15 - 10:15)
    resampled_df = df.resample(timeframe, label='right', closed='right', origin='start').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    # Get the latest minute data
    latest_minute = df.index.max()
    latest_hourly_close_time = resampled_df.index.max()

    # ⚠️ If the last hourly close time is beyond the latest available minute, drop it
    if latest_hourly_close_time and latest_hourly_close_time > latest_minute:
        resampled_df = resampled_df.iloc[:-1]  # Remove incomplete hourly bar

    # Reset index
    resampled_df.reset_index(inplace=True)

    # Extract date and time
    resampled_df['date'] = resampled_df['datetime'].dt.strftime('%Y%m%d').astype(int)
    resampled_df['time'] = resampled_df['datetime'].dt.strftime('%H%M').astype(int)

    # Drop datetime column and reorder columns
    resampled_df.drop(columns=['datetime'], inplace=True)
    resampled_df = resampled_df[['date', 'time', 'open', 'high', 'low', 'close', 'volume']]

    return resampled_df

# # Load data and convert the timeframe for a custom session
# path = r"C:\Users\user\PycharmProjects\Backtest_engine\Data_script\MIDCPNIFTY.csv"
# data = pd.read_csv(path)
# data_time = convert_to_timeframe(data, '5min', '09:15', '15:30')
# print(data_time)


# this is complete time frame

def analyze_trades_windos(csv_file, output_excel, percentage_cost=0.000125, per_unit_cost=1.5):
    try:
        # Read the CSV file
        trades_df = pd.read_csv(csv_file)

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
            min_qty = df['qty'].min()
            gross_profit = df[df['MTM'] > 0]['MTM'].sum()
            gross_loss = df[df['MTM'] < 0]['MTM'].sum()
            profit_factor = gross_profit / -gross_loss if gross_loss != 0 else float('inf')
            day_max_profit = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().max()
            day_max_loss = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().min()
            total_trades = len(df)
            max_daily_dd = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['Drawdown'].max().max()

            # Calculate maximum monthly and yearly drawdown
            max_monthly_dd = df.groupby(df['entry_month'])[
                'Drawdown'].max().max() if 'entry_month' in df.columns else 0
            max_yearly_dd = df.groupby(df['entry_year'])[
                'Drawdown'].max().max() if 'entry_year' in df.columns else 0

            return {
                'Net profit': round(net_profit, 2),
                'MAX DD': round(max_dd, 2),
                'CALMA ratio': round(calma_ratio, 2),
                'Max qty': max_qty,
                'Min qty': min_qty,
                'Gross Profit': round(gross_profit, 2),
                'Gross Loss': round(gross_loss, 2),
                'Profit Factor': round(profit_factor, 2),
                'Day Max Profit': round(day_max_profit, 2),
                'Day Max Loss': round(day_max_loss, 2),
                'Total Trades': total_trades,
                'Max daily DD': round(max_daily_dd, 2),
                'Max monthly DD': round(max_monthly_dd, 2),
                'Max Yearly DD': round(max_yearly_dd, 2),
                'Average Daily Profit': round(
                    df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().mean(), 2),
                'Average Monthly Profit': round(df.groupby(df['entry_month'])['MTM'].sum().mean(), 2),
                'Average Yearly Profit': round(df.groupby(df['entry_year'])['MTM'].sum().mean(), 2)
            }

        # Separate long and short trades
        long_trades = trades_df[trades_df['qty'] > 0]
        short_trades = trades_df[trades_df['qty'] < 0]

        # Calculate metrics for all, long, and short trades
        all_metrics = calculate_metrics(trades_df)
        long_metrics = calculate_metrics(long_trades)
        short_metrics = calculate_metrics(short_trades)

        # Create a DataFrame for better visualization of metrics
        metrics_df = pd.DataFrame({
            'All Trades': pd.Series(all_metrics),
            'Long Trades': pd.Series(long_metrics),
            'Short Trades': pd.Series(short_metrics)
        })

        # Tkinter setup
        root = Tk()
        root.title("Trade Analysis Summary")

        # Create a notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")

        # Tab for Metrics
        metrics_frame = Frame(notebook)
        notebook.add(metrics_frame, text="Metrics")

        # Display metrics in tabular format
        Label(metrics_frame, text="Metrics", font=("Helvetica", 16, "bold")).pack(pady=10)

        metrics_text = Text(metrics_frame)
        metrics_text.pack(expand=True, fill="both")
        metrics_text.insert(END, metrics_df.to_string())

        # Tab for Trades
        trades_frame = Frame(notebook)
        notebook.add(trades_frame, text="Trades")

        # Display trades data
        trades_text = Text(trades_frame)
        trades_text.pack(expand=True, fill="both")
        trades_text.insert(END, trades_df.to_string(index=False))

        # Tab for Daily Profit
        daily_frame = Frame(notebook)
        notebook.add(daily_frame, text="Daily Profit")

        daily_text = Text(daily_frame)
        daily_text.pack(expand=True, fill="both")
        daily_text.insert(END, daily_profit.to_string(index=False))

        # Tab for Monthly Profit
        monthly_frame = Frame(notebook)
        notebook.add(monthly_frame, text="Monthly Profit")

        monthly_text = Text(monthly_frame)
        monthly_text.pack(expand=True, fill="both")
        monthly_text.insert(END, monthly_profit.to_string(index=False))

        # Tab for Yearly Profit
        yearly_frame = Frame(notebook)
        notebook.add(yearly_frame, text="Yearly Profit")

        yearly_text = Text(yearly_frame)
        yearly_text.pack(expand=True, fill="both")
        yearly_text.insert(END, yearly_profit.to_string(index=False))

        # Write the analysis data to an Excel file
        with pd.ExcelWriter(output_excel) as writer:
            trades_df.to_excel(writer, sheet_name='Trades', index=False)
            daily_profit.to_excel(writer, sheet_name='Daily Profit', index=False)
            monthly_profit.to_excel(writer, sheet_name='Monthly Profit', index=False)
            yearly_profit.to_excel(writer, sheet_name='Yearly Profit', index=False)
            metrics_df.to_excel(writer, sheet_name='Metrics')

        # Tab for Equity Curve
        equity_frame = Frame(notebook)
        notebook.add(equity_frame, text="Equity Curve")

        # Display the equity curve
        plt.figure(figsize=(8, 5))
        plt.plot(trades_df['entry_date'], trades_df['CumulativeMTM'], label='Cumulative MTM', color='blue')
        plt.xlabel('Date')
        plt.ylabel('Cumulative MTM')
        plt.title('Equity Curve')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        # Save the plot to a file
        plot_file = output_excel.replace('.xlsx', '_equity_curve.png')
        plt.savefig(plot_file)

        # Display the plot in Tkinter
        fig = plt.gcf()
        canvas = FigureCanvasTkAgg(fig, master=equity_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

        # Run the Tkinter main loop
        root.mainloop()


    except Exception as e:
        print(f"Error: {e}")

def analyze_trades_terminal(csv_file, output_excel, percentage_cost=0.000125, per_unit_cost=1.5):
    try:
        # Read the CSV file
        trades_df = pd.read_csv(csv_file)

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
            min_qty = df['qty'].min()
            gross_profit = df[df['MTM'] > 0]['MTM'].sum()
            gross_loss = df[df['MTM'] < 0]['MTM'].sum()
            profit_factor = gross_profit / -gross_loss if gross_loss != 0 else float('inf')
            day_max_profit = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().max()
            day_max_loss = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum().min()
            total_trades = len(df)
            max_daily_dd = df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['Drawdown'].max().max()

            # Calculate maximum monthly and yearly drawdown
            max_monthly_dd = df.groupby(df['entry_month'])['Drawdown'].max().max() if 'entry_month' in df.columns else 0
            max_yearly_dd = df.groupby(df['entry_year'])['Drawdown'].max().max() if 'entry_year' in df.columns else 0

            return {
                'Net profit': net_profit,
                'MAX DD': max_dd,
                'CALMA ratio': calma_ratio,
                'Max qty': max_qty,
                'Min qty': min_qty,
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

        # Print metrics to terminal
        print("Analysis Metrics:")
        for metric_set, label in zip([all_metrics, long_metrics, short_metrics],
                                     ['All Trades', 'Long Trades', 'Short Trades']):
            print(f"\n{label}:")
            for metric, value in metric_set.items():
                print(f"{metric}: {value:.2f}" if isinstance(value, (int, float)) else f"{metric}: {value}")

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
                'Metric': ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty','Min qty', 'Gross Profit', 'Gross Loss',
                           'Profit Factor',
                           'Day Max Profit', 'Day Max Loss', 'Total Trades', 'Max daily DD', 'Max monthly DD',
                           'Max Yearly DD',
                           'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit'],
                'All Trades': [all_metrics.get(m) for m in
                               ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty','Min qty', 'Gross Profit',
                                'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                                'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                                'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit']],
                'Long Trades': [long_metrics.get(m) for m in
                                ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty','Min qty', 'Gross Profit',
                                 'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                                 'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                                 'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit']],
                'Short Trades': [short_metrics.get(m) for m in
                                 ['Net profit', 'MAX DD', 'CALMA ratio', 'Max qty','Min qty', 'Gross Profit',
                                  'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                                  'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                                  'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit']]
            })
            analysis_df.to_excel(writer, sheet_name='Analysis', index=False)

        print(f"\nTrade analysis has been written to {output_excel}")

    except Exception as e:
        print(f"An error occurred: {e}")

def myratio(data, value1, value2):
    """
    Calculate indicators based on the input data and rolling window values.

    Parameters:
    - data (pd.DataFrame): The input data containing 'open', 'close', 'high', and 'low' columns.
    - value1 (int): The rolling window size for value1 (difference between 'open' and 'close').
    - value2 (int): The rolling window size for value2 (difference between 'high' and 'low').

    Returns:
    - pd.DataFrame: The original data with additional columns for calculated indicators.
    """

    # Calculate value1 and value2
    data['value1'] = data['open'] - data['close']
    data['value2'] = data['high'] - data['low']

    # Calculate rolling sums
    data['value1_sum'] = data['value1'].rolling(window=value1).sum()
    data['value2_sum'] = data['value2'].rolling(window=value2).sum()

    # Calculate the custom indicator 'myindi'
    data['myindi'] = (data['value1_sum'] / data['value2_sum']) * 100

    return data

def calculate_sma(data, window):
    data['sma'] = data['close'].rolling(window=window).mean()
    return data

def calculate_sma_high(data, window):
    data['smah'] = data['high'].rolling(window=window).mean()
    return data

def calculate_sma_low(data, window):
    data['smal'] = data['low'].rolling(window=window).mean()
    return data

def calculate_ema(data, window):
    data['ema'] = data['close'].ewm(span=window, adjust=False).mean()
    return data

def calculate_bollinger_bands(data, window=20,dev=2):
    data['bb_middle'] = data['close'].rolling(window=window).mean()
    data['bb_upper'] = data['bb_middle'] + dev * data['close'].rolling(window=window).std()
    data['bb_lower'] = data['bb_middle'] - dev * data['close'].rolling(window=window).std()
    return data

def calculate_rsi(data, window=14):
    data['diff'] = data['close'].diff()
    data['gain'] = data['diff'].where(data['diff'] > 0, 0)
    data['loss'] = -data['diff'].where(data['diff'] < 0, 0)
    data['avg_gain'] = data['gain'].rolling(window=window, min_periods=1).mean()
    data['avg_loss'] = data['loss'].rolling(window=window, min_periods=1).mean()
    data['rs'] = data['avg_gain'] / data['avg_loss']
    data['rsi'] = 100 - (100 / (1 + data['rs']))
    return data.drop(columns=['diff', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs'])

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    data['macd'] = data['close'].ewm(span=short_window, adjust=False).mean() - \
                   data['close'].ewm(span=long_window, adjust=False).mean()
    data['macd_signal'] = data['macd'].ewm(span=signal_window, adjust=False).mean()
    data['macd_hist'] = data['macd'] - data['macd_signal']
    return data

def calculate_atr(data, window=14):
    data['tr1'] = data['high'] - data['low']
    data['tr2'] = abs(data['high'] - data['close'].shift())
    data['tr3'] = abs(data['low'] - data['close'].shift())
    data['tr'] = data[['tr1', 'tr2', 'tr3']].max(axis=1)
    data['atr'] = data['tr'].rolling(window=window).mean()
    return data.drop(columns=['tr1', 'tr2', 'tr3', 'tr'])

def calculate_stochastic(data, window=14):
    data['low_min'] = data['low'].rolling(window=window).min()
    data['high_max'] = data['high'].rolling(window=window).max()
    data['stochastic'] = 100 * (data['close'] - data['low_min']) / (data['high_max'] - data['low_min'])
    return data.drop(columns=['low_min', 'high_max'])

def calculate_cci(data, window=20):
    data['tp'] = (data['high'] + data['low'] + data['close']) / 3
    data['tp_sma'] = data['tp'].rolling(window=window).mean()
    data['tp_mean_dev'] = data['tp'].rolling(window=window).apply(lambda x: pd.Series(x).mad())
    data['cci'] = (data['tp'] - data['tp_sma']) / (0.015 * data['tp_mean_dev'])
    return data.drop(columns=['tp', 'tp_sma', 'tp_mean_dev'])

def calculate_roc(data, window=12):
    data['roc'] = data['close'].pct_change(periods=window) * 100
    return data

def calculate_williams_r(data, window=14):
    data['low_min'] = data['low'].rolling(window=window).min()
    data['high_max'] = data['high'].rolling(window=window).max()
    data['williams_r'] = -100 * (data['high_max'] - data['close']) / (data['high_max'] - data['low_min'])
    return data.drop(columns=['low_min', 'high_max'])

def calculate_psar(data, af=0.02, max_af=0.2):
    data['psar'] = data['close']  # Initialize PSAR column
    data['psar'] = data['psar'].shift()  # Start the PSAR calculation

    # Variables to hold the trend direction, extreme point, and acceleration factor
    uptrend = True
    ep = data['low'][0]
    af = af

    for i in range(1, len(data)):
        if uptrend:
            data.at[i, 'psar'] = data.at[i - 1, 'psar'] + af * (ep - data.at[i - 1, 'psar'])
            if data.at[i, 'low'] < data.at[i, 'psar']:
                uptrend = False
                data.at[i, 'psar'] = ep
                af = 0.02
                ep = data.at[i, 'high']
        else:
            data.at[i, 'psar'] = data.at[i - 1, 'psar'] + af * (ep - data.at[i - 1, 'psar'])
            if data.at[i, 'high'] > data.at[i, 'psar']:
                uptrend = True
                data.at[i, 'psar'] = ep
                af = 0.02
                ep = data.at[i, 'low']

        if uptrend:
            ep = max(ep, data.at[i, 'high'])
        else:
            ep = min(ep, data.at[i, 'low'])

        if uptrend and data.at[i, 'high'] > ep:
            af = min(af + 0.02, max_af)
        elif not uptrend and data.at[i, 'low'] < ep:
            af = min(af + 0.02, max_af)

    return data

def calculate_ichimoku(data, conversion_line_period=9, base_line_period=26, leading_span_b_period=52, lagging_span_period=26):
    data['conversion_line'] = (data['high'].rolling(window=conversion_line_period).max() +
                               data['low'].rolling(window=conversion_line_period).min()) / 2
    data['base_line'] = (data['high'].rolling(window=base_line_period).max() +
                         data['low'].rolling(window=base_line_period).min()) / 2
    data['leading_span_a'] = ((data['conversion_line'] + data['base_line']) / 2).shift(lagging_span_period)
    data['leading_span_b'] = ((data['high'].rolling(window=leading_span_b_period).max() +
                               data['low'].rolling(window=leading_span_b_period).min()) / 2).shift(lagging_span_period)
    data['lagging_span'] = data['close'].shift(-lagging_span_period)

    return data

def calculate_obv(data):
    data['obv'] = (data['volume'] * ((data['close'] > data['close'].shift()).astype(int) -
                                     (data['close'] < data['close'].shift()).astype(int))).cumsum()
    return data

def calculate_adl(data):
    clv = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
    data['adl'] = (clv * data['volume']).cumsum()
    return data

def calculate_mfi(data, window=14):
    tp = (data['high'] + data['low'] + data['close']) / 3
    raw_money_flow = tp * data['volume']
    pos_money_flow = raw_money_flow.where(data['close'] > data['close'].shift(), 0)
    neg_money_flow = raw_money_flow.where(data['close'] < data['close'].shift(), 0)

    data['mfi'] = 100 - (100 / (1 + pos_money_flow.rolling(window=window).sum() /
                                    neg_money_flow.rolling(window=window).sum()))

    return data

def calculate_cmf(data, window=20):
    mf_multiplier = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
    mf_volume = mf_multiplier * data['volume']
    data['cmf'] = mf_volume.rolling(window=window).sum() / data['volume'].rolling(window=window).sum()
    return data

def calculate_adx(data, window=14):
    data['tr'] = data[['high', 'low']].max(axis=1) - data[['high', 'low']].min(axis=1)
    data['+dm'] = data['high'].diff()
    data['-dm'] = data['low'].diff()

    data['+di'] = 100 * (data['+dm'].rolling(window=window).mean() / data['tr'].rolling(window=window).mean())
    data['-di'] = 100 * (data['-dm'].rolling(window=window).mean() / data['tr'].rolling(window=window).mean())

    data['dx'] = 100 * abs(data['+di'] - data['-di']) / (data['+di'] + data['-di'])
    data['adx'] = data['dx'].rolling(window=window).mean()

    return data.drop(columns=['tr', '+dm', '-dm', '+di', '-di', 'dx'])

def calculate_vwap(data):
    data['vwap'] = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()
    return data

def calculate_keltner_channels(data, window=20, multiplier=2):
    data['atr'] = data['high'] - data['low']
    data['kc_middle'] = data['close'].ewm(span=window, adjust=False).mean()
    data['kc_upper'] = data['kc_middle'] + multiplier * data['atr'].ewm(span=window, adjust=False).mean()
    data['kc_lower'] = data['kc_middle'] - multiplier * data['atr'].ewm(span=window, adjust=False).mean()
    return data.drop(columns=['atr'])

def calculate_donchian_channels(data, window=20):
    data['dc_upper'] = data['high'].rolling(window=window).max()
    data['dc_lower'] = data['low'].rolling(window=window).min()
    data['dc_middle'] = (data['dc_upper'] + data['dc_lower']) / 2
    return data

def calculate_ad(data):
    # Money Flow Multiplier (MFM)
    data['mfm'] = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])

    # Money Flow Volume (MFV)
    data['mfv'] = data['mfm'] * data['volume']

    # Accumulation/Distribution (A/D)
    data['ad'] = data['mfv'].cumsum()

    return data.drop(columns=['mfm', 'mfv'])


# def strategy1(data, stock_name):
#     # Local trades variable
#     trades = []
#
#     # Read settings from settings.csv file
#     settings_df = pd.read_csv('settings.csv')
#
#     # Extract the settings for strategy 1 (case-sensitive match)
#     strategy1_settings = settings_df[settings_df['Strategy'] == 'strategy1'].iloc[0]
#
#     # Convert data to the desired timeframe
#
#     Timeframe = int(strategy1_settings['Timeframe'])
#     data = Indicater.convert_to_timeframe(data, f'{Timeframe}min', '09:15', '15:30')
#
#     # Initialize strategy-specific variables
#     Precision = 2
#     ShortEntryPrice = 0
#     LongEntryPrice = 0
#     Flag = 0
#     LongTarget = 0
#     ShortTarget = 0
#     LongStopP = 0
#     ShortStopP = 0
#     LongStopA = 0
#     ShortStopA = 0
#     LongStop = 0
#     ShortStop = 0
#     LongTargetP = 0
#     ShortTargetP = 0
#     LongTargetA = 0
#     ShortTargetA = 0
#     LastEntryPrice = 0
#     ShortTrades = 0
#     LongTrades = 0
#     HighestHigh = 0
#     LowestLow = 0
#     LongTrailP = 0
#     ShortTrailP = 0
#     LongTrailA = 0
#     ShortTrailA = 0
#     ExitBarNo = 0
#     TradeBarnumber = 0
#     TradesTaken = 0
#     LongTrade = 0
#     ShortTrade = 0
#     LongSignal = 0
#     ShortSignal = 0
#     DateOfTrade = 0
#     DateOfTime = 0
#     LastTradeType = 0
#     Exit_price = 0
#     Exit_time = 0
#     Exit_action = ""
#     day_high = 0
#     day_low = 0
#
#     # Assign settings to variables
#     strategy_name = strategy1_settings['Strategy']
#     Segment = int(strategy1_settings['Segment'])
#     QtyAbs = int(strategy1_settings['QtyAbs'])
#     Qty = int(strategy1_settings['Qty'])
#     Capital = int(strategy1_settings['Capital'])
#     IntraDayExit = int(strategy1_settings['IntraDayExit'])
#     IntraExitTime = int(strategy1_settings['IntraExitTime'])
#     LongOnly = int(strategy1_settings['LongOnly'])
#     ShortOnly = int(strategy1_settings['ShortOnly'])
#     LongAlternate = int(strategy1_settings['LongAlternate'])
#     ShortAlternate = int(strategy1_settings['ShortAlternate'])
#     UndisputedLong = int(strategy1_settings['UndisputedLong'])
#     UndisputedShort = int(strategy1_settings['UndisputedShort'])
#     LSL_P = float(strategy1_settings['LSL_P'])
#     SSL_P = float(strategy1_settings['SSL_P'])
#     LSL_A = float(strategy1_settings['LSL_A'])
#     SSL_A = float(strategy1_settings['SSL_A'])
#     LT_P = float(strategy1_settings['LT_P'])
#     ST_P = float(strategy1_settings['ST_P'])
#     LT_A = float(strategy1_settings['LT_A'])
#     ST_A = float(strategy1_settings['ST_A'])
#     LTrailPercent = float(strategy1_settings['LTrailPercent'])
#     STrailPercent = float(strategy1_settings['STrailPercent'])
#     LTrailAbs = float(strategy1_settings['LTrailAbs'])
#     STrailAbs = float(strategy1_settings['STrailAbs'])
#     AllowedTradesLong = int(strategy1_settings['AllowedTradesLong'])
#     AllowedTradesShort = int(strategy1_settings['AllowedTradesShort'])
#     AllowedTrades = int(strategy1_settings['AllowedTrades'])
#     LETime = int(strategy1_settings['LETime'])
#     LXTime = int(strategy1_settings['LXTime'])
#     SETime = int(strategy1_settings['SETime'])
#     SXTime = int(strategy1_settings['SXTime'])
#     value1 = int(strategy1_settings['value1'])
#     value2 = int(strategy1_settings['value2'])
#     value3 = float(strategy1_settings['value3'])
#     value4 = float(strategy1_settings['value4'])
#     value5 = float(strategy1_settings['value5'])
#     value6 = float(strategy1_settings['value6'])
#     value7 = float(strategy1_settings['value7'])
#     value8 = float(strategy1_settings['value8'])
#     value9 = float(strategy1_settings['value9'])
#     value10 = float(strategy1_settings['value10'])
#
#
#     # indicater part
#
#     myratio =  Indicater.myratio(data, value1, value2)
#     mysma = Indicater.calculate_sma(data,window=6)
#     myema = Indicater.calculate_ema(data,window=9)
#     myvwap = Indicater.calculate_vwap(data=data)
#
#
#
#
#     # Iterate through data for strategy 1
#     for i in range(1, len(data)):
#         # ------------------------------- INTRA EXIT -------------------------------------------------------
#
#         # Reset trades at the beginning of a new day
#         if data['date'].iloc[i] != data['date'].iloc[i - 1]:
#             LongTrade = 0
#             ShortTrade = 0
#             TradesTaken = 0
#             opend = data['open'].iloc[i]
#
#             day_high = data['high'].iloc[i]
#             day_low = data['low'].iloc[i]
#             x = 1
#         else:
#             x = 0
#
#         # Initialize trade signals
#         LongSignal = 0
#         ShortSignal = 0
#
#         # Signal generation based on myindiz
#         if Flag < 1  and 1000 < data['time'].iloc[i] <= 1500 and data['time'].iloc[i] <= IntraExitTime:
#             if (data['time'].iloc[i] == 1525):
#                 LongSignal = 1
#
#         if Flag > -1  and 920 < data['time'].iloc[i] <= 1500 and data['time'].iloc[i] <= IntraExitTime :
#             if (data['close'].iloc[i] < myvwap['vwap'].iloc[i]*1.1):
#                 ShortSignal = 1
#             # if (data['time'].iloc[i] == 1118):
#             #     ShortSignal = 1
#
#             # ------------------------------BUY SELL CHECK--------------------------------------------
#
#         if LongSignal == 1 and ShortSignal == 1:
#             LongSignal = 0
#             ShortSignal = 0
#
#         if LongOnly == 1 and ShortSignal == 1:
#             if Flag == 1:
#                 # exit long position
#                 Exit_Date = data['date'].iloc[i]
#                 Exit_price = data['close'].iloc[i]
#                 Exit_time = data['time'].iloc[i]
#                 Exit_action = "El"
#                 Flag = 0
#             ShortSignal = 0
#
#         if ShortOnly == 1 and LongSignal == 1:
#             if Flag == -1:
#                 # exit short position
#                 Exit_price = data['close'].iloc[i]
#                 Exit_Date = data['date'].iloc[i]
#                 Exit_time = data['time'].iloc[i]
#                 Exit_action = "ES"
#                 Flag = 0
#             LongSignal = 0
#
#         # Handle reversal situations
#
#         if LongSignal == 1 and Flag == -1:  # Reverse from Short to Long
#             Exit_price = data['close'].iloc[i]
#             Exit_time = data['time'].iloc[i]
#             Exit_action = "Reversal to Long"
#             trades[-1].update({
#                 'exit_date': data['date'].iloc[i],
#                 'exit_time': Exit_time,
#                 'exit_price': Exit_price,
#                 'exit_action': Exit_action,
#             })
#             Flag = 0  # Exit the short trade before entering the long
#
#         if ShortSignal == 1 and Flag == 1:  # Reverse from Long to Short
#             Exit_price = data['close'].iloc[i]
#             Exit_time = data['time'].iloc[i]
#             Exit_action = "Reversal to Short"
#             trades[-1].update({
#                 'exit_date': data['date'].iloc[i],
#                 'exit_time': Exit_time,
#                 'exit_price': Exit_price,
#                 'exit_action': Exit_action,
#             })
#             Flag = 0  # Exit the long trade before entering the short
#
#
#
#
#         # ------------------------------BUY SELL CHECK--------------------------------------------
#
#
#
#         # Entry logic after handling potential reversals
#         if LongSignal == 1 and Flag !=1 and LETime <= data['time'].iloc[
#             i] <= LXTime and LongTrade < AllowedTradesLong and TradesTaken < AllowedTrades and (
#                 LongAlternate == 0 or (LongAlternate == 1 and (LastTradeType == -1 or LastTradeType == 0))
#         ) and UndisputedShort == 0:
#             Action = "BUY"
#             Flag = 1
#             LastTradeType = 1
#             DateOfTrade = data['date'].iloc[i]
#             DateOfTime = data['time'].iloc[i]
#             TradeBarnumber = i
#             HighestHigh = data['high'].iloc[i]
#             LowestLow = data['low'].iloc[i]
#             LongTrade += 1
#             TradesTaken += 1
#             LongEntryPrice = data['close'].iloc[i]
#             LastEntryPrice = data['close'].iloc[i]
#             if LSL_P != 0:
#                 LongStopP = LongEntryPrice - (LongEntryPrice * 0.01 * LSL_P)
#             if LT_P != 0:
#                 LongTargetP = LongEntryPrice + (LongEntryPrice * 0.01 * LT_P)
#             if LTrailPercent != 0:
#                 LongTrailP = (data['close'].iloc[i] * 0.01 * LTrailPercent)
#             if LSL_A != 0:
#                 LongStopA = LongEntryPrice - LSL_A
#             if LT_A != 0:
#                 LongTargetA = LongEntryPrice + LT_A
#             if LTrailAbs != 0:
#                 LongTrailA = LTrailAbs
#
#             # Determine final Long Stop and Target values
#             # Determine final Long Stop value
#             LongStop = max([val for val in [LongStopP, LongStopA] if val not in (None, 0)], default=0)
#             LongTarget = min([val for val in [LongTargetP, LongTargetA] if val not in (None, 0)], default=0)
#
#             trades.append({
#                 'strategy': stock_name,
#                 'entry_action': Action,
#                 'SL': LongStop,
#                 'TP': LongTarget,
#                 'qty': +Qty if QtyAbs ==1 else int(Capital/data['close'].iloc[i]),
#                 'entry_date': DateOfTrade,
#                 'entry_time': DateOfTime,
#                 'entry_price': LastEntryPrice,
#
#             })
#
#         if ShortSignal == 1 and Flag !=-1 and SETime <= data['time'].iloc[
#             i] <= SXTime and ShortTrade < AllowedTradesShort and TradesTaken < AllowedTrades and (
#                 ShortAlternate == 0 or (ShortAlternate == 1 and (LastTradeType == 1 or LastTradeType == 0))
#         ) and UndisputedLong == 0:
#             Action = "SELL"
#             Flag = -1
#             LastTradeType = -1
#             DateOfTrade = data['date'].iloc[i]
#             DateOfTime = data['time'].iloc[i]
#             TradeBarnumber = i
#             HighestHigh = data['high'].iloc[i]
#             LowestLow = data['low'].iloc[i]
#             ShortTrade += 1
#             TradesTaken += 1
#             ShortEntryPrice = data['close'].iloc[i]
#             LastEntryPrice = data['close'].iloc[i]
#             if SSL_P != 0:
#                 ShortStopP = ShortEntryPrice + (ShortEntryPrice * 0.01 * SSL_P)
#             if ST_P != 0:
#                 ShortTargetP = ShortEntryPrice - (ShortEntryPrice * 0.01 * ST_P)
#             if STrailPercent != 0:
#                 ShortTrailP = (data['close'].iloc[i] * 0.01 * STrailPercent)
#             if SSL_A != 0:
#                 ShortStopA = ShortEntryPrice + SSL_A
#             if ST_A != 0:
#                 ShortTargetA = ShortEntryPrice - ST_A
#             if STrailAbs != 0:
#                 ShortTrailA = STrailAbs
#
#             # Determine final Short Stop value
#             ShortStop = min([val for val in [ShortStopP, ShortStopA] if val not in (None, 0)], default=0)
#             ShortTarget = max([val for val in [ShortTargetP, ShortTargetA] if val not in (None, 0)], default=0)
#
#             trades.append({
#                 'strategy': stock_name,
#                 'entry_action': Action,
#                 'SL': ShortStop ,
#                 'TP': ShortTarget,
#                 'qty': -Qty if QtyAbs ==1 else -int(Capital/data['close'].iloc[i]),
#                 'entry_date': DateOfTrade,
#                 'entry_time': DateOfTime,
#                 'entry_price': LastEntryPrice,
#
#             })
#         # ----------------------------STOP TGT SELECTION-----------------------------------------------
#
#         if Flag == 1 and data['high'].iloc[i] > HighestHigh:
#             HighestHigh = data['high'].iloc[i]
#         if Flag == 1 and data['low'].iloc[i] < LowestLow:
#             LowestLow = data['low'].iloc[i]
#
#         LongStop = 0
#         if LSL_P != 0 and LongStop == 0:
#             LongStop = LongStopP
#         if LTrailPercent != 0 and (LongStop == 0 or HighestHigh - LongTrailP > LongStopP):
#             LongStop = round(HighestHigh - LongTrailP, Precision)
#         if LTrailAbs != 0 and (LongStop == 0 or HighestHigh - LongTrailA > LongStop):
#             LongStop = round(HighestHigh - LongTrailA, Precision)
#         if LSL_A != 0 and (LongStop == 0 or LongStopA > LongStop):
#             LongStop = LongStopA
#
#         LongTarget = 0
#         if LT_A != 0 and LongTargetA > LongTarget:
#             LongTarget = LongTargetA
#         if LT_P != 0 and (LongTarget == 0 or LongTargetP < LongTarget):
#             LongTarget = LongTargetP
#
#         ShortStop = 0
#         if SSL_P != 0 and ShortStop == 0:
#             ShortStop = ShortStopP
#         if STrailPercent != 0 and (ShortStop == 0 or (LowestLow + ShortTrailP) < ShortStop):
#             ShortStop = round(LowestLow + ShortTrailP, Precision)
#         if STrailAbs != 0 and (ShortStop == 0 or (LowestLow + ShortTrailA) < ShortStop):
#             ShortStop = round(LowestLow + ShortTrailA, Precision)
#         if SSL_A != 0 and (ShortStop == 0 or ShortStopA < ShortStop):
#             ShortStop = ShortStopA
#
#         ShortTarget = 0
#         if ST_A != 0 and ShortTargetA < ShortTarget:
#             ShortTarget = ShortTargetA
#         if ST_P != 0 and (ShortTarget == 0 or ShortTargetP < ShortTarget):
#             ShortTarget = ShortTargetP
#
#         # ----------------------------Exit Conditions-----------------------------------------------
#
#         if Flag == 1 and data['close'].iloc[i] >= LongTarget and LongTarget != 0:
#             Exit_price = LongTarget
#             Exit_time = data['time'].iloc[i]
#             Exit_action = "LT"
#             Flag = 0
#         if Flag == 1 and data['close'].iloc[i] <= LongStop and LongStop != 0:
#             Exit_price = LongStop
#             Exit_time = data['time'].iloc[i]
#             Exit_action = "LSL"
#             Flag = 0
#         if Flag == -1 and data['close'].iloc[i] <= ShortTarget and ShortTarget != 0:
#             Exit_price = ShortTarget
#             Exit_time = data['time'].iloc[i]
#             Exit_action = "ST"
#             Flag = 0
#         if Flag == -1 and data['close'].iloc[i] >= ShortStop and ShortStop != 0:
#             Exit_price = ShortStop
#             Exit_time = data['time'].iloc[i]
#             Exit_action = "SSL"
#             Flag = 0
#
#         # Intra-day exit logic
#         if  Flag !=0 and IntraDayExit == 1 and (data['time'].iloc[i] == IntraExitTime or (data['time'].iloc[i] >= IntraExitTime and data['time'].iloc[i-1] < IntraExitTime))  :
#             Exit_price = data['close'].iloc[i]
#             Exit_time = data['time'].iloc[i]
#             Exit_action = "INTRA"
#             Flag = 0
#
#         if Exit_action:
#             trades[-1].update({
#                 'exit_date': data['date'].iloc[i],
#                 'exit_time': Exit_time,
#                 'exit_price': Exit_price,
#                 'exit_action': Exit_action,
#             })
#
#             Exit_action = ""
#
#
#     # Convert trades list to DataFrame and save to CSV
#     # trades_df = pd.DataFrame(trades)
#     # trades_df.to_csv(f"trades_{stock_name}.csv", index=False)
#
#     # print(f"{stock_name} tradesheet generated successfully.")
#
#     return pd.DataFrame(trades)


# Example Usage:

# # Assuming 'df' is your DataFrame containing 'open', 'high', 'low', 'close', and 'volume' columns
# df = calculate_sma(df, window=14)
# df = calculate_ema(df, window=14)
# df = calculate_bollinger_bands(df, window=20)
# df = calculate_rsi(df, window=14)
# df = calculate_macd(df)
# df = calculate_atr(df, window=14)
# df = calculate_stochastic(df, window=14)
# df = calculate_cci(df, window=20)
# df = calculate_roc(df, window=12)
# df = calculate_williams_r(df, window=14)
# df = calculate_psar(df)
# df = calculate_ichimoku(df)
# df = calculate_obv(df)
# df = calculate_adl(df)
# df = calculate_mfi(df)
# df = calculate_cmf(df)
# df = calculate_adx(df)
# df = calculate_vwap(df)
# df = calculate_keltner_channels(df)
# df = calculate_donchian_channels(df)



