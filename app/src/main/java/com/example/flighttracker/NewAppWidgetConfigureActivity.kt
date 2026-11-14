//package com.example.flighttracker
//
//import android.app.Activity
//import android.appwidget.AppWidgetManager
//import android.content.Context
//import android.content.Intent
//import android.os.Bundle
//import android.view.View
//import android.widget.EditText
//import com.example.flighttracker.databinding.NewAppWidgetConfigureBinding
//
///**
// * The configuration screen for the [NewAppWidget] AppWidget.
// */
//class NewAppWidgetConfigureActivity : Activity() {
//    private var appWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID
//    private lateinit var appWidgetText: EditText
//    private var onClickListener = View.OnClickListener {
//        val context = this@NewAppWidgetConfigureActivity
//
//        // When the button is clicked, store the string locally
//        val widgetText = appWidgetText.text.toString()
//        saveTitlePref(context, appWidgetId, widgetText)
//
//        // It is the responsibility of the configuration activity to update the app widget
//        val appWidgetManager = AppWidgetManager.getInstance(context)
//        updateAppWidget(context, appWidgetManager, appWidgetId)
//
//        // Make sure we pass back the original appWidgetId
//        val resultValue = Intent()
//        resultValue.putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
//        setResult(RESULT_OK, resultValue)
//        finish()
//    }
//    private lateinit var binding: NewAppWidgetConfigureBinding
//
//    public override fun onCreate(icicle: Bundle?) {
//        super.onCreate(icicle)
//
//        // Set the result to CANCELED.  This will cause the widget host to cancel
//        // out of the widget placement if the user presses the back button.
//        setResult(RESULT_CANCELED)
//
//        binding = NewAppWidgetConfigureBinding.inflate(layoutInflater)
//        setContentView(binding.root)
//
//        appWidgetText = binding.appwidgetText as EditText
//        binding.addButton.setOnClickListener(onClickListener)
//
//        // Find the widget id from the intent.
//        val intent = intent
//        val extras = intent.extras
//        if (extras != null) {
//            appWidgetId = extras.getInt(
//                AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID
//            )
//        }
//
//        // If this activity was started with an intent without an app widget ID, finish with an error.
//        if (appWidgetId == AppWidgetManager.INVALID_APPWIDGET_ID) {
//            finish()
//            return
//        }
//
//        appWidgetText.setText(loadTitlePref(this@NewAppWidgetConfigureActivity, appWidgetId))
//    }
//
//}
//
//private const val PREFS_NAME = "com.example.flighttracker.NewAppWidget"
//private const val PREF_PREFIX_KEY = "appwidget_"
//
//// Write the prefix to the SharedPreferences object for this widget
//internal fun saveTitlePref(context: Context, appWidgetId: Int, text: String) {
//    val prefs = context.getSharedPreferences(PREFS_NAME, 0).edit()
//    prefs.putString(PREF_PREFIX_KEY + appWidgetId, text)
//    prefs.apply()
//}
//
//// Read the prefix from the SharedPreferences object for this widget.
//// If there is no preference saved, get the default from a resource
//internal fun loadTitlePref(context: Context, appWidgetId: Int): String {
//    val prefs = context.getSharedPreferences(PREFS_NAME, 0)
//    val titleValue = prefs.getString(PREF_PREFIX_KEY + appWidgetId, null)
//    return titleValue ?: context.getString(R.string.appwidget_text)
//}
//
//internal fun deleteTitlePref(context: Context, appWidgetId: Int) {
//    val prefs = context.getSharedPreferences(PREFS_NAME, 0).edit()
//    prefs.remove(PREF_PREFIX_KEY + appWidgetId)
//    prefs.apply()
//}


package com.example.flighttracker

import android.app.Activity
import android.appwidget.AppWidgetManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.EditText
import com.example.flighttracker.databinding.NewAppWidgetConfigureBinding

class NewAppWidgetConfigureActivity : Activity() {
    private var appWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID

    // 1. Declare the two new input fields
    private lateinit var originInput: EditText
    private lateinit var destInput: EditText

    private var onClickListener = View.OnClickListener {
        val context = this@NewAppWidgetConfigureActivity

        // 2. Get the typed airport codes, make them uppercase, and remove spaces
        val origin = originInput.text.toString().uppercase().trim()
        val dest = destInput.text.toString().uppercase().trim()

        // 3. Save both to SharedPreferences
        saveRoutePrefs(context, appWidgetId, origin, dest)

        // 4. Tell the widget to update immediately with the new data
        val appWidgetManager = AppWidgetManager.getInstance(context)
        updateAppWidget(context, appWidgetManager, appWidgetId)

        // 5. Pass back the success signal and close screen
        val resultValue = Intent()
        resultValue.putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
        setResult(RESULT_OK, resultValue)
        finish()
    }

    private lateinit var binding: NewAppWidgetConfigureBinding

    public override fun onCreate(icicle: Bundle?) {
        super.onCreate(icicle)
        setResult(RESULT_CANCELED)

        binding = NewAppWidgetConfigureBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // 6. Bind the UI elements using the IDs we set in the XML
        originInput = binding.originInput
        destInput = binding.destInput
        binding.addButton.setOnClickListener(onClickListener)

        val intent = intent
        val extras = intent.extras
        if (extras != null) {
            appWidgetId = extras.getInt(
                AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID
            )
        }

        if (appWidgetId == AppWidgetManager.INVALID_APPWIDGET_ID) {
            finish()
            return
        }
    }
}

private const val PREFS_NAME = "com.example.flighttracker.NewAppWidget"

// --- Helper Functions to Save and Load the Data ---

internal fun saveRoutePrefs(context: Context, appWidgetId: Int, origin: String, dest: String) {
    val prefs = context.getSharedPreferences(PREFS_NAME, 0).edit()
    prefs.putString("origin_$appWidgetId", origin)
    prefs.putString("dest_$appWidgetId", dest)
    prefs.apply()
}

// You will call this function in your AppWidgetProvider class later
internal fun loadOriginPref(context: Context, appWidgetId: Int): String {
    val prefs = context.getSharedPreferences(PREFS_NAME, 0)
    return prefs.getString("origin_$appWidgetId", "KUL") ?: "KUL"
}

// You will call this function in your AppWidgetProvider class later
internal fun loadDestPref(context: Context, appWidgetId: Int): String {
    val prefs = context.getSharedPreferences(PREFS_NAME, 0)
    return prefs.getString("dest_$appWidgetId", "KHI") ?: "KHI"
}

internal fun deleteTitlePref(context: Context, appWidgetId: Int) {
    val prefs = context.getSharedPreferences(PREFS_NAME, 0).edit()
    prefs.remove("origin_$appWidgetId")
    prefs.remove("dest_$appWidgetId")
    prefs.apply()
}