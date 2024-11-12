package com.example.loyalitysys.qrgenerator

import android.graphics.Bitmap
import com.google.zxing.BarcodeFormat
import com.google.zxing.WriterException
import com.google.zxing.common.BitMatrix
import com.journeyapps.barcodescanner.BarcodeEncoder
import java.util.Optional

class QR {
    private val DefaultUserID = "User0"

    private fun generateQRCode(userID: String): Optional<Bitmap> {
        val barcodeEncoder = BarcodeEncoder()
        try {
            val bitMatrix: BitMatrix = barcodeEncoder.encode(userID, BarcodeFormat.QR_CODE, 600, 600)
            val bitmap: Bitmap = barcodeEncoder.createBitmap(bitMatrix)
            return Optional.of(bitmap)
        } catch (e: WriterException) {
            e.printStackTrace()
        }
        return Optional.empty()
    }

    public fun getQR(userID: String = DefaultUserID): Optional<Bitmap> {
        return generateQRCode(userID)
    }
}
