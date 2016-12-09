import errno
import os
from optparse import OptionParser
import matplotlib.pyplot as plt
import numpy
from lib.galago import GalagoRank

if __name__ == '__main__':
    parser = OptionParser(description='Generate a ranking using Galago')
    parser.set_usage(parser.get_usage().replace('\n', '') + ' <xml_file_input>')
    parser.add_option('-g', '--galago', dest="galago_bin", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/galago/galago-3.10-bin/bin/galago',
                        help='Galago "home" directory')
    parser.add_option('-d', '--document', dest="document_dir", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/assignments/a4/code-report/cacm',
                        help='Document directory to be indexed')
    parser.add_option('-j', '--judgements', dest="judgements_file", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/assignments/a4/code-report/cacm.rel',
                      help='File .rel as galago eval judgments')
    parser.add_option('-r', '--result', dest="result_count", default='10', help='Number of result')

    (options, args) = parser.parse_args()
    options = vars(options)

    if len(args) < 1:
        parser.print_help()
        exit()


    out_dir = os.path.abspath('output')

    try: os.makedirs(out_dir)
    except OSError, e:
        if e.errno != errno.EEXIST: raise

    index_dir = os.path.abspath(os.path.join(os.path.pardir, 'index'))
    xml_query_file = os.path.abspath(args[0])
    json_query_file = os.path.join(out_dir, 'query.json')
    rel_file = os.path.join(out_dir, 'result.rel')
    res_file = os.path.join(out_dir, 'result.res')
    eval_file = os.path.join(out_dir, 'result.eval')

    recals_precisions = []
    maps = []
    ndcg_5s = []
    ndcg_10s = []
    prec_10s = []
    galago = GalagoRank(options['galago_bin'], options['judgements_file'])
    if galago.index(options['document_dir'], index_dir):
        for q_id in range(1, 64):
            json_query_file = os.path.join(out_dir, 'query_{}.json'.format(q_id))
            res_file = os.path.join(out_dir, 'result_{}.res'.format(q_id))
            eval_file = os.path.join(out_dir, 'result_{}.eval'.format(q_id))

            json_query = galago.build_json_input(xml_query_file, json_query_file, q_id)

            rel_docs = galago.get_relevance_docs(q_id)
            res_docs = galago.search(index_dir, json_query_file, res_file, options['result_count'])

            precisions = galago.get_all_precisions(rel_docs, res_docs)
            recals = galago.get_all_recalls(rel_docs, res_docs)

            map = galago.get_map(rel_docs, res_docs)
            maps.append(map)
            ndcg_5s.append(galago.get_ndcg(5, rel_docs, res_docs))
            ndcg_10s.append(galago.get_ndcg(10, rel_docs, res_docs))
            prec_10s.append(galago.get_all_precisions(rel_docs, res_docs)[9])

            recals_precisions.append((recals, precisions))

            print 'Processing Query #{} ==> avg. precision={}'.format(q_id, map)

    # Calculate avg of map
    print 'Mean Average Precision of All Queries    = {}'.format(float(sum(maps)) / len(maps))
    print 'NDCG @5                                  = {}'.format(float(sum(ndcg_5s)) / len(ndcg_5s))
    print 'NDCG @10                                 = {}'.format(float(sum(ndcg_10s)) / len(ndcg_10s))
    print 'Precision @10                            = {}'.format(float(sum(prec_10s)) / len(prec_10s))

    # Graph
    # Transpose
    recals_precisions = numpy.asarray(recals_precisions).T.tolist()

    recalls = []
    precisions = []
    for d_recalls, d_precisions in recals_precisions:
        recalls.append(float(sum(d_recalls)) / len(d_recalls))
        precisions.append(float(sum(d_precisions)) / len(d_precisions))

    plt.plot(recals, precisions, marker='o', linestyle='None', color='r')
    plt.plot(recals, precisions, marker='None', linestyle='--', color='r')

    plt.xlabel('Precision')
    plt.ylabel('Recall')
    plt.title('Recall-Precision Graph')
    plt.savefig(os.path.join(out_dir, 'recall-precision.png'))
    plt.show()
    plt.clf()
