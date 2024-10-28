package com.example.loyalitysys.network

import android.widget.TextView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.*

class NetworkHandler(val levelTextView: TextView, val saleTextView: TextView, url: String = "", shouldFake: Boolean = false) {
    init {
        if (!shouldFake) {
            fetchLastPurchase(url);
        } else {
            fakeLastPurchase();
        }
    }

    private fun fetchLastPurchase(baseUrl: String) {
        // TODO: discuss how we get updates
    }

    private fun updateViews(level: Int, sale: Int) =
        GlobalScope.launch(Dispatchers.Main.immediate) {
            levelTextView.text = "Loyalty Level: ${level}"
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