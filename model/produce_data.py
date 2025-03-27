#kam, luo, mcandrew
# produce_data.py

def produce_data():
    import pandas as pd
    from epiweeks import Week
    
    # Set the working directory for hospital admission 
    file_path_hosp = "https://raw.githubusercontent.com/cdcepi/FluSight-forecast-hub/refs/heads/main/target-data/target-hospital-admissions.csv"

    # Set the working directory for ilidata 
    file_path_ili = "https://raw.githubusercontent.com/computationalUncertaintyLab/iliplus/refs/heads/main/ili_plus.csv"

    # Read the CSV file for ili 
    ilidata = pd.read_csv(file_path_ili)

    # Cleaning offseason out of "season" column 
    ilidata = ilidata[ilidata["season"] != "offseason"]

    # Removing the epiweek column 
    ilidata = ilidata.drop(columns=['epiweek'])

    # Function for season week instead of epiweek 
    def ili_season_week(row):
        if row.week <= 20:
            start_week = Week(row.year - 1, 40)
        else:
            start_week = Week(row.year, 40)

        num_weeks = 0
        row_week = Week(row.year, row.week)
        while start_week < row_week:
            start_week = start_week + 1
            num_weeks += 1
        return num_weeks

    ilidata['season_week'] = ilidata.apply(ili_season_week, axis=1)
    ilidata = ilidata.sort_values(by=['season', 'season_week'])

    # Add start and end date
    def add_start_and_end_date(row):
        ew = Week(row.year, row.week)
        start_date = ew.startdate()
        end_date = ew.enddate()
        row["start_date"] = start_date.strftime("%Y-%m-%d")
        row["end_date"] = end_date.strftime("%Y-%m-%d")
        return row

    ilidata = ilidata.apply(add_start_and_end_date, axis=1)

    hospdata = pd.read_csv(file_path_hosp)
    
    ili_plus_hosp = ilidata.merge(hospdata, left_on=['location', 'location_name', 'end_date'], right_on=['location', 'location_name', 'date'], how='left')
    ili_plus_hosp = ili_plus_hosp.rename(columns={"value": "hospitalizations"})
    
    ili_plus_hosp = ili_plus_hosp.melt(id_vars=["location", "location_name", "season", "year", "week", "season_week"], value_vars=["ili_plus", "ili_plus_a", "ili_plus_b", "hospitalizations"], value_name="y")

    return ili_plus_hosp.to_csv("./ili_plus_hosp.csv", index=False)

if __name__ == "__main__":

    produce_data()
    

