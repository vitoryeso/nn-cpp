g++ -o bin/main_value main_value.cpp value.cpp

./bin/main_value > graph.dot

python3 plot.py
