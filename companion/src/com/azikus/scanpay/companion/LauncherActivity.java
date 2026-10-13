package com.azikus.scanpay.companion;

/** Existing public entry point hosts the panel directly; private activities stay private.
 * Restricted secondary displays require initial placement by the authorized ADB launch script.
 */
public final class LauncherActivity extends CompanionActivity {
  @Override public void onCreate(android.os.Bundle state) {
    super.onCreate(state);
    android.app.ActivityOptions options=android.app.ActivityOptions.makeBasic();
    options.setLaunchDisplayId(0);
    android.content.Intent journey=new android.content.Intent(this,JourneyActivity.class).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK);
    try {
      startActivity(journey,options.toBundle());
    } catch (RuntimeException error) {
      android.widget.Toast.makeText(this,"Could not open the system journey on the primary display.",android.widget.Toast.LENGTH_LONG).show();
    }
  }
}
