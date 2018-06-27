'''
Created on Nov 17, 2017

@author: prasun
'''

from os import path as path
import re
import pandas as pd

# Number of items in new reduced file. Can be changed to create any sized file.
max_count = 4000
# Number of total items in current input file.
sample = 548552

file_path = path.abspath(path.join(__file__, "../../../../data/")) 
file_in_name = "amazon-meta.txt"
file_out_name = "amazon_reduced_data" + str(max_count) + ".txt"

show_customer_comment_count = False

'''
Reads from input file and skips the first 3 lines as those are not necessary.
Creates a list with all products and returns. 
'''
def read_items_from_file():
    items = []
    file_name = path.abspath(path.join(file_path, file_in_name))

    with open(file_name) as fin:
        for _ in xrange(3):
            next(fin)
        i = 0
        item = ""
        for line in fin:
            if line.strip() == "":
                items.append(item)
                item = ""
                i += 1
            else:
                item += line
            if i > sample:
                break
    fin.close()
    return items


'''
Keeps the id of the items and based on review count, discards or keeps items.
if Review count == 1, len(pairs) = 6, if count >= 2, len >= 8        
'''
def parse_item_info(items):
    rows = []
    discontinued = 0

    pattern = '(Id|downloaded|cutomer):|discontinued'
     
    item_count = 0
    for item in items:
        item_count += 1
        pairs = re.split(pattern, item)[1:]
        
        if len(pairs) > 8:
            o_dict = {}
            for i in range(2):
                key = pairs[i * 2].strip()
                if i == 0:
                    o_dict[key] = int(pairs[i * 2 + 1].strip().split("\r\n")[0])                
                elif i == 1:
                    try:
                        customer_count = int(pairs[i * 2 + 1].strip().split(" ")[0])
                        customers = [pairs[c * 2 + 5].strip().split(" ")[0] for c in range(customer_count)]
                        o_dict['customer'] = customers
                        rows.append(o_dict)
                    except:
                        continue
        else:
            discontinued += 1
 
        # Just for checking how many items we're reading!
        if item_count % 100000 == 0:
            print ("Case count: {}".format(item_count))
 
    return rows


'''
This function prints the number of total users making a specific number of comments.
if 2 users reviewed 5 items and 15 users reviewed one 1 item. It will print
1|15
2|5
and so on
'''
def print_customer_comment_count(df):
    print("----Printing user count--------")
    df1 = df[['Id', 'customer']].groupby(['customer'])['Id'].count().reset_index(name='count').sort_values(['count'], ascending= False)#.head(50)
    
    l = list(pd.Series(df1['count'].values))
    hist_ = {i:l.count(i) for i in set(l)}
    
    for k,v in hist_.iteritems():
        print("{}|{}".format(k, v))


'''
Creates DataFrame with Id, Customer column for each product.
prints the user count for specific number of comments, if checked as True.
Identifies unique customers per product and sort them based on their purchased product count.
Starting items taken from top customer, fill up the reduced dataset's list until it reaches max_count.  
Sort products by their Id for easiness.
'''
def get_products_id_purchased_by_top_buyers(all_item_list): 
    df = pd.DataFrame(all_item_list)
     
    df2 = df.set_index(['Id'])['customer'].apply(pd.Series).stack().reset_index()
    df2.columns = ['Id', 'customer_index', 'customer']
    print("----New DF created--------")

    # This prints how many user made different number of comments.
    if show_customer_comment_count:     
        print_customer_comment_count(df2)
     
    # This is to group by unique items purchased by each user. Same user may have multiple review for an item.
    df2 = df2[['Id', 'customer']].groupby(['customer'])['Id'].unique()
    print("----Uniqueness completed--------")
             
    cust_item = dict()
    for i, row in df2.iteritems():
        cust_item[i] = row.tolist()     
    print("----Convert to list completed--------")
 
    # This is for sorting according to max items purchased by a customer.
    cust_item = sorted(cust_item.items(), key=lambda item: len(item[1]), reverse=True)
    print("----Sorting done--------")
     
    items_id_list = []
    item_count = 0
    for cust_, item_ in cust_item:
        if item_count > max_count:
            break
        for i in item_:
            if i not in items_id_list:
                item_count += 1
                items_id_list.append(i)
                if item_count > max_count:
                    break
    
    # For beautification, just to maintain ID order
    items_id_list.sort()
    
    return items_id_list
          
          
'''
Generates reduced dataset file.
'''      
def write_to_file(info_list, data):          
    file_out = path.abspath(path.join(file_path, file_out_name))
              
    with open(file_out, "w") as fout:
        for i in info_list:
            fout.write("{}\n".format(data[i]))
    fout.close()
    
    
if __name__ == "__main__":    
    raw_items = read_items_from_file()
    print("----File Read completed--------")
     
    parsed_items = parse_item_info(raw_items)
    print("----Parsing completed--------")
     
    items_id_list = get_products_id_purchased_by_top_buyers(parsed_items)
    print("----Item List prepared--------")
     
    write_to_file(items_id_list, raw_items)
    print("----File write completed--------")
    