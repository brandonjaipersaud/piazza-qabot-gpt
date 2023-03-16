import pandas as pd

def view_csv(df:pd.DataFrame, args, view_stats=True):
    if args.cols:
        df = df[args.cols]
    print(df.keys())
    if view_stats:
        print('Viewing stats')
        print(df.mean())
        print(df.std())
    
    print(df)