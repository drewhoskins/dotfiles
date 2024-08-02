import argparse
import subprocess

# Example usage:
# python ./bin/create_issues.py -t "My cool feature" -b "more info" --features --dry-run --combo core-plus
# Fake-create issues for Go, Java, Core, and feature repos and prints out the text to put in the PR description to copy into the feature
# python ./bin/create_issues.py -t "My cool feature" -b "more info" --dry-run Python Go .NET CLI
# Fake-create issues for Python, Go, .NET, and CLI repos
# Leave off --dry-run to actually create the issues

SDKS = {
    "Java": "sdk-java",
    "Go": "sdk-go",
    "Python": "sdk-python",
    "Core": "sdk-core",
    "TypeScript": "sdk-typescript",
    "PHP": "sdk-php",
    ".NET": "sdk-dotnet",
    "CLI": "cli",
}

ALL = {"Java", "Go", "Python", "Core", "TypeScript", "PHP", ".NET", "CLI"}
LANGUAGES = {"Java", "Go", "Python", "TypeScript", "PHP", ".NET"}
CORE_PLUS = {"Java", "Go", "Core"}


def create_issue(title, body, label, repo, *, dry_run) -> subprocess.CompletedProcess:
    input = ["gh", "issue", "create", "--title", title, "--body", body]
    if label is not None:
        input.extend(["--label", label])
    input.extend(["-R", f"temporalio/{repo}"])
    if dry_run:
        print("Would run: " + subprocess.list2cmdline(input))
        return subprocess.CompletedProcess(args=input, returncode=0, stdout=b"<dry run>", stderr=b"")
    else:
        print("Running: " +  " ".join(input))
        return subprocess.run(input, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def sdks_set(sdks, combo) -> set[str]:
    if sdks and combo:
        raise ValueError("Cannot both list SDKs and specify a --combo")
    if not sdks and not combo:
        raise ValueError("Must either list SDKs at the end of your commandline or specify a --combo")
    
    if combo == "all":
        return ALL
    elif combo == "languages":
        return LANGUAGES
    elif combo == "core-plus":
        return CORE_PLUS
    else:
        return set(sdks)

def main():
    parser = argparse.ArgumentParser(description="Create GitHub issues for Temporal SDKs")
    parser.add_argument("-f", "--features", required=False, help="Create an issue for the features repo", default=False, action="store_true")
    parser.add_argument("-t", "--title", required=True, help="Title of the issue")
    parser.add_argument("-b", "--body", required=True, help="Body of the issue")
    parser.add_argument("-l", "--label", required=False, help="GitHub label for the issue", default=None)
    parser.add_argument("-c", "--combo", required=False, help="Create an issue for common sets of SDKs", default=None, 
                        choices=["all", "languages", "core-plus"])
    parser.add_argument("--dry-run", required=False, help="Print the commands and output that would be run", default=False, action="store_true")
    parser.add_argument("sdks", nargs="*", help="SDKs to create the issue for")

    args = parser.parse_args()

    if not args.title or not args.body:
        parser.error("Please specify both --title/-t and --body/-b")

    if args.features:
        result = create_issue(args.title, args.body, args.label, "features", dry_run=args.dry_run)
        print(f"\nFeatures repo: {result.stdout.decode().strip()}\n")

    SDKS_lower = {sdk.lower(): SDKS[sdk] for sdk in SDKS.keys()}
    sdks = sdks_set(args.sdks, args.combo)
    to_print = ""
    for sdk in sdks:
        sdk_lower = sdk.lower()
        if sdk_lower not in SDKS_lower:
            parser.error(f"Invalid SDK: {sdk}")
        repo = SDKS_lower[sdk_lower]
        result = create_issue(args.title, args.body, args.label, repo, dry_run=args.dry_run)
        to_print += f"* [ ] {sdk} {result.stdout.decode().strip()}\n"
    print("\nPut this in the feature branch PR description:\n")
    print(to_print)

if __name__ == "__main__":
    main()
