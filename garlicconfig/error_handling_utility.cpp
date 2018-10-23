#include <string>
#include <vector>
#include <exception>

#include <GarlicConfig/exceptions.h>

using namespace std;
using namespace garlic;


vector<string> get_native_error()
{
  try {
    throw;
  } catch (const ConfigNotFound& e) {
    string msg = "Config '" + e.config_name() + "' was not found!";
    return vector<string>{"ConfigNotFound", msg};
  } catch (const exception& e) {
    return vector<string>{"RuntimeError", e.what()};
  } catch (...) {
    return vector<string>{"RuntimeError", "Uncaught C++ Exception."};
  }
}
