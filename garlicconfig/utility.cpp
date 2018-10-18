#include <iostream>
#include <string>
#include <map>

#include "GarlicConfig/garlicconfig.h"


using namespace std;
using namespace garlic;


void save_str_to_repo(ConfigRepository* repo, const string& name, const string& content) {
    repo->save(name, [&content](ostream& output_stream) {
        output_stream << content;
    });
}


string read_str_from_repo(ConfigRepository* repo, const string& name) {
    return string(istreambuf_iterator<char>(repo->retrieve(name)->rdbuf()), {});
}


shared_ptr<LayerValue> load_value(ConfigRepository* repo, Decoder* decoder, const string& name) {
    return decoder->load(*repo->retrieve(name));
}
