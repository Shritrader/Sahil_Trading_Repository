import pandas as pd
# import matplotlib.pyplot as plt
from tkinter import Tk, Frame, Label, Text, ttk, END
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def convert_to_timeframe(df, timeframe, session_start, session_end):
    """
    Convert 1-minute OHLC data to a specified timeframe OHLC data, considering a specific trading session.

    Parameters:
    df (pd.DataFrame): Input DataFrame with columns ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
    timeframe (str): Desired timeframe for aggregation (e.g., '5T' for 5 minutes, '15T' for 15 minutes)
    session_start (str): Session start time in 'HH:MM' format (e.g., '09:15')
    session_end (str): Session end time in 'HH:MM' format (e.g., '15:30')

    Returns:
    pd.DataFrame: DataFrame with aggregated OHLC data for the specified timeframe within the session
    """
    # Combine 'date' and 'time' columns to create a datetime index
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + df['time'].astype(str).str.zfill(4), format='%Y%m%d%H%M')
    df.set_index('datetime', inplace=True)

    # Filter data to only include the session times
    session_start_time = pd.to_datetime(df.index.date.astype(str) + session_start, format='%Y-%m-%d%H:%M')
    session_end_time = pd.to_datetime(df.index.date.astype(str) + session_end, format='%Y-%m-%d%H:%M')
    df = df[(df.index >= session_start_time) & (df.index <= session_end_time)]

    # Resample the data to the desired timeframe
    resampled_df = df.resample(timeframe, label='right', closed='right').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    # Drop rows with NaN values if any
    resampled_df.dropna(inplace=True)

    # Reset index to have 'datetime' as a column again
    resampled_df.reset_index(inplace=True)

    # Extract and format date and time
    resampled_df['date'] = resampled_df['datetime'].dt.strftime('%Y%m%d').astype(int)
    resampled_df['time'] = resampled_df['datetime'].dt.strftime('%H%M').astype(int)

    # Drop the original 'datetime' column
    resampled_df.drop('datetime', axis=1, inplace=True)

    # Reorder the columns to match the desired format
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

def calculate_ema(data, window):
    data['ema'] = data['close'].ewm(span=window, adjust=False).mean()
    return data

def calculate_bollinger_bands(data, window=20):
    data['bb_middle'] = data['close'].rolling(window=window).mean()
    data['bb_upper'] = data['bb_middle'] + 2 * data['close'].rolling(window=window).std()
    data['bb_lower'] = data['bb_middle'] - 2 * data['close'].rolling(window=window).std()
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