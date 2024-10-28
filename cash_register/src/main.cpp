#include <iostream>
#include <vector>
#include <string>
#include <random>

#include <third-party/httplib.h>
#include <third-party/json.h>

using json = nlohmann::json;

std::random_device rd;
std::mt19937 gen(rd());
std::uniform_int_distribution<> user_id_dist(1000, 9999);
std::uniform_int_distribution<> product_count_dist(1, 10);
std::uniform_real_distribution<> price_dist(10.0, 100.0);

const int uninitialized_user_id = -1;

struct Product {
    std::string name;
    double price;
};

void purchase(const httplib::Request& req, httplib::Response& res) {
    int user_id = uninitialized_user_id;
    std::vector<Product> products;

    try {
        json request_json = json::parse(req.body);
        if (request_json.is_object()) {
            if (request_json.contains("user_id")) {
                user_id = request_json["user_id"];
            }

            if (request_json.contains("products") && request_json["products"].is_array()) {
                std::string::size_type sz;
                for (const auto& product : request_json["products"]) {
                    if (product.is_object() && product.contains("name") && product.contains("price")) {
                        std::string price = product["price"];
                        products.push_back({product["name"], std::stod(price, &sz)});
                    }
                }
            }
        }
    } catch (const std::exception& e) {
        std::cout << "DEBUG: Error while JSON. Error = " << e.what() << "; json = " << req.body << std::endl;
    }

    if (user_id == uninitialized_user_id) {
        user_id = user_id_dist(gen);
    }

    if (products.empty()) {
        int product_count = product_count_dist(gen);
        for (int i = 0; i < product_count; ++i) {
            products.push_back({std::string("Product ") + std::to_string(i + 1), price_dist(gen)});
        }
    }

    std::cout << "DEBUG: User ID = " << user_id << std::endl;
    std::cout << "DEBUG: Products = {" << std::endl;
    for (const auto& product : products) {
        std::cout << "    " << product.name << ": " << product.price << std::endl;
    }
    std::cout << "}" << std::endl << std::endl;

    double total_cost = 0;
    for (const auto& product : products) {
        total_cost += product.price;
    }

    json response_json;
    response_json["user_id"] = user_id;
    response_json["total_cost"] = std::to_string(total_cost);

    res.set_content(response_json.dump(), "application/json");
}

int main() {
    httplib::Server server;
    server.Post("/purchase", purchase);
    server.listen("0.0.0.0", 1234);
    return 0;
}
