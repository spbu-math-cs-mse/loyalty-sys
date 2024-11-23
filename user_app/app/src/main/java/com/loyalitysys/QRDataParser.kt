package com.loyalitysys

import android.util.Log
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.Optional

data class ReceiptData(
    val dateTime: LocalDateTime,
    val sum: Long,
    val fiscalNumber: String,
    val documentNumber: String,
    val fiscalSign: String,
    val operationType: Int
)

object QRDataParser {

    private val dateTimeFormatter = DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmm")

    fun parseQRCode(qrCode: String): Optional<ReceiptData> {
        val parameters = qrCode.split("&")
            .associate {
                val (key, value) = it.split("=")
                key to value
            }
        Log.d("QR scanner", parameters.toString())
        if (!isValid(parameters)) {
            return Optional.empty()
        }

        val dateTime = LocalDateTime.parse(parameters["t"], dateTimeFormatter)
        val sumInRubles = parameters["s"]?.toDoubleOrNull() ?: 0.0
        val sumInKopecks = (sumInRubles * 100).toLong()
        val operationType = parameters["n"]?.toIntOrNull() ?: 0

        return Optional.of(ReceiptData(
            dateTime = dateTime,
            sum = sumInKopecks,
            fiscalNumber = parameters["fn"] ?: "",
            documentNumber = parameters["i"] ?: "",
            fiscalSign = parameters["fp"] ?: "",
            operationType = operationType
        ))
    }

    private fun isValid(parameters: Map<String, String>): Boolean {
        return parameters.keys.containsAll(listOf("t", "s", "fn", "i", "fp", "n")) &&
                parameters["t"]?.startsWith("202") == true &&
                parameters["s"]?.matches(Regex("^[0-9]+([.][0-9]{1,2})?$")) == true &&
                parameters["n"]?.matches(Regex("^[1-4]+$")) == true
    }
}
