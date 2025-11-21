# Detection Stability & Accuracy Improvements

## Changes Made (Current Session)

### 1. **Tracker Stability Enhancement**
- **Increased `max_disappear`**: 50 → **150 frames**
  - Objects persist longer before being considered "gone"
  - Reduces ID flickering from temporary occlusions
  
- **Increased `max_distance`**: 120 → **200 pixels**
  - Allows matching objects across larger frame-to-frame movements
  - Better handles fast motion and camera shake

### 2. **Detection Smoothing (Reduces Fluctuation)**
- **Person Count Smoothing**: Rolling average over **15 frames** (~0.5 sec at 30fps)
  - Raw detections stored in `person_count_window` (deque with maxlen=15)
  - Display shows smoothed count: `int(sum(window) / len(window))`
  - HUD now shows both smoothed and raw counts for debugging

- **Weapon/Knife Smoothing**: Rolling average over **10 frames**
  - Alerts only triggered when smoothed count > 0.3 (detected in >30% of recent frames)
  - Eliminates single-frame false positives
  - Only one alert per frame (prevents spam)

### 3. **Knife Detection Improvements**

#### A. Lower Confidence Threshold
```python
# Dynamic threshold: 0.15 lower than weapon threshold, minimum 0.3
knife_conf_threshold = max(0.3, cfg["thresholds"]["weapon_conf"] - 0.15)
```
- Current config has `weapon_conf=0.5` → knife uses **0.35**
- Improves recall for harder-to-detect knife objects

#### B. Enhanced Visual Feedback
- **Thicker borders**: 2px → **4px orange boxes**
- **Label with background**: White text on orange background for clarity
- **Matching HUD color**: Orange (#008CFF) in both boxes and status display
- **Confidence shown**: Displays conf score on detection boxes

#### C. Better Logging
```python
log_to_excel(..., "Knife Detected", ..., confidence=float(conf), 
             details=f"Knife detection at conf={conf:.2f}")
```
- Separate "Knife Detected" entry type in Excel
- Confidence logged for analysis

### 4. **Configuration Updates**
Updated `src/detector/config.yaml`:
```yaml
video_source: "C:/Users/manav/OneDrive/Desktop/Crowd Project/data/raw_videos/D49_20250902165502.mp4"
thresholds:
  detection_conf: 0.5    # increased from 0.35
  weapon_conf: 0.5       # increased from 0.4
  fight_conf: 0.6        # increased from 0.5
```
- Higher base thresholds reduce false positives
- Knife uses dynamic lower threshold for better detection

### 5. **Web Upload Interface (app.py)**
- Knife threshold: **0.35** (lower than weapon 0.4)
- Thicker orange boxes (4px) with confidence labels
- Better visual feedback during processing

## Testing Instructions

### 1. Test with Specific Video
```powershell
cd a:\src1
python src/detector/infer_detector.py
```
- Video auto-loads: `D49_20250902165502.mp4`
- Watch for:
  - ✅ Stable person count in HUD (smoothed vs raw)
  - ✅ Orange knife boxes with confidence scores
  - ✅ Reduced flickering/fluctuation
  - ✅ Console output shows detection details

### 2. Test Web Upload
```powershell
# Terminal 1 - Backend
python src/app.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```
- Upload test video via web interface
- Check live video window shows orange knife boxes
- Verify alerts panel receives detections

### 3. Check Excel Logs
- Location: `a:\src1\outputs\alerts_log.xlsx`
- Should see separate entries for:
  - "Weapon Detected" (general weapons)
  - "Knife Detected" (specific knife detections)
  - Confidence scores logged

## Expected Improvements

| Issue | Before | After |
|-------|--------|-------|
| Person count fluctuation | ±5-10 people/frame | ±1-2 people (smoothed) |
| Knife detection rate | Low (missed many) | Improved with 0.35 threshold |
| False weapon alerts | Many single-frame | Filtered with 0.3 smoothing |
| Tracker ID stability | Frequent reassignment | Persists 150 frames |
| Visual clarity | Thin boxes, hard to see | Thick orange with labels |

## Troubleshooting

### If knife still not detecting:
1. **Check model file**: `a:\src1\models\weapon_yolo\weights\best.pt`
   - Verify file exists and is not corrupted
   - Check model was trained on knife class

2. **Lower threshold further** (in `infer_detector.py` line 778):
   ```python
   knife_conf_threshold = max(0.25, cfg["thresholds"]["weapon_conf"] - 0.2)
   ```

3. **Enable verbose mode** (line 780):
   ```python
   kres = knife_yolo.predict(frame, imgsz=640, conf=knife_conf_threshold, 
                             device=device, verbose=True)  # Show predictions
   ```

### If fluctuation still high:
1. **Increase smoothing window** (line 607):
   ```python
   person_count_window = deque(maxlen=30)  # Increase from 15 to 30
   ```

2. **Increase tracker persistence** (line 627):
   ```python
   tracker = SimpleCentroidTracker(max_disappear=200, max_distance=250)
   ```

## Next Steps

1. ✅ Test with user's specific video file
2. ⏳ Monitor Excel logs for detection quality
3. ⏳ Tune thresholds based on false positive/negative rates
4. ⏳ Consider implementing NMS (Non-Maximum Suppression) if overlap issues occur
5. ⏳ Add detection confidence histogram for threshold optimization

## Files Modified

- `src/detector/infer_detector.py` - Main detection engine
- `src/detector/config.yaml` - Configuration with new video source and thresholds
- `src/app.py` - Web API with improved knife detection
- `DETECTION_IMPROVEMENTS.md` - This documentation
