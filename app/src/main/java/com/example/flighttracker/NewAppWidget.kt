package com.example.flighttracker

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.widget.RemoteViews
import org.json.JSONObject
import java.net.URL

/**
 * Implementation of App Widget functionality.
 * App Widget Configuration implemented in [NewAppWidgetConfigureActivity]
 */
class NewAppWidget : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        // There may be multiple widgets active, so update all of them
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onDeleted(context: Context, appWidgetIds: IntArray) {
        // When the user deletes the widget, delete the preference associated with it.
        for (appWidgetId in appWidgetIds) {
            deleteTitlePref(context, appWidgetId)
        }
    }

    override fun onEnabled(context: Context) {
        // Enter relevant functionality for when the first widget is created
    }

    override fun onDisabled(context: Context) {
        // Enter relevant functionality for when the last widget is disabled
    }
}

//internal fun updateAppWidget(
//    context: Context,
//    appWidgetManager: AppWidgetManager,
//    appWidgetId: Int
//) {
//    val widgetText = loadTitlePref(context, appWidgetId)
//    // Construct the RemoteViews object
//    val views = RemoteViews(context.packageName, R.layout.new_app_widget)
//    views.setTextViewText(R.id.appwidget_text, widgetText)
//
//    // Instruct the widget manager to update the widget
//    appWidgetManager.updateAppWidget(appWidgetId, views)
//}

internal fun updateAppWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int) {
    // 1. Load the customized Origin and Destination the user saved
    val origin = loadOriginPref(context, appWidgetId)
    val dest = loadDestPref(context, appWidgetId)

    // Target date (you can hardcode this or update it later)
    val targetDate = "2027-02-27"

    // 2. Set the initial loading state on the widget
    val views = RemoteViews(context.packageName, R.layout.new_app_widget)
    views.setTextViewText(R.id.tv_route, "$origin -> $dest")
    views.setTextViewText(R.id.tv_date, targetDate)
    views.setTextViewText(R.id.tv_price, "Fetching...")
    appWidgetManager.updateAppWidget(appWidgetId, views)

    // 3. Fetch the live price on a background thread (Network calls crash the main thread)
    Thread {
        try {
            // Construct the exact URL for your Render API
            val urlString = "https://flight-tracker-407r.onrender.com/get_price?origin=$origin&dest=$dest&date=$targetDate"

            // Make the request and parse the JSON string
            val response = URL(urlString).readText()
            val json = JSONObject(response)

            // Extract data
            val price = if (json.has("lowest_price")) json.getString("lowest_price") else "N/A"

            // Update the widget UI again with the final price
            views.setTextViewText(R.id.tv_price, price)
            appWidgetManager.updateAppWidget(appWidgetId, views)

        } catch (e: Exception) {
            // If the server is asleep or phone has no internet, show an error state
            views.setTextViewText(R.id.tv_price, "Error")
            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }.start()
}