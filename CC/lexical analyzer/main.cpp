// Used for input and output (I/O) operations.
#include <iostream>
#include <fstream>  // For file I/O
#include <string>
#include <vector>
#include <cctype>
#include <map>
#include <regex>

using namespace std;

// User-defined type, consists of a set of named integral constants
enum TokenType {
    DT, ID, IF, ELSE, WHILE, BREAK,
    SEMICOLON, COMMA, DOT, L_BRACE, R_BRACE,
    L_PAREN, R_PAREN, L_BRACKET, R_BRACKET,
    INC_DEC, PM, MDM, ROP, LOGICAL_AND, LOGICAL_OR, ASSIGN,
    CLASS, ABSTRACT, CONSTRUCTOR, IMPORT, RETURN, THIS, NEW, AM, EXPAND,
    FLOAT_CONST, INT_CONST, CHAR_CONST, STRING_CONST, UNKNOWN
};

// Converts TokenType to corresponding string representation
string tokenTypeToString(TokenType type) {
    switch (type) {
        case DT: return "DT";
        case ID: return "ID";
        case IF: return "if";
        case ELSE: return "else";
        case WHILE: return "while";
        case BREAK: return "break";
        case SEMICOLON: return ";";
        case COMMA: return ",";
        case DOT: return ".";
        case L_BRACE: return "{";
        case R_BRACE: return "}";
        case L_PAREN: return "(";
        case R_PAREN: return ")";
        case L_BRACKET: return "[";
        case R_BRACKET: return "]";
        case INC_DEC: return "inc_dec";
        case PM: return "PM";
        case MDM: return "MDM";
        case ROP: return "ROP";
        case LOGICAL_AND: return "&&";
        case LOGICAL_OR: return "||";
        case ASSIGN: return "=";
        case CLASS: return "class";
        case ABSTRACT: return "abs";
        case CONSTRUCTOR: return "const";
        case IMPORT: return "im";
        case RETURN: return "return";
        case THIS: return "this";
        case NEW: return "new";
        case AM: return "AM";
        case EXPAND: return "expand";
        case FLOAT_CONST: return "float_const";
        case INT_CONST: return "int_const";
        case CHAR_CONST: return "char_const";
        case STRING_CONST: return "string_const";
        default: return "Unknown";
    }
}

// Represents a token with its type, value, and the line number where it appears
class Token {
public:
    string classPart;  // Will hold the TokenType as a string
    string valuePart;  // Will hold the token value
    int lineNo;  // Line number

    // Constructor to initialize Token object
    Token(string cp, string vp, int ln) : classPart(cp), valuePart(vp), lineNo(ln) {}
};

// Maps keywords to their corresponding TokenType
map<string, TokenType> keywords = {
    {"float", DT}, {"char", DT}, {"string", DT}, {"if", IF}, {"else", ELSE}, 
    {"while", WHILE}, {"break", BREAK}, 
    {"class", CLASS}, {"abstract", ABSTRACT}, {"constructor", CONSTRUCTOR},
    {"import", IMPORT}, {"return", RETURN}, {"this", THIS}, 
    {"new", NEW}, {"public", AM}, {"private", AM},{"protected", AM},{"static", AM}, {"expand", EXPAND}
};

// Maps operators to their corresponding TokenType
map<string, TokenType> operators = {
    {"++", INC_DEC}, {"--", INC_DEC}, {"+", PM}, {"-", PM}, {"*", MDM},
    {"/", MDM}, {"%", MDM}, {"<", ROP}, {">", ROP}, {"<=", ROP},
    {">=", ROP}, {"!=", ROP}, {"==", ROP}, {"&&", LOGICAL_AND},
    {"||", LOGICAL_OR}, {"=", ASSIGN}
};

// Maps single character punctuators to their corresponding TokenType
map<char, TokenType> punctuators = {
    {';', SEMICOLON}, {'.', DOT}, {',', COMMA},
    {'{', L_BRACE}, {'}', R_BRACE},
    {'(', L_PAREN}, {')', R_PAREN},
    {'[', L_BRACKET}, {']', R_BRACKET}
};

// Checks if a string is a floating-point constant using a regular expression
bool isFloatConst(const string &str) {
    return regex_match(str, regex("^[+-]?([0-9][.][0-9]+|[0-9]+[.][0-9])([eE][+-]?[0-9]+)?$"));
}

// Checks if a string is an integer constant using a regular expression
bool isIntConst(const string &str) {
    return regex_match(str, regex("^[+-]?[0-9]+$"));
}

// Checks if a string is a character constant using a regular expression
bool isCharConst(const string &str) {
    return regex_match(str, regex("^'(\\\\.|[^\\\\'])'$"));
}

// Checks if a string is a string constant using a regular expression
bool isStringConst(const string &str) {
    return regex_match(str, regex("^\"(\\\\.|[^\\\\\"])*\"$"));
}

// Checks if a string is a valid identifier using a regular expression
bool isIdentifier(const string &str) {
    return regex_match(str, regex("^[A-Za-z_][A-Za-z_\\d]*$"));
}

// Tokenizes the input string into a list of tokens
vector<Token> tokenize(const string &input) {
    vector<Token> tokens;
    string current;
    int line = 1;  // Tracks the current line number
    bool inString = false;  // Tracks if inside a string literal
    bool inChar = false;    // Tracks if inside a character literal

    for (size_t i = 0; i < input.length(); i++) {
        char ch = input[i];

        // Increment line number on newline character
        if (ch == '\n') {
            line++;
            continue;
        }

        // Skip whitespace characters outside of strings or characters
        if (isspace(ch) && !inString && !inChar) {
            continue;
        }

        // If inside a string literal, continue building the string
        if (inString) {
            current += ch;
            if (ch == '"' && (i == 0 || input[i - 1] != '\\')) {  // End of string literal
                tokens.push_back(Token(tokenTypeToString(STRING_CONST), current.substr(1, current.length() - 2), line));
                current.clear();
                inString = false;
            }
            continue;
        } 

        // If inside a character literal, continue building the character
        if (inChar) {
            current += ch;
            if (ch == '\'' && (i == 0 || input[i - 1] != '\\')) {  // End of character literal
                tokens.push_back(Token(tokenTypeToString(CHAR_CONST), current.substr(1, current.length() - 2), line));
                current.clear();
                inChar = false;
            }
            continue;
        }

        // Start of a string literal
        if (ch == '"') {
            inString = true;
            current += ch;
            continue;
        }

        // Start of a character literal
        if (ch == '\'') {
            inChar = true;
            current += ch;
            continue;
        }

        // Handling punctuators
        if (punctuators.count(ch)) {
            tokens.push_back(Token(tokenTypeToString(punctuators[ch]), string(1, ch), line));
            continue;
        }

        // Handling operators
        if (i < input.length() - 1 && operators.count(input.substr(i, 2))) {
            tokens.push_back(Token(tokenTypeToString(operators[input.substr(i, 2)]), input.substr(i, 2), line));
            i++;
            continue;
        } else if (operators.count(string(1, ch))) {
            tokens.push_back(Token(tokenTypeToString(operators[string(1, ch)]), string(1, ch), line));
            continue;
        }

        // Building identifiers, constants, or unknown tokens
        if (isalnum(ch) || ch == '_' || ch == '.') {
            current += ch;

            // End of token detection
            if (i + 1 == input.length() || !isalnum(input[i + 1]) && input[i + 1] != '_' && input[i + 1] != '.') {
                if (keywords.count(current)) {
                    tokens.push_back(Token(tokenTypeToString(keywords[current]), current, line));
                } else if (isFloatConst(current)) {
                    tokens.push_back(Token(tokenTypeToString(FLOAT_CONST), current, line));
                } else if (isIntConst(current)) {
                    tokens.push_back(Token(tokenTypeToString(INT_CONST), current, line));
                } else if (isCharConst(current)) {
                    tokens.push_back(Token(tokenTypeToString(CHAR_CONST), current, line));
                } else if (isStringConst(current)) {
                    tokens.push_back(Token(tokenTypeToString(STRING_CONST), current, line));
                } else if (isIdentifier(current)) {
                    tokens.push_back(Token(tokenTypeToString(ID), current, line));
                } else {
                    tokens.push_back(Token(tokenTypeToString(UNKNOWN), current, line));
                }
                current.clear();
            }
            continue;
        }
    }

    return tokens;
}

int main() {
    // Open the file for reading
    ifstream inputFile("source.txt");
    if (!inputFile.is_open()) {
        cerr << "Error opening file." << endl;
        return 1;
    }

    // Read the entire file into a string
    string input((istreambuf_iterator<char>(inputFile)), istreambuf_iterator<char>());
    inputFile.close();

    // Tokenize the input string
    vector<Token> tokens = tokenize(input);

    // Open the tokens.txt file for writing
    ofstream tokensFile("token.txt");
    if (!tokensFile.is_open()) {
        cerr << "Error opening tokens.txt for writing." << endl;
        return 1;
    }

    // Write the tokens to the file
    tokensFile << "(Class part,\t Value Part, \tLine no)" << endl;
    for (const auto &token : tokens) {
        tokensFile << "(" << token.classPart << ", " << token.valuePart << ", " << token.lineNo << ")" << endl;
    }

    // Close the tokens file
    tokensFile.close();

    // Optionally, print to console as well
    cout << "(Class part,\t Value Part, \tLine no)" << endl;
    for (const auto &token : tokens) {
        cout << "(" << token.classPart << ", " << token.valuePart << ", " << token.lineNo << ")" << endl;
    }

    return 0;
}
