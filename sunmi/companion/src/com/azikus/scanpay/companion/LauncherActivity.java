package com.azikus.scanpay.companion;
import android.app.*;
import android.os.Bundle;
import android.content.*;
import android.hardware.display.DisplayManager;
import android.view.Display;
public final class LauncherActivity extends Activity {
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    Display[] panels=((DisplayManager)getSystemService(DISPLAY_SERVICE)).getDisplays(DisplayManager.DISPLAY_CATEGORY_PRESENTATION);
    ActivityOptions options=ActivityOptions.makeBasic();
    options.setLaunchDisplayId(panels.length>0?panels[0].getDisplayId():Display.DEFAULT_DISPLAY);
    startActivity(new Intent(this,CompanionActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),options.toBundle());
    if(getSharedPreferences("connection",MODE_PRIVATE).getString("mode","vision").equals("scanpay")){
      ActivityOptions main=ActivityOptions.makeBasic();main.setLaunchDisplayId(Display.DEFAULT_DISPLAY);
      startActivity(new Intent(this,JourneyActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),main.toBundle());
    }
    finish();
  }
}
