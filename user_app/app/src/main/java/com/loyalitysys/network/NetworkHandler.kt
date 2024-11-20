@file:OptIn(DelicateCoroutinesApi::class)

package com.loyalitysys.network

import android.util.Log
import kotlinx.coroutines.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

object NetworkSettings {
    const val baseUrl = "http://adress:port/"
}

// Snake case for correct json field name in request
data class Product(val product_id: String, val quantity: String)

// Snake case for correct json field name in request
data class PurchaseRequest(val user_id: String, val products: List<Product>)

interface ApiService {
    @POST("/user/user_id/purchase")
    fun getLastPurchase(@Body body: PurchaseRequest): Call<Unit>
}

object NetworkHandler {
    fun sendLastPurchase(userID: String, products: List<Product> = listOf(Product("T-shirt", (1).toString()))) {
        val retrofit = Retrofit.Builder()
            .baseUrl(NetworkSettings.baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(ApiService::class.java)
        GlobalScope.launch {
                apiService.getLastPurchase(PurchaseRequest(userID, products)).enqueue(object : Callback<Unit> {
                    override fun onResponse(
                        call: Call<Unit>,
                        response: Response<Unit>
                    ) {
                        Log.d("Got response", response.code().toString())
                    }

                    override fun onFailure(call: Call<Unit>, t: Throwable) {
                        Log.e("Request failed", t.toString())
                    }
                })
        }
    }
}
