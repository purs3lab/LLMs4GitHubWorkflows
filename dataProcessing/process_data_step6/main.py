import argus_components
import argparse

def main(yaml_file, repo_lang, dependencies):
    stats = argus_components.Stats(yaml_file, repo_lang, dependencies)
    stats.translate_nl()
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml_file", type=str, required=True, help="The yaml file to parse.")
    parser.add_argument("--repo_lang", required=True, type=str, help="The major language of repository.")
    parser.add_argument("--dependencies", required=True, type=str, help="The dependencies of yaml file.")
    args = parser.parse_args()
    main(args.yaml_file, args.repo_lang, args.dependencies)
