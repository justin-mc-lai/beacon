# Beacon Keep / Discard Policy（v1.1.5）

## Hard Gate
以下任一失败即 discard：
- verify-materials
- verify-delivery
- gate/report/status 被破坏
- machine artifacts 丢失
- human surface 被重新污染

## Soft Score
- Human Cognitive Load Score
- Drift Detection Score
- Confidence Calibration Score
- Doctor Repair Success Score
- Cost / Complexity Score
