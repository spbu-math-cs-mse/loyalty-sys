package com.example.loyalitysys

import android.graphics.Bitmap
import android.os.Bundle
import android.util.Log
import android.widget.ImageView
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.example.loyalitysys.network.NetworkHandler
import com.example.loyalitysys.network.PurchaseResponse
import com.example.loyalitysys.qrgenerator.QR
import com.example.loyalitysys.ui.theme.LoyalitySysTheme
import com.google.zxing.BarcodeFormat
import com.google.zxing.WriterException
import com.google.zxing.common.BitMatrix
import com.journeyapps.barcodescanner.BarcodeEncoder

class MainActivity : ComponentActivity() {
    private lateinit var loyaltyLevelTextView: TextView
    private lateinit var saleAmountTextView: TextView
    private lateinit var qrCodeImageView: ImageView

    private val baseUrl = "https://your_api_base_url/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        loyaltyLevelTextView = findViewById(R.id.loyaltyLevelTextView)
        saleAmountTextView = findViewById(R.id.saleAmountTextView)
        qrCodeImageView = findViewById(R.id.qrCodeImageView)

        NetworkHandler(loyaltyLevelTextView, saleAmountTextView, baseUrl, true)
        QR().getQR("User1589")
    }
}