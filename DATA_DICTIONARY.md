# CTR Master Dataset - Data Dictionary

## Overview
The CTR Master Dataset contains Commute Trip Reduction survey data for the City of Bellevue from 1993 to 2025. Each row represents a single worksite's data for one survey cycle.

## Column Definitions

### Identification & Basic Info
- **Survey_Cycle** (string): Survey period in format "YYYY/YYYY" (e.g., "2023-2025")
- **Organization_Name** (string): Name of the employer/worksite
- **Location** (category): Geographic location code
  - `DT` = Downtown Bellevue
  - `ODT` = Outside Downtown

### Employee & Survey Metrics
- **Total_Employees** (integer): Total number of employees at the worksite
- **Surveys_Returned** (integer): Number of completed survey responses
- **Response_Rate** (float): Percentage of employees who responded (0.0 to 1.0)

### Drive-Alone Metrics
- **Drive_Alone_Rate** (float): Worksite's drive-alone rate (0.0 to 1.0)
  - Calculated as: (Single-occupancy vehicle trips) / (Total trips)
- **Weekly_Drive_Alone_Trips** (integer): Number of drive-alone trips per week

### Mode Split - Weekly Trip Counts
All trip counts represent weekly totals reported by survey respondents:

- **Weekly_Bus_Trips** (integer): Bus/rapid transit trips
- **Weekly_Train_Trips** (integer): Light rail/commuter rail trips  
- **Weekly_Carpool_Trips** (integer): Carpool trips (2+ people)
- **Weekly_Vanpool_Trips** (integer): Vanpool trips
- **Weekly_Walk_Trips** (integer): Walking trips
- **Weekly_Bike_Trips** (integer): Bicycle trips
- **Weekly_Telework_Days** (integer): Days worked from home
- **Total_Weekly_Trips** (integer): Sum of all trip types

### Vehicle Miles Traveled (VMT)
- **VMT_per_Employee** (float): Average vehicle miles traveled per employee per day
- **Yearly_Total_VMT** (float): Annual total VMT for the worksite
  - Calculated as: VMT_per_Employee × Total_Employees × 250 workdays

### Environmental Impact
- **Yearly_GHG_Metric_Tons** (float): Annual greenhouse gas emissions in metric tons
  - Estimated from VMT using standard emissions factors

## Calculation Notes

### Weighted vs. Unweighted Metrics
The dashboard calculates two types of averages:

1. **Weighted DAR** (Official Metric):
   - Trip/employee-volume weighted
   - Larger employers have proportional influence
   - Used for WSDOT reporting and goal tracking
   - Formula: `SUM(Weekly_Drive_Alone_Trips) / SUM(Total_Weekly_Trips)`

2. **Unweighted DAR** (Worksite Average):
   - Simple average across all worksites
   - Each employer weighted equally
   - Used for program effectiveness analysis
   - Formula: `MEAN(Drive_Alone_Rate)`

### Response Rate
Response rates below 50% may indicate data quality issues. Per CTR guidelines, a minimum 50% response rate is required for compliance.

### Missing Data
- Some early cycles (pre-2007) may not have all fields populated
- VMT data is generally only available from 2007 forward
- Missing values are handled gracefully in dashboard calculations

## Data Quality Standards

Per CTR Data Analysis Guidelines (Updated 3/24/2017):
- Surveys are census-based (not sample-based)
- Expanded Surveys Returned used for weighting calculations
- 2007 protocol change: 1-person motorcycles count as drive-alone
- Minimum 50% response rate required for compliance

## File Format
- **Type**: CSV (Comma-Separated Values)
- **Encoding**: UTF-8
- **Size**: ~2-5 MB (varies by year)
- **Rows**: ~2,500-4,000 (varies by number of worksites and cycles)

## Usage in Dashboard
The dashboard loads this file on startup and caches it for performance. Updates to the CSV require a dashboard reload (TTL: 1 hour) or browser refresh.

## Questions?
Contact: City of Bellevue Transportation Department - CTR Program
