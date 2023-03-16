import os
import argparse


import pandas as pd


from csv_manipulation import generate_embeddings, generate_timestamps, csv_utils
from metrics.compute_metrics import compute_metrics_on_csv, compute_aggregate_statistics
from csv_viewing.view_csv import view_csv
from experiments import run_experiments

def parse_args():
    parser = argparse.ArgumentParser()

    # top level args
    parser.add_argument('--load', type=str, help="path to csv to augment", required=False)
    parser.add_argument('--save', type=str,  help="optional save path", required=False)
    parser.add_argument('--no-save', help="don't save the manipulated csv", required=False, action='store_true')
    parser.add_argument('--overwrite', help="overwrite df", required=False, action='store_true')

    parser.add_argument('--size', type=int,  help="truncate the csv")


    subparsers = parser.add_subparsers(help='sub-command help')

    # running experiments such as classification, answering and generating *model answer* logprobs
    # relies on hyperparameters.py in experiments/ to configure experiment parameters
    parser_exp = subparsers.add_parser('experiments', help='view help')
    parser_exp.add_argument('-re','--run_experiment', help='run experiment help', action='store_true')

    # csv viewing
    parser_view = subparsers.add_parser('view', help='view help')
    parser_view.add_argument('view', help='view help', action='store_true')
    parser_view.add_argument('-c', '--cols', help='view cols', nargs='+')



    # csv augmentation
    parser_aug = subparsers.add_parser('augment', help='augment help')
    parser_aug.add_argument('augment', help='augment help', action='store_true')
    parser_aug.add_argument('-all',  help="do all augmentation steps", action='store_true')
    
    
    subparsers_aug = parser_aug.add_subparsers(help='sub-command help')

    parser_general = subparsers_aug.add_parser('general', help='general help')
    parser_general.add_argument('general', help='general help', action='store_true')
    parser_general.add_argument('-s', '--split', help='split answer(s) column', action='store_true')
    parser_general.add_argument('-ct', '--compare-timestamps', help='compare timestamps between instructor answer and model answer', action='store_true')
    parser_general.add_argument('-awc', '--augment_with_columns', help='add columns from df2 into df1', nargs='+')
    parser_general.add_argument('-mc', '--merge_columns', help='redundant since df1.left_join(df2) is performed', nargs='+', default=['question_id'])
    # simple df ops
    parser_general.add_argument('-sc', '--select_columns', help='', nargs='+')
    parser_general.add_argument('-mtc', '--merge_title_and_content', help='', action='store_true')




    # embed columns
    parser_emb = subparsers_aug.add_parser('embed', help='augment help')
    parser_emb.add_argument('embed', help='embed help', action='store_true')
    parser_emb.add_argument('--api', type=str,  help="api to produce embeddings", default='cohere', choices=['cohere', 'openai', 'both'])
    parser_emb.add_argument('-i',  help="create instructor answer embeddings", action='store_true')
    parser_emb.add_argument('-m',  help="create model answer embeddings", action='store_true')
    parser_emb.add_argument('--openai-api-key-path', type=str, help="", default="./sensitive/openai_api_key.txt")
    parser_emb.add_argument('--cohere-api-key-path', type=str, help="", default="./sensitive/cohere_api_key.txt")
    parser_emb.add_argument('-s', '--split',  help="split answer(s) column. redundant.", action='store_true')
    parser_emb.add_argument('--size', type=int, help="how many samples to compute embeddings for. Set to -1 to do full dataframe. redundant.", default=-1)
   

    # parser_emb.add_argument('-ge', '--generate-embeddings',  help="", action='store_true')
    
    # add timestamps
    parser_time = subparsers_aug.add_parser('timestamp', help='augment help')
    parser_time.add_argument('timestamp', help='augment help', action='store_true')
    parser_time.add_argument('-ma', '--model-answer',  help="", action='store_true')
    parser_time.add_argument('-ha', '--human-answer',  help="", action='store_true')
    parser_time.add_argument('-clp', '--course-log-path',  help="")
    parser_time.add_argument('-cf', '--piazza-creds-file',  help="", required=True)


    # compute metrics
    parser_cm = subparsers.add_parser('metrics', help='augment help')
    parser_cm.add_argument('metrics', help='augment help', action='store_true')
    parser_cm.add_argument('-m', '--metric',  help="", choices=['all', 'rouge', 'embedding_distance', 'perplexity'], default='all')
    parser_cm.add_argument('-agg', '--aggregate_statistics',  help="", action='store_true')
    parser_cm.add_argument('-gb', '--group-by',  help="", default='classification')

    # specify which metrics to compute. by default compute all?


    args = parser.parse_args()

    
    return args, parser


def main():
    """
    csv augmentation
        generate_embeddings
        generate_timestamps 
        logprobs parsing
            - generation of logprobs must be done at time of question answering
            - parsing handled in perplexity via. json.loads()

    compute metrics 

    aggregate statistics *

    classification/question answering -- run experiments *
    scrape piazza posts *

    """
    args:argparse.Namespace = None
    parser:argparse.ArgumentParser = None
    args, parser = parse_args()

    print(args)


    if 'run_experiment' in args:
        run_experiments.main()
        return


    if not args.load:
        print("Please specify --load path!")
        return

    # load df 
    print(f'Loading from {args.load}')

    df = None
    if args.load:
        df = pd.read_csv(args.load)

    if args.size:
        df = df.head(args.size)
    
    filename = os.path.basename(args.load).split('.')[0]
    dirname = os.path.dirname(args.load)

    file_suffix = ""


    if 'view' in args:
        view_csv(df, args)
        exit(0)

    if 'general' in args:
        file_suffix = "_general_aug"
        print('General augmentation')
        if args.split:
            file_suffix += '_split'
            print('Splitting')
            df = csv_utils.split_answers_csv(df)

        if args.compare_timestamps:
            file_suffix += '_timestamp'
            print('Comparing timestamps')
            df = csv_utils.compare_timestamps_csv(df)


        if args.augment_with_columns:
            file_suffix += '_aug_col'
            print('Augment with column')
            augment_df = pd.read_csv(args.augment_with_columns[0])
            augment_columns = list(args.augment_with_columns[1:])
            merge_columns = args.merge_columns
    
            df = csv_utils.augment_with_columns(df, augment_df, augment_columns, merge_columns=merge_columns)

        if args.select_columns:
            file_suffix += '_select_col'
            df = csv_utils.select_columns_df(df, args.select_columns)

        if args.merge_title_and_content:
            file_suffix += '_merge_tc'
            df = csv_utils.merge_title_and_content_csv(df)

    if 'embed' in args:
        file_suffix = "_embeddings"

        print('Augmenting with embeddings')
        df = generate_embeddings.parse_args(args, df)


    if 'timestamp' in args:
        file_suffix = "_timestamp"
        print('Augmenting with timestamp')
        df = generate_timestamps.parse_args(args, df)
 
        
    if 'metrics' in args:
        file_suffix = "_metrics"

        print('Augmenting with metrics')
        df = compute_metrics_on_csv(args, df)

        if args.aggregate_statistics:
            mean, std = compute_aggregate_statistics(df,groupby_column=args.group_by)
            print('Mean')
            print(mean)
            print('Std')
            print(std)
            if not args.no_save:
                print(f'Saving to {dirname}/{filename}_metrics_mean.csv')
                print(f'Saving to {dirname}/{filename}_metrics_std.csv')
                mean.to_csv(f'{dirname}/{filename}_metrics_mean.csv', index=False)
                std.to_csv(f'{dirname}/{filename}_metrics_std.csv', index=False)

       

    # persist changes

    if args.no_save:
        print('Not saving csv')
        print(df)

    if args.overwrite:
        print(f'OVERWRITING to: {dirname}/{filename}.csv')
        df.to_csv(f'{dirname}/{filename}.csv', index=False)
    else:
        # custom save location specified
        if args.save and not args.no_save:   
            print(f'Saving to: {args.save}')
            df.to_csv(args.save, index=False)

        # create new file save location based on augmentations performed
        if not args.save and not args.no_save:
            print(f'Saving to: {dirname}/{filename}{file_suffix}.csv')
            df.to_csv(f'{dirname}/{filename}{file_suffix}.csv', index=False)


    

if __name__ == "__main__":
    main()