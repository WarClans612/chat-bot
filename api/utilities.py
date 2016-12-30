import os

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
        return True
    except OSError as exception:
        return False

def write_to_file(filename, text, append=True, add_linefeed=True, encoding='utf-8'):
    if append is True:
        mode = 'a'
    else:
        mode = 'w'
    linefeed = ''
    if add_linefeed is True:
        linefeed = '\n'
    with open(filename, mode, encoding=encoding) as fw:
        fw.write(str(text) + linefeed)

def write_to_file_buffered(filename, text_list, append=True, encoding='utf-8'):
    debug('Writing file: {}'.format(filename))
    buffer_size = 10000
    counter = 0
    temp_str = ""
    for text in text_list:
        if counter <= buffer_size:
            temp_str = temp_str + text + '\n'
        else:
            write_to_file(filename, temp_str, append, False, encoding)
            temp_str = ""
            counter = 0
        counter += 1
    # Write remaining text
    if temp_str != "":
        write_to_file(filename, temp_str, append, False, encoding)