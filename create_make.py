# ######################################## #
#          Author: Liam Dougherty          #
#           File: create_make.py           #
# Description: Creates a C or C++ Makefile #
# ######################################## #


import time
import os
import mmap
import sys


# ########### #
# MISC MACROS #
# ########### #
FILE_EXTS = {
    'LIB_SUF': '.a',
    'OBJ_SUF': '.o',
    'C_SUF_LOW': '.c',
    'C_SUF_UPP': '.C',
    'CPP_SUC': '.cpp',
    'ASSE_SUF_LOW': '.s',
    'ASSE_SUF_UPP': '.S'
}
VAR = '$'


# ############# #
# HEADER MACROS #
# ############# #
COMMENT = '#'
SPACE = ' '
BEG_COMMENT = COMMENT + SPACE
END_COMMENT = SPACE + COMMENT


# ################ #
# DEFINITON MACROS #
# ################ #
NAME_TARGET = VAR + '@'
FIR_PRE_REQ = VAR + '<'
ALL_PRE_REQ = VAR + '^'
FILE_STEM = VAR + '*'
WILDCARD = VAR + '%'


# ##################### #
# USER DEFINITON MACROS #
# ##################### #
SUF_NAME = '.SUFFIXES:'
PREC_NAME = '.PRECIOUS:'

COMP = VAR + '(COMPILE'
CXX = VAR + '(CXX)'
CXXFLAGS = VAR + '(CXXFLAGS)'

CPP = VAR + '(CPP)'
CC = VAR + '(CC)'
CFLAGS = VAR + '(CFLAGS)'
CPPFLAGS = VAR + '(CPPFLAGS)'
LDFLAGS = VAR + '(LDFLAGS)'

CPP_FILES = VAR + '(CPP_FILES)'
C_FILES = VAR + '(C_FILES)'
PS_FILES = VAR + '(PS_FILES)'
S_FILES = VAR + '(S_FILES)'
H_FILES = VAR + '(H_FILES)'
SOURCE_FILES = VAR + '(SOURCEFILES)'
OBJ_FILES = VAR + '(OBJFILES)'
CLIBFLAGS = VAR + '(CLIBFLAGS)'
CCLIBFLAGS = VAR + '(CCLIBFLAGS)'

C_VAL = CC + ' ' + CFLAGS + ' ' + CPPFLAGS + ' '
CC_VAL = CXX + ' ' + CXXFLAGS + ' ' + CPPFLAGS + ' '
CPP_VAL = CPP + ' ' + CPPFLAGS + ' '
SOURCE_VAL = H_FILES + ' ' + CPP_FILES + ' ' + C_FILES + ' ' + S_FILES

AR = VAR + '(AR)'
AR_FLAG = VAR + '(ARFLAGS)'
RM = VAR + '(RM)'


# ######### #
# GCC FLAGS #
# ######### #
OUTPUT = '-o'
COMPILE = '-c'
DEBUGGER = '-ggdb'
MATH_LIB = '-lm'


# ################## #
# Class Declarations #
# ################## #
class MultipleMainError(Exception):
    """
    Exception for multiple source files containing main functions.
    """
    def __init__(self, first_file, second_file, msg='Two Main functions found. Cannot generate Makefile.'):
        super().__init__(msg)
        print("Main found in two files:\n\t" + first_file + '\n\t' + second_file)

class PathNotFound(FileNotFoundError):
    """
    Exception for the path not existing.
    """
    def __init__(self, dir):
        super().__init__()
        print("Path Not Found: " + dir)

class Source_Files():
    """
    Contains all file and path information needed for Makefile.

    @var path (str): full path to source folder
    @var files (dict): holds information about the files
            key (str): file extensions
            val ( [ [str,...], str, int ] ): holds the list of files, all files as a string, and the number of files
    @var main ( [str, str] ): The filename, by itself, and the file extension of the source file with the main method
    @var obj ( [ [str,...], str, int ] ): see files key above
    @var total_files (int): total files held
    """
    def __init__(self, dir=None):
        """
        Initalizes the class.

        @param dir (str): the directory source files are contained in
            @default: None, the current directory gets searched
        """
        if dir:
            if os.path.exists(os.getcwd() + '\\' + dir):
                self.path = os.getcwd() + '\\' + dir + '\\'
            elif os.path.exists(dir):
                self.path = dir + '\\'
            else:
                raise PathNotFound(dir)
        else:
            self.path = os.getcwd() + '\\'
        
        self.files = {
            '.c': [[], '', 0],
            '.cpp': [[], '', 0],
            '.ps': [[], '', 0],
            '.s': [[], '', 0],
            '.h': [[], '', 0]
        }
        self.main = ['', '']
        self.obj = [[], '', 0]
        self.total_files = 0

    def add_file(self, file):
        """
        Adds a file to the class if it has the appropriate file extension.

        @param file (nt.DirEntry): The file to be added, potentially
        """
        split_filename = file.name.split('.')
        if len(split_filename) != 2:
            ext = 'None'
        else:
            name, ext = file.name.split('.')
            ext = '.' + ext.strip()
        if ext in self.files:
            self.files[ext.strip()][0].append(file.name)
            self.files[ext.strip()][1] += file.name + ' '
            self.files[ext.strip()][2] += 1
            self.total_files += 1
        if ext == '.c' or ext == '.cpp':
            with open(file.path) as reader:
                with mmap.mmap(reader.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_reader:
                    is_main = mmap_reader.find(b"int main(")
                    if is_main == -1:
                        self.obj[0].append(name + FILE_EXTS['OBJ_SUF'])
                        self.obj[1] += name + FILE_EXTS['OBJ_SUF'] + ' '
                        self.obj[2] += 1
                    else:
                        if self.get_full_main() != '':
                            raise MultipleMainError(self.get_full_main(), file.name)
                        self.main = [name, ext]
    
    def get_files(self, ext):
        """
        Gets all files with appropriate extension.

        @param ext (str): the file extensions to search for

        @return [str,...]: the list of files with appropriate extension
        """
        if ext.strip() in self.files:
            return self.files[ext.strip()][1]
        elif ext.strip() == '.o':
            return self.obj[1]

    def get_full_main(self):
        """
        Gets file with main method inside.

        @return (str): the main file
        """
        return self.main[0] + self.main[1]


# ################# #
# UTILITY FUNCTIONS #
# ################# #
def get_curr_time():
    """
    Gets the current local time.

    @format: Day Month Date Hour:Minute:Second Year 

    @return (str): the time
    """
    t = time.localtime()
    return time.strftime("%a %b %d %I:%M:%S %Y", t)

def create_var(name, val):
    """
    Creates a Makefile variable

    @param name (str): Variable name
    @param val (str): Variable value

    @return (str): the full variable.
    """
    return name + ' =\t' + val + '\n'


# ################## #
# DIR SCAN FUNCTIONS #
# ################## #
def read_header(path):
    """
    Reads the header text file for custom gcc compilation flags.
    Otherwise, it sets default flags.

    @path (str): The path to the header.txt file

    @return (str): The gcc flags
    """
    if os.path.exists(path+'header.txt'):
        header_msg = "Flags from 'header.txt'"
        flags = ""
        with open(path+'header.txt', 'r') as reader:
            for line in reader:
                line = line.strip()
                if line != '':
                    flags += line + '\n'
    else:
        header_msg = "Default Flags (create your own with a 'header.txt' file)"
        flags = create_var('CXXFLAGS', DEBUGGER) + create_var('CFLAGS', DEBUGGER)
        flags += create_var('CLIBFLAGS', MATH_LIB) + create_var('CCLIBFLAGS', '')
    header = create_header(header_msg)
    return header + flags + '\n' + create_ender(header_msg)

def gather_files(files):
    """
    Gathers all files inside directory, adds them to Source_Files, and outputs Makefile organization.

    @param files (Source_Files): obj containing files

    @return (str): Makefile variables for files
    """
    scan_files(files)

    cpp_files = create_var('CPP_FILES', files.get_files('.cpp'))
    c_files = create_var('C_FILES', files.get_files('.c'))
    ps_files = create_var('PS_FILES', files.get_files('.ps'))
    s_files = create_var('S_FILES', files.get_files('.s'))
    h_files = create_var('H_FILES', files.get_files('.h'))

    source = create_var('SOURCEFILES', SOURCE_VAL)
    precious = PREC_NAME + '\t' + SOURCE_FILES + '\n'

    obj_files = create_var('OBJFILES', files.get_files('.o'))
    
    return cpp_files + c_files + ps_files + s_files + h_files + source + precious + obj_files

def scan_files(files):
    """
    Scans the files directory and adds all neccesary files.

    @param files (Source_File): obj to place files into
    """
    with os.scandir(files.path) as entries:
        for entry in entries:
            if entry.is_file():
                files.add_file(entry)



# ######################### #
# GENERATE OUTPUT FUNCTIONS #
# ######################### #
def create_header(msg):
    """
    Creates a header with a message.

    @param msg (str): Message to display

    @return (str): Message header
    """
    length_msg = len(msg)
    header = BEG_COMMENT + (length_msg*COMMENT) + END_COMMENT + '\n'
    header += BEG_COMMENT + msg + END_COMMENT + '\n'
    header += BEG_COMMENT + (length_msg*COMMENT) + END_COMMENT + '\n\n'
    return header

def create_ender(msg):
    """
    Creates an ending comment to close header

    @param msg (str): Message to determine length of ender

    @return (str): Message ender
    """
    return '# ' + len(msg)*'#' + ' #\n\n'

def s_rule(suffix):
    """
    Determines rule for '.s' extensions (assembly files)

    @param suffix (str): suffix of file to have s_rule performed on

    @return (str) s rule
    """
    rule = suffix + FILE_EXTS['ASSE_SUF_LOW'] + ':\n\t'
    if suffix == '.cpp' or suffix == '.C' or suffix == '.s':
        suffix = '.cc'
    rule += CPP + ' ' + OUTPUT + ' ' + FILE_STEM + FILE_EXTS['ASSE_SUF_LOW'] + ' ' + FIR_PRE_REQ + '\n'
    return rule

def o_rule(suffix):
    """
    Determines rule for '.o' extensions (object files)

    @param suffix (str): suffix of file to have o_rule performed on

    @return (str) o rule
    """
    rule = suffix + FILE_EXTS['OBJ_SUF'] + ':\n\t'
    if suffix == '.cpp' or suffix == '.C' or suffix == '.s':
        suffix = '.cc'
    rule += COMP + suffix + ') ' + FIR_PRE_REQ + '\n'
    return rule

def a_rule(suffix):
    """
    Determines rule for '.a' extensions (static library files)

    @param suffix (str): suffix of file to have a_rule performed on

    @return (str) a rule
    """
    rule = suffix + FILE_EXTS['LIB_SUF'] + ':\n\t'
    if suffix == '.cpp' or suffix == '.C' or suffix == '.s':
        suffix = '.cc'
    rule += COMP + suffix + ') ' + OUTPUT + ' ' + WILDCARD + ' ' + FIR_PRE_REQ + '\n\t'
    rule += AR + ' ' + AR_FLAG + ' ' + NAME_TARGET + ' ' + WILDCARD + '\n\t'
    rule += RM + ' ' + WILDCARD + '\n'
    return rule

def create_definitions(files):
    """
    Creates all Makefile definitions

    @param files (Soruce_Files) obj containing neccesary files

    @return (str): all Makefile definitions
    """
    definition = SUF_NAME + '\n' + SUF_NAME + '\t.a .o .c .C .cpp .s .S\n'

    rules = o_rule('.c') + o_rule('.C') + o_rule('.cpp')
    rules += s_rule('.S') + o_rule('.s')
    rules += a_rule('.c') + a_rule('.C') + a_rule('.cpp') + '\n'

    user_vars = create_var('CC', 'gcc') + create_var('CXX', 'g++') + '\n'
    user_vars += create_var('RM', 'rm -f') + create_var('AR', 'ar')
    user_vars += create_var('LINK.c', C_VAL+LDFLAGS) + create_var('LINK.cc', CC_VAL+LDFLAGS)
    user_vars += create_var('COMPILE.c', C_VAL+COMPILE) + create_var('COMPILE.cc', CC_VAL+COMPILE)
    user_vars += create_var('CPP', CPP_VAL) + '\n'

    header_mak = read_header(files.path) + '\n\n'

    
    source_vars = gather_files(files)
    return definition + rules + user_vars + header_mak + source_vars

def create_target(files):
    """
    Determines the target, the main method file, and gcc command.

    @param files (Soruce_Files) obj containing neccesary files

    @return (str): Makefile target
    """
    file_head = files.main[0]
    file_ext = files.main[1]
    file_obj = files.main[0] + FILE_EXTS['OBJ_SUF']

    if file_ext == '.c':
        lang = CC
        flag = CFLAGS
        libflag = CLIBFLAGS
    else:
        lang = CXX
        flag = CXXFLAGS
        libflag = CCLIBFLAGS
    all_str = "all:\t" + file_head + '\n\n'
    target = files.main[0] + ':\t' + file_obj + ' ' + OBJ_FILES + '\n\t'
    target += lang + ' ' + flag + ' ' + OUTPUT + ' ' + file_head + ' ' 
    target += file_obj + ' ' + OBJ_FILES + ' ' + libflag + '\n\n'
    return all_str + target

#TODO too slow. Change how Source_Files is structured so grabbing headers, cs, cpps, etc is O(1)
def find_includes(files, filename):
    """
    Searches source files for all include preprocessor directives.

    @param files (Soruce_Files) obj containing neccesary files
    @param filename (str): the file to be searhced for's name

    @return (str): all header files dependent on filename
    """
    includes = ''
    filepath = files.path + filename
    with open(filepath, 'r') as reader:
        with mmap.mmap(reader.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_reader:
            for header in files.files['.h'][0]:
                found_byte = mmap_reader.find(header.encode('utf-8'))
                if found_byte == -1:
                    continue
                else:
                    preprocessor_start = found_byte
                    while mmap_reader[preprocessor_start] != ord('#') or found_byte-preprocessor_start > 100:
                        preprocessor_start -= 1
                    if mmap_reader[preprocessor_start:preprocessor_start+len('include')+1].decode('utf-8') == '#include':
                        includes += header + ' '
    return includes

#TODO too slow. Change how Source_Files is structured so grabbing headers, cs, cpps, etc is O(1)
def create_depend(files):
    """
    Looks for all dependencies on all source files.

    @param files (Soruce_Files) obj containing neccesary files

    @return (str): source files with their dependencies.
    """
    depends = ''
    for filename in files.obj[0]:
        depends += filename + ': '
        name_c = filename[:-2] + '.c'
        name_cpp = filename[:-2] + '.cpp'
        if name_c in files.files['.c'][0]:
            includes = find_includes(files, name_c)
        elif name_cpp in files.files['.cpp'][0]:
            includes = find_includes(files, name_cpp)
        depends += includes + '\n'
    return depends

#TODO add check for UNIX vs Windows
def create_misc(files):
    """
    Miscellaneous rules for extra make command manipulation.

    @param files (Soruce_Files) obj containing neccesary files

    @return (str): clean and realclean commands to clear directory on Windows
    """
    #archive = 'Archive:\tarchive.tgz\n\n'
    
    #archive_tgz = 'archive.tgz:\t' + SOURCE_FILES + ' Makefile\n\t'
    #archive_tgz += 'tar cf - ' + SOURCE_FILES + ' Makefile | gzip > archive.tgz\n\n'

    file_head = files.main[0]
    file_obj = files.main[0] + FILE_EXTS['OBJ_SUF']
    
    clean = 'clean:\n\t'
    clean += 'del -f ' + OBJ_FILES + ' ' + file_obj + ' ' + 'core\n\n'

    realclean = 'realclean:\tclean\n\t'
    realclean += 'del -f ' + file_head + '.exe\n'

    return clean + realclean

def output_Makefile(string, path):
    """
    Outputs the collected Makefile content to a Makefile in specified directory.

    @param string (str): All of the Makefile content
    @param path (str): The path for the Makefile creation.
    """
    with open(path+'Makefile', 'w') as writer:
        writer.write(string)


# ############# #
# MAIN FUNCTION #
# ############# #    
if __name__== "__main__":
    """
    Main method.
    Creates the Makefile based on directory's C/C++ code.
    """
    if len(sys.argv) > 1:
        files = Source_Files(dir=sys.argv[1])
    else:
        files = Source_Files()


    curr_time = get_curr_time()
    file_header = create_header(curr_time)
    #print(file_header,end='')

    def_header = create_header('Definitions')
    def_section = create_definitions(files)
    def_ender = create_ender('Definitions')
    def_total = def_header + def_section + def_ender
    #print(def_total,end='')

    target_header = create_header('Targets')
    target_section = create_target(files)
    target_ender = create_ender('Targets')
    target_total = target_header + target_section + target_ender
    #print(target_total,end='')

    depend_header = create_header('Dependencies')
    depend_section = create_depend(files)
    depend_ender = create_ender('Dependencies')
    depend_total = depend_header + depend_section + depend_ender
    #print(depend_total,end='')

    misc_header = create_header('Miscellaneous')
    misc_section = create_misc(files)
    misc_ender = create_ender('Miscellaneous')
    misc_total = misc_header + misc_section + misc_ender
    #print(misc_total,end='')

    output_Makefile(file_header + def_total + target_total + depend_total + misc_total, files.path)