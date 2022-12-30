#!/usr/bin/env python

import subprocess
import sys
from tempfile import NamedTemporaryFile

import yamllint.config
import yamllint.linter
from rich.prompt import Prompt

yaml_config = yamllint.config.YamlLintConfig("extends: default")

EDITOR = "/usr/bin/vim"


def edit(old_data):

    new_data = None

    term_in = sys.stdin
    term_out = sys.stdout

    if not term_in.isatty():
        term_in = open(os.ctermid())
    if not term_out.isatty():
        term_out = open(os.ctermid(), "w")

    with NamedTemporaryFile() as tf:
        tf.write(bytes(old_data, "utf-8"))
        tf.flush()

        ok = subprocess.check_call([EDITOR, tf.name], stdin=term_in, stdout=term_out)
        
        tf.seek(0)
        new_data = tf.read().decode("utf-8")
        tf.close()

    return new_data


def rengu_lint(data):
    return
    yield


def editor_loop(data):

    orig_data = data
    new_data = edit(data)

    if new_data == orig_data:
        ok = Prompt.ask(
            "No changes to data. Proceed? (y/n)", choices=["y", "n"], default="y"
        )

        if ok == "n":
            return editor_loop(data)

    if yaml_problems := "\n".join(
        [
            f"# {y.line} {y.rule} {y.desc}"
            for y in yamllint.linter.run(new_data, yaml_config)
        ]
    ):
        print("YAML errors")
        print(yaml_problems)

        ok = Prompt.ask(
            "Proceed (y)? Fix YAML errors in new (n)? Or revert to original and edit (o)?",
            choices=["y", "n", "o"],
            default="y",
        )

        match ok:

            case "n":
                data = yaml_problems + "\n" + new_data
                return editor_loop(data)

            case "o":
                return editor_loop(orig_data)

    elif rengu_problems := "\n".join([f"# {error}" for error in rengu_lint(data)]):
        print("Rengu errors")
        print(rengu_problems)

        ok = Prompt.ask(
            "Proceed (y)? Fix Rengu errors in new (n)? Or revert to original and edit (o)?",
            choices=["y", "n", "o"],
            default="y",
        )

        match ok:

            case "n":
                data = rengu_problems + "\n" + new_data
                return editor_loop(data)

            case "o":
                return editor_loop(orig_data)

    return new_data


def main():

    for file in sys.argv[1:]:
        print(f"editing {file}")

        with open(file, "r") as fd:
            data = fd.read()
            data = editor_loop(data)

        with open(file, "w") as fd:
            fd.write(data)


if __name__ == "__main__":
    main()
