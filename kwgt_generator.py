import json
import zipfile

GITHUB_USERNAME = "ahmednaeem786"
GIST_ID = "GIST ID HERE"
GIST_URL = f"https://gist.githubusercontent.com/{GITHUB_USERNAME}/{GIST_ID}/raw/flight_price.json"

preset = {
    "preset_info": {
        "version": 11,
        "title": "Batik Air Flight Tracker",
        "description": "KUL <-> KHI Live Price Widget",
        "width": 720,
        "height": 280,
        "xscreens": 1,
        "yscreens": 1,
        "features": "",
    },
    "preset_root": {
        "internal_type": "RootLayerModule",
        "internal_toggles": {},
        "globals": {"url": {"type": "TEXT", "title": "Gist URL", "value": GIST_URL}},
        "internal_events": [
            {"action": "KUSTOM_ACTION", "kustom_action": "TEXT_UPDATE"}
        ],
        "viewgroup_items": [
            {
                "internal_type": "OverlapLayerModule",
                "internal_title": "Boarding Pass Card",
                "position_anchor": "CENTER",
                "viewgroup_items": [
                    # 1. Main Yellow Rounded Card
                    {
                        "internal_type": "ShapeModule",
                        "internal_title": "Card Background",
                        "shape_type": "RECT",
                        "shape_width": 680,
                        "shape_height": 240,
                        "shape_corners": 44,
                        "paint_color": "#FFFFF248",
                        "position_anchor": "CENTER",
                    },
                    # 2. Airline Brand (Top Left)
                    {
                        "internal_type": "TextModule",
                        "internal_title": "Airline",
                        "text_expression": "Batik Air",
                        "text_size": 26,
                        "paint_color": "#FF111111",
                        "position_anchor": "TOPLEFT",
                        "position_padding_left": 36,
                        "position_padding_top": 24,
                    },
                    # 3. Last Updated (Top Right)
                    {
                        "internal_type": "TextModule",
                        "internal_title": "Updated",
                        "text_expression": f'Updated $wg("{GIST_URL}", json, .updated_at)$',
                        "text_size": 20,
                        "paint_color": "#FF333333",
                        "position_anchor": "TOPRIGHT",
                        "position_padding_right": 36,
                        "position_padding_top": 28,
                    },
                    # 4. Origin Code (Middle Left)
                    {
                        "internal_type": "TextModule",
                        "internal_title": "Origin",
                        "text_expression": "KUL",
                        "text_size": 68,
                        "paint_color": "#FF000000",
                        "position_anchor": "CENTERLEFT",
                        "position_padding_left": 36,
                        "position_padding_bottom": 12,
                    },
                    # 5. Flight Path & Plane (Center)
                    {
                        "internal_type": "TextModule",
                        "internal_title": "Flight Path",
                        "text_expression": "• ━━ ✈ - - - - •",
                        "text_size": 28,
                        "paint_color": "#FF222222",
                        "position_anchor": "CENTER",
                        "position_padding_bottom": 12,
                    },
                    # 6. Destination Code (Middle Right)
                    {
                        "internal_type": "TextModule",
                        "internal_title": "Destination",
                        "text_expression": "KHI",
                        "text_size": 68,
                        "paint_color": "#FF000000",
                        "position_anchor": "CENTERRIGHT",
                        "position_padding_right": 36,
                        "position_padding_bottom": 12,
                    },
                    # 7. Outbound Price (Bottom Left)
                    {
                        "internal_type": "TextModule",
                        "internal_title": "Outbound Price",
                        "text_expression": f'27 Feb: $wg("{GIST_URL}", json, .outbound.lowest_price)$',
                        "text_size": 24,
                        "paint_color": "#FF111111",
                        "position_anchor": "BOTTOMLEFT",
                        "position_padding_left": 36,
                        "position_padding_bottom": 24,
                    },
                    # 8. Inbound Price (Bottom Right)
                    {
                        "internal_type": "TextModule",
                        "internal_title": "Inbound Price",
                        "text_expression": f'13 Mar: $wg("{GIST_URL}", json, .inbound.lowest_price)$',
                        "text_size": 24,
                        "paint_color": "#FF111111",
                        "position_anchor": "BOTTOMRIGHT",
                        "position_padding_right": 36,
                        "position_padding_bottom": 24,
                    },
                ],
            }
        ],
    },
}

output_file = "batik_flight_tracker.kwgt"
with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("preset.json", json.dumps(preset, indent=2))

print(f"Created {output_file} successfully.")
