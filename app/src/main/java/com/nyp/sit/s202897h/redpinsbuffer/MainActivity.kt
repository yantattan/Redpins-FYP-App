package com.nyp.sit.s202897h.redpinsbuffer

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.animation.AnimationUtils
import android.webkit.*

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        var webView = findViewById<WebView>(R.id.webview)
        webView.settings.domStorageEnabled = true
        webView.settings.javaScriptEnabled = true
        webView.settings.cacheMode = WebSettings.LOAD_CACHE_ELSE_NETWORK
        webView.settings.setAppCacheEnabled(true)
        webView.scrollBarStyle = View.SCROLLBARS_INSIDE_OVERLAY
        webView.loadUrl("http://10.0.2.2:5000/")

        class CustWebViewClient: WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)

                val anim = AnimationUtils.loadAnimation(baseContext, android.R.anim.fade_out)
                webView.startAnimation(anim)
            }
        }

        webView.webViewClient = CustWebViewClient()
        webView.webChromeClient = object: WebChromeClient() {
            override fun onGeolocationPermissionsShowPrompt(origin: String?, callback: GeolocationPermissions.Callback?) {
                super.onGeolocationPermissionsShowPrompt(origin, callback)

                callback?.invoke(origin, true, false)
            }

            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                Log.d("WebView", consoleMessage.toString())
                return super.onConsoleMessage(consoleMessage)
            }
        }
    }


}