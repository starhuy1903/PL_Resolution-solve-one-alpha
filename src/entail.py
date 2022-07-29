import sys
import getopt
import copy


def read_file(input_file):
    """
    :param: input_file: input file's directory
    :return: dnf alpha: list, KB: list
    """
    with open(input_file, "r") as fin:
        # read 1 line alpha
        clause = fin.readline().replace('OR', '')
        clause_lst = []
        for literal in clause.split():
            if literal[0] == '-':
                clause_lst.append(literal[1])
            else:
                clause_lst.append('-'+literal)

        alpha = clause_lst

        # read KB
        n_KB = int(fin.readline())
        KB = []
        for _ in range(n_KB):
            clause = list(filter(None, fin.readline().replace(
                'OR', '').rstrip('\n').split(' ')))
            KB.append(clause)

    return alpha, KB


def negative(literal):
    """
    ['A'] -> ['-A']
    ['-A'] -> ['A']
    """
    literal_copy = copy.deepcopy(literal)
    if literal[0] == '-':
        return literal_copy[1:]
    else:
        return '-' + literal_copy


def resolve(clause_A, clause_B):
    """
    :param clause_a: clause
    :param clause_b: clause
    :return: res as resolved clause of 2 param
    """
    clause_a = copy.deepcopy(clause_A)
    clause_b = copy.deepcopy(clause_B)
    if (len(clause_a) == 1 and len(clause_a) == len(clause_b)):
        if clause_a[0] == negative(clause_b[0]):
            return "{}"

    for literal in clause_A:
        if negative(literal) in clause_B:
            clause_b.remove(negative(literal))
            clause_a.remove(literal)
            result = clause_a + clause_b
            return list(set(result))
    return []


def is_equivalent(clause):
    """
    The clause [A,B,-B] is considered equivalent to [A,True] and hence equivalent to True.
    Deducing that True is true is not very helpful.
    Therefore,any clause in which two complementary literals appear can be discarded.
    :return: True if clause is useless 
    """
    for literal in clause:
        if negative(literal) in clause:
            return True
    return False


def comparator_form(literal):
    """
    ['A'] -> ['A']
    ['-A'] -> ['A']
    """
    if literal[0] == "-":
        return literal[1:]
    else:
        return literal


def trim(clause):
    """
    Bubble sort for clause - by alphabet
    :param clause:
    :return: sorted clause
    """
    i = 0
    while(i < len(clause)-1):
        j = i+1
        while(j < len(clause)):
            if clause[i] == clause[j]:
                del clause[j]
                j -= 1
                i -= 1
            j += 1
        i += 1

    for i in range(len(clause)-1):
        for j in range(i+1, len(clause)):
            if (comparator_form(clause[i]) > comparator_form(clause[j])):
                clause[i], clause[j] = clause[j], clause[i]
    return clause


def to_string(clause):
    """
    trans to string to write file output
    :param clause:
    :return: string
    """
    ans = ""
    for i in range(len(clause)-1):
        ans += clause[i]
        ans += " OR "
    ans += clause[-1]
    ans += "\n"
    return ans


def PL_RESOLUTION(negative_alpha, KB, output_file):
    """
    Check if KB entails alpha and write to output_file
    """
    with open(output_file, "w") as fout:
        clauses = KB
        clauses.append(negative_alpha)

        is_entailed = False
        while True:
            new_clauses = []
            num_of_res = 0
            string_write = ""
            for i in range(len(clauses)-1):
                for j in range(i+1, len(clauses)):
                    new_clause = resolve(clauses[i], clauses[j])
                    new_clause = trim(new_clause)
                    # print(num_of_res,clauses[i], "+", clauses[j], "=",new_clause) #$
                    if new_clause == [] or (new_clause in clauses) or (new_clause in new_clauses) or is_equivalent(new_clause):
                        continue
                    if new_clause == "{}":  # New clause is dump
                        is_entailed = True
                    string_write += to_string(
                        new_clause) if new_clause != '{}' else '{}\n'
                    print('[^] Resolve', clauses[i], "and",
                          clauses[j], "get", new_clause)
                    num_of_res += 1
                    new_clauses.append(new_clause)
            string_write = str(num_of_res) + "\n" + string_write
            fout.write(string_write)
            if new_clauses == []:  # Can not resolve new clause.
                string_write += "0\nNO"
                fout.write("NO")
                return False
            elif is_entailed:
                string_write += "\nYES"
                fout.write("YES")
                return True

            clauses += new_clauses  # Add new clause to KB


def DNF_to_CNF(alpha):
    return trim(sorted(set(alpha)))


def main(argv):
    input_file = '../input/1-3-1.txt'
    output_file = '../output/out_1-3-1.txt'
    try:
        opts, args = getopt.getopt(
            argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('entail.py -i <input_file> -o <output_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('entail.py -i <input_file> -o <output_file>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    # read data from file
    alpha, KB = read_file(input_file)
    print(f'[!] Finished read file {input_file}')
    print('[I] KB:', KB)

    # convert alpha to not alpha
    not_alpha = DNF_to_CNF(alpha)
    print('[I] NOT alpha:', not_alpha)

    p = PL_RESOLUTION(not_alpha, KB, output_file)

    if p:
        print("[R] KB entails alpha.")
    else:
        print("[R] KB does not entail alpha.")
    print(f"[!] Finished write to {output_file}.")


if __name__ == "__main__":
    main(sys.argv[1:])
