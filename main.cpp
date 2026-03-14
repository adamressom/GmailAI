#include <iostream>
#include <string>
using namespace std;

int main() {
    string subject;

    cout << "What subject are you struggling with? ";
    getline(cin, subject);

    cout << "Thanks. I will help you study " << subject << "." << endl;

    return 0;
}