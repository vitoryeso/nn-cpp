#include <iostream>
#include "value.cpp"

using namespace std;

int main() {
  
  Value x1(2, "x1");
  Value x2(0, "x2");

  Value w1(-3, "w1");
  Value w2(1, "w2");

  Value b(8, "b");

  Value h1(0, "h1");
  Value h2(0, "h2");
  h1 = x1*w1;
  h2 = x2*w2;

  Value n(0, "n");
  n = h1 + h2 + b;

  Value o(0, "o");
  o = n.tanh();

  cout << graphviz(o) << endl;
}
