package com.azikus.scanpay.companion;

/** Existing public entry point hosts the panel directly; private activities stay private.
 * SUNMI USB displays require initial placement by the authorized ADB launch script.
 */
public final class LauncherActivity extends CompanionActivity {
  @Override public void onCreate(android.os.Bundle state) {
    super.onCreate(state);
    if(getSharedPreferences("connection",MODE_PRIVATE).getString("mode","vision").equals("scanpay")){
      android.app.ActivityOptions options=android.app.ActivityOptions.makeBasic();
      options.setLaunchDisplayId(0);
      android.content.Intent journey=new android.content.Intent(this,JourneyActivity.class).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
      startActivity(journey,options.toBundle());
    }
  }
}
