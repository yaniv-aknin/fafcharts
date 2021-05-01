#!/usr/bin/env python

import argparse
import sys
import io

import pandas as pd
import seaborn as sns
sns.set()

from flask import Flask, render_template, request, current_app
app = Flask(__name__)

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('parquet')
    options = parser.parse_args(argv[1:])
    return options

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/charts')
def charts():
    return {"charts": ["/charts/multi/apm_to_rating"]}

@app.route('/charts/multi/apm_to_rating')
def apm_to_rating():
    #sns.boxplot(x='player1.rating_bucket', y='features.player1.mean_apm.overall', data=current_app.df)
    return ""

if __name__ == '__main__':
    options = parse_arguments(sys.argv)
    df = pd.read_parquet(options.parquet)
    for prefix in ('player1.player.', 'player2.player.'):
        df[prefix + 'faf_rating.before'] = df[prefix + 'trueskill_mean_before'] - 3 * df[prefix + 'trueskill_deviation_before']
    df['player1.rating_bucket'] = pd.cut(df['player1.player.faf_rating.before'], bins=10)
    with app.app_context():
        current_app.df = df
    app.run(debug=True)
