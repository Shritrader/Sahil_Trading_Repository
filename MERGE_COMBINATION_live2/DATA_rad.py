import os
import shutil
import time
import re

# Define source and destination directories
source_dir = r"C:\Users\ADMIN\PycharmProjects\Data_engine\Index_data"
call_dest_dir = r"C:\Users\ADMIN\PycharmProjects\MERGE_COMBINATION_live2\Call"
put_dest_dir = r"C:\Users\ADMIN\PycharmProjects\MERGE_COMBINATION_live2\Put"

# List of selected strikes for Call and Put options
selected_call_strikes = ["13350","13375","13400","13425"]  # Update with your actual Call strikes
selected_put_strikes = ["13350","13325","13300","13275"]  # Update with your actual Put strikes

def extract_strike_price(filename):
    # Updated regex to match filenames like NSE_MIDCPNIFTY2490213000PE.csv
    # match = re.match(r"NSE_MIDCPNIFTY\d{5}(\d{4,5})(CE|PE)\.csv", filename)  #midcp
    match = re.match(r"NSE_MIDCPNIFTY\d{5}(\d{4,5})(CE|PE)\.csv", filename)  #banknifty

    if match:
        strike_price, option_type = match.groups()
        # Print extracted values for debugging
        print(f"Extracted strike price: {strike_price}, option type: {option_type}")
        return strike_price, option_type
    # Print message if filename does not match
    print(f"Filename does not match pattern: {filename}")
    return None, None

def move_and_rename_files():
    for filename in os.listdir(source_dir):
        try:
            # Print filename for debugging
            print(f"Processing file: {filename}")

            # Ensure filename ends with .csv
            if not filename.endswith(".csv"):
                print(f"Skipping file {filename}: not a CSV file.")
                continue

            strike_price, option_type = extract_strike_price(filename)

            # Check if we got valid strike price and option type
            if strike_price and option_type:
                # Print extracted values for debugging
                print(f"Found strike price: {strike_price}, option type: {option_type}")

                # Determine if the file should be moved based on the option type and strike price
                if option_type == "CE" and strike_price in selected_call_strikes:
                    new_filename = f"{strike_price}CE.csv"
                    dest_dir = call_dest_dir
                elif option_type == "PE" and strike_price in selected_put_strikes:
                    new_filename = f"{strike_price}PE.csv"
                    dest_dir = put_dest_dir
                else:
                    print(f"Skipping file {filename}: strike price or option type not selected.")
                    continue  # Skip if strike doesn't match selected strikes

                # Move and rename the file
                src_file = os.path.join(source_dir, filename)
                dest_file = os.path.join(dest_dir, new_filename)

                # Check if source file exists and destination directory exists
                if not os.path.exists(src_file):
                    print(f"Source file does not exist: {src_file}")
                    continue
                if not os.path.exists(dest_dir):
                    print(f"Destination directory does not exist: {dest_dir}")
                    os.makedirs(dest_dir)  # Create destination directory if it doesn't exist

                # Move the file
                shutil.copy(src_file, dest_file)
                print(f"Moved file {filename} to {dest_file}")
            else:
                print(f"Filename does not match pattern: {filename}")
        except Exception as e:
            print(f"Error processing file {filename}: {e}")

def main():
    try:
        while True:
            move_and_rename_files()
            time.sleep(1)  # Wait for 1 second before checking again
    except KeyboardInterrupt:
        print("Script interrupted by user. Exiting...")

if __name__ == "__main__":
    main()


# import re
#
# def extract_strike_price(filename):
#     # Updated regex to match filenames like NSE_MIDCPNIFTY2490213000PE.csv
#     match = re.match(r"NSE_MIDCPNIFTY\d{5}(\d{4,5})(CE|PE)\.csv", filename)
#     if match:
#         strike_price, option_type = match.groups()
#         # Print extracted values for debugging
#         print(f"Extracted strike price: {strike_price}, option type: {option_type}")
#         return strike_price, option_type
#     # Print message if filename does not match
#     print(f"Filename does not match pattern: {filename}")
#     return None, None
#
# # Test the function with example filenames
# test_filenames = [
#     "NSE_MIDCPNIFTY2490213000PE.csv",
#     "NSE_MIDCPNIFTY2490212750CE.csv",
#     "NSE_MIDCPNIFTY2490212650PE.csv",
#     "NSE_MIDCPNIFTY2490212600CE.csv"
# ]
#
# for test_filename in test_filenames:
#     print(f"Testing with filename: {test_filename}")
#     extract_strike_price(test_filename)

