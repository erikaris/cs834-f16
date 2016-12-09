import os
from optparse import OptionParser

import errno
from tabulate import tabulate
from lib.galago import GalagoRank
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    parser = OptionParser(description='Generate a ranking using Galago')
    parser.set_usage(parser.get_usage().replace('\n', '') + ' <xml_file_input> [q1 ... qn]')
    parser.add_option('-g', '--galago', dest="galago_bin", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/galago/galago-3.10-bin/bin/galago',
                        help='Galago "home" directory')
    parser.add_option('-d', '--document', dest="document_dir", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/assignments/a4/code-report/cacm',
                        help='Document directory to be indexed')
    parser.add_option('-j', '--judgements', dest="judgements_file", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/assignments/a4/code-report/cacm.rel',
                      help='File .rel as galago eval judgments')
    parser.add_option('-r', '--result', dest="result_count", default='10', help='Number of result')

    (options, args) = parser.parse_args()
    options = vars(options)

    if len(args) < 2:
        parser.print_help()
        exit()


    out_dir = os.path.abspath('output')

    try: os.makedirs(out_dir)
    except OSError, e:
        if e.errno != errno.EEXIST: raise

    index_dir = os.path.join(os.path.pardir, 'index')
    xml_query_file = os.path.abspath(args[0])

    q_ids = []
    if len(args) > 1:
        q_ids = args[1:]

    recals_precisions = []
    galago = GalagoRank(options['galago_bin'], options['judgements_file'])
    if galago.index(options['document_dir'], index_dir):
        for q_id in q_ids:
            json_query_file = os.path.join(out_dir, 'query_{}.json'.format(q_id))
            res_file = os.path.join(out_dir, 'result_{}.res'.format(q_id))
            eval_file = os.path.join(out_dir, 'result_{}.eval'.format(q_id))

            json_query = galago.build_json_input(xml_query_file, json_query_file, q_id)

            rel_docs = galago.get_relevance_docs(q_id)
            res_docs = galago.search(index_dir, json_query_file, res_file, options['result_count'])

            precisions = galago.get_all_precisions(rel_docs, res_docs)
            recals = galago.get_all_recalls(rel_docs, res_docs)

            recals_precisions.append((recals, precisions))

            table = [['Position', ] + range(1, 11)]
            table.append(['Precision', ] + precisions)
            table.append(['Recall', ] + recals)

            print '#{}. {}'.format(json_query['number'], json_query['text'])
            print tabulate(table)
            print('')


    # Uninterpolated
    colors = 'rbgcmyk'
    sub_plots = []
    for i, (recals, precisions) in enumerate(recals_precisions):
        plt.plot(recals, precisions, marker='o', linestyle='None', color=colors[i])
        sp, = plt.plot(recals, precisions, marker='None', linestyle='--', color=colors[i])
        sub_plots.append(sp)

    plt.legend(sub_plots, ['Query #{}'.format(q_ids[0]),'Query #{}'.format(q_ids[1])])
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Uninterpolated Recall-Precision Graph')
    plt.savefig(os.path.join(out_dir, 'uninterpolated.png'))
    plt.show()


    # Interpolated
    # Reference : http://stackoverflow.com/questions/39836953/how-to-draw-a-precision-recall-curve-with-interpolation-in-python
    # plt.clf()

    colors = 'rbgcmyk'
    sub_plots = {}
    intp_precissions = []
    for j, (recals, precisions) in enumerate(recals_precisions):
        recals = np.asarray(recals)
        precisions = np.asarray(precisions)
        precisions2 = precisions.copy()

        i = recals.shape[0] - 2
        while i >= 0:
            if precisions[i + 1] > precisions[i]:
                precisions[i] = precisions[i + 1]
            i = i - 1

        intp_precission = []
        intp_precission.append(precisions.tolist()[1])
        for i in range(recals.shape[0] - 1):
            intp_precission.append(precisions.tolist()[i + 1])

            plt.plot((recals[i], recals[i]), (precisions[i], precisions[i + 1]), 'k-', label='', color=colors[j])  # vertical
            sp, = plt.plot((recals[i], recals[i + 1]), (precisions[i + 1], precisions[i + 1]), 'k-', label='', color=colors[j])  # horizontal
            plt.plot(recals, precisions2, marker='o', linestyle='None', color=colors[j])
            sub_plots[j] = sp

        intp_precissions.append(intp_precission)

    table = [['Recall', ] + np.arange(0,1,0.1).tolist()]
    table.append(['Query #{} '.format(q_ids[0]), ] + intp_precissions[0])
    table.append(['Query #{}'.format(q_ids[1]), ] + intp_precissions[1])

    print 'Interpolated Precision'
    print tabulate(table)
    print('')

    plt.legend(sub_plots.values(), ['Query #{}'.format(q_ids[0]), 'Query #{}'.format(q_ids[1])])
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Interpolated Recall-Precision Graph')
    plt.savefig(os.path.join(out_dir, 'interpolated.png'))
    plt.show()


    # Average Interpolated
    intp_precissions_transpose = np.array(intp_precissions).T.tolist()
    intp_precissions_avg = []
    for e in intp_precissions_transpose:
        intp_precissions_avg.append(float(sum(e)) / len(e))

    table = [['Recall', ] + np.arange(0, 1, 0.1).tolist()]
    table.append(['Query #{} '.format(q_ids[0]), ] + intp_precissions[0])
    table.append(['Query #{}'.format(q_ids[1]), ] + intp_precissions[1])
    table.append(['Average', ] + intp_precissions_avg)

    print 'Average Interpolated Precision'
    print tabulate(table)
    print('')

    colors = 'rbgcmyk'
    sub_plots = {}
    for j, (recals, precisions) in enumerate(recals_precisions):
        recals = np.asarray(recals)
        precisions = np.asarray(precisions)
        precisions2 = precisions.copy()

        i = recals.shape[0] - 2
        while i >= 0:
            if precisions[i + 1] > precisions[i]:
                precisions[i] = precisions[i + 1]
            i = i - 1

        for i in range(recals.shape[0] - 1):
            plt.plot((recals[i], recals[i]), (precisions[i], precisions[i + 1]), 'k--', label='',
                     color=colors[j])  # vertical
            sp, = plt.plot((recals[i], recals[i + 1]), (precisions[i + 1], precisions[i + 1]), 'k--', label='',
                           color=colors[j])  # horizontal
            plt.plot(recals, precisions2, marker='o', linestyle='None', color=colors[j])
            sub_plots[j] = sp

    intp_precissions_avg = [intp_precissions_avg[0], ] + intp_precissions_avg
    sp, = plt.plot(np.arange(0, 1.1, 0.1).tolist(), intp_precissions_avg, marker='None', linestyle='-', color=colors[2])
    sub_plots[j+1] = sp

    plt.legend(sub_plots.values(), ['Query #{}'.format(q_ids[0]), 'Query #{}'.format(q_ids[1]), 'Average'])
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Average Interpolated Recall-Precision Graph')
    plt.savefig(os.path.join(out_dir, 'avg-interpolated.png'))
    plt.show()
