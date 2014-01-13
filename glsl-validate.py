#!/usr/bin/python
import argparse
import os
import platform
import re
import shutil
import subprocess

DIR=os.path.dirname(os.path.realpath(__file__))

# Select the correct essl_to_glsl executable for this platform
if platform.system() == 'Darwin':
    ESSL_TO_GLSL = os.path.join(DIR, "angle/essl_to_glsl_osx")
elif platform.system() == 'Linux':
    ESSL_TO_GLSL = os.path.join(DIR, "angle/essl_to_glsl_linux")
elif platform.system() == 'Windows':
    ESSL_TO_GLSL = os.path.join(DIR, "angle/essl_to_glsl_win.exe")
else:
    print "Unsupported platform"
    exit(1)

# Color terminal output
def color(s, color):
    return "\033[1;%dm%s\033[1;m" % (color, s)

def grey(s):
    return color(s, 30)

def validate_shader(shader_file):
    extension = os.path.splitext(shader_file)[1]
    tmp_file_name = "tmp%s" % extension

    # Load in the prefix for the shader first and then append the actual shader
    with open(os.path.join(DIR, "prefix/prefix%s" % extension), 'r') as f:
        shader_prefix = f.read()
    with open(shader_file, 'r') as f:
        shader = f.read()
    with open(os.path.join(DIR, tmp_file_name), 'w') as f:
        f.write(shader_prefix)
        f.write(shader)

    # Run essl_to_glsl over the shader, reporting any errors
    p = subprocess.Popen([ESSL_TO_GLSL,
                          "-s=w",
                          "-x=d",
                          os.path.join(DIR, tmp_file_name)],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    ret_code = p.wait()
    os.remove(os.path.join(DIR, tmp_file_name))

    if ret_code != 0:
        # Get the number of lines in the prefix file, so we can report line numbers correctly
        shader_prefix_lines = shader_prefix.count("\n")
        raw_errors = p.stdout.readlines()[1:-4]

        # Write out formatted errors
        header = "ERROR in %s:" % shader_file
        error = ""
        for e in raw_errors:
            # Error format is: 'ERROR: 0:<line number>: <error message>
            details = re.match("ERROR: 0:(\d+): (.*)", e)
            line_number = int(details.group(1)) - shader_prefix_lines
            error_message = details.group(2)
            error_format = grey("%s:%d ") + "%s\n"
            error += error_format % (shader_file, line_number, error_message)
        print error
        exit(1)

def standalone():
    parser = argparse.ArgumentParser(description='Validate three.js shaders')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                               help='files to validate')
    args = parser.parse_args()
    files = args.files
    bad_extensions = filter(lambda f: not re.match('^\.(vert|frag)$', os.path.splitext(f)[1]), files)
    for f in bad_extensions:
        print "Invalid file: %s, only support .frag and .vert files" % f
        exit(1)

    map(validate_shader, files)

if __name__ == "__main__":
    standalone()
