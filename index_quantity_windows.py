import pandas as pd,csv
import numpy as np
from logging_util import logger


def read_and_search_csv(read_csv_file, write_csv_file,live_csv_file):
    # creating key value pair for BR_CODE and title (for matching purpose)
    br_code = {'RKSK' : '|| S2', 'RKTE' : '|| S1', 'RKDS' : '|| S3', 'RKP':'|| S4', 'RKTM':'|| S5', 'RKKA':'|| S6', 'RKRP':'|| S7', 'RKN':'|| S8', 'RKA':'|| S9', 'RKW':'|| S10', 'RKPM':'|| S11' }

    # creating key value pair for BR_CODE and Location (for matching purpose)
    br_code_location = {"RKTE" : "1 RKTE", "RKSK" : "2 RKSK", "RKDS" : "3 RKDS","RKP":"4 RKP","RKTM": "5 RKTM","RKKA": "6 RKKA","RKRP": "7 RKRP","RKN": "8 RKN","RKA": "9 RKA","RKW": "10 RKW","RKPM": "11 RKPM"}

    sku_code = []    #storing all Variant SKU of write_csv_file

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

    # iterating write_file_df and appending all Variant SKU in sku_code array
    for product in write_file_df:
        sku_code.append(str(product[8]).replace("'",''))

    # iterating read_file_df and appending all Variant SKU in p_code_from_read_file_df array
    for product in read_file_df:
        p_code_from_read_file_df.append(str(product[1]).replace("'",''))

    check_alredy_done = []
    final_all_value_edited = []

    final_all_details_for_zero_qnty = []
    for item in live_file_df:
        
        start_details = "Start Working ................... " + str(item[0]) 
        logger.info(start_details)

        code_from_live = str(item[0])     #P_CODE from live_file_pdf
        
        if code_from_live not in check_alredy_done:
            
            check_alredy_done.append(code_from_live)

            if code_from_live in p_code_from_read_file_df:   #checking code_from_live is present in read_file_df
                # if yes code_from_live present then finding all index of that code_from_live from p_code_from_read_file_df array
                finding_all_index_of_p_code = [index for index,items in enumerate(p_code_from_read_file_df) if items == code_from_live]

                store_all_details = []
                for index_of_p_code in finding_all_index_of_p_code:   #now start checking index by index in read_file_df
                    code_from_read_file = str(read_file_df[index_of_p_code][1])

                    p_code , br_vale = code_from_read_file, str(read_file_df[index_of_p_code][0])    #finding P_CODE and BR_CODE
                    bal_qty = str(int(float(read_file_df[index_of_p_code][3])))
                    
                    all_details = {'P_CODE' : p_code, 'BR_CODE' : br_vale, 'BAL_QTY' : bal_qty}
                    store_all_details.append(all_details)
                    logger.info(all_details)
                    
                    if code_from_read_file in sku_code:    #checking that code present in sku_code or not
                        # if yes code_from_read_file present then finding all index of that code_from_read_file from sku_code array
                        finding_all_index_of_sku_code = [index for index,items in enumerate(sku_code) if items == str(item[0])]

                        for index_of_sku_code in finding_all_index_of_sku_code:
                            if br_code[br_vale] in write_file_df[index_of_sku_code][1] and br_code_location[br_vale] in write_file_df[index_of_sku_code][11]:
                                find_index_detail = "P_CODE : " + p_code + "  is present in SKU CODE file (reading file ...)"
                                logger.info(find_index_detail)
                                
                                if str(write_file_df[index_of_sku_code][15]) == bal_qty and str(write_file_df[index_of_sku_code][16]) ==  bal_qty:
                                    both_equal = "both are equal... write file pdf :  " + str(write_file_df[index_of_sku_code][15]) + " and " + str(write_file_df[index_of_sku_code][16]) + " and read file file : " + bal_qty
                                    logger.info(both_equal)
                                else:
                                    not_equal = "both are not equal... write file pdf " + str(write_file_df[index_of_sku_code][15]) + " and " + str(write_file_df[index_of_sku_code][16])+ " and read file file : " + bal_qty
                                    logger.info(not_equal)

                                    write_file_df[index_of_sku_code][15] = bal_qty
                                    write_file_df[index_of_sku_code][16] = bal_qty

                                    after_changing = "After changing the value of Quantity we get : " + str(write_file_df[index_of_sku_code][15]) + " and " + str(write_file_df[index_of_sku_code][16])
                                    logger.info(after_changing)
                                    
                                    final_all_value_edited.append(write_file_df[index_of_sku_code])

                            else:
                                pass

                #checking which BR_CODE is not present in read file
                # After that storing all values in a new list for further process
                br_code_for_delete = ['RKDS', 'RKTE', 'RKSK','RKP','RKTM','RKKA','RKRP','RKN','RKA','RKW','RKPM']
                p_code_new = ''
                for store in store_all_details:
                    p_code_new = store['P_CODE']
                    if store['BR_CODE'] in br_code_for_delete:
                        br_code_for_delete.remove(store['BR_CODE'])

                if len(br_code_for_delete) > 0:
                    for codes in br_code_for_delete:
                        new_all_details = {'P_CODE' : p_code_new, 'BR_CODE' : codes}
                        final_all_details_for_zero_qnty.append(new_all_details)


    # #doing operations (searching in write file and over writting quantity as 0)                 
    for final_details in final_all_details_for_zero_qnty:
        find_final_details_in_write_file = "Searching : " + final_details.__str__() + " in write file."
        logger.info(find_final_details_in_write_file)
        for row_items in write_file_df:
            if final_details['P_CODE'] == row_items[8] and br_code[final_details['BR_CODE']] in row_items[1] and br_code_location[final_details['BR_CODE']] in row_items[11]:
                find_index_detail = "We find this P_CODE : " + final_details['P_CODE'] + "  is not present in (reading file ...) So we are changing quantity to 0."
                logger.info(find_index_detail)
                row_items[15] = 0
                row_items[16] = 0
                final_all_value_edited.append(row_items)


    
    write_and_save_csv(write_file_df)
    save_file_after_editing(final_all_value_edited)

    return "Process Completed ............. !"

def write_and_save_csv(write_file_df):
    with open(write_csv_file, mode='w', newline='', encoding='UTF-8') as file:
        writer = csv.writer(file)
        header = ['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'SKU', 'HS Code', 'COO', 'Location', 'Incoming', 'Unavailable', 'Committed', 'Available', 'On hand']
        writer.writerow(header)
        writer.writerows(write_file_df)


def save_file_after_editing(final_all_value_edited):
    head1 = ["Handle", "Title", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value", "SKU", "HS Code", "COO", "Location", "Incoming", "Unavailable", "Committed", "Available", "On hand"]
    with open('save_inventory_file.csv', 'w', newline='', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(head1)
        for value in final_all_value_edited:
            writer.writerow(value)


# read_csv_file = '/Users/Desktop/Rohit_project_Automation/web_product_search.csv'  #put always search csv file
# write_csv_file = '/Users/Desktop/Rohit_project_Automation/products_export_write.csv'  #put always write csv file
# live_csv_file = '/Users/Desktop/Rohit_project_Automation/Dark Store SKU.csv'  #put always live csv file

read_csv_file = 'read.csv'
write_csv_file = 'inventory.csv'
live_csv_file = 'Dark Store SKU.csv'
print(read_and_search_csv(read_csv_file, write_csv_file,live_csv_file))

# checking and writing for price