package com.example.loyalitysys.qrgenerator

import android.graphics.Bitmap
import com.google.zxing.BarcodeFormat
import com.google.zxing.WriterException
import com.google.zxing.common.BitMatrix
import com.journeyapps.barcodescanner.BarcodeEncoder

class QR {
    private fun generateQRCode(userID: String): Bitmap {
        val barcodeEncoder = BarcodeEncoder()
        try {
            val bitMatrix: BitMatrix = barcodeEncoder.encode(userID, BarcodeFormat.QR_CODE, 600, 600)
            val bitmap: Bitmap = barcodeEncoder.createBitmap(bitMatrix)
            writeQRToDatabase(userID, bitMatrix)
            return bitmap
        } catch (e: WriterException) {
            e.printStackTrace()
        }
        return barcodeEncoder.createBitmap(BitMatrix(0))
    }

    private fun writeQRToDatabase(userID: String, qr: BitMatrix) {
        // TODO: implement
    }

    private fun getQRFromDatabase(userID: String): Bitmap? {
        // TODO: implement
        return null
    }

    public fun getQR(userID: String): Bitmap {
        var qr = getQRFromDatabase(userID)
        if (qr == null) {
            qr = generateQRCode(userID)
        }
        return qr
    }
}