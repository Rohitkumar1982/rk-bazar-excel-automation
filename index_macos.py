import pandas as pd,csv
import numpy as np
from logging_util import logger
import chardet


def read_and_search_csv(read_csv_file, write_csv_file,live_csv_file):
    # creating key value pair for BR_CODE and title (for matching purpose)
    br_code = {'RKBB' : '|| S2', 'RKTE' : '|| S1', 'RKDA' : '|| S3', 'RKP':'|| S4'}

    sku_code = []    #storing all Variant SKU of write_csv_file

    p_code_from_live_file = []    ##storing all P_CODE of live_csv_file

    p_code_from_read_file_df = []    ##storing all P_CODE of read_file_df

    # reading live_csv_file and after converting into array
    live_file_df = pd.read_csv(live_csv_file, encoding='utf-8')
    live_file_df = live_file_df.values.tolist()

    # reading read_csv_file and after converting into array
    try:
        read_file_df = pd.read_csv(read_csv_file, encoding='latin1')
    except:
        read_file_df = pd.read_csv(read_csv_file, encoding='ISO-8859-1')
    read_file_df = read_file_df.values.tolist()

    # reading write_csv_file and after converting into array
    # try:
    #      write_file_df_1 = pd.read_csv(write_csv_file, encoding='latin1')
    # except:
    #      write_file_df_1 = pd.read_csv(write_csv_file, encoding='ISO-8859-1')   
    with open(write_csv_file, 'rb') as f:
        result = chardet.detect(f.read())

    encoding = result['encoding']
    try:
        write_file_df_1 = pd.read_csv(write_csv_file, encoding=encoding, on_bad_lines='skip')
    except UnicodeDecodeError:
        # If there's an encoding issue, try 'latin1'
        write_file_df_1 = pd.read_csv(write_csv_file, encoding='latin1', on_bad_lines='skip')
    write_file_df = write_file_df_1.replace(np.nan,"")   #removing all spaces with a empty string value
    write_file_df = write_file_df.values.tolist()

    header_row = write_file_df_1.columns.tolist()
    check_status_index = False
    if str(header_row.index('Status')) == "54":
        check_status_index = True

    # iterating live_file_df and appending all P_CODE in p_code_from_live_file array
    for live_product in live_file_df:
        p_code_from_live_file.append(str(live_product[0]).replace("'",''))

    # iterating write_file_df and appending all Variant SKU in sku_code array
    for write_product in write_file_df:
        sku_code.append(str(write_product[17]).replace("'",''))

    # iterating read_file_df and appending all Variant SKU in p_code_from_read_file_df array
    for read_product in read_file_df:
        p_code_from_read_file_df.append(str(read_product[1]).replace("'",''))

    check_alredy_done = []
    seriel_num_edited = []
    final_all_value_edited = []

    i = 0
    for item in live_file_df:
        
        start_details = "Start Working ................... " + str(item[0]) 
        logger.info(start_details)

        code_from_live = str(item[0])     #P_CODE from live_file_pdf
        
        if code_from_live not in check_alredy_done:
            
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
                                        del write_file_df[index_of_sku_code][-4]
                                        del write_file_df[index_of_sku_code][-5]
                                        del write_file_df[index_of_sku_code][-6]
                                        del write_file_df[index_of_sku_code][-7]
                                        del write_file_df[index_of_sku_code][10]
                                        del write_file_df[index_of_sku_code][13]
                                        del write_file_df[index_of_sku_code][16]
                                        write_file_df[index_of_sku_code].insert(17, '')
                                        write_file_df[index_of_sku_code].insert(36, '')
                                        write_file_df[index_of_sku_code].insert(37, '')
                                        final_all_value_edited.append(write_file_df[index_of_sku_code])
                                        value_you_editied = write_and_save_csv(index_of_sku_code,mrp,net_sale_rate)
                                        # final_all_value_edited.append({p_code : br_vale})
                                        if value_you_editied not in seriel_num_edited:
                                            seriel_num_edited.append(value_you_editied)
                                    
                                    elif str(int(float(write_file_df[index_of_sku_code][22]))) not in  str(net_sale_rate) or str(int(float(write_file_df[index_of_sku_code][23]))) not in  str(mrp):
                                        find_index_detail = "Find exact serial number for this P_CODE : " + p_code + "  where we have to change the value i.e "+ str(index_of_sku_code+1) + " Index number"
                                        logger.info(find_index_detail)
                                        write_file_df[index_of_sku_code][22] = net_sale_rate
                                        write_file_df[index_of_sku_code][23] = mrp
                                        del write_file_df[index_of_sku_code][-4]
                                        del write_file_df[index_of_sku_code][-5]
                                        del write_file_df[index_of_sku_code][-6]
                                        del write_file_df[index_of_sku_code][-7]
                                        del write_file_df[index_of_sku_code][10]
                                        del write_file_df[index_of_sku_code][13]
                                        del write_file_df[index_of_sku_code][16]
                                        write_file_df[index_of_sku_code].insert(17, '')
                                        write_file_df[index_of_sku_code].insert(36, '')
                                        write_file_df[index_of_sku_code].insert(37, '')
                                        final_all_value_edited.append(write_file_df[index_of_sku_code])
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
    save_file_after_editing(final_all_value_edited,check_status_index)
    logger.info(edited_value)  
    logger.info(final_all_value_edited)    

    return seriel_num_edited

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
        exact_value = "Earlier NET_SALE_RATE is : " + str(data[final_index+1][19]) + " After changing this value we get : " + str(float(net_sale_rate))
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
        exact_value = "Earlier Variant Compare At Price is : " + str(data[final_index+1][20]) + " After changing this value we get : " + str(float(mrp))
        logger.info(changing_value)
        logger.info(exact_value)
        data[row_index][col_index] = new_value
        with open(write_csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    return str(final_index+2)


def save_file_after_editing(final_all_value_edited,check_status_index):
    head1 = ["Handle", "Title", "Body (HTML)",	"Vendor" ,"Product Category", "Type", "Tags", "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Gift Card", "SEO Title", "SEO Description", "Google Shopping / Google Product Category", "Google Shopping / Gender", "Google Shopping / Age Group", "Google Shopping / MPN", "Google Shopping / Condition", "Google Shopping / Custom Product",  "Google Shopping / AdWords Grouping", "Google Shopping / AdWords Labels", "Google Shopping / Custom Label 0", "Google Shopping / Custom Label 1", "Google Shopping / Custom Label 2", "Google Shopping / Custom Label 3", "Google Shopping / Custom Label 4", "Variant Image", "Variant Weight Unit", "Variant Tax Code", "Cost per item", "Price / International", "Compare At Price / International", "Status"]
    # "Google Shopping / AdWords Grouping", "Google Shopping / AdWords Labels",
    with open('save_final_file.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(head1)
        if check_status_index == True:
            for value in final_all_value_edited:
                del value[-2]
                del value[-3]
                writer.writerow(value)
        else:
            for value in final_all_value_edited:
                writer.writerow(value)


# read_csv_file = '/Users/Desktop/Rohit_project_Automation/web_product_search.csv'  #put always search csv file
# write_csv_file = '/Users/Desktop/Rohit_project_Automation/products_export_write.csv'  #put always write csv file
# live_csv_file = '/Users/deepak.kumar/Desktop/Rohit_project_Automation/Dark Store SKU.csv'  #put always live csv file

read_csv_file = 'read.csv'
write_csv_file = 'write.csv'
live_csv_file = 'Dark Store SKU.csv'
print(read_and_search_csv(read_csv_file, write_csv_file,live_csv_file))

 