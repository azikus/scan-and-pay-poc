package com.azikus.scanpay.displaytest;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.PixelCopy;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;

/** Offline, synthetic content for testing independent SUNMI display operation. */
public final class DisplayTestActivity extends Activity {
    private WebView web;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        web = new WebView(this);
        web.setBackgroundColor(0xff0a0a0a);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setAllowFileAccess(false);
        web.getSettings().setAllowContentAccess(false);
        web.getSettings().setAllowFileAccessFromFileURLs(false);
        web.getSettings().setAllowUniversalAccessFromFileURLs(false);
        web.getSettings().setDomStorageEnabled(false);
        web.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                applyTestMode();
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return true;
            }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (request.getUrl().toString().startsWith("file:///android_asset/")) return null;
                return new WebResourceResponse("text/plain", "UTF-8", new ByteArrayInputStream(new byte[0]));
            }
        });
        setContentView(web);
        web.loadUrl("file:///android_asset/index.html");
    }

    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        applyTestMode();
    }

    private void applyTestMode() {
        String mode = getIntent().getStringExtra("test_mode");
        if ("sample".equals(mode)) web.evaluateJavascript("byId('run').click()", null);
        else if ("next".equals(mode)) web.evaluateJavascript("byId('next').click()", null);
        else if ("idle".equals(mode)) web.evaluateJavascript("byId('idle').click()", null);
        if (!getIntent().getBooleanExtra("capture", false)) return;
        new Handler().postDelayed(() -> {
            if (isDestroyed() || web.getWidth() == 0 || web.getHeight() == 0) return;
            Bitmap image = Bitmap.createBitmap(web.getWidth(), web.getHeight(), Bitmap.Config.ARGB_8888);
            PixelCopy.request(getWindow(), image, result -> {
                if (result == PixelCopy.SUCCESS) {
                    try (FileOutputStream output = new FileOutputStream(new File(getExternalFilesDir(null), "display-test.png"))) {
                        image.compress(Bitmap.CompressFormat.PNG, 100, output);
                        Log.i("ScanpayDisplayTest", "Captured own test window");
                    } catch (Exception failure) {
                        Log.w("ScanpayDisplayTest", "Test capture failed", failure);
                    }
                } else Log.w("ScanpayDisplayTest", "PixelCopy result " + result);
                image.recycle();
            }, new Handler());
        }, 1500);
    }

    @Override protected void onDestroy() {
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
