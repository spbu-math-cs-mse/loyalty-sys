#include <iostream>
#include <vector>
#include <string>
#include <random>

#include <third-party/httplib.h>
#include <third-party/json.h>
#include <common/logger.hpp>

using json = nlohmann::json;

struct RandomGenerator {
    static constexpr double kMinUserId = 1000;
    static constexpr double kMaxUserId = 9999;
    static constexpr int kMinProductCount = 1;
    static constexpr int kMaxProductCount = 10;
    static constexpr double kMinprice_rub = 10.0;
    static constexpr double kMaxprice_rub = 100.0;

    std::random_device rd;
    std::mt19937 gen;
    std::uniform_int_distribution<> user_id_dist;
    std::uniform_int_distribution<> product_count_dist;
    std::uniform_real_distribution<> price_rub_dist;

    RandomGenerator() : gen(rd()),
        user_id_dist(kMinUserId, kMaxUserId),
        product_count_dist(kMinProductCount, kMaxProductCount),
        price_rub_dist(kMinprice_rub, kMaxprice_rub) {}

    int get_random_user_id() {
        return user_id_dist(gen);
    }

    int get_random_product_count() {
        return product_count_dist(gen);
    }

    double get_random_product_price_rub() {
        return price_rub_dist(gen);
    }
};

struct Product {
    std::string name;
    double price_rub;
};

const int PORT = 1234;

void purchase(const httplib::Request& req, httplib::Response& res) {
    RandomGenerator generator;
    std::optional<int> user_id;
    std::vector<Product> products;

    try {
        json request_json = json::parse(req.body);
        if (!request_json.is_object()) {
            throw std::runtime_error("request is not a json object");
        }
        if (request_json.contains("user_id")) {
            user_id = request_json["user_id"];
        }

        if (request_json.contains("products")) {
            if (!request_json["products"].is_array()) {
                throw std::runtime_error("wrong json format for products field");
            }

            std::string::size_type size;
            for (const auto& product : request_json["products"]) {
                if (product.is_object()) {
                    if (!(product.contains("name") && product.contains("price"))) {
                        throw std::runtime_error("wrong json format for product");
                    }

                    const std::string& price_rub = product["price"];
                    products.push_back({product["name"], std::stod(price_rub, &size)});
                }
            }
        }
    } catch (const std::exception& e) {
        ERROR("Error while JSON. Error = " << e.what() << "; json = " << req.body);
    }

    if (!user_id.has_value()) {
        user_id = generator.get_random_user_id();
    }

    if (products.empty()) {
        int product_count = generator.get_random_product_count();
        products.reserve(product_count);

        for (int i = 0; i < product_count; ++i) {
            products.push_back({std::string("Product ") + std::to_string(i + 1), generator.get_random_product_price_rub()});
        }
    }

    DEBUG("User ID = " << user_id.value());
    DEBUG("Products = {");
    for (const auto& product : products) {
        DEBUG("    " << product.name << ": " << product.price_rub);
    }
    DEBUG("}");

    double total_cost = 0;
    for (const auto& product : products) {
        total_cost += product.price_rub;
    }

    json response_json;
    response_json["user_id"] = user_id.value();
    response_json["total_cost"] = std::to_string(total_cost);

    res.set_content(response_json.dump(), "application/json");
}

int main() {
    httplib::Server server;

    server.Post("/purchase", purchase);
    
    server.listen("0.0.0.0", PORT);
    return 0;
}
