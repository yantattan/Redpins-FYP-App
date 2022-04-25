package com.nyp.sit.s202897h.redpinsbuffer

import android.annotation.SuppressLint
import android.app.Service
import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.util.Log
import android.view.animation.AnimationUtils
import android.webkit.*
import android.webkit.WebResourceResponse

import android.webkit.WebResourceRequest

import android.webkit.WebView

import android.webkit.WebResourceError

import android.webkit.WebViewClient

import android.graphics.PixelFormat
import android.os.*
import android.view.*
import android.webkit.JavascriptInterface
import android.widget.Toast




class MainActivity : AppCompatActivity() {
    var webAppUrl = "http://10.0.2.2:5000/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        var webView = findViewById<WebView>(R.id.webview)
        webView.settings.domStorageEnabled = true
        webView.settings.javaScriptEnabled = true
        webView.settings.setGeolocationEnabled(true)
        webView.scrollBarStyle = View.SCROLLBARS_INSIDE_OVERLAY

        val newUrl = intent.getStringExtra("newUrl")
        if (newUrl.isNullOrEmpty())
            webView.loadUrl(webAppUrl)
        else {
            val claimBonusUrl = webAppUrl + "qrCode/claim-bonus/"
            val usePointsUrl = webAppUrl + "qrCode/use-points/"
            Log.d("Hihello", newUrl)
            Log.d("Hihello", newUrl.take(usePointsUrl.length))
            if (newUrl.take(claimBonusUrl.length) == claimBonusUrl || newUrl.take(usePointsUrl.length) == usePointsUrl)
                webView.loadUrl(newUrl)
            else
                webView.loadUrl(webAppUrl + "qrCode/invalidCode")
        }


        class CustWebViewClient: WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                // Check if the site goes to qr-scanner
                Log.d("Hi", url!!)
                if (url == webAppUrl + "qr-scanner") {
                    Log.d("Hi", "IM here")
                    var navQrScanner = Intent(this@MainActivity, QrScannerActivity::class.java)
                    startActivity(navQrScanner)
                }

                // Animation to next page
//                val anim = AnimationUtils.loadAnimation(baseContext, android.R.anim.slide_in_left)
//                webView.startAnimation(anim)

                super.onPageFinished(view, url)
            }
        }

        // Run as background
        class BackgroundService: Service() {
            override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
                val windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
                val params = WindowManager.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    WindowManager.LayoutParams.TYPE_PHONE,
                    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                            or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
                    PixelFormat.TRANSLUCENT
                )

                params.gravity = Gravity.TOP or Gravity.START
                params.x = 0
                params.y = 0
                params.width = 0
                params.height = 0

                val wv = WebView(this)

                wv.webViewClient = object : WebViewClient() {
                    override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
                        Log.d("Error", "loading web view: request: $request error: $error")
                    }

                    override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
                        return if (request.url.toString().contains("/endProcess")) {
                            windowManager.removeView(wv)
                            wv.post { wv.destroy() }
                            stopSelf()
                            WebResourceResponse("bgsType", "utf-8", null)
                        } else {
                            null
                        }
                    }
                }
                wv.loadUrl("http://10.0.2.2:5000/")
                windowManager.addView(wv, params)

                return super.onStartCommand(intent, flags, startId)
            }

            override fun onBind(intent: Intent?): IBinder? {
                TODO("Not yet implemented")
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