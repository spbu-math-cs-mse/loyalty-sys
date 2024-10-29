package com.loyalitysys

import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.activity.ComponentActivity
import com.example.loyalitysys.network.NetworkHandler
import com.example.loyalitysys.qrgenerator.QR
import kotlin.jvm.optionals.getOrNull

class MainActivity : ComponentActivity() {
    private lateinit var loyalityLevelTextView: TextView
    private lateinit var saleAmountTextView: TextView
    private lateinit var qrCodeImageView: ImageView

    private val baseUrl = "https://your_api_base_url/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        loyalityLevelTextView = findViewById(R.id.loyalityLevelTextView)
        saleAmountTextView = findViewById(R.id.saleAmountTextView)
        qrCodeImageView = findViewById(R.id.qrCodeImageView)

        NetworkHandler(loyalityLevelTextView, saleAmountTextView)
        qrCodeImageView.setImageBitmap(QR().getQR().getOrNull())
    }
}
