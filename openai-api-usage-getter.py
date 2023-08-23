import argparse
from prettytable import PrettyTable
import os
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
import csv
from collections import defaultdict
import time


def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch OpenAI usage data between two dates.")
    parser.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format.")
    parser.add_argument("-e", "--encoding", type=str, default="%Y-%m-%d", help="Date encoding format.")
    parser.add_argument("-o", "--org", type=str, required=True, help="OpenAI Organization string.")
    parser.add_argument("-c", "--csv", action="store_true", help="Create a CSV file with daily data.")
    parser.add_argument("--rate", type=float, default=2.5, help="Rate limit in seconds for regular requests.")
    parser.add_argument("--rate_limit_wait", type=float, default=10, help="Wait time in seconds when rate limited.")   
    return parser.parse_args()


def validate_date(date_str, encoding):
    try:
        return datetime.strptime(date_str, encoding)
    except ValueError:
        raise ValueError(f"Invalid date format. Expected format: {encoding}")

def validate_environment_variable():
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("Environment variable OPENAI_API_KEY is not defined.")

def make_request(date, org, rate, rate_limit_wait):
    url = f"https://api.openai.com/v1/usage?date={date}"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Openai-Organization": org
    }

    while True: 
        response = requests.get(url, headers=headers)
        if response.status_code == 429: 
            print(f"Rate limit error for date {date}. Waiting for {rate_limit_wait} seconds and increasing regular wait time.")
            rate += 0.5 
            time.sleep(rate_limit_wait)
            continue
        time.sleep(rate) 
        return response.json()['data'], rate 


def process_data(start_date, end_date, data, create_csv=False):
    snapshot_data = defaultdict(lambda: defaultdict(int))
    total_prompt = total_completion = 0

    daily_totals, snapshot_ids = process_daily_data(data)

    for date_str, daily_total in daily_totals.items():
        for snapshot_id in snapshot_ids:
            snapshot_data[snapshot_id]["prompt"] += daily_total[f"{snapshot_id}_prompt"]
            snapshot_data[snapshot_id]["completion"] += daily_total[f"{snapshot_id}_completion"]
            total_prompt += daily_total[f"{snapshot_id}_prompt"]
            total_completion += daily_total[f"{snapshot_id}_completion"]

    if create_csv:
        create_csv_file(daily_totals, snapshot_ids, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    return snapshot_data, total_prompt, total_completion

def process_daily_data(data):
    daily_totals = defaultdict(lambda: defaultdict(int))
    snapshot_ids = set()

    for date_str, daily_data in data.items():
        for entry in daily_data:
            snapshot_id = entry["snapshot_id"]
            daily_totals[date_str][f"{snapshot_id}_prompt"] += entry["n_context_tokens_total"]
            daily_totals[date_str][f"{snapshot_id}_completion"] += entry["n_generated_tokens_total"]
            snapshot_ids.add(snapshot_id)

    return daily_totals, snapshot_ids

def create_csv_file(daily_totals, snapshot_ids, start_date, end_date):
    filename = f"tokens_usage_{start_date}_{end_date}.csv"
    header = ["day"] + [f"{snapshot_id}_prompt" for snapshot_id in snapshot_ids] + \
             [f"{snapshot_id}_completion" for snapshot_id in snapshot_ids] + ["total_prompt", "total_completion"]
    csv_data = [header]

    for date_str, daily_total in daily_totals.items():
        total_prompt = total_completion = 0
        row = [date_str]
        for snapshot_id in snapshot_ids:
            row.append(daily_total[f"{snapshot_id}_prompt"])
            row.append(daily_total[f"{snapshot_id}_completion"])
            total_prompt += daily_total[f"{snapshot_id}_prompt"]
            total_completion += daily_total[f"{snapshot_id}_completion"]
        row.append(total_prompt)
        row.append(total_completion)
        csv_data.append(row)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

def print_table(snapshot_data, total_prompt, total_completion):
    table = PrettyTable()
    table.field_names = ["Snapshot ID", "Prompt Tokens", "Completion Tokens"]
    for snapshot_id, values in snapshot_data.items():
        table.add_row([snapshot_id, values["prompt"], values["completion"]])
    table.add_row(["Total", total_prompt, total_completion])
    print(table)

def main():
    args = parse_arguments()
    validate_environment_variable()
    start_date = validate_date(args.start_date, args.encoding)
    end_date = validate_date(args.end_date, args.encoding)

    data = defaultdict(list)
    date_range = (end_date - start_date).days + 1
    rate = args.rate
    with tqdm(total=date_range) as pbar:
       current_date = start_date
       while current_date <= end_date:
           date_str = current_date.strftime(args.encoding)
           response, rate = make_request(date_str, args.org, rate, args.rate_limit_wait) 
           data[date_str] = response
           current_date += timedelta(days=1)
           pbar.update(1)

    snapshot_data, total_prompt, total_completion = process_data(start_date, end_date, data, args.csv)
    print_table(snapshot_data, total_prompt, total_completion)

if __name__ == "__main__":
    main()
