### **2️⃣ validate_module.md**

```markdown
# Validation Module

**File:** `optimizer/validate_schedule.py`  
**Purpose:** Validates the optimized schedule for correctness.

## Checks Performed
1. Departures happen after arrivals
2. No overlapping conflicts
3. Conflicts resolved properly
4. No negative delays
5. Train priorities are respected

## Output
- `reports/validation_report.txt`

## Usage
```bash
python optimizer/validate_schedule.py

---
