# Power BI Real-Time Integration Guide

## 📊 Setup Instructions for Auto-Refresh Power BI Dashboard

### Step 1: Configure Power BI Data Source

1. **Open your Power BI file**: `A:\Manav Mule power bi.pbix`

2. **Add Excel Data Source**:
   - Click "Get Data" → "Excel"
   - Browse to: `A:\src1\detection_alerts.xlsx`
   - Select the "Detection Alerts" sheet
   - Click "Load"

3. **Enable Automatic Refresh**:
   - Go to: **File** → **Options and settings** → **Options**
   - Select: **Data Load** → **Background Data**
   - Check: ✅ "Allow data preview to download in the background"
   - Check: ✅ "Enable Data Preview"

4. **Set Refresh Interval** (Power BI Desktop):
   - Go to: **File** → **Options and settings** → **Data source settings**
   - Select your Excel file
   - Click "Edit Permissions"
   - Set refresh schedule if publishing to Power BI Service

### Step 2: Configure Auto-Refresh in Power BI Desktop

Since Power BI Desktop doesn't have automatic refresh while the file is open, you have two options:

#### Option A: Manual Refresh (Simple)
- Click the **"Refresh"** button in Power BI whenever you want to see new data
- Or press: `Ctrl + R`

#### Option B: Auto-Refresh with Power Query (Advanced)
1. Go to: **Home** → **Transform Data** → **Advanced Editor**
2. Add this code to enable periodic refresh:
```m
let
    Source = Excel.Workbook(File.Contents("A:\src1\detection_alerts.xlsx"), null, true),
    Sheet = Source{[Item="Detection Alerts",Kind="Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true])
in
    #"Promoted Headers"
```

### Step 3: Publish to Power BI Service (For True Auto-Refresh)

1. **Publish Dashboard**:
   - Click: **File** → **Publish** → **Publish to Power BI**
   - Sign in with your Power BI account
   - Select workspace

2. **Configure Scheduled Refresh**:
   - Go to: [PowerBI.com](https://app.powerbi.com)
   - Find your dataset → **Settings**
   - Under "Scheduled refresh":
     - Enable: ✅ "Keep your data up to date"
     - Set frequency: **Every 15 minutes** (minimum)
     - Set time zone
     - Click "Apply"

3. **Setup Gateway** (if needed):
   - Download and install: [Power BI Gateway](https://powerbi.microsoft.com/en-us/gateway/)
   - Configure gateway to access local Excel file
   - Add data source path: `A:\src1\detection_alerts.xlsx`

### Step 4: Using the Analytics Button in Dashboard

1. **Click "Analytics" Button** in the top-right corner of CrowdSense dashboard
2. Power BI file will automatically open with latest data
3. Click "Refresh" in Power BI to load newest detections

### Recommended Power BI Visualizations

Create these visuals in your Power BI dashboard:

#### 1. **Detection Summary Card**
- Visual: Card
- Field: Count of detections
- Title: "Total Alerts Today"

#### 2. **Detection Timeline**
- Visual: Line Chart
- X-axis: Date + Time
- Y-axis: Count
- Legend: Detection Type
- Colors: Red (Weapon), Orange (Fight), Yellow (Crowd)

#### 3. **Detection Type Breakdown**
- Visual: Donut Chart
- Values: Count by Detection Type
- Colors: Match your alert colors

#### 4. **Camera Activity**
- Visual: Bar Chart
- Axis: Camera ID
- Values: Count of detections

#### 5. **Confidence Scores**
- Visual: Gauge
- Values: Average Confidence
- Min: 0%, Max: 100%

#### 6. **Recent Alerts Table**
- Visual: Table
- Columns: Date, Time, Camera, Detection Type, Confidence
- Filters: Last 24 hours

#### 7. **Hourly Heatmap**
- Visual: Matrix
- Rows: Hour of Day
- Columns: Detection Type
- Values: Count

### Excel Data Refresh Automation

The Excel file (`detection_alerts.xlsx`) is automatically updated when:
- ✅ Weapon detected → New row added with screenshot
- ✅ Fight detected (after 3 sec) → New row added with screenshot
- ✅ Crowd detected (5+ people for 60 sec) → New row added with screenshot

### Power BI Auto-Refresh Options

| Method | Refresh Speed | Complexity | Cost |
|--------|---------------|------------|------|
| Manual Refresh | On-demand | Easy | Free |
| Power BI Service (Scheduled) | 15 min intervals | Medium | Free/Pro |
| Power BI Service (Streaming) | Real-time | High | Premium |
| Power BI Gateway | 15 min intervals | Medium | Free |

### Troubleshooting

#### Power BI doesn't open when clicking "Analytics":
- Check file path: `A:\Manav Mule power bi.pbix`
- Ensure Power BI Desktop is installed
- Check backend console for error messages

#### Data not updating in Power BI:
1. Click "Refresh" button in Power BI
2. Check if Excel file is being updated: `A:\src1\detection_alerts.xlsx`
3. Verify data source path in Power BI settings
4. Close and reopen Excel file if it's locked

#### Excel file locked error:
- Close Excel if it's open
- Ensure no other programs are accessing the file
- Check file permissions

### Files Location

- **Excel File**: `A:\src1\detection_alerts.xlsx`
- **Screenshots**: `A:\src1\screenshots\`
- **Power BI**: `A:\Manav Mule power bi.pbix`
- **JSON Logs**: `A:\src1\detections\`

### Quick Setup Checklist

- [x] Excel data source added to Power BI
- [x] Auto-refresh enabled in Power BI settings
- [x] Analytics button added to dashboard
- [x] Backend API endpoint created
- [x] Excel file path configured
- [ ] Power BI visualizations created
- [ ] (Optional) Published to Power BI Service
- [ ] (Optional) Gateway configured for auto-refresh

---

## 🚀 Quick Start

1. Open Power BI Desktop
2. Load Excel file: `A:\src1\detection_alerts.xlsx`
3. Create visualizations using the data
4. Save Power BI file
5. Click "Analytics" button in CrowdSense dashboard
6. Power BI opens automatically with latest data
7. Click "Refresh" to see newest detections

## 📈 Real-Time Workflow

```
Detection Occurs → Excel Updated → Click "Analytics" → Power BI Opens → Click Refresh → See Latest Data
```

For true real-time (< 1 second refresh), consider upgrading to Power BI Premium with streaming datasets.
