#pragma once

#include <iostream>
#include <string>

enum LogLevel { DEBUG, INFO, WARN, ERROR };

namespace {
std::string getLevel(LogLevel level) {
  switch (level) {
  case DEBUG:
    return "DEBUG";
  case INFO:
    return "INFO";
  case WARN:
    return "WARN";
  case ERROR:
    return "ERROR";
  }

  throw std::runtime_error("Unexpected level");
}
} // namespace

class LOG {
public:
  LOG(LogLevel level) { std::cout << "[" << getLevel(level) << "] "; }

  LOG() : LOG(DEBUG) {}

  ~LOG() { std::cout << std::endl; }

  template <class T> LOG &operator<<(const T &message) {
    std::cout << message;
    return *this;
  }
};
