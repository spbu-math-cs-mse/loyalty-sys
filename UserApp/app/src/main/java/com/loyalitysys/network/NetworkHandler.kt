@file:OptIn(DelicateCoroutinesApi::class)

package com.example.loyalitysys.network

import android.util.Log
import android.widget.TextView
import com.loyalitysys.network.PurchaseResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

object NetworkSetting {
    const val baseUrl = "http://84.201.154.253:1235/"
}

data class Product(val name: String, val price: String)

data class PurchaseRequest(val user_id: String, val products: List<Product>)

interface ApiService {
    @POST("purchase")
    fun getLastPurchase(@Body body: PurchaseRequest): Call<PurchaseResponse>
}

class NetworkHandler(val levelTextView: TextView, val saleTextView: TextView, shouldFake: Boolean = false) {
    init {
        if (!shouldFake) {
            fetchLastPurchase();
        } else {
            fakeLastPurchase();
        }
    }

    private fun fetchLastPurchase() {
        val retrofit = Retrofit.Builder()
            .baseUrl(NetworkSetting.baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val apiService = retrofit.create(ApiService::class.java)
        GlobalScope.launch {
            delay(1000L * (3..9).random())
            for (purchaseNumber in 1..3) {
                apiService.getLastPurchase(PurchaseRequest("User0", listOf(Product("Random", (1000L).toString())))).enqueue(object : Callback<PurchaseResponse> {
                    override fun onResponse(
                        call: Call<PurchaseResponse>,
                        response: Response<PurchaseResponse>
                    ) {
                        Log.d("Got response", response.code().toString())
                        var responseBody = response.body()!!
                        responseBody.total_cost = responseBody.total_cost * purchaseNumber;
                        Log.d("Got response", responseBody.toString())
                        if (!response.isSuccessful) {
                            return;
                        }
                        response.body()?.let { purchase ->
                            val level: Int = (purchase.total_cost / 1000).toInt()
                            updateViews(level + 1, level * 5)
                        }
                    }

                    override fun onFailure(call: Call<PurchaseResponse>, t: Throwable) {
                        Log.e("Request failed", t.toString())
                    }
                })
                delay(10000)
            }
        }
    }

    private fun updateViews(level: Int, sale: Int) =
        GlobalScope.launch(Dispatchers.Main.immediate) {
            levelTextView.text = "Loyality Level: ${level}"
            saleTextView.text = "Sale: ${sale}%"
        }

    private fun fakeLastPurchase() =
        GlobalScope.launch {
            updateViews(1, 1)
            delay(10000)
            updateViews(3, 5)
            delay(10000)
            updateViews(5, 15)
    }

}
