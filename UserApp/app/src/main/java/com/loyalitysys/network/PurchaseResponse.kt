package com.loyalitysys.network

data class PurchaseResponse(
    val user_id: String,
    var total_cost: Long
)