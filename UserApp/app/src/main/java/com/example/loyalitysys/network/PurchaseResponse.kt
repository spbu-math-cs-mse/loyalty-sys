package com.example.loyalitysys.network

data class PurchaseResponse(
    val loyaltyLevel: Int,
    val lastPurchaseAmount: Long
)
