#!/usr/bin/python
import argparse
import os
import re
import shutil
import subprocess

DIR=os.path.dirname(os.path.realpath(__file__))

# Color terminal output
def color(s, color):
    return "\033[1;%dm%s\033[1;m" % (color, s)

def red(s):
    return color(s, 31)

def grey(s):
    return color(s, 30)

def validate_shader(shader_file):
    extension = os.path.splitext(shader_file)[1]
    tmp_file_name = "tmp%s" % extension

    # Load in the prefix for the shader first and then append the actual shader
    shutil.copyfile(os.path.join(DIR, "prefix/prefix%s" % extension), os.path.join(DIR, tmp_file_name))
    with open(shader_file, 'r') as f:
        shader = f.read()
    with open(os.path.join(DIR, tmp_file_name), 'a') as f:
        f.write(shader)

    # Run essl_to_glsl over the shader, reporting any errors
    p = subprocess.Popen([os.path.join(DIR, "angle/essl_to_glsl_osx"),
                          "-s=w",
                          "-x=d",
                          os.path.join(DIR, tmp_file_name)],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    ret_code = p.wait()
    os.remove(os.path.join(DIR, tmp_file_name))

    if ret_code != 0:
        header = "ERROR in %s:" % shader_file
        error = red(header + "\n")
        error += grey(len(header) * "=" + "\n")
        error += "".join(p.stdout.readlines()[1:-4])
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
