#include <iostream>
#include "value.cpp"

using namespace std;

int main() {
  
  Value a(2, "a");
  Value b(-3, "b");
  Value c(10, "c");


  Value e(0, "e"), d(0, "d");
  e = a*b;// e.label = "e";
  d = e + c;// d.label = "d"; 
  Value f(-2, "f");
  Value L(0, "L");
  L = d * f;
  list.append(pair<Value> L.getChildren())
  //
  //dfdL = L.children[0].grad = L - children[0].data
  //dddL = L.children[1].grad = L - children[1].data

  cout << graphviz(L) << endl;
}
