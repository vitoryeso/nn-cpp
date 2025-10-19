g++ -o main_value main_value.cpp value.cpp

./main_value > graph.dot

python3 plot.py
