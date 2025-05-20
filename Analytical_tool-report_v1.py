import os
import pandas as pd


print("0  - This option generates a report for each individual trade sheet file.")
print("1  - This option generates a standard pivot table report.")
print("2  - This option generates a custom linear table report.")
File_select = int(input("Enter the FILE Type (e.g., 0 or  1 or 2): "))


if File_select == 0 :
    print("0  - This option generates a report for each individual trade sheet file.")


    def analyze_trades(csv_file, output_excel, percentage_cost=0.000125, per_unit_cost=1.5):


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


    # Define directories
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



if File_select == 1:
    print("1  - This option generates a standard pivot table report.")

    def calculate_metrics(df):
        df['CumulativeMTM'] = df['MTM'].cumsum()
        df['Peak'] = df['CumulativeMTM'].cummax()
        df['Drawdown'] = df['Peak'] - df['CumulativeMTM']

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
        max_monthly_dd = df.groupby(df['entry_month'])['Drawdown'].max().max()
        max_yearly_dd = df.groupby(df['entry_year'])['Drawdown'].max().max()

        daily_profitability = (df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum() > 0).mean()
        monthly_profitability = (df.groupby(df['entry_month'])['MTM'].sum() > 0).mean()
        yearly_profitability = (df.groupby(df['entry_year'])['MTM'].sum() > 0).mean()

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
            'Average Yearly Profit': df.groupby(df['entry_year'])['MTM'].sum().mean(),
            'Daily Profitability': daily_profitability,
            'Monthly Profitability': monthly_profitability,
            'Yearly Profitability': yearly_profitability
        }

    def analyze_trades(input_dir, output_excel, percentage_cost=0.000125, per_unit_cost=1.5):
        all_trades = []

        for file_name in os.listdir(input_dir):
            if file_name.endswith('.csv'):
                csv_file = os.path.join(input_dir, file_name)
                try:
                    trades_df = pd.read_csv(csv_file)
                    if trades_df.empty or trades_df.isnull().all().all():
                        print(f"Skipped blank or empty file: {file_name}")
                        continue
                except pd.errors.EmptyDataError:
                    print(f"Skipped empty file: {file_name}")
                    continue
                except Exception as e:
                    print(f"Skipped file {file_name} due to error: {e}")
                    continue

                trades_df['PercentageCost'] = trades_df['entry_price'] * 2 * percentage_cost * abs(trades_df['qty'])
                trades_df['PerUnitCost'] = per_unit_cost * abs(trades_df['qty'])
                trades_df['MTM'] = ((trades_df['exit_price'] - trades_df['entry_price']) * trades_df['qty']) - trades_df['PercentageCost'] - trades_df['PerUnitCost']

                trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date'], format='%Y%m%d', errors='coerce')
                trades_df.dropna(subset=['entry_date'], inplace=True)
                trades_df = trades_df.sort_values(by='entry_date')
                trades_df['CumulativeMTM'] = trades_df['MTM'].cumsum()
                trades_df['file_name'] = file_name
                all_trades.append(trades_df)

        if not all_trades:
            print("No valid trades to process.")
            return

        combined_trades = pd.concat(all_trades)

        daily_profit = combined_trades.groupby(['entry_date', 'file_name']).agg(DailyMTM=('MTM', 'sum')).reset_index()
        daily_pivot = daily_profit.pivot(index='entry_date', columns='file_name', values='DailyMTM').fillna(0).reset_index()

        combined_trades['entry_month'] = combined_trades['entry_date'].dt.to_period('M')
        monthly_profit = combined_trades.groupby(['entry_month', 'file_name']).agg(MonthlyMTM=('MTM', 'sum')).reset_index()
        monthly_pivot = monthly_profit.pivot(index='entry_month', columns='file_name', values='MonthlyMTM').fillna(0).reset_index()

        combined_trades['entry_year'] = combined_trades['entry_date'].dt.year
        yearly_profit = combined_trades.groupby(['entry_year', 'file_name']).agg(YearlyMTM=('MTM', 'sum')).reset_index()
        yearly_pivot = yearly_profit.pivot(index='entry_year', columns='file_name', values='YearlyMTM').fillna(0).reset_index()

        long_trades = combined_trades[combined_trades['qty'] > 0]
        short_trades = combined_trades[combined_trades['qty'] < 0]

        all_metrics = calculate_metrics(combined_trades)
        long_metrics = calculate_metrics(long_trades)
        short_metrics = calculate_metrics(short_trades)

        metrics_df = pd.DataFrame({
            'Metric': [
                'Net profit', 'MAX DD', 'CALMA ratio', 'Max qty', 'Gross Profit',
                'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit',
                'Daily Profitability', 'Monthly Profitability', 'Yearly Profitability'
            ],
            'All Trades': list(all_metrics.values()),
            'Long Trades': list(long_metrics.values()),
            'Short Trades': list(short_metrics.values())
        })

        with pd.ExcelWriter(output_excel) as writer:
            combined_trades[['entry_date', 'entry_price', 'exit_price', 'qty', 'MTM', 'file_name']].to_excel(writer, sheet_name='Trade Analysis', index=False)
            daily_pivot.to_excel(writer, sheet_name='Daily Profit Analysis', index=False)
            monthly_pivot.to_excel(writer, sheet_name='Monthly Profit Analysis', index=False)
            yearly_pivot.to_excel(writer, sheet_name='Yearly Profit Analysis', index=False)
            metrics_df.to_excel(writer, sheet_name='Analysis', index=False)

        print(f"Trade analysis has been written to {output_excel}")

    input_dir = 'Tradesheet'
    output_excel = 'report_analysis/combined_analysis.xlsx'

    percentage_cost = float(input("Enter the percentage cost (e.g., 0.000125 for 0.1%): "))
    per_unit_cost = float(input("Enter the per-unit cost: "))

    os.makedirs(os.path.dirname(output_excel), exist_ok=True)
    analyze_trades(input_dir, output_excel, percentage_cost, per_unit_cost)





if File_select == 2 :
    print("2  - This option generates a custom linear table report.")

    def calculate_metrics(df):
        # Calculate cumulative MTM
        df['CumulativeMTM'] = df['MTM'].cumsum()

        # Calculate the drawdown
        df['Peak'] = df['CumulativeMTM'].cummax()
        df['Drawdown'] = df['Peak'] - df['CumulativeMTM']

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
        max_monthly_dd = df.groupby(df['entry_month'])['Drawdown'].max().max()
        max_yearly_dd = df.groupby(df['entry_year'])['Drawdown'].max().max()

        # Calculate profitability metrics
        daily_profitability = (df.groupby(df['entry_date'].dt.strftime('%Y%m%d'))['MTM'].sum() > 0).mean()
        monthly_profitability = (df.groupby(df['entry_month'])['MTM'].sum() > 0).mean()
        yearly_profitability = (df.groupby(df['entry_year'])['MTM'].sum() > 0).mean()

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
            'Average Yearly Profit': df.groupby(df['entry_year'])['MTM'].sum().mean(),
            'Daily Profitability': daily_profitability,
            'Monthly Profitability': monthly_profitability,
            'Yearly Profitability': yearly_profitability
        }


    def analyze_trades(input_dir, output_excel, percentage_cost=0.000125, per_unit_cost=1.5):
        all_trades = []

        for file_name in os.listdir(input_dir):
            if file_name.endswith('.csv'):
                csv_file = os.path.join(input_dir, file_name)
                trades_df = pd.read_csv(csv_file)

                # Calculate percentage and per-unit costs
                trades_df['PercentageCost'] = trades_df['entry_price'] * 2 * percentage_cost * abs(trades_df['qty'])
                trades_df['PerUnitCost'] = per_unit_cost * abs(trades_df['qty'])

                # Calculate MTM for each trade, including costs
                trades_df['MTM'] = ((trades_df['exit_price'] - trades_df['entry_price']) * trades_df['qty']) - \
                                   trades_df[
                                       'PercentageCost'] - trades_df['PerUnitCost']

                # Convert entry_date to datetime
                trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date'], format='%Y%m%d')

                # Calculate cumulative MTM for drawdown
                trades_df = trades_df.sort_values(by='entry_date')
                trades_df['CumulativeMTM'] = trades_df['MTM'].cumsum()

                trades_df['file_name'] = file_name
                all_trades.append(trades_df)

        combined_trades = pd.concat(all_trades)

        # Calculate Daily MTM and drawdown
        daily_profit = combined_trades.groupby(['entry_date', 'file_name']).agg(
            DailyMTM=('MTM', 'sum')
        ).reset_index()
        daily_profit['CumulativeMTM'] = daily_profit.groupby('file_name')['DailyMTM'].cumsum()
        daily_profit['Peak'] = daily_profit.groupby('file_name')['CumulativeMTM'].cummax()
        daily_profit['Drawdown'] = daily_profit['Peak'] - daily_profit['CumulativeMTM']
        daily_pivot = daily_profit.pivot(index='entry_date', columns='file_name', values='DailyMTM')
        daily_pivot.fillna(0, inplace=True)
        daily_pivot.reset_index(inplace=True)

        # Calculate Monthly MTM and drawdown
        combined_trades['entry_month'] = combined_trades['entry_date'].dt.to_period('M')
        monthly_profit = combined_trades.groupby(['entry_month', 'file_name']).agg(
            MonthlyMTM=('MTM', 'sum')
        ).reset_index()
        monthly_profit['CumulativeMTM'] = monthly_profit.groupby('file_name')['MonthlyMTM'].cumsum()
        monthly_profit['Peak'] = monthly_profit.groupby('file_name')['CumulativeMTM'].cummax()
        monthly_profit['Drawdown'] = monthly_profit['Peak'] - monthly_profit['CumulativeMTM']
        monthly_pivot = monthly_profit.pivot(index='entry_month', columns='file_name', values='MonthlyMTM')
        monthly_pivot.fillna(0, inplace=True)
        monthly_pivot.reset_index(inplace=True)

        # Calculate Yearly MTM and drawdown
        combined_trades['entry_year'] = combined_trades['entry_date'].dt.year
        yearly_profit = combined_trades.groupby(['entry_year', 'file_name']).agg(
            YearlyMTM=('MTM', 'sum')
        ).reset_index()
        yearly_profit['CumulativeMTM'] = yearly_profit.groupby('file_name')['YearlyMTM'].cumsum()
        yearly_profit['Peak'] = yearly_profit.groupby('file_name')['CumulativeMTM'].cummax()
        yearly_profit['Drawdown'] = yearly_profit['Peak'] - yearly_profit['CumulativeMTM']
        yearly_pivot = yearly_profit.pivot(index='entry_year', columns='file_name', values='YearlyMTM')
        yearly_pivot.fillna(0, inplace=True)
        yearly_pivot.reset_index(inplace=True)

        # Separate long and short trades
        long_trades = combined_trades[combined_trades['qty'] > 0]
        short_trades = combined_trades[combined_trades['qty'] < 0]

        # Calculate metrics for all, long, and short trades
        all_metrics = calculate_metrics(combined_trades)
        long_metrics = calculate_metrics(long_trades)
        short_metrics = calculate_metrics(short_trades)

        # Create a DataFrame for the Analysis sheet
        metrics_df = pd.DataFrame({
            'Metric': [
                'Net profit', 'MAX DD', 'CALMA ratio', 'Max qty', 'Gross Profit',
                'Gross Loss', 'Profit Factor', 'Day Max Profit', 'Day Max Loss',
                'Total Trades', 'Max daily DD', 'Max monthly DD', 'Max Yearly DD',
                'Average Daily Profit', 'Average Monthly Profit', 'Average Yearly Profit',
                'Daily Profitability', 'Monthly Profitability', 'Yearly Profitability'
            ],
            'All Trades': [
                all_metrics['Net profit'], all_metrics['MAX DD'], all_metrics['CALMA ratio'], all_metrics['Max qty'],
                all_metrics['Gross Profit'], all_metrics['Gross Loss'], all_metrics['Profit Factor'],
                all_metrics['Day Max Profit'], all_metrics['Day Max Loss'], all_metrics['Total Trades'],
                all_metrics['Max daily DD'], all_metrics['Max monthly DD'], all_metrics['Max Yearly DD'],
                all_metrics['Average Daily Profit'], all_metrics['Average Monthly Profit'],
                all_metrics['Average Yearly Profit'],
                all_metrics['Daily Profitability'], all_metrics['Monthly Profitability'],
                all_metrics['Yearly Profitability']
            ],
            'Long Trades': [
                long_metrics['Net profit'], long_metrics['MAX DD'], long_metrics['CALMA ratio'],
                long_metrics['Max qty'],
                long_metrics['Gross Profit'], long_metrics['Gross Loss'], long_metrics['Profit Factor'],
                long_metrics['Day Max Profit'], long_metrics['Day Max Loss'], long_metrics['Total Trades'],
                long_metrics['Max daily DD'], long_metrics['Max monthly DD'], long_metrics['Max Yearly DD'],
                long_metrics['Average Daily Profit'], long_metrics['Average Monthly Profit'],
                long_metrics['Average Yearly Profit'],
                long_metrics['Daily Profitability'], long_metrics['Monthly Profitability'],
                long_metrics['Yearly Profitability']
            ],
            'Short Trades': [
                short_metrics['Net profit'], short_metrics['MAX DD'], short_metrics['CALMA ratio'],
                short_metrics['Max qty'],
                short_metrics['Gross Profit'], short_metrics['Gross Loss'], short_metrics['Profit Factor'],
                short_metrics['Day Max Profit'], short_metrics['Day Max Loss'], short_metrics['Total Trades'],
                short_metrics['Max daily DD'], short_metrics['Max monthly DD'], short_metrics['Max Yearly DD'],
                short_metrics['Average Daily Profit'], short_metrics['Average Monthly Profit'],
                short_metrics['Average Yearly Profit'],
                short_metrics['Daily Profitability'], short_metrics['Monthly Profitability'],
                short_metrics['Yearly Profitability']
            ]
        })

        with pd.ExcelWriter(output_excel) as writer:
            combined_trades[['entry_date', 'entry_price', 'exit_price', 'qty', 'MTM', 'file_name', 'CumulativeMTM',
                             'Drawdown']].to_excel(
                writer, sheet_name='Trade Analysis', index=False
            )
            daily_profit.to_excel(writer, sheet_name='Daily Profit Analysis', index=False)
            monthly_profit.to_excel(writer, sheet_name='Monthly Profit Analysis', index=False)
            yearly_profit.to_excel(writer, sheet_name='Yearly Profit Analysis', index=False)
            metrics_df.to_excel(writer, sheet_name='Analysis', index=False)

        print(f"Trade analysis has been written to {output_excel}")


    # Define directories
    input_dir = 'Tradesheet'
    output_excel = 'report_analysis/combined_analysis.xlsx'

    # Get user inputs for costs
    percentage_cost = float(input("Enter the percentage cost (e.g., 0.000125 for 0.1%): "))
    per_unit_cost = float(input("Enter the per-unit cost: "))

    # Create output directory if it does not exist
    os.makedirs(os.path.dirname(output_excel), exist_ok=True)

    # Analyze trades from the input directory and save to Excel
    analyze_trades(input_dir, output_excel, percentage_cost, per_unit_cost)
