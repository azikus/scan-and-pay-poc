package com.azikus.scanpay.companion;

import android.app.*;
import android.content.*;
import android.os.Bundle;
import android.graphics.Color;
import android.net.Uri;
import android.view.*;
import android.webkit.*;
import android.widget.*;
import android.security.keystore.*;
import android.util.Base64;
import java.io.ByteArrayInputStream;
import java.security.KeyStore;
import java.util.Locale;
import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;
import org.json.JSONObject;

/** Display placement and protected connection settings only. No extraction API access. */
public class CompanionActivity extends Activity implements SharedPreferences.OnSharedPreferenceChangeListener {
  private WebView web;
  private SharedPreferences prefs;
  private volatile String origin="";
  private static final String KEY="scanpay-companion-token";
  protected boolean primary() { return false; }
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    getWindow().getDecorView().setSystemUiVisibility(5894);
    prefs=getSharedPreferences("connection",MODE_PRIVATE);
    prefs.edit().remove("mode").apply();
    prefs.registerOnSharedPreferenceChangeListener(this);
    web=new WebView(this); web.setBackgroundColor(Color.rgb(16,17,19)); setContentView(web);
    WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(false);
    s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setCacheMode(WebSettings.LOAD_NO_CACHE);s.setSaveFormData(false);s.setMediaPlaybackRequiresUserGesture(true);
    CookieManager.getInstance().setAcceptCookie(false);
    web.addJavascriptInterface(new Bridge(),"Scanpay");
    web.setWebViewClient(new WebViewClient(){
      @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r){return !allowed(r.getUrl());}
      @Override public WebResourceResponse shouldInterceptRequest(WebView v,WebResourceRequest r){
        if(allowed(r.getUrl())&&r.getMethod().equals("GET"))return null;
        if(sameOrigin(r.getUrl()) && "/v1/admin/selection".equals(r.getUrl().getPath()) && r.getMethod().equals("PUT"))return null;
        return new WebResourceResponse("text/plain","UTF-8",403,"Blocked",null,new ByteArrayInputStream(new byte[0]));
      }
      @Override public void onReceivedError(WebView v,WebResourceRequest r,WebResourceError error){
        if(r.isForMainFrame()) showOffline();
      }
    });
    if(prefs.getString("origin","").isEmpty()) settings(); else load();
  }
  private boolean sameOrigin(Uri uri){return origin.equals(uri.getScheme()+"://"+uri.getEncodedAuthority());}
  private boolean allowed(Uri uri){
    return sameOrigin(uri) &&
      ("/demo".equals(uri.getPath()) || uri.getPath().startsWith("/demo/assets/") ||
       "/v1/profiles".equals(uri.getPath()) || "/v1/demo/events".equals(uri.getPath()) || "/v1/demo/snapshot".equals(uri.getPath()));
  }
  private void showOffline(){
    LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(60,60,60,60);
    TextView text=new TextView(this);text.setText("Backend connection unavailable. Check the network and backend address.");text.setTextColor(Color.WHITE);text.setTextSize(26);box.addView(text);
    Button retry=new Button(this);retry.setText("Reconnect");retry.setOnClickListener(v->{setContentView(web);load();});box.addView(retry);
    Button settings=new Button(this);settings.setText("Connection settings");settings.setOnClickListener(v->settings());box.addView(settings);setContentView(box);
  }
  private void load(){
    origin=prefs.getString("origin","");if(origin.isEmpty())return;
    setContentView(web);
    String view=primary()?"technical":"customer";
    web.loadUrl(origin+"/demo?view="+view);
  }
  @Override public void onSharedPreferenceChanged(SharedPreferences p,String key){
    if(key.equals("origin")||key.equals("token")||key.equals("session"))load();
  }
  @Override public void onBackPressed(){settings();}
  @Override protected void onDestroy(){prefs.unregisterOnSharedPreferenceChangeListener(this);web.removeJavascriptInterface("Scanpay");web.destroy();super.onDestroy();}
  private javax.crypto.SecretKey key() throws Exception {
    KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);
    if(!ks.containsAlias(KEY)){
      KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
      generator.init(new KeyGenParameterSpec.Builder(KEY,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());generator.generateKey();
    }
    return (javax.crypto.SecretKey)ks.getKey(KEY,null);
  }
  private String token() throws Exception {
    String stored=prefs.getString("token","");if(stored.isEmpty())return "";
    byte[] data=Base64.decode(stored,Base64.NO_WRAP);byte[] iv=java.util.Arrays.copyOfRange(data,0,12);
    Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,iv));
    return new String(cipher.doFinal(data,12,data.length-12),java.nio.charset.StandardCharsets.UTF_8);
  }
  private String encrypt(String token) throws Exception {
    Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,key());
    byte[] encrypted=cipher.doFinal(token.getBytes(java.nio.charset.StandardCharsets.UTF_8));byte[] output=new byte[12+encrypted.length];
    System.arraycopy(cipher.getIV(),0,output,0,12);System.arraycopy(encrypted,0,output,12,encrypted.length);return Base64.encodeToString(output,Base64.NO_WRAP);
  }
  static String localOrigin(String input) {
    Uri u=Uri.parse(input.trim());String host=u.getHost();String scheme=u.getScheme();
    if(host==null||!"http".equals(scheme)||u.getUserInfo()!=null||u.getQuery()!=null||u.getFragment()!=null||!(u.getPath().isEmpty()||u.getPath().equals("/")))throw new IllegalArgumentException();
    boolean local=host.toLowerCase(Locale.ROOT).endsWith(".local");
    String[] octets=host.split("\\.");
    if(octets.length==4){try{int a=Integer.parseInt(octets[0]),b=Integer.parseInt(octets[1]);for(String octet:octets)if(Integer.parseInt(octet)<0||Integer.parseInt(octet)>255)throw new IllegalArgumentException();local=a==10||(a==172&&b>=16&&b<=31)||(a==192&&b==168)||(a==169&&b==254);}catch(NumberFormatException e){throw new IllegalArgumentException();}}
    if(!local||u.getPort()>65535||u.getPort()==0)throw new IllegalArgumentException();
    return "http://"+u.getEncodedAuthority();
  }
  private void settings(){
    LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(28,18,28,18);
    EditText address=new EditText(this);address.setHint("http://backend-local-address:8000");address.setSingleLine();address.setText(prefs.getString("origin",""));box.addView(address);
    EditText secret=new EditText(this);secret.setHint("Local access token (blank keeps saved token)");secret.setSingleLine();secret.setInputType(129);box.addView(secret);
    AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Backend connection").setView(box).setNegativeButton("Cancel",null).setPositiveButton("Save",null).create();
    dialog.setOnShowListener(d->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
      try{String next=localOrigin(address.getText().toString());String access=secret.getText().toString();if(access.isEmpty())access=token();if(access.isEmpty())throw new IllegalArgumentException();String protectedToken=encrypt(access);prefs.edit().putString("token",protectedToken).putString("origin",next).apply();secret.setText("");dialog.dismiss();load();}
      catch(Exception e){address.setError("Enter a private backend HTTP address and access token.");}
    }));dialog.show();
  }
  public final class Bridge {
    @JavascriptInterface public String configuration(){
      try{JSONObject result=new JSONObject();result.put("token",token());result.put("session",prefs.getString("session",""));return result.toString();}catch(Exception e){return "{}";}
    }
    @JavascriptInterface public void follow(String session){if(session.isEmpty()||session.matches("[0-9a-fA-F-]{36}"))runOnUiThread(()->prefs.edit().putString("session",session).apply());}
    @JavascriptInterface public void settings(){runOnUiThread(()->CompanionActivity.this.settings());}
  }
}
