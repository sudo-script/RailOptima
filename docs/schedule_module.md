# Schedule Optimizer Module

**File:** `optimizer/optimizer_schedule.py`  
**Purpose:** Optimizes train departure times, resolves conflicts, and outputs results.

## Input
- `schedule.json` (JSON file with a `schedule` key containing train info)

## Process
1. Load schedule data into a DataFrame
2. Convert times into datetime objects
3. Sort trains by scheduled departure
4. Adjust `optimized_departure` to avoid overlap
5. Calculate delays in minutes
6. Save outputs

## Output
- `schedule_output.json`  
- `schedule_output.csv`  
- Includes resolved conflicts count and delay information

## Usage
```bash
python optimizer/optimizer_schedule.py

---






