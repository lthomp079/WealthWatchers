#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <string>

using namespace std;

struct Transaction {
    string date;
    double amount;
    string category;
    string description;
    string paymentMethod;
};

// ---------------- Name Handling ----------------
string getName() {
    string name;
    ifstream in("data/name.txt");
    if (in) {
        getline(in, name);
        in.close();
    } else {
        cout << "Welcome! What is your name?\n";
        getline(cin, name);
        ofstream out("data/name.txt");
        out << name;
        out.close();
    }
    return name;
}

// ---------------- Transaction Handling ----------------
vector<Transaction> transactions;

void loadTransactions() {
    transactions.clear(); // 🔥 THIS LINE FIXES EVERYTHING

    ifstream in("data/Transactions.csv");
    string line;
    while (getline(in, line)) {
        if (line.empty()) continue;

        stringstream ss(line);
        Transaction t;

        getline(ss, t.date, '|');
        ss.ignore(2);
        ss >> t.amount;
        ss.ignore(3);
        getline(ss, t.category, '|');
        getline(ss, t.description, '|');
        getline(ss, t.paymentMethod);

        transactions.push_back(t);
    }
    in.close();
}


void saveAllTransactions() {
    ofstream out("data/Transactions.csv");
    for (auto t : transactions) {
        out << t.date << " | $" << t.amount << " | "
            << t.category << " | " << t.description
            << " | " << t.paymentMethod << "\n";
    }
    out.close();
}

void addTransaction(const string& date, double amount, const string& category, const string& description, const string& paymentMethod) {
    Transaction t = {date, amount, category, description, paymentMethod};
    transactions.push_back(t);
    ofstream out("data/Transactions.csv", ios::app);
    out << t.date << " | $" << t.amount << " | "
        << t.category << " | " << t.description
        << " | " << t.paymentMethod << "\n";
    out.close();
}

void viewTransactions() {
    int idx = 0;
    for (auto t : transactions) {
        cout << idx << " | " << t.date << " | $" << t.amount << " | "
             << t.category << " | " << t.description
             << " | " << t.paymentMethod << "\n";
        idx++;
    }
}

void deleteLastTransaction() {
    if (!transactions.empty()) {
        transactions.pop_back();
        saveAllTransactions();
        cout << "Last transaction deleted.\n";
    } else {
        cout << "No transactions to delete.\n";
    }
}

void deleteTransactionById(int id) {
    if (id >= 0 && id < transactions.size()) {
        transactions.erase(transactions.begin() + id);
        saveAllTransactions();
        cout << "Transaction deleted.\n";
    } else {
        cout << "Invalid transaction ID.\n";
    }
}

void updateTransactionById(int id, const string& field, const string& value) {
    if (id < 0 || id >= transactions.size()) {
        cout << "Invalid transaction ID.\n";
        return;
    }
    Transaction& t = transactions[id];
    if (field == "date") t.date = value;
    else if (field == "amount") t.amount = stod(value);
    else if (field == "category") t.category = value;
    else if (field == "description") t.description = value;
    else if (field == "payment_method") t.paymentMethod = value;
    else { cout << "Invalid field.\n"; return; }
    saveAllTransactions();
    cout << "Transaction updated.\n";
}

// ---------------- Main ----------------
int main(int argc, char* argv[]) {
    string name = getName();
    loadTransactions();

    if (argc > 1) {
        string command = argv[1];
        if (command == "add") {
            string date = argv[2];
            double amount = stod(argv[3]);
            string category = argv[4];
            string description = argv[5];
            string paymentMethod = argv[6];
            addTransaction(date, amount, category, description, paymentMethod);
            cout << "Transaction added.\n";
        } else if (command == "view") {
            viewTransactions();
        } else if (command == "delete_last") {
            deleteLastTransaction();
        } else if (command == "delete_transaction") {
            int id = stoi(argv[2]);
            deleteTransactionById(id);
        } else if (command == "edit_transaction") {
            int id = stoi(argv[2]);
            string field = argv[3];
            string value = argv[4];
            updateTransactionById(id, field, value);
        } else {
            cout << "Invalid command.\n";
        }
        return 0;
    }

    // Interactive mode (unchanged)
    while (true) {
        cout << "\n--- Personal Finance Tracker ---\n";
        cout << "1. Add transaction\n";
        cout << "2. View transactions\n";
        cout << "3. Delete last transaction\n";
        cout << "4. Exit\n";
        cout << "Choice: ";
        int choice;
        cin >> choice;
        cin.ignore();
        if (choice == 1) {
            string date, category, description, paymentMethod;
            double amount;
            cout << "Date (YYYY-MM-DD): "; getline(cin, date);
            cout << "Amount: "; cin >> amount; cin.ignore();
            cout << "Category: "; getline(cin, category);
            cout << "Description: "; getline(cin, description);
            cout << "Payment Method: "; getline(cin, paymentMethod);
            addTransaction(date, amount, category, description, paymentMethod);
            cout << "Transaction added.\n";
        } else if (choice == 2) {
            viewTransactions();
        } else if (choice == 3) {
            deleteLastTransaction();
        } else if (choice == 4) {
            break;
        } else {
            cout << "Invalid choice.\n";
        }
    }
    return 0;
}
