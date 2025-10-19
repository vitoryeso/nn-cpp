#include <iostream>
#include <vector>
#include <sstream>
#include <functional>
#include <unordered_set>
#include <cstdint>
#include <cmath>

using namespace std;

class Value {
  private:
    int data;
    vector<Value> children;
    string op;
    
  public:
    int grad;
    string label;

    Value(void) {
      this->data = 0;
      this->grad = 0;
      this->label = "";
    }
    // Construtor por cópia
    Value(const Value& V) {
      this->data = V.data;
      this->grad = V.grad;
      this->children = V.children;
      this->op = V.op;
      this->label = V.label;
      // label não passa pois caso o objeto ja tenha label, a label deve permanecer.
    }

    Value(int a, vector<Value> children={}, std::string op="", int grad=0) {
      this->data = a;
      this->children = children;
      this->op = op;
      this->grad = grad;
    }
    Value(int a, std::string label, int grad=0) {
      this->data = a;
      this->children = vector<Value>();
      this->label = label;
      this->grad = grad;
    }
    Value operator+(Value& V) {
      return Value(this->data + V.data, vector<Value>({*this, V}), "+");
    }
    Value operator*(Value& V) {
      return Value(this->data * V.data, vector<Value>({*this, V}), "*");
    }
    Value operator-(Value& V) {
      return Value(this->data - V.data, vector<Value>({*this, V}), "-");
    }
    Value operator/(Value& V) {
      return Value(this->data / V.data, vector<Value>({*this, V}), "/");
    }

    operator int() const { return this->data; }
    operator double() const { return (double) this->data; }
    Value exp(int n_iterations=5) {
      double sum = 1.0;
      double term = 1.0;
      for (int i = 1; i <= n_iterations; ++i) {
        term *= (double)this->data / i;
        sum += term;
      }
      Value result((int)(sum));
      return result;
    }
    Value tanh(void) {
      Value x(0);
      Value c1(2, "c1");
      Value c2(1, "c2");
      Value o(0, "o");
      Value h1(0, "h1");
      Value h2(0, "h2");

      x = this->data;
      h1 = c1 * x;
      h1 = h1.exp();
      h1 = h1 - c2;
      h2 = c1 * x;
      h2 = h2.exp();
      h2 = h2 + c2;
      o = h1/h2;
      Value t(ceil(o.data), {*this}, "tanh");
      return t;
    }
    // Custom assignment operator to preserve the label
    Value& operator=(const Value& other) {
        // Check for self-assignment
        if (this != &other) {
            this->data = other.data;
            this->children = other.children;
            this->op = other.op;
            // Notice: The label of the current object (this) is NOT overwritten.
        }
        return *this;
    }
    vector<Value> getChildren(void) {
	    return this->children;
    }
        // NOTE: The graphviz function has been refactored to show operation nodes separately.
    friend string graphviz(const Value& root) {
        stringstream ss;
        ss << "digraph G {\n";
        ss << "  rankdir=LR;\n";
        ss << "  node [shape=record, fontname=\"Consolas\", fontsize=10, "
           << "style=filled, fillcolor=\"#f9f9f9\", color=\"#555555\"];\n";
        ss << "  edge [color=\"#666666\"];\n\n";

        unordered_set<const Value*> visited;

        function<void(const Value&)> build = [&](const Value& v) {
            if (visited.count(&v)) return;
            visited.insert(&v);

            string uid = "n" + to_string(reinterpret_cast<uintptr_t>(&v));

            // Create the node for the Value object (box with label and data)
            ss << "  " << uid << " [label=\"{ "
               << (v.label.empty() ? "(unnamed)" : v.label)
               << " | data: " << v.data
               << " | grad: " << v.grad
               << " }\"];\n";
            
            // If this Value was created by an operation, create the op node
            if (!v.op.empty()) {
                // Create a circular node for the operation
                string op_id = uid + "_op";
                ss << "  " << op_id
                   << " [label=\"" << v.op
                   << "\", shape=circle, style=filled, fillcolor=\"#eeeeee\", color=\"#444444\"];\n";
                
                // Connect the operation node to the result Value node (1 output)
                ss << "  " << op_id << " -> " << uid << ";\n";
                
                // Connect the children to the operation node (2 inputs)
                for (const auto& child : v.children) {
                    string child_id = "n" + to_string(reinterpret_cast<uintptr_t>(&child));
                    ss << "  " << child_id << " -> " << op_id << ";\n";
                    build(child); // Recursively build the graph for children
                }
            }
        };

        build(root);
        ss << "}\n";
        return ss.str();
    }
    /*
    friend Value backpropagation(Value V) {
      V.grad = 1;

      //vector<Value> layer_1 = V.getChildren();
      //layer_1[0].grad = V.data - layer_1[0].data;
      //layer_1[1].grad = V.data - layer_1[1].data;

      vector<Value> current_layer;
      current_layer = V.getChildren();
      while (current_layer.size() > 1) {
        for (int i=0;i<current_layer.size(); i++) {
          current_layer[i].grad = V.data - current_layer[i].data;
        }  
        current_layer = current_layer[0].getChildren()
      }






      return Value(0);
    }
    */
};


