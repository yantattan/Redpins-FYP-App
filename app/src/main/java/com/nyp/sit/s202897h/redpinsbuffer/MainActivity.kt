package com.nyp.sit.s202897h.redpinsbuffer

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        var webView = findViewById<WebView>(R.id.webview)
        webView.setWebViewClient(WebViewClient())
        webView.loadUrl("http://10.0.2.2:5000/")
    }


}