@file:OptIn(DelicateCoroutinesApi::class)

package com.example.loyalitysys.network

import android.util.Log
import android.widget.TextView
import kotlinx.coroutines.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

object NetworkSetting {
    const val baseUrl = "http://adress:port/"
}

data class Product(val product_id: String, val quantity: String)

data class PurchaseRequest(val user_id: String, val products: List<Product>)

interface ApiService {
    @POST("/user/user_id/purchase")
    fun getLastPurchase(@Body body: PurchaseRequest): Call<Unit>
}

object NetworkHandler {
    fun sendLastPurchase(user_id: String, products: List<Product> = listOf(Product("T-shirt", (1).toString()))) {
        val retrofit = Retrofit.Builder()
            .baseUrl(NetworkSetting.baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(ApiService::class.java)
        GlobalScope.launch {
                apiService.getLastPurchase(PurchaseRequest(user_id, products)).enqueue(object : Callback<Unit> {
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
