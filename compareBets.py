import pandas as pd
import numpy as np
import csv

def convert_american_to_decimal(american_odds):
    if american_odds > 0:
        decimal_odds = 1 + (american_odds / 100)
    elif american_odds < 0:
        decimal_odds = 1 + (100 / abs(american_odds))
    else:
        decimal_odds = 1
    return round(decimal_odds, 2)

def convert_decimal_to_american(decimal_odds):
    if isinstance(decimal_odds, pd.Series):
        american_odds = decimal_odds.apply(lambda odds: convert_decimal_to_american(odds))
    else:
        if decimal_odds >= 2.0:
            american_odds = round((decimal_odds - 1) * 100)
        else:
            american_odds = round(-100 / (decimal_odds - 1))
    return american_odds

dataUbet = pd.read_csv('ubet_props.csv')
dataPinnacle = pd.read_csv('pinnacle_props.csv')

measure_metric_mapping = {
    'PLAYER TOTAL BASES': 'Total Bases',
    'PITCHER STRIKEOUTS': 'Total Strikeouts',
    'PITCHER OUTS': 'Pitching Outs',
    'PITCHER HITS ALLOWED': 'Hits Allowed',
    'PITCHER RUNS EARNED': 'Earned Runs',
    "PLAYER HOME RUNS": "Home Runs"
}

#Filter dataUbet for rows with desired measure
filtered_dataUbet = dataUbet[dataUbet['Measure'].isin(measure_metric_mapping.keys())]

#Merge on Player Name
merged_df = pd.merge(filtered_dataUbet, dataPinnacle, on = 'Player Name')

#Filter the merged DataFrame based on measure-metric matches
filtered_df = merged_df[
    merged_df.apply(lambda row: row['Measure'] == row['Metric'] if row['Measure'] not in measure_metric_mapping else 
                    measure_metric_mapping[row['Measure']] == row['Metric'], axis=1)  & 
                    (merged_df['Amount'] == merged_df['Amount Ubet'])]



filtered_df['Over Odds Ubet'] = filtered_df['Over Odds Ubet'].apply(convert_american_to_decimal)
filtered_df['Under Odds Ubet'] = filtered_df['Under Odds Ubet'].apply(convert_american_to_decimal)

#Select the desired variables in the final filtered DataFrame
desired_columns = ['Player Name', 'Metric', 'Amount Ubet', 'Over Odds Ubet', 'Under Odds Ubet', 'Amount', 
                   'Over Odds', 'Under Odds', "First Team", "Second Team"]
filtered_df = filtered_df[desired_columns]


filtered_df.drop('Amount', axis=1, inplace=True)

#calculate true probability without dealer's edge
def true_probability(over_odds, under_odds):
    total_prob = 1.0 / over_odds + 1.0/under_odds
    overProb = 1.0 / over_odds / total_prob
    underProb = 1.0 / under_odds / total_prob
    return overProb, underProb

#returns yes if there is positive value on the over, no otherwise. Also returns the value
def over_value(over_odds_Ubet, true_over_odds):
    ubet = 1 / over_odds_Ubet
    val = true_over_odds - ubet
    result = np.where(val > 0, "yes", "no")
    return result, val * 100

def under_value(under_odds_Ubet, true_under_odds):
    ubet = 1 / under_odds_Ubet
    val = true_under_odds - ubet
    result = np.where(val > 0, "yes", "no")
    return result, val * 100

def probability(odds):
    return 1 / odds



filtered_df["Real Over Probability"] = true_probability(filtered_df["Over Odds"], filtered_df["Under Odds"])[0]
filtered_df["Real Under Probability"] = true_probability(filtered_df["Over Odds"], filtered_df["Under Odds"])[1]
filtered_df["Over Bet Indicator"] = over_value(filtered_df["Over Odds Ubet"], filtered_df["Real Over Probability"])[0]
filtered_df["Over Bet Value"] = over_value(filtered_df["Over Odds Ubet"], filtered_df["Real Over Probability"])[1]
filtered_df["Under Bet Indicator"] = under_value(filtered_df["Under Odds Ubet"], filtered_df["Real Under Probability"])[0]
filtered_df["Under Bet Value"] = under_value(filtered_df["Under Odds Ubet"], filtered_df["Real Under Probability"])[1]
filtered_df["Ubet Over %"] = probability(filtered_df["Over Odds Ubet"])
filtered_df["Ubet Under %"] = probability(filtered_df["Under Odds Ubet"])
filtered_df["Ubet Over"] = convert_decimal_to_american(filtered_df["Over Odds Ubet"])
filtered_df["Ubet Under"] = convert_decimal_to_american(filtered_df["Under Odds Ubet"])
filtered_df["Pinnacle Over"] = convert_decimal_to_american(filtered_df["Over Odds"])
filtered_df["Pinnacle Under"] = convert_decimal_to_american(filtered_df["Under Odds"])
filtered_df.drop('Over Odds Ubet', axis=1, inplace=True)
filtered_df.drop('Under Odds Ubet', axis=1, inplace=True)
filtered_df.drop('Over Odds', axis=1, inplace=True)
filtered_df.drop('Under Odds', axis=1, inplace=True)



df = pd.DataFrame(filtered_df)
df = df.astype(str)

placeBetsSimple = filtered_df[(filtered_df["Over Bet Indicator"] == "yes") | (filtered_df["Under Bet Indicator"] == "yes")]

placeBetsSimple.to_csv("bets.csv", index=False, quoting=csv.QUOTE_NONE, encoding='utf-8')
#Print only the positive EV bets
print(placeBetsSimple)

