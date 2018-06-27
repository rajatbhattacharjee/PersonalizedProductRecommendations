AmazonReview contains the entire project with source codes.

Folder structure is 
AmazonReview/data/
AmazonReview/src/com/analysis/
AmazonReview/src/com/preprocess/


----
"data" stores all the outputs (graph pdf, reduced dataset).
Input file should also be stored in this folder.


----
"analysis" has 2 python files. 
1. ARClass.py
2. ReviewNetwork.py

ARClass defines the structure of each product and stores informations from amazon data.

ReviewNetwork does all the calculation and computations.
- generates the graph and saves in pdf (if item count < 200)
- uses page rank to sort items based on helpfulness and categories
- gives 5 recommendations for any random item. 


----
"preprocess" has only 1 python file.
1. ReduceDataset.py

As name suggests, it reduces the dataset. 


----
Running the project:

1. If running with original dataset (amazon-meta.txt), then it must be reduced using ReduceDataset.py.
2. You can define your reduced filename in there. However, for now it generates "amazon_reduced_data_100.txt" for 100 items. Item count can be set in this file in "max_count" variable.
3. This expects the input file to be in "data" folder and will save the output file in same "data" folder.

Note: We've added 2 reduced dataset of size 100 and 4000.

4. To just see the recommendation, run "ReviewNetwork.py".
5. It expects an input filename as "amazon_reduced_data_100.txt". However, 100 can be changed by changing value of "input_size" variable in the file.
6. Number of recommendations per product can also be set from the file by "number_of_recommendation" variable.
7. If "input_size" is less then 200 items, it will show the generated graph (nodes and edges) and save it in "data" folder as pdf format.
8. Output will be shown in terminal, but will not be saved in file.