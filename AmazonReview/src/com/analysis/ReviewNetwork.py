'''
Created on Nov 23, 2017

@author: prasun
'''

from os import path as path
import networkx as nx
import re, random
from ARClass import Item_Info
import matplotlib.pyplot as plt
from collections import Counter
import time

helpfulness_thres = 0.5
edge_weight_in_similar_category_thres = 0.7
edge_weight_in_similar_group_thres = 0.8
edge_weight_in_other_category_thres = 0.9999

number_of_recommendation = 5

# Select from 100, 4000, 50000
input_size = 4000
file_path = path.abspath(path.join(__file__, "../../../../data/")) 
file_in_name = "amazon_reduced_data" + str(input_size) + ".txt"

# Keeps the item graph and Item (class) informations in a dictionary.
item_graph = nx.DiGraph()
item_info_dict = dict()


'''
Parse information from file and generate Item_Info object.
And, create a node in graph after each Item is read.
We won't add an item if it's review_score is 0. Either people doesn't found the reviews helpful or the rating is low.
'''
def generate_graph_from_file():
    
    items = []
    file_name = path.abspath(path.join(file_path, file_in_name))

    with open(file_name) as fin:
        item = ""
        for line in fin:
            if line.strip() == "":
                items.append(item)
                item = ""
            else:
                item += line
    fin.close()
    
    pattern = '(Id|ASIN|title|group|salesrank|similar|categories|reviews):'
              
    for item in items:
        item_info = Item_Info()
        pairs = re.split(pattern, item)[1:]
        for i in range(8):
            if i == 6 or i == 7:
                parsed_info = pairs[i * 2 + 1].strip()
                if i == 6:
                    item_info.categories = get_product_category(item_info.group, parsed_info)
                else:
                    item_info.review_score = get_product_rating(parsed_info)
            else:
                parsed_info = pairs[i * 2 + 1].strip().split("\r\n")[0]
            
                if i == 0: 
                    item_info.id = int(parsed_info)
                elif i == 1:
                    item_info.asin = parsed_info
                elif i == 2:
                    item_info.title = parsed_info
                elif i == 3:
                    item_info.group = parsed_info
                elif i == 4:
                    item_info.salesrank = int(parsed_info)     
                elif i == 5:
                    similar = parsed_info.split("  ")[1:]
                    item_info.similar = similar
            
        if item_info.review_score != 0.0:
            item_graph.add_node(item_info.id, weight=item_info.review_score)
            item_info_dict[item_info.id] = item_info
            

'''
Method to get the category of an item.
Splitting the category string to get the 1st number. This is count for how many categories an item belongs to.
For Music and Book, 4th element is the generic category. But, for Video/ DVD, "genre" is there. So, take 5th element.
If an item belongs to multiple categories, take take the most common one.
List all of these categories and then use Collections to find most_common(), it gives a the list we take 1st item.
This is list and we take 0 index which is the category.
'''
def get_product_category(item_group, category_str):
    cat_count, category_str = category_str.split("\r\n", 1)
    category_each_line_list = category_str.split("\r\n")
    category = list()
    for i in range(int(cat_count)):
        if (item_group == "Video") or (item_group == "DVD"):
            try:
                category.append(category_each_line_list[i].strip().split("|")[4])
            except:
                pass
        else:
            try:
                category.append(category_each_line_list[i].strip().split("|")[3])
            except:
                pass
    top_category = Counter(category).most_common()[0]
    return top_category[0]


'''
Method for calculating the edge weight based on review and its helpfulness.
We don't need the first rating! That is the default average. So, loop starts from the 2nd line.
Return will scale the rating dividing by 5, so that it always stays in 0~1 range.
If, total_helpfulness is 0, it returns 0 by default regardless whatever the rating is.
'''
def get_product_rating(review_str):
    review_info = review_str.split("\r\n")
    pattern = '(rating|votes|helpful):'
    total_rating_helpfulness_mult = 0.0
    total_helpfulness = 0.0
    for i in range(1, len(review_info)):
        parsed_review_info = re.split(pattern, review_info[i].strip())[1:]
        try:
            helpfulness = float(parsed_review_info[5].strip()) / float(parsed_review_info[3].strip())
            if helpfulness >= helpfulness_thres:
                total_helpfulness += helpfulness
                total_rating_helpfulness_mult += helpfulness * float(parsed_review_info[1].strip())
        except ZeroDivisionError:
            pass

    try:
        return total_rating_helpfulness_mult / total_helpfulness / 5
    except ZeroDivisionError:
        return 0.0
    
    
'''
Takes current item, graph and number of items to recommend from graph as parameter.
Use Pagerank to rank all items and tries to fill up 5 recommendations from similar category.
If it's not enough, fills up with items from all category top list.
Returns list of items id.
'''    
def get_top_recommendation(current_item, pr_dict):
    
    nei = list(item_graph.neighbors(current_item))
 
    i = 0
    recommendation = list()
    recommendation_categorywise_dict = {'similar_category':[], 'similar_group':[], 'top':[k[0] for k in iter(pr_dict)]}
    
    for item in iter(pr_dict):
        if item[0] in nei:
            if item_info_dict[item[0]].categories == item_info_dict[current_item].categories:
                i += 1
                recommendation_categorywise_dict['similar_category'].append(item[0])
            elif item_info_dict[item[0]].group == item_info_dict[current_item].group:
                recommendation_categorywise_dict['similar_group'].append(item[0])
            if i >= number_of_recommendation:
                break
            
    if i != 0:
        recommendation = [recommendation_categorywise_dict['similar_category'][i] for i in range(min(len(recommendation_categorywise_dict['similar_category']), number_of_recommendation))]
            
    if len(recommendation) < number_of_recommendation:
        recommendation.extend(recommendation_categorywise_dict['similar_group'][0:number_of_recommendation - len(recommendation)])
            
    if len(recommendation) < number_of_recommendation:
        recommendation.extend(recommendation_categorywise_dict['top'][0:number_of_recommendation - len(recommendation)])
        
    # Takes the top 5 or all items, whichever is smaller.
    for k, v in recommendation_categorywise_dict.items():
        recommendation_categorywise_dict[k] = v[0:min(len(v), number_of_recommendation)]
        
    return recommendation, recommendation_categorywise_dict
    
    
'''
This prints the recommended items (ASIN) for current item.
Printing order:
1. Top items from same category (Like Jazz in Music or Literature & Fiction in Books)
2. Top items from same group (Book, Music, DVD, Video)
3. Regardless of category, top items.
4. Selects top items in following order to make a list of 5 or so items:
a. Same category is first priority.
b. Consider Same group items, if list not filled
c. Take from Generic to fill up the rest items.

This also prints Amazon suggested similar, which is from data set as it was. 
'''
def print_recommended_items(current_item_id, recommended_items, recommendation_categorywise_dict):    
    recommneded_items_asin = [item_info_dict[item_id].asin for item_id in recommended_items]
    print("Top {} Recommended Items for current item ASIN: {}:".format(number_of_recommendation, item_info_dict[current_item_id].asin))
    print("From same {0: <8} \"{1: <35}\" are: {2:}".format("Category", item_info_dict[current_item_id].categories, [item_info_dict[item_id].asin for item_id in recommendation_categorywise_dict['similar_category']]))
    print("From same {0: <8} \"{1: <35}\" are: {2:}".format("Group", item_info_dict[current_item_id].group, [item_info_dict[item_id].asin for item_id in recommendation_categorywise_dict['similar_group']]))
    print("From all categories are {0: <36}: {1:}".format("", [item_info_dict[item_id].asin for item_id in recommendation_categorywise_dict['top']]))        
    print("Combined top {1:} recommendations (category > group > other) {0:<2}: {2:}".format("",number_of_recommendation, recommneded_items_asin))
    print("Amazon suggested similar {0:<35}: {1:}".format("",item_info_dict[current_item_id].similar))
    matched_item = set(recommneded_items_asin) & set(item_info_dict[current_item_id].similar)
    if len(matched_item) > 0:
        print("Items matched with our recommendation with Amazon: {}\n".format(matched_item)) 
    print("")   
    return

        
'''
Saves the graph in pdf format. 
Marks current node in Red, Recommended items in Black and all other items as Green color.
Though, our graph is directed, but for plotting the graph, we make it as undirected.
Will not print if item count > 200, takes too much time!
'''
def save_graph(current_item, recommended_items):
    color_map = {i:'black' for i in recommended_items}
    color_map[current_item] = 'r'
    node_color = [color_map.get(node, 'g') for node in item_graph.nodes()]    
    
    # Graph plotting
    f_out_name = path.abspath(path.join(file_path, "output_" + str(item_graph.number_of_nodes()) + "_" + str(item_graph.number_of_edges()) + ".pdf"))  
    pos = nx.spring_layout(item_graph)
    plt.figure(figsize=(11, 11))
    nx.draw_networkx_nodes(item_graph, pos, node_color=node_color, node_size=250)
    nx.draw_networkx_edges(item_graph.to_undirected(), pos, item_graph.edges(), edge_color='b', width=0.2)
    plt.axis('off')
    plt.savefig(f_out_name)
    plt.show()
    return


'''
Creates graph first and creates edges based on following rule:
Edge weight is based on priority. If items are of same category, has full weight. 
If items are of same group (Both are books), weight/ 2. Otherwise, weight/ 3 

Calculates PageRank and sort by top ranked item first.
Gives recommendation for 5 random items.
Prints time takes to perform each tasks as well.
'''
if __name__ == '__main__':
    
    start_time = task_start_time = time.clock()
    generate_graph_from_file()
    task_end_time = time.clock()
    print("Graph generation time: {}".format(task_end_time - task_start_time))
    l = [node[0] for node in item_graph.nodes().items()]

    # Edge creation  
    task_start_time = time.clock()  
    for i in l:
        for j in l:
            if i != j:
                if item_info_dict[i].categories == item_info_dict[j].categories and item_graph.nodes[j]['weight'] > edge_weight_in_similar_category_thres:
                    item_graph.add_edge(i, j, weight=item_graph.nodes[j]['weight'])
                if item_info_dict[i].group == item_info_dict[j].group and item_graph.nodes[j]['weight'] > edge_weight_in_similar_group_thres:
                    item_graph.add_edge(i, j, weight=item_graph.nodes[j]['weight'] / 2.0)
                else:
                    if item_graph.nodes[j]['weight'] > edge_weight_in_other_category_thres:
                        item_graph.add_edge(i, j, weight=(item_graph.nodes[j]['weight'] / 3.0))
    task_end_time = time.clock()   
    print("Edge creation time: {}".format(task_end_time - task_start_time))
    print("Items Count: {}, Total number of connections: {}\n".format(item_graph.number_of_nodes(), item_graph.number_of_edges()))
              
    # PageRank
    task_start_time = time.clock()   
    pagerank_dict = nx.pagerank(item_graph)
    task_end_time = time.clock()   
    print("PageRank calculation time: {}".format(task_end_time - task_start_time))    
    pagerank_dict = sorted(pagerank_dict.items(), key=lambda(k, v): v, reverse=True)     
          
    # For example, 5 random items and their recommendation.
    for i in range(5):
        # This is our current node. Find recommendation for it.
        current_item_id = random.choice(l)
        task_start_time = time.clock()   
        recommended_items, recommendation_categorywise_dict = get_top_recommendation(current_item_id, pagerank_dict)
        task_end_time = time.clock()   
        print("Get recommendation time: {}".format(task_end_time - task_start_time))    

        print_recommended_items(current_item_id, recommended_items, recommendation_categorywise_dict)
    
    end_time = time.clock()
    print("Total time elapsed: {}".format(end_time - start_time))    
          
    if input_size < 200:
        save_graph(current_item_id, recommended_items)