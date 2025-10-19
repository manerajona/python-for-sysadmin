#!/usr/bin/env python3
"""
stdio.py

Demonstrates common ways to handle stdin, stdout and stderr in Python:
 - reading from stdin (streaming and full read)
 - writing to stdout (print and sys.stdout.write)
 - writing to stderr (print(..., file=sys.stderr) and sys.stderr.write)
 - capturing/redirecting stdout and stderr for tests using contextlib.redirect_*
 - running subprocesses and capturing their stdout/stderr with subprocess.run

Usage examples:
  echo "hello world" | python stdio.py
  python stdio.py --uppercase < input.txt
  python stdio.py --demo-subprocess
"""

import sys
import argparse
import io
import subprocess
from contextlib import redirect_stdout, redirect_stderr


def process_stream_uppercase(in_stream, out_stream, err_stream):
    """
    Read lines from in_stream, write uppercased lines to out_stream.
    Any empty lines will produce a warning to err_stream.
    """
    for lineno, raw in enumerate(in_stream, start=1):
        line = raw.rstrip("\n")
        if line == "":
            print(f"warning: empty line {lineno}", file=err_stream)
            continue
        out_stream.write(line.upper() + "\n")
        out_stream.flush()


def demo_capturing():
    """Show capturing stdout / stderr into in-memory buffers (useful for tests)."""
    fake_out = io.StringIO()
    fake_err = io.StringIO()

    # We'll call the same processing function but capture its outputs.
    sample_input = io.StringIO("first line\n\nsecond line\n")
    with redirect_stdout(fake_out), redirect_stderr(fake_err):
        # process_stream_uppercase writes to the global sys.* if we call directly;
        # to keep it explicit in this demo, call it with the actual sys objects:
        # (but here we instead print directly to stdout/stderr to show redirect)
        for lineno, raw in enumerate(sample_input, start=1):
            line = raw.rstrip("\n")
            if line == "":
                print(f"captured warning: empty line {lineno}", file=sys.stderr)
            else:
                print(line.upper())  # goes to captured stdout

    captured_out = fake_out.getvalue()
    captured_err = fake_err.getvalue()
    return captured_out, captured_err


def demo_subprocess():
    """
    Example: run an external command and capture its stdout and stderr.
    This demonstrates subprocess.run with capture_output=True.
    """
    # We'll run a small shell command that writes to both stdout and stderr.
    # The command is POSIX; on Windows replace with a suitable command, e.g.:
    # python -c "import sys; print('out'); print('err', file=sys.stderr)"
    cmd = ['python', '-c', "import sys; print('hello from subprocess'); print('oops', file=sys.stderr)"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # result.stdout and result.stderr are captured as strings (text=True).
    return result.returncode, result.stdout, result.stderr


def main():
    parser = argparse.ArgumentParser(description="StdIO example: read stdin, write stdout/stderr, demo capture and subprocess.")
    parser.add_argument("--uppercase", action="store_true", help="Read stdin and write uppercased lines to stdout (warnings to stderr).")
    parser.add_argument("--fullread", action="store_true", help="Read entire stdin at once and print it to stdout.")
    parser.add_argument("--demo-capture", action="store_true", help="Run an in-process capture demo and print what was captured.")
    parser.add_argument("--demo-subprocess", action="store_true", help="Run a subprocess that emits to stdout/stderr and show captured outputs.")
    args = parser.parse_args()

    # If user wants the streaming uppercase behavior:
    if args.uppercase:
        # uses sys.stdin (file-like), sys.stdout, sys.stderr
        process_stream_uppercase(sys.stdin, sys.stdout, sys.stderr)
        return

    # If user wants to read entire stdin at once:
    if args.fullread:
        data = sys.stdin.read()
        if not data:
            print("No input received on stdin.", file=sys.stderr)
            return
        # demonstrate writing with sys.stdout.write (no extra newline)
        sys.stdout.write("FULLREAD RECEIVED:\n")
        sys.stdout.write(data)
        return

    # Demo capture
    if args.demo_capture:
        out, err = demo_capturing()
        print("Captured stdout:")
        print(out)
        print("Captured stderr:")
        print(err, file=sys.stdout)  # printed to real stdout so user sees it
        return

    # Demo subprocess
    if args.demo_subprocess:
        rc, out, err = demo_subprocess()
        print(f"Subprocess exited with code: {rc}")
        print("--- subprocess stdout ---")
        print(out, end="")
        print("--- subprocess stderr ---")
        print(err, end="", file=sys.stderr)
        return

    # Default behavior: show help-ish message and example of writing to stderr
    print("No mode selected. Try --uppercase, --fullread, --demo-capture, or --demo-subprocess.", file=sys.stdout)
    print("Example: echo 'hello' | python stdio_example.py --uppercase", file=sys.stderr)


if __name__ == "__main__":
    main()