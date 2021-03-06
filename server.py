#!/usr/bin/env python

import argparse
import sys
import io
import functools

import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib.axes import Axes
import seaborn as sns
sns.set()

from flask import Flask, render_template, request, current_app, send_file

class PlotFlask(Flask):
    def plot(self, *route_args, **route_kwargs):
        "A route()-like decorator for matplotlib plots"
        def decorator(func):
            @functools.wraps(func)
            def inner(*view_args, **view_kwargs):
                ax = func(*view_args, **view_kwargs)
                if not isinstance(ax, Axes):
                    raise ValueError("expected a matplotlib Axes instance")
                image = io.BytesIO()
                ax.figure.set_size_inches(10, 5)
                ax.figure.savefig(image)
                image.seek(0)
                if current_app.debug:
                    return image.getvalue(), 200, {'Content-Type': 'img/png'}
                return send_file(image, mimetype='img/png')
            return self.route(*route_args, **route_kwargs)(inner)
        return decorator

app = PlotFlask(__name__)

def load_df(parquet_path, app):
    df = pd.read_parquet(parquet_path)
    df['player1.rating_bucket'] = pd.cut(df['player1.player.faf_rating.before'], bins=5)
    with app.app_context():
        current_app.df = df

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
    return {"charts": [
        "/charts/multi/apm_to_rating",
        "/charts/multi/area_after_5m",
        ]
    }

@app.plot('/charts/multi/apm_to_rating')
def apm_to_rating():
    return sns.boxplot(x='player1.rating_bucket', y='features.player1.mean_apm.overall', data=current_app.df)

@app.plot('/charts/multi/area_after_5m')
def apm_over_time():
    return sns.boxplot(x='player1.rating_bucket', y='features.player1.command_area.first.5m', data=current_app.df)

if __name__ == '__main__':
    options = parse_arguments(sys.argv)
    load_df(options.parquet, app)
    app.run(debug=True)
