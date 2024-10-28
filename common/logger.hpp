#pragma once

#include <iostream>
#include <string>
#include <sstream>

enum LogLevel {
   DEBUG,
   INFO,
   WARN,
   ERROR
};

namespace {
std::string getLevel(LogLevel level) {
   switch(level) {
       case DEBUG: return "DEBUG";
       case INFO:  return "INFO";
       case WARN:  return "WARN";
       case ERROR: return "ERROR";
   }
   
   throw std::runtime_error("Unexpected level");
}    
}

class LOG {
public:
    LOG(LogLevel level) {
        std::cout << "[" << getLevel(level) << "] ";
    }
    
    LOG() : LOG(DEBUG) {
    }
    
    ~LOG() {
        std::cout << std::endl;
    }
   
    template<class T>
    LOG &operator<<(const T &message) {
        std::cout << message;
        return *this;
    }
};

#define DEBUG(x) LOG(DEBUG) << x
#define INFO(x)  LOG(INFO)  << x
#define WARN(x)  LOG(WARN)  << x
#define ERROR(x) LOG(ERROR) << x
