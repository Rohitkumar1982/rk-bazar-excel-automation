import pandas as pd,csv
import numpy as np
from logging_util import logger


def read_and_search_csv(read_csv_file, write_csv_file):
    # creating key value pair for BR_CODE and title (for matching purpose)
    br_code = {'RKBS' : '|| S2', 'RKM' : '|| S1', 'RKDA' : '|| S3'}

    sku_code = []    #storing all Variant SKU of write_csv_file

    # reading read_csv_file and after converting into array
    read_file_df = pd.read_csv(read_csv_file)
    read_file_df = read_file_df.values.tolist()

    # reading write_csv_file and after converting into array
    write_file_df = pd.read_csv(write_csv_file)
    write_file_df = write_file_df.replace(np.nan,"")   #removing all spaces with a empty string value
    write_file_df = write_file_df.values.tolist()

    # iterating write_file_df and appending all Variant SKU in sku_code array
    for product in write_file_df:
        sku_code.append(str(product[14]).replace("'",''))

    # iterating read_file_df to searching all stuffs
    for item in read_file_df:
        p_code , br_vale = str(item[1]), str(item[0])    #finding P_CODE and BR_CODE
        mrp , net_sale_rate = str(item[4]), str(item[5])  

        logger.info("Start Working ................... ")

        if p_code in sku_code:
            finding_all_index = [index for index,item in enumerate(sku_code) if item == p_code]  #finding all index of P_CODE in Variant SKU
            for final_index in finding_all_index:
                if br_code[br_vale] in write_file_df[final_index][1]:   #now finding specific P_CODE with BR_CODE
                    all_details = {'P_CODE' : p_code, 'BR_CODE' : br_vale, 'MRP' : mrp , 'NET_SALE_RATE' : net_sale_rate  }
                    logger.info(all_details)
                    find_index_detail = "Find exact serial number for this P_CODE : " + p_code + "  where we have to change the value i.e "+ str(final_index+2) + " Index number"
                    logger.info(find_index_detail)
                    if (write_file_df[final_index][19] == '') or (write_file_df[final_index][20] == ''):
                        write_and_save_csv(final_index,mrp,net_sale_rate)

                    elif int(float(write_file_df[final_index][19]))!= int(float(net_sale_rate)) or int(float(write_file_df[final_index][20]))!= int(float(mrp)):
                        write_and_save_csv(final_index,mrp,net_sale_rate) 
                    
                    else:
                        logger.info("Both price are matched.")
                else:
                    find_index_detail = "No BR_CODE Found in Title for this P_CODE : "+ str(p_code)
                    logger.info(find_index_detail)
                    pass    
    

#writing and save cav file (changing Variant Price and Variant Compare At Price)
def write_and_save_csv(final_index,mrp,net_sale_rate):
    with open(write_csv_file, mode='r') as file:
        write_file = csv.reader(file)
        data = list(write_file)

    logger.info("Start checking value for changing purpose....")

    # checking Variant Price and NET_SALE_RATE 
    # if both are same just pass else changing the value of Variant Price
    if (data[final_index+1][19] == ''):
        data[final_index+1][19] = 0

    if int((float(data[final_index+1][19])) == int(float(net_sale_rate))):
        pass
    else:
        row_index = final_index+1
        col_index = 19
        new_value = net_sale_rate
        changing_value = "Variant Price and NET_SALE_RATE are not matching for serial number " + str(row_index) + " So, we are changing the value according to read_file_df"
        exact_value = "Earlier NET_SALE_RATE is :" + str(data[final_index+1][19]) + " After changing this value we get : " + str(float(net_sale_rate))
        logger.info(changing_value)
        logger.info(exact_value)
        data[row_index][col_index] = new_value
        with open(write_csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    # checking Variant Compare At Price and MRP 
    # if both are same just pass else changing the value of Variant Compare At Price
    if (data[final_index+1][20] == ''):
        data[final_index+1][20] = 0

    if int((float(data[final_index+1][20])) == int(float(mrp))):
        pass
    else:
        row_index = final_index+1
        col_index = 20
        new_value = mrp
        changing_value = "Variant Compare At Price and MRP are not matching for serial number " + str(row_index) + " So, we are changing the value according to read_file_df"
        exact_value = "Earlier Variant Compare At Price is :" + str(data[final_index+1][20]) + " After changing this value we get : " + str(float(mrp))
        logger.info(changing_value)
        logger.info(exact_value)
        data[row_index][col_index] = new_value
        with open(write_csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)



read_csv_file = '/Users/deepak.kumar/Desktop/Rohit_project_Automation/web_product_search.csv'  #put always search csv file
write_csv_file = '/Users/deepak.kumar/Desktop/Rohit_project_Automation/products_export_write.csv'  #put always write csv file
print(read_and_search_csv(read_csv_file, write_csv_file))