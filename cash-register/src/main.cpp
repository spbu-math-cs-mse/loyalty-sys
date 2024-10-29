#include <exception>
#include <optional>
#include <random>
#include <string>
#include <vector>

#include <../common/logger.hpp>
#include <third-party/cxxopts.hpp>
#include <third-party/httplib.h>
#include <third-party/json.h>

using json = nlohmann::json;

struct RandomGenerator {
  static constexpr uint64_t kMinUserId = 1000;
  static constexpr uint64_t kMaxUserId = 9999;
  static constexpr uint32_t kMinProductCount = 1;
  static constexpr uint32_t kMaxProductCount = 10;
  static constexpr uint64_t kMinPriceKopeck = 10'00;
  static constexpr uint64_t kMaxPriceKopeck = 1000'00;

  std::random_device rd;
  std::mt19937 gen;
  std::uniform_int_distribution<> user_id_dist;
  std::uniform_int_distribution<> product_count_dist;
  std::uniform_int_distribution<> price_kopeck_dist;

  RandomGenerator()
      : gen(rd()), user_id_dist(kMinUserId, kMaxUserId),
        product_count_dist(kMinProductCount, kMaxProductCount),
        price_kopeck_dist(kMinPriceKopeck, kMaxPriceKopeck) {}

  std::string get_random_user_id() {
    return "User" + std::to_string(user_id_dist(gen));
  }

  uint32_t get_random_product_count() { return product_count_dist(gen); }

  uint64_t get_random_product_price_kopeck() { return price_kopeck_dist(gen); }
};

struct Product {
  std::string name;
  uint64_t price_kopeck;
};

void purchase(const httplib::Request &req, httplib::Response &res) {
  RandomGenerator generator;
  std::optional<std::string> user_id;
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

      for (const auto &product : request_json["products"]) {
        if (product.is_object()) {
          if (!(product.contains("name") && product.contains("price"))) {
            throw std::runtime_error("wrong json format for product");
          }

          const std::string &price_kopek = product["price"];
          products.push_back(
              {.name = product["name"],
               .price_kopeck = static_cast<uint64_t>(std::stoll(price_kopek))});
        }
      }
    }
  } catch (const std::exception &e) {
    LOG(ERROR) << "Error while JSON. Error = " << e.what()
               << "; json = " << req.body;
  }

  if (!user_id.has_value()) {
    user_id = generator.get_random_user_id();
  }

  if (products.empty()) {
    const auto product_count = generator.get_random_product_count();
    products.reserve(product_count);

    for (size_t product_id = 1; product_id <= product_count; ++product_id) {
      products.push_back({std::string("Product ") + std::to_string(product_id),
                          generator.get_random_product_price_kopeck()});
    }
  }

  LOG(DEBUG) << "User ID = " << user_id.value();
  LOG(DEBUG) << "Products = {";

  for (const auto &product : products) {
    LOG(DEBUG) << "    " << product.name << ": " << product.price_kopeck;
  }

  LOG(DEBUG) << "}";

  uint64_t total_cost = 0;
  for (const auto &product : products) {
    total_cost += product.price_kopeck;
  }

  json response_json;
  response_json["user_id"] = user_id.value();
  response_json["total_cost"] = std::to_string(total_cost);

  res.set_content(response_json.dump(), "application/json");
}

std::optional<size_t> parse_args(int argc, char **argv) {
  try {
    cxxopts::Options options("cach-register");

    options.add_options()("p,port", "Port number", cxxopts::value<size_t>());

    const auto result = options.parse(argc, argv);

    return result["port"].as_optional<size_t>();
  } catch (const std::exception &exception) {
    LOG(ERROR) << "Error while command line arguments parsing: "
               << exception.what();
  }

  return std::nullopt;
}

int main(int argc, char *argv[]) {
  static constexpr auto kLocalHost = "0.0.0.0";
  static constexpr size_t kDefaultPort = 1234;

  httplib::Server server;

  server.Post("/purchase", purchase);

  const auto port = parse_args(argc, argv).value_or(kDefaultPort);
  server.listen(kLocalHost, port);
  return 0;
}
