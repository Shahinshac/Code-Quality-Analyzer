import argparse
import json
import os
from .parser import extract_features_from_file
from .detectors import RuleBasedDetector
from .ml_classifier import train_model, load_dataset, predict_code_quality, compute_quality_score
from .suggestion_engine import suggestions_for_smells, autofix_code


def train_command(args):
    df = load_dataset(args.dataset)
    os.makedirs(os.path.dirname(args.model_out), exist_ok=True)
    acc = train_model(df, args.model_out)
    print(f'Trained model saved at {args.model_out} with test accuracy {acc:.3f}')


def analyze_command(args):
    with open(args.file, 'r', encoding='utf8') as fh:
        src = fh.read()
    detector = RuleBasedDetector()
    if args.file.endswith('.java'):
        smells = detector.detect_java_issues(src)
    else:
        smells = detector.detect_all(src)
    suggestions = suggestions_for_smells(smells)
    result = {
        'file': args.file,
        'smells': [s.to_dict() for s in smells],
        'suggestions': suggestions,
    }
    if args.model:
        try:
            label, prob = predict_code_quality(src, args.model)
            result['ml_classification'] = {'label': label, 'confidence': prob}
            result['quality_score'] = compute_quality_score(label, prob, smells)
        except Exception as e:
            print('Error using ML model:', e)
    else:
        result['quality_score'] = compute_quality_score(None, None, smells)
    print(json.dumps(result, indent=2))


def autofix_command(args):
    with open(args.file, 'r', encoding='utf8') as fh:
        src = fh.read()
    fixed = autofix_code(src)
    if args.inplace:
        with open(args.file, 'w', encoding='utf8') as fh:
            fh.write(fixed)
        print(f'File fixed in-place: {args.file}')
    else:
        out = args.out or (args.file + '.fixed')
        with open(out, 'w', encoding='utf8') as fh:
            fh.write(fixed)
        print(f'Fixed file written to: {out}')


def serve_command(args):
    # run the lightweight Flask app
    from .webapp import create_app
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


def main():
    parser = argparse.ArgumentParser(prog='code-quality-analyzer')
    sub = parser.add_subparsers(dest='command')

    ptrain = sub.add_parser('train')
    ptrain.add_argument('--dataset', required=True)
    ptrain.add_argument('--model-out', required=True, dest='model_out')
    ptrain.set_defaults(func=train_command)

    panalyze = sub.add_parser('analyze')
    panalyze.add_argument('--file', required=True)
    panalyze.add_argument('--model', required=False)
    panalyze.set_defaults(func=analyze_command)

    pserve = sub.add_parser('serve')
    pserve.add_argument('--host', default='127.0.0.1')
    pserve.add_argument('--port', type=int, default=5000)
    pserve.add_argument('--debug', action='store_true')
    pserve.set_defaults(func=serve_command)

    pfix = sub.add_parser('autofix')
    pfix.add_argument('--file', required=True)
    pfix.add_argument('--inplace', action='store_true')
    pfix.add_argument('--out', required=False)
    pfix.set_defaults(func=autofix_command)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
