#!./venv python
# -*- coding: utf-8 -*-
"""
evaluation.py: evaluating KGQAn online service against QALD-3 benchmark
"""
___lab__ = "CoDS Lab"
__copyright__ = "Copyright 2020-29, GINA CODY SCHOOL OF ENGINEERING AND COMPUTER SCIENCE, CONCORDIA UNIVERSITY"
__credits__ = ["CoDS Lab"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "CODS Lab"
__email__ = "essam.mansour@concordia.ca"
__status__ = "debug"
__created__ = "2020-02-07"

import os
import json
import time
import traceback
import csv
import argparse

import joblib
from termcolor import colored, cprint
from itertools import count
import xml.etree.ElementTree as Et
import numpy as np

from kgqan.kgqan import KGQAn

file_dir = os.path.dirname(os.path.abspath(__file__))

file_name = os.path.join(file_dir, "qald9/qald-9-test-multilingual.json")


def generate_dump_file(dump_data, max_answers, max_Vs, max_Es, limit_VQuery, limit_EQuery, filter_enabled):
    # Create a formatted string with all parameters
    filename = (
        f"config_"
        f"nMaxAns-{max_answers}_"
        f"nMaxVs-{max_Vs}_"
        f"nMaxEs-{max_Es}_"
        f"nLimVQuery-{limit_VQuery}_"
        f"nLimEQuery-{limit_EQuery}_"
        f"filter-{filter_enabled}"
    )

    # Ensure the filename is filesystem-safe by replacing spaces or special characters if necessary
    safe_filename = filename.replace(" ", "_").replace(":", "-")

    joblib.dump(dump_data, safe_filename + ".joblib", compress=5)


if __name__ == '__main__':
    root_element = Et.Element('dataset')
    root_element.set('id', 'dbpedia-test')
    author_comment = Et.Comment(f'created by CoDS Lab')
    root_element.append(author_comment)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    total_time = 0
    total_understanding_time = 0
    total_linking_time = 0
    total_execution_time = 0

    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", type=str, default="True", help="argument to enable filtration")
    args = parser.parse_args()
    filter = args.filter.lower() == 'true'

    # The main param: 
    # max no of vertices and edges to annotate the PGP
    # max no of SPARQL queries to be generated from PGP 
    max_Vs = 1
    max_Es = 21
    max_answers = 41
    limit_VQuery = 400
    limit_EQuery = 25


    max_Vs = 3
    max_Es = 21
    max_answers = 41
    limit_VQuery = 400
    limit_EQuery = 25

    with open(file_name) as f:
        qald9_testset = json.load(f)
    dataset_id = qald9_testset['dataset']['id']
    MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es,
                    n_limit_VQuery=limit_VQuery, n_limit_EQuery=limit_EQuery, filtration_enabled=filter)
    qCount = count(1)

    kgqan_qald9 = {"dataset": {"id": dataset_id}, "questions": []}
    count_arr = []
    dump_data = []
    for i, question in enumerate(qald9_testset['questions']):

        # [27, 63, 86, 116, 160, 198]
        # 63- the correct V is Scarface_(rapper) and we get Scarface
        # 116 - Who was called Rodzilla - use nick predicate
        # if int(question['id']) not in [1, 14, 31, 88, 164, 177]:
        #     continue

        # hard to annotate/link with the KG
        # if int(question['id']) in [167]:
        #     continue

        # Questions with no detected Relation or NE
        # R [214, 199, 137, 136, 132, 124, 111, 10, 84, 213, 162]
        # E [168, 166, 140, 123, 59, 39, 83, 209, 212]
        # Questions with one NE
        # if int(question['id']) not in [99, 98, 86, 64, 56, 44, 37, 31, 29, 23, 68, 22, 203, 197, 196, 188, 187, 62,
        #                               173, 160, 158, 155, 150, 149, 25, 143, 139, 134, 128, 122, 117, 104, 1, 178,
        #                               129, 183, 181, 7, 135, 50, 71, 105, 52, 102, 21, 34, 145, 154, 198]:
        #     continue

        # if int(question['id']) not in [81]:
        #     continue

        # if int(question['id'] <= 1097):
        #     continue
        # if int(question['id']) in [10, 45, 64, 69, 70, 100, 106, 114, 126, 132, 153, 165, 167, 182, 189, 194, 207,
        #                            221, 248, 258, 268, 279, 289, 340, 359, 362, 366, 377, 394, 398, 427, 516, 520,
        #                            524, 536, 547, 549, 553, 563, 584, 588, 594, 598, 622, 625, 641, 664, 669, 713,
        #                            721, 729, 742, 743, 753, 756, 758, 760, 768, 769, 779, 801, 802, 815, 826, 838,
        #                            844, 887, 896, 914, 929, 934, 938, 942, 1016, 1017, 1024, 1066, 1077, 1082, 1093,
        #                            1097]:
        #     continue

        # long time queries 51
        # if int(question['id']) in [27, 167]:
        #     continue

        qc = next(qCount)
        # question_text = ''
        for language_variant_question in question['question']:
            if language_variant_question['language'] == 'en':
                question_text = language_variant_question['string'].strip()
                break

        text = colored(f"[PROCESSING: ] Question count: {qc}, ID {question['id']}  >>> {question_text}", 'blue',
                       attrs=['reverse', 'blink'])
        cprint(f"== {text}  ")

        st = time.time()
        # question_text = 'Which movies starring Brad Pitt were directed by Guy Ritchie?'
        # question_text = 'When did the Boston Tea Party take place and led by whom?'
        try:
            answers, nodes, edges, understanding_time, linking_time, execution_time, sparkqls \
                = MyKGQAn.ask(question_text=question_text, answer_type=question['answertype'],
                              question_id=question['id'], knowledge_graph='dbpedia', )
            dump_data.append((question, answers, sparkqls))
        except Exception as e:
            traceback.print_exc()
            continue

        all_bindings = list()
        for answer in answers:
            if answer['results'] and answer['results']['bindings']:
                all_bindings.extend(answer['results']['bindings'])

        try:
            if 'results' in question['answers'][0]:
                question['answers'][0]['results']['bindings'] = all_bindings.copy()
                all_bindings.clear()
        except:
            question['answers'] = []

        kgqan_qald9['questions'].append(question)

        et = time.time()
        total_time = total_time + (et - st)
        total_understanding_time = total_understanding_time + understanding_time
        total_linking_time = total_linking_time + linking_time
        total_execution_time = total_execution_time + execution_time
        text = colored(f'[DONE!! in {et - st:.2f} SECs]', 'green', attrs=['bold', 'reverse', 'blink', 'dark'])
        cprint(f"== {text} ==")

    generate_dump_file(dump_data, max_answers, max_Vs, max_Es, limit_VQuery, limit_EQuery, filter)
    # break
    text1 = colored(f'total_time = [{total_time:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    text2 = colored(f'avg time = [{total_time / qc:.2f} sec]', 'yellow', attrs=['reverse', 'blink'])
    cprint(f"== QALD 9 Statistics : {qc} questions, Total Time == {text1}, Average Time == {text2} ")
    cprint(f"== Understanding : {qc} questions, Total Time == {total_understanding_time}, Average Time == {total_understanding_time / qc} ")
    cprint(f"== Linking : {qc} questions, Total Time == {total_linking_time}, Average Time == {total_linking_time / qc} ")
    cprint(f"== Execution : {qc} questions, Total Time == {total_execution_time}, Average Time == {total_execution_time / qc} ")
    response_time = [{"Question Understanding": total_understanding_time / qc,
                      "Linking": total_linking_time / qc,
                      "Execution": total_execution_time / qc}]

    with open(os.path.join(file_dir, f'output/qald.json'), encoding='utf-8', mode='w') as rfobj:
        json.dump(kgqan_qald9, rfobj)
        rfobj.write('\n')

    field_names = response_time[0].keys()
    with open(os.path.join(file_dir, f'output/qald_response_time.csv'), mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(response_time)

    # with open(os.path.join(file_dir, f'output/MyKGQAn_result_{timestr}_MaxAns{max_answers}_MaxVs{max_Vs}_MaxEs{max_Es}'
    #           f'_limit_VQuery{limit_VQuery}_limit_VQuery{limit_EQuery}_TTime{total_time:.2f}Sec_Avgtime{total_time / qc:.2f}Sec.json'),
    #           encoding='utf-8', mode='w') as rfobj:
    #     json.dump(kgqan_qald9, rfobj)
    #     rfobj.write('\n')
