import errno
import os
from optparse import OptionParser
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

    index_dir = os.path.join(os.path.pardir, 'index')
    xml_query_file = os.path.abspath(args[0])
    json_query_file = os.path.join(out_dir, 'query.json')
    rel_file = os.path.join(out_dir, 'result.rel')
    res_file = os.path.join(out_dir, 'result.res')
    eval_file = os.path.join(out_dir, 'result.eval')

    galago = GalagoRank(options['galago_bin'], options['judgements_file'])
    if galago.index(options['document_dir'], index_dir):
        maps = []
        ndcg_5s = []
        ndcg_10s = []
        prec_10s = []
        recip_ranks = []
        r_precs = []

        for q_id in range(1, 64):
            print 'Processing Query #{}'.format(q_id)

            json_query_file = os.path.join(out_dir, 'query_{}.json'.format(q_id))
            res_file = os.path.join(out_dir, 'result_{}.res'.format(q_id))
            eval_file = os.path.join(out_dir, 'result_{}.eval'.format(q_id))

            json_query = galago.build_json_input(xml_query_file, json_query_file, q_id)

            rel_docs = galago.get_relevance_docs(q_id)
            res_docs = galago.search(index_dir, json_query_file, res_file, max(len(rel_docs), int(options['result_count'])))

            galago.eval(options['judgements_file'], res_file, eval_file)

            maps.append(galago.get_map(rel_docs, res_docs))
            ndcg_5s.append(galago.get_ndcg(5, rel_docs, res_docs))
            ndcg_10s.append(galago.get_ndcg(10, rel_docs, res_docs))
            prec_10s.append(galago.get_all_precisions(rel_docs, res_docs)[9])
            recip_ranks.append(galago.get_reciprocal_rank(rel_docs, res_docs))
            r_precs.append(galago.get_r_precision(rel_docs, res_docs))


        print 'Mean Average Precision   = {}'.format(float(sum(maps)) / len(maps))
        print 'NDCG @5                  = {}'.format(float(sum(ndcg_5s)) / len(ndcg_5s))
        print 'NDCG @10                 = {}'.format(float(sum(ndcg_10s)) / len(ndcg_10s))
        print 'Precision @10            = {}'.format(float(sum(prec_10s)) / len(prec_10s))
        print 'Reciprocal Rank          = {}'.format(float(sum(recip_ranks)) / len(recip_ranks))
        print 'R-Precision              = {}'.format(float(sum(r_precs)) / len(r_precs))
