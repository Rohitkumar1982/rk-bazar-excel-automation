import pandas as pd,csv
import numpy as np
from logging_util import logger

# Mapping BR_CODE to descriptive titles, key value pair for BR_CODE and title (for matching purpose)
BR_CODE = {
    'RKSK': '|| S2', 'RKTE': '|| S1', 'RKDS': '|| S3', 'RKPO': '|| S4', 
    'RKTM': '|| S5', 'RKKA': '|| S6', 'RKSN': '|| S7', 'RKN': '|| S8', 
    'RKA': '|| S9', 'RKW': '|| S10', 'RKPM': '|| S11'
}
BRICK = "-----------------------------------------------------------------------------\n"

def read_and_convert_csv(csv_file):
    """Reads CSV and replaces NaN with empty strings, returns as list of rows."""
    df = pd.read_csv(csv_file).replace(np.nan, "")
    return df.values.tolist()


def fetch_data(read_csv, write_csv, live_csv):
    """Reads all required CSVs and returns them as lists."""
    return (
        read_and_convert_csv(live_csv),
        read_and_convert_csv(read_csv),
        read_and_convert_csv(write_csv)
    )

def extract_codes(live_data, read_data, write_data):
    """Extracts and returns SKU and P_CODE lists from data."""
    live_p_codes = [str(row[0]).strip("'") for row in live_data]
    read_p_codes = [str(row[1]).strip("'") for row in read_data]
    sku_codes = [str(row[17]).strip("'") for row in write_data]
    return sku_codes, live_p_codes, read_p_codes


def verify_sku_codes(read_csv, write_csv, live_csv):

    seriel_num_edited = []
    final_all_value_edited = []

    """Verifies presence and relation of P_CODEs across files."""
    live_data, read_data, write_data = fetch_data(read_csv, write_csv, live_csv)
    sku_codes, live_p_codes, read_p_codes = extract_codes(live_data, read_data, write_data)

    for live_code in live_p_codes:
        message = f"▶ Start Working for P_CODE: {live_code} ............."
        logger.info(message)

        if live_code not in read_p_codes:
            logger.warning(f"⛔ P_CODE: {live_code} not found in read CSV. Skipping automation.")
            logger.info(BRICK)
            continue

        if live_code not in sku_codes:
            logger.warning(f"⛔ P_CODE {live_code} is present in read CSV but not found in write CSV. Skipping automation.")
            logger.info(BRICK)
            continue

        read_file_indexes = [i for i, code in enumerate(read_p_codes) if code == live_code]
        logger.info(f"✅ P_CODE {live_code} found in read CSV at rows: {[i + 2 for i in read_file_indexes]}")

        write_file_indexes = [i for i, sku in enumerate(sku_codes) if sku == live_code]
        logger.info(f"✅ P_CODE {live_code} found in write CSV at rows: {[i + 2 for i in write_file_indexes]}")

        for r_index in read_file_indexes:

            br_code = str(read_data[r_index][0])
            mrp, net_rate = str(read_data[r_index][4]), str(read_data[r_index][5])
            logger.info(f"📦 Details from read CSV according to {r_index+2} index: P_CODE={live_code}, BR_CODE={br_code}, MRP={mrp}, NET_SALE_RATE={net_rate}, BR_VALUE: {BR_CODE[br_code]}")

            for w_index in write_file_indexes:
                # if BR_CODE[br_code] in write_data[w_index][1] and '||'+write_data[w_index][1].split('||')[-1]:
                if BR_CODE[br_code] == f"||{write_data[w_index][1].split('||')[-1]}":
                    find_index_detail = f"SKU CODE or P_CODE : {live_code} and BR_VALUE: '{BR_CODE[br_code]}' found in write CSV file at rows {w_index+2}"
                    logger.info(find_index_detail)

                    try:
                        if write_data[w_index][22] == '' or write_data[w_index][23] == '':
                            find_index_detail = "Find exact serial number for this P_CODE : " + live_code + "  where we have to change the value i.e "+ str(w_index+1) + " Index number"
                            logger.info(find_index_detail)
                            write_data[w_index][22] = net_rate
                            write_data[w_index][23] = mrp
                            final_all_value_edited.append(list(write_data[w_index]))
                            value_you_editied = write_and_save_csv(w_index,mrp,net_rate)
                            # final_all_value_edited.append({p_code : br_vale})
                            if value_you_editied not in seriel_num_edited:
                                seriel_num_edited.append(value_you_editied)
                        
                        elif str(int(float(write_data[w_index][22]))) not in  str(net_rate) or str(int(float(write_data[w_index][23]))) not in  str(mrp):
                            find_index_detail = "Find exact serial number for this P_CODE : " + live_code + "  where we have to change the value i.e "+ str(w_index+2) + " Index number"
                            logger.info(find_index_detail)
                            write_data[w_index][22] = net_rate
                            write_data[w_index][23] = mrp
                            final_all_value_edited.append(list(write_data[w_index]))
                            value_you_editied = write_and_save_csv(w_index,mrp,net_rate)
                            # final_all_value_edited.append({p_code : br_vale})
                            if value_you_editied not in seriel_num_edited:
                                seriel_num_edited.append(value_you_editied)
                        else:
                            message = "MRP and Net Sale Rate both are same in read and write file, So skipping the modication."
                            logger.info(message)

                    except ValueError:
                        except_detail =str(live_code) + " with value of BR_CODE " + br_code + " has been repeated hence discard to change the value"
                        logger.info(except_detail)
                        pass
                    except Exception as ex:
                        logger.info(ex)
                    break        
        logger.info(BRICK)
    edited_value = "Value You had edited in Write csv file are : " +  seriel_num_edited.__str__()
    save_file_after_editing(final_all_value_edited)
    logger.info(edited_value)  
    logger.info(final_all_value_edited)    

    return seriel_num_edited





def read_and_search_csv(read_csv_file, write_csv_file,live_csv_file):
    verify_sku_codes(read_csv_file, write_csv_file, live_csv_file)
    # creating key value pair for BR_CODE and title (for matching purpose)
    br_code = {'RKBK' : '|| S2', 'RKTE' : '|| S1', 'RKDS' : '|| S3', 'RKPO':'|| S4', 'RKTM':'|| S5', 'RKKA':'|| S6', 'RKSN':'|| S7', 'RKN':'|| S8', 'RKA':'|| S9', 'RKW':'|| S10', 'RKPM':'|| S11'}

    sku_code = []    #storing all Variant SKU of write_csv_file

    p_code_from_live_file = []    ##storing all P_CODE of live_csv_file

    p_code_from_read_file_df = []    ##storing all P_CODE of read_file_df

    # reading live_csv_file and after converting into array
    live_file_df = pd.read_csv(live_csv_file)
    live_file_df = live_file_df.values.tolist()

    # reading read_csv_file and after converting into array
    read_file_df = pd.read_csv(read_csv_file)
    read_file_df = read_file_df.values.tolist()

    # reading write_csv_file and after converting into array
    write_file_df = pd.read_csv(write_csv_file)
    write_file_df = write_file_df.replace(np.nan,"")   #removing all spaces with a empty string value
    write_file_df = write_file_df.values.tolist()

    # iterating live_file_df and appending all P_CODE in p_code_from_live_file array
    for product in live_file_df:
        p_code_from_live_file.append(str(product[0]).replace("'",''))

    # iterating write_file_df and appending all Variant SKU in sku_code array
    for product in write_file_df:
        sku_code.append(str(product[17]).replace("'",''))

    # iterating read_file_df and appending all Variant SKU in p_code_from_read_file_df array
    for product in read_file_df:
        p_code_from_read_file_df.append(str(product[1]).replace("'",''))

    check_alredy_done = []
    seriel_num_edited = []
    final_all_value_edited = []

    i = 0
    for item in live_file_df:
        
        start_details = "Start Working ................... " + str(item[0]) 
        logger.info(start_details)

        code_from_live = str(item[0])     #P_CODE from live_file_pdf
        
        if code_from_live not in check_alredy_done:  # checking for duplication of p_code which is present in dark sku code
            
            check_alredy_done.append(code_from_live)
            if code_from_live in p_code_from_read_file_df:   #checking code_from_live is present in read_file_df
                # if yes code_from_live present then finding all index of that code_from_live from p_code_from_read_file_df array
                finding_all_index_of_p_code = [index for index,items in enumerate(p_code_from_read_file_df) if items == code_from_live]

                for index_of_p_code in finding_all_index_of_p_code:   #now start checking index by index in read_file_df
                    code_from_read_file = str(read_file_df[index_of_p_code][1])

                    p_code , br_vale = code_from_read_file, str(read_file_df[index_of_p_code][0])    #finding P_CODE and BR_CODE
                    mrp , net_sale_rate = str(read_file_df[index_of_p_code][4]), str(read_file_df[index_of_p_code][5])
                    
                    all_details = {'P_CODE' : p_code, 'BR_CODE' : br_vale, 'MRP' : mrp , 'NET_SALE_RATE' : net_sale_rate  }
                    logger.info(all_details)
                    
                    if code_from_read_file in sku_code:    #checking that code present in sku_code or not
                        # if yes code_from_read_file present then finding all index of that code_from_read_file from sku_code array
                        finding_all_index_of_sku_code = [index for index,items in enumerate(sku_code) if items == str(item[0])]

                        for index_of_sku_code in finding_all_index_of_sku_code:
                            if br_code[br_vale] in write_file_df[index_of_sku_code][1]:
                                find_index_detail = "P_CODE : " + p_code + "  is present in SKU CODE file (writting file)"
                                logger.info(find_index_detail)

                                try:

                                    if write_file_df[index_of_sku_code][22] == '' or write_file_df[index_of_sku_code][23] == '':
                                        find_index_detail = "Find exact serial number for this P_CODE : " + p_code + "  where we have to change the value i.e "+ str(index_of_sku_code+1) + " Index number"
                                        logger.info(find_index_detail)
                                        write_file_df[index_of_sku_code][22] = net_sale_rate
                                        write_file_df[index_of_sku_code][23] = mrp
                                        final_all_value_edited.append(list(write_file_df[index_of_sku_code]))
                                        value_you_editied = write_and_save_csv(index_of_sku_code,mrp,net_sale_rate)
                                        # final_all_value_edited.append({p_code : br_vale})
                                        if value_you_editied not in seriel_num_edited:
                                            seriel_num_edited.append(value_you_editied)
                                    
                                    elif str(int(float(write_file_df[index_of_sku_code][22]))) not in  str(net_sale_rate) or str(int(float(write_file_df[index_of_sku_code][23]))) not in  str(mrp):
                                        find_index_detail = "Find exact serial number for this P_CODE : " + p_code + "  where we have to change the value i.e "+ str(index_of_sku_code+1) + " Index number"
                                        logger.info(find_index_detail)
                                        write_file_df[index_of_sku_code][22] = net_sale_rate
                                        write_file_df[index_of_sku_code][23] = mrp
                                        final_all_value_edited.append(list(write_file_df[index_of_sku_code]))
                                        value_you_editied = write_and_save_csv(index_of_sku_code,mrp,net_sale_rate)
                                        # final_all_value_edited.append({p_code : br_vale})
                                        if value_you_editied not in seriel_num_edited:
                                            seriel_num_edited.append(value_you_editied)


                                except ValueError:
                                    except_detail =str(p_code) + " with value of BR_CODE " + br_vale + " has been repeated hence discard to change the value"
                                    logger.info(except_detail)
                                    pass
                                except Exception as exe:
                                    logger.info(exe)

    
    edited_value = "Value You had edited in Write csv file are : " +  seriel_num_edited.__str__()
    save_file_after_editing(final_all_value_edited)
    logger.info(edited_value)  
    logger.info(final_all_value_edited)    

    return seriel_num_edited

def write_and_save_csv(final_index,mrp,net_sale_rate):
    with open(write_csv_file, mode='r',encoding='UTF-8') as file:
        write_file = csv.reader(file)
        data = list(write_file)

    logger.info("Start checking value for changing purpose....")
    # checking Variant Price and NET_SALE_RATE 
    # if both are same just pass else changing the value of Variant Price
    if (data[final_index+1][22] == ''):
        data[final_index+1][22] = 0

    if int((float(data[final_index+1][22])) == int(float(net_sale_rate))):
        pass
    else:
        row_index = final_index+1
        col_index = 22
        new_value = net_sale_rate
        changing_value = "Variant Price and NET_SALE_RATE are not matching for serial number " + str(row_index+1) + " So, we are changing the value according to read_file_df"
        exact_value = "Earlier NET_SALE_RATE is : " + str(data[row_index][22]) + " After changing this value we get : " + str(float(net_sale_rate))
        logger.info(changing_value)
        logger.info(exact_value)
        data[row_index][col_index] = new_value
        with open(write_csv_file, mode='w', newline='',encoding='UTF-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    # checking Variant Compare At Price and MRP 
    # if both are same just pass else changing the value of Variant Compare At Price
    if (data[final_index+1][23] == ''):
        data[final_index+1][23] = 0

    if int((float(data[final_index+1][23])) == int(float(mrp))):
        pass
    else:
        row_index = final_index+1
        col_index = 23
        new_value = mrp
        changing_value = "Variant Compare At Price and MRP are not matching for serial number " + str(row_index+1) + " So, we are changing the value according to read_file_df"
        exact_value = "Earlier Variant Compare At Price is : " + str(data[row_index][23]) + " After changing this value we get : " + str(float(mrp))
        logger.info(changing_value)
        logger.info(exact_value)
        data[row_index][col_index] = new_value
        with open(write_csv_file, mode='w', newline='',encoding='UTF-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    return str(final_index+2)


def save_file_after_editing(final_all_value_edited):
    # header is taken from write.csv itself, so the output always matches the Shopify template
    head1 = pd.read_csv(write_csv_file, nrows=0).columns.tolist()

    with open('save_final_file.csv', 'w', newline='',encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(head1)
        for value in final_all_value_edited:
            writer.writerow(value)


# read_csv_file = 'C://Users//hp//Rohit_project_Automation//web_product_search.csv'  #put always search csv file
# write_csv_file = 'C://Users//hp//Rohit_project_Automation//products_export_write.csv'  #put always write csv file
# live_csv_file = 'C://Users//hp//Rohit_project_Automation//Dark Store SKU.csv'  #put always live csv file

read_csv_file = 'read.csv'  #put always search csv file
write_csv_file = 'write.csv'  #put always write csv file
live_csv_file = 'Dark Store SKU.csv'  #put always live csv file

# print(read_and_search_csv(read_csv_file, write_csv_file,live_csv_file))
print(verify_sku_codes(read_csv_file, write_csv_file,live_csv_file))
# ValueError
